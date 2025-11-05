from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/health", summary="Health check", description="Basic readiness probe")
def health():
    return {"status": "ok"}

