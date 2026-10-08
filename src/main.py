import asyncio
from contextlib import asynccontextmanager

from dishka import AsyncContainer, make_async_container
from dishka.integrations import fastapi as fastapi_integration
from fastapi import FastAPI, Security
from faststream.rabbit import RabbitBroker

from src.api.dependencies import verify_api_key
from src.api.exception_handler import register_exception_handlers
from src.api.payment import router as payment_router
from src.core.config import Config
from src.ioc import AppProvider, UseCaseProvider
from src.services.outbox_relay import OutboxRelay


def create_app() -> FastAPI:

    config: Config = Config()
    container: AsyncContainer = make_async_container(
        AppProvider(),
        UseCaseProvider(),
        context={Config: config},
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        broker = await container.get(RabbitBroker)
        await broker.start()
        outbox = OutboxRelay(container=container, broker=broker)
        task = asyncio.create_task(outbox.run())
        try:
            yield
        finally:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            await broker.stop()

    app: FastAPI = FastAPI(
        title="Асинхронный сервис процессинга платежей",
        dependencies=[Security(verify_api_key)],
        lifespan=lifespan,
    )
    app.include_router(payment_router, prefix="/api/v1/payments", tags=["Payments"])
    fastapi_integration.setup_dishka(container=container, app=app)
    register_exception_handlers(app=app)

    return app
