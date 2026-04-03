from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_active_user, require_roles
from app.modules.assembleia.pauta.schemas import PautaCreate, PautaResponse
from app.modules.assembleia.votacao.schemas import OpcaoVotacaoResponse
from app.modules.assembleia.pauta.service import (
    create_pauta,
    encerrar_votacao_pauta,
    iniciar_votacao_pauta,
    list_opcoes_votacao,
    list_pautas_by_assembleia,
)

router = APIRouter(prefix="/pautas", tags=["pautas"])


@router.post(
    "",
    response_model=PautaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def create_pauta_route(
    payload: PautaCreate,
    db: Annotated[Session, Depends(get_db)],
) -> PautaResponse:
    return create_pauta(db, payload)


@router.get(
    "",
    response_model=list[PautaResponse],
    dependencies=[Depends(get_current_active_user)],
)
def list_pautas_route(
    assembleia_id: UUID = Query(...),
    db: Session = Depends(get_db),
) -> list[PautaResponse]:
    return list_pautas_by_assembleia(db, assembleia_id)


@router.get(
    "/{pauta_id}/opcoes",
    response_model=list[OpcaoVotacaoResponse],
    dependencies=[Depends(get_current_active_user)],
)
def list_opcoes_votacao_route(
    pauta_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> list[OpcaoVotacaoResponse]:
    return list_opcoes_votacao(db, pauta_id)


@router.post(
    "/{pauta_id}/iniciar-votacao",
    response_model=PautaResponse,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def iniciar_votacao_pauta_route(
    pauta_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> PautaResponse:
    return iniciar_votacao_pauta(db, pauta_id)


@router.post(
    "/{pauta_id}/encerrar-votacao",
    response_model=PautaResponse,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def encerrar_votacao_pauta_route(
    pauta_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> PautaResponse:
    return encerrar_votacao_pauta(db, pauta_id)

