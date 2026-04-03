from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_active_user, require_roles
from app.votacao.schemas import (
    OpcaoVotacaoCreate,
    OpcaoVotacaoResponse,
    ResultadoManualCreate,
    ResultadoManualResponse,
    ResultadoPautaResponse,
    VotoCreate,
    VotoResponse,
)
from app.votacao.service import (
    create_opcao_votacao,
    get_resultado_pauta,
    register_manual_result,
    register_manual_vote,
)


router = APIRouter(tags=["votacao"])


@router.post(
    "/pautas/{pauta_id}/opcoes",
    response_model=OpcaoVotacaoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def create_opcao_votacao_route(
    pauta_id: UUID,
    payload: OpcaoVotacaoCreate,
    db: Annotated[Session, Depends(get_db)],
) -> OpcaoVotacaoResponse:
    return create_opcao_votacao(db, pauta_id, payload)


@router.post(
    "/votos",
    response_model=VotoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def register_manual_vote_route(
    payload: VotoCreate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(get_current_active_user),
) -> VotoResponse:
    client_ip = request.client.host if request.client else None
    return register_manual_vote(db, payload, current_user, client_ip)


@router.post(
    "/resultado-manual",
    response_model=list[ResultadoManualResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def register_manual_result_route(
    payload: ResultadoManualCreate,
    db: Annotated[Session, Depends(get_db)],
) -> list[ResultadoManualResponse]:
    return register_manual_result(db, payload)


@router.get(
    "/pautas/{pauta_id}/resultado",
    response_model=ResultadoPautaResponse,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def get_resultado_pauta_route(
    pauta_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> ResultadoPautaResponse:
    return get_resultado_pauta(db, pauta_id)
