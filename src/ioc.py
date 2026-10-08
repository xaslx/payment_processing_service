from collections.abc import AsyncIterable

from dishka import Provider, Scope, from_context, provide
from faststream.rabbit import RabbitBroker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.config import Config
from src.db.postgres import new_session_maker
from src.db.uow import IUnitOfWork, SqlAlchemyUnitOfWork
from src.use_cases.payment.create import CreatePaymentUseCase
from src.use_cases.payment.get_detail import GetPaymentUseCase


class AppProvider(Provider):
    
    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def get_session_maker(self, config: Config) -> async_sessionmaker[AsyncSession]:
        return new_session_maker(config.postgres)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with session_maker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def uow(
        self,
        session: AsyncSession,
    ) -> IUnitOfWork:
        return SqlAlchemyUnitOfWork(session)

    @provide(scope=Scope.APP)
    def get_broker(self, config: Config) -> RabbitBroker:
        return RabbitBroker(config.rabbit.url)


class UseCaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def create_payment_use_case(self, uow: IUnitOfWork) -> CreatePaymentUseCase:
        return CreatePaymentUseCase(uow=uow)

    @provide
    def get_payment_use_case(self, uow: IUnitOfWork) -> GetPaymentUseCase:
        return GetPaymentUseCase(uow=uow)
