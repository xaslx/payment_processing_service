from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka as Depends
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Header, Path, Security, status

from src.api.dependencies import verify_api_key
from src.schemas.payment import (
    PaymentCreate,
    PaymentCreatedResponse,
    PaymentDetailResponse,
)
from src.use_cases.payment.create import CreatePaymentUseCase
from src.use_cases.payment.get_detail import GetPaymentUseCase

router: APIRouter = APIRouter()


@router.post(
    "/",
    response_model=PaymentCreatedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Создание нового платежа",
    description=(
        "Принимает данные платежа, проверяет Idempotency-Key и создаёт платёж."
    ),
    responses={
        status.HTTP_202_ACCEPTED: {
            "description": "Запрос принят. Платеж создан или уже существовал.",
        },
        status.HTTP_409_CONFLICT: {
            "description": "Конфликт идемпотентности или платёж уже существует.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Невалидный или отсутствующий API Key"
        },
    },
)
@inject
async def create_payment(
    payload: PaymentCreate,
    use_case: Depends[CreatePaymentUseCase],
    idempotency_key: Annotated[
        str,
        Header(
            alias="Idempotency-Key",
            description="Уникальный ключ",
            max_length=100,
        ),
    ],
    api_key: str = Security(verify_api_key),
):
    return await use_case.execute(schema=payload, idempotency_key=idempotency_key)


@router.get(
    "/{payment_id}",
    response_model=PaymentDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить детали платежа",
    description=(
        "Возвращает полную информацию о платеже по UUID. "
        "Требуется API Key в заголовках."
    ),
    responses={
        status.HTTP_200_OK: {"description": "Успешный возврат данных платежа"},
        status.HTTP_404_NOT_FOUND: {
            "description": "Платеж с таким ID не найден",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Невалидный или отсутствующий API Key"
        },
    },
)
@inject
async def get_payment_info(
    payment_id: Annotated[
        UUID,
        Path(
            description="Идентификатор транзакции в формате UUID",
            examples=["123ec456-f10b-12d3-a498-64641651656a"],
        ),
    ],
    use_case: Depends[GetPaymentUseCase],
    api_key: str = Security(verify_api_key),
):
    return await use_case.execute(payment_id=payment_id)
