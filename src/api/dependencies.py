from dishka.integrations.fastapi import FromDishka, inject
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from src.core.config import Config

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


@inject
async def verify_api_key(
    config: FromDishka[Config],
    api_key: str = Security(api_key_header),
):
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Отсутствует API Key"
        )
    if api_key != config.x_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Неверный API Key"
        )
    return api_key
