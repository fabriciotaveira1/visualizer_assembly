from fastapi import APIRouter

from app.auth.router import router as auth_router


router = APIRouter()
router.include_router(auth_router)


@router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
