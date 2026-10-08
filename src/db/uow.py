from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.outbox import IOutboxRepository, SqlAlchemyOutboxRepository
from src.db.repositories.payment import IPaymentRepository, SqlAlchemyPaymentRepository


class IUnitOfWork(ABC):
    payments: IPaymentRepository
    outbox: IOutboxRepository

    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork": ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

    @abstractmethod
    async def flush(self) -> None: ...


class SqlAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.payments = SqlAlchemyPaymentRepository(session)
        self.outbox = SqlAlchemyOutboxRepository(session)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()

    async def commit(self):
        await self.session.commit()


    async def rollback(self):
        await self.session.rollback()

    async def flush(self):
        await self.session.flush()
