from fastapi import APIRouter

from app.auth.router import router as auth_router
from app.condominio.router import router as condominio_router
from app.integracoes.importador.router import router as importador_router
from app.morador.router import router as morador_router
from app.presenca.router import router as presenca_router
from app.procuracao.router import router as procuracao_router
from app.telao.router import router as telao_router
from app.unidade.router import router as unidade_router
from app.votacao.router import router as votacao_router
from app.telao.websocket import router as telao_websocket_router


router = APIRouter()
router.include_router(auth_router)
router.include_router(condominio_router)
router.include_router(unidade_router)
router.include_router(morador_router)
router.include_router(importador_router)
router.include_router(votacao_router)
router.include_router(presenca_router)
router.include_router(procuracao_router)
router.include_router(telao_router)
router.include_router(telao_websocket_router)


@router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
