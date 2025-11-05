from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from .config import settings


api_key_header = APIKeyHeader(name=settings.api_key_header_name, auto_error=False)


def require_api_key(x_api_key: Optional[str] = Depends(api_key_header)) -> bool:
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")
    return True

