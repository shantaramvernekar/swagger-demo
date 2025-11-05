from fastapi import APIRouter, Depends

from app.core.security import require_api_key


router = APIRouter(prefix="/secure", tags=["secure"], dependencies=[Depends(require_api_key)])


@router.get("/secret", summary="Protected endpoint (API key required)")
def secret():
    return {"secret": "42"}

