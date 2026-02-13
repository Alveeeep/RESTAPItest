from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from starlette.requests import Request
from loguru import logger
from app.config import settings

API_KEY_NAME = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def verify_api_key(
        request: Request,
        api_key: str = Security(api_key_header)
):
    if not api_key:
        logger.warning(f"Отсутствует API ключ. IP: {request.client.host}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key is missing"
        )

    if api_key != settings.API_KEY:
        logger.warning(f"Неверный API ключ: {api_key}. IP: {request.client.host}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )

    return api_key
