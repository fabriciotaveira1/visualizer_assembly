from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.configuracoes.schemas import ConfiguracaoCondominioPayload, ConfiguracaoCondominioResponse
from app.configuracoes.service import get_or_create_configuracao, upsert_configuracao
from app.core.security import require_roles


router = APIRouter(prefix="/configuracoes", tags=["configuracoes"])


@router.get(
    "/{condominio_id}",
    response_model=ConfiguracaoCondominioResponse,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def get_configuracao_route(
    condominio_id: UUID,
    db: Session = Depends(get_db),
) -> ConfiguracaoCondominioResponse:
    return get_or_create_configuracao(db, condominio_id)


@router.post(
    "/{condominio_id}",
    response_model=ConfiguracaoCondominioResponse,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def upsert_configuracao_route(
    condominio_id: UUID,
    payload: ConfiguracaoCondominioPayload,
    db: Session = Depends(get_db),
) -> ConfiguracaoCondominioResponse:
    return upsert_configuracao(db, condominio_id, payload)
