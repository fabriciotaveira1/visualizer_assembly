from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import require_roles
from app.presenca.schemas import PresencaCreate, PresencaResponse, QuorumResponse, StatusUnidadesResponse, UnidadeStatusItem
from app.presenca.service import get_quorum, get_status_unidades, list_absent_units, list_presencas_by_assembleia, register_presenca


router = APIRouter(prefix="/presencas", tags=["presencas"])


@router.post(
    "",
    response_model=PresencaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def register_presenca_route(
    payload: PresencaCreate,
    db: Annotated[Session, Depends(get_db)],
) -> PresencaResponse:
    return register_presenca(db, payload)


@router.get(
    "/assembleia/{assembleia_id}",
    response_model=list[PresencaResponse],
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def list_presencas_route(
    assembleia_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> list[PresencaResponse]:
    return list_presencas_by_assembleia(db, assembleia_id)


@router.get(
    "/assembleia/{assembleia_id}/faltantes",
    response_model=list[UnidadeStatusItem],
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def list_absent_units_route(
    assembleia_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> list[UnidadeStatusItem]:
    unidades = list_absent_units(db, assembleia_id)
    return [
        UnidadeStatusItem(
            unidade_id=unidade.id,
            identificador_externo=unidade.identificador_externo,
            bloco=unidade.bloco,
            numero=unidade.numero,
            fracao_ideal=unidade.fracao_ideal,
        )
        for unidade in unidades
    ]


@router.get(
    "/assembleia/{assembleia_id}/quorum",
    response_model=QuorumResponse,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def get_quorum_route(
    assembleia_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> QuorumResponse:
    return get_quorum(db, assembleia_id)


@router.get(
    "/assembleia/{assembleia_id}/status-unidades",
    response_model=StatusUnidadesResponse,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def get_status_unidades_route(
    assembleia_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> StatusUnidadesResponse:
    return get_status_unidades(db, assembleia_id)
