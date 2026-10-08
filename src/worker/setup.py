from dishka import make_async_container
from dishka.integrations.faststream import setup_dishka
from faststream import FastStream
from faststream.rabbit import RabbitBroker

from src.core.config import Config
from src.ioc import AppProvider, UseCaseProvider
from src.worker.handler import router


def create_worker() -> FastStream:

    config = Config()
    broker = RabbitBroker(config.rabbit.url)
    broker.include_router(router)

    container = make_async_container(
        AppProvider(), UseCaseProvider(), context={Config: config, RabbitBroker: broker}
    )

    app = FastStream(broker)
    setup_dishka(container, app)
    return app


app = create_worker()
