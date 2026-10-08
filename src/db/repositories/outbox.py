import uuid
from abc import ABC, abstractmethod
from collections.abc import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.outbox import OutboxEvent


class IOutboxRepository(ABC):
    @abstractmethod
    async def add(self, event: OutboxEvent) -> None: ...

    @abstractmethod
    async def get_unprocessed(self, limit: int) -> Sequence[OutboxEvent]: ...

    @abstractmethod
    async def mark_as_processed(self, event_id: uuid.UUID) -> None: ...


class SqlAlchemyOutboxRepository(IOutboxRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, event: OutboxEvent) -> None:
        self.session.add(event)

    async def get_unprocessed(self, limit: int = 10) -> Sequence[OutboxEvent]:
        stmt = (
            select(OutboxEvent)
            .where(OutboxEvent.processed.is_(False))
            .order_by(OutboxEvent.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def mark_as_processed(self, event_id: uuid.UUID) -> None:
        stmt = (
            update(OutboxEvent).where(OutboxEvent.id == event_id).values(processed=True)
        )
        await self.session.execute(stmt)
