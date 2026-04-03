from fastapi import APIRouter

from app.modules.assembleia.assembleia.router import router as assembleia_router
from app.modules.usuarios.auth.router import router as auth_router
from app.modules.condominio.condominio.router import router as condominio_router
from app.modules.sistema.configuracoes.router import router as configuracoes_router
from app.modules.sistema.dashboard.router import router as dashboard_router
from app.modules.sistema.integracoes.importador.router import router as importador_router
from app.modules.condominio.morador.router import router as morador_router
from app.modules.assembleia.pauta.router import router as pauta_router
from app.modules.assembleia.presenca.router import router as presenca_router
from app.modules.assembleia.procuracao.router import router as procuracao_router
from app.modules.assembleia.relatorios.router import router as relatorios_router
from app.modules.assembleia.telao.router import router as telao_router
from app.modules.assembleia.telao.websocket import router as telao_websocket_router
from app.modules.condominio.unidade.router import router as unidade_router
from app.modules.assembleia.votacao.router import router as votacao_router


router = APIRouter()
router.include_router(auth_router)
router.include_router(condominio_router)
router.include_router(configuracoes_router)
router.include_router(dashboard_router)
router.include_router(unidade_router)
router.include_router(morador_router)
router.include_router(assembleia_router)
router.include_router(pauta_router)
router.include_router(importador_router)
router.include_router(votacao_router)
router.include_router(presenca_router)
router.include_router(procuracao_router)
router.include_router(relatorios_router)
router.include_router(telao_router)
router.include_router(telao_websocket_router)


@router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}

