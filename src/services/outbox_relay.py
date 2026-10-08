import asyncio
import logging
from collections.abc import Sequence

from dishka import AsyncContainer
from faststream.rabbit import RabbitBroker

from src.broker.queues import dlq_queue, main_queue
from src.db.uow import IUnitOfWork
from src.models.outbox import OutboxEvent
from src.schemas.outbox import OutboxSchema

logger = logging.getLogger(__name__)


class OutboxRelay:
    def __init__(self, container: AsyncContainer, broker: RabbitBroker):
        self.container = container
        self.broker = broker
        self._queues_declared = False

    async def _ensure_queues(self) -> None:
        if self._queues_declared:
            return
        await self.broker.declare_queue(dlq_queue)
        await self.broker.declare_queue(main_queue)
        self._queues_declared = True

    async def run(self) -> None:
        while True:
            try:
                await self._ensure_queues()
                async with self.container() as request_container:
                    uow: IUnitOfWork = await request_container.get(IUnitOfWork)
                    async with uow:
                        events: Sequence[OutboxEvent] = (
                            await uow.outbox.get_unprocessed(limit=10)
                        )
                        if events:
                            for event in events:
                                event_schema = OutboxSchema.model_validate(event)
                                await self.broker.publish(
                                    message=event_schema,
                                    queue=main_queue,
                                    mandatory=True,
                                    persist=True,
                                )
                                await uow.outbox.mark_as_processed(event.id)

                            await uow.commit()

                await asyncio.sleep(2)
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Outbox relay failed")
                await asyncio.sleep(5)
