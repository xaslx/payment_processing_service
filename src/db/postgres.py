from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import PostgresConfig


def new_session_maker(psql_config: PostgresConfig) -> async_sessionmaker[AsyncSession]:

    engine = create_async_engine(
        psql_config.dsn,
        pool_size=psql_config.pool_size,
        max_overflow=psql_config.max_overflow,
    )

    return async_sessionmaker(
        bind=engine, class_=AsyncSession, autoflush=False, expire_on_commit=False
    )
