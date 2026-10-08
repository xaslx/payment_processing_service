import asyncio
import logging
import random
from uuid import UUID

import httpx
from dishka.integrations.faststream import FromDishka, inject
from faststream import Logger
from faststream.rabbit import RabbitRouter
from tenacity import (
    before_sleep_log,
    retry,
    stop_after_attempt,
    wait_exponential,
)

from src.broker.queues import main_queue
from src.db.uow import IUnitOfWork
from src.models.payment import PaymentStatus
from src.schemas.outbox import OutboxSchema

router = RabbitRouter()

logger = logging.getLogger(__name__)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=10),
    reraise=True,
    before_sleep=before_sleep_log(logger, logging.INFO),
)
async def send_webhook(
    webhook_url: str,
    payment_id: UUID,
    status: PaymentStatus,
    log: Logger,
) -> None:
    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=5.0)) as client:
        response = await client.post(
            webhook_url,
            json={
                "payment_id": str(payment_id),
                "status": status.value,
            },
        )
        response.raise_for_status()
        log.info(f"Вебхук для {payment_id} успешно отправлен")


async def process_payment_logic(
    payment_id: UUID, uow: IUnitOfWork, log: Logger
) -> None:
    log.info(f"Начало обработки платежа {payment_id}")

    async with uow:
        payment = await uow.payments.get_by_id(payment_id)
        if not payment:
            log.error(f"Платеж {payment_id} не найден в базе")
            return
        if payment.status != PaymentStatus.PENDING:
            log.info(
                f"Платеж {payment_id} уже в статусе {payment.status.value}, пропуск"
            )
            return

    await asyncio.sleep(random.uniform(2, 5))

    new_status = (
        PaymentStatus.SUCCEEDED
        if random.random() >= 0.1
        else PaymentStatus.FAILED
    )
    if new_status == PaymentStatus.FAILED:
        log.warning(f"Эмуляция ошибки шлюза для платежа {payment_id}")

    webhook_url: str | None = None
    async with uow:
        payment = await uow.payments.get_by_id(payment_id)
        if not payment:
            log.error(f"Платеж {payment_id} не найден в базе")
            return
        if payment.status != PaymentStatus.PENDING:
            log.info(
                f"Платеж {payment_id} уже в статусе {payment.status.value}, пропуск"
            )
            return

        payment.status = new_status
        webhook_url = payment.webhook_url
        await uow.commit()
        log.info(f"Платеж {payment_id} обновлён до статуса {new_status.value}")

    if webhook_url:
        await send_webhook(webhook_url, payment_id, new_status, log)


@router.subscriber(main_queue)
@inject
async def handle_msg(
    event: OutboxSchema, logger: Logger, uow: FromDishka[IUnitOfWork]
):
    payment_id = event.payload.get("payment_id")
    await process_payment_logic(UUID(payment_id), uow, logger)
