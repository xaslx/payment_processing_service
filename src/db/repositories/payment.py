from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.payment import Payment


class IPaymentRepository(ABC):
    @abstractmethod
    async def add(self, payment: Payment) -> None: ...

    @abstractmethod
    async def get_by_id(self, payment_id: UUID) -> Payment | None: ...

    @abstractmethod
    async def get_by_idempotency_key(self, key: str) -> Payment | None: ...


class SqlAlchemyPaymentRepository(IPaymentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, payment: Payment) -> None:
        self.session.add(payment)

    async def get_by_id(self, payment_id: UUID) -> Payment | None:
        return await self.session.get(Payment, payment_id)

    async def get_by_idempotency_key(self, key: str) -> Payment | None:
        stmt = select(Payment).where(Payment.idempotency_key == key)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
