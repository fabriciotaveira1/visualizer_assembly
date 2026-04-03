from fastapi import APIRouter

from app.auth.router import router as auth_router
from app.condominio.router import router as condominio_router
from app.integracoes.importador.router import router as importador_router
from app.morador.router import router as morador_router
from app.unidade.router import router as unidade_router


router = APIRouter()
router.include_router(auth_router)
router.include_router(condominio_router)
router.include_router(unidade_router)
router.include_router(morador_router)
router.include_router(importador_router)


@router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
