from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresConfig(BaseSettings):
    host: str = Field(alias="POSTGRES_HOST")
    port: int = Field(alias="POSTGRES_PORT")
    user: str = Field(alias="POSTGRES_USER")
    password: str = Field(alias="POSTGRES_PASSWORD")
    database: str = Field(alias="POSTGRES_DB")

    pool_size: int = Field(alias="POSTGRES_POOL_SIZE", default=15)
    max_overflow: int = Field(alias="POSTGRES_MAX_OVERFLOW", default=15)

    @property
    def dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
        )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class RabbitMQConfig(BaseSettings):
    user: str = Field(alias="RABBITMQ_DEFAULT_USER", default="guest")
    password: str = Field(alias="RABBITMQ_DEFAULT_PASS", default="guest")
    host: str = Field(alias="RABBITMQ_HOST", default="rabbitmq")
    port: int = Field(alias="RABBITMQ_PORT", default=5672)

    @property
    def url(self) -> str:
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class Config(BaseSettings):
    postgres: PostgresConfig = Field(default_factory=lambda: PostgresConfig())
    rabbit: RabbitMQConfig = Field(default_factory=lambda: RabbitMQConfig())
    x_api_key: str = Field(alias="X_API_KEY")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
