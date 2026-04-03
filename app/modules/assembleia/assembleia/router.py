from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_active_user, require_roles
from app.modules.assembleia.assembleia.schemas import AssembleiaCreate, AssembleiaResponse
from app.modules.assembleia.assembleia.service import (
    abrir_assembleia,
    create_assembleia,
    encerrar_assembleia,
    finalizar_assembleia,
    get_assembleia_by_id,
    iniciar_assembleia,
    list_assembleias,
)

router = APIRouter(prefix="/assembleias", tags=["assembleias"])


@router.post(
    "",
    response_model=AssembleiaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def create_assembleia_route(
    payload: AssembleiaCreate,
    db: Annotated[Session, Depends(get_db)],
) -> AssembleiaResponse:
    return create_assembleia(db, payload)


@router.get(
    "",
    response_model=list[AssembleiaResponse],
    dependencies=[Depends(get_current_active_user)],
)
def list_assembleias_route(
    db: Annotated[Session, Depends(get_db)],
) -> list[AssembleiaResponse]:
    return list_assembleias(db)


@router.get(
    "/{assembleia_id}",
    response_model=AssembleiaResponse,
    dependencies=[Depends(get_current_active_user)],
)
def get_assembleia_route(
    assembleia_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> AssembleiaResponse:
    return get_assembleia_by_id(db, assembleia_id)


@router.post(
    "/{assembleia_id}/abrir",
    response_model=AssembleiaResponse,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def abrir_assembleia_route(
    assembleia_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> AssembleiaResponse:
    return abrir_assembleia(db, assembleia_id)


@router.post(
    "/{assembleia_id}/iniciar",
    response_model=AssembleiaResponse,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def iniciar_assembleia_route(
    assembleia_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> AssembleiaResponse:
    return iniciar_assembleia(db, assembleia_id)


@router.post(
    "/{assembleia_id}/encerrar",
    response_model=AssembleiaResponse,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def encerrar_assembleia_route(
    assembleia_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> AssembleiaResponse:
    return encerrar_assembleia(db, assembleia_id)


@router.post(
    "/{assembleia_id}/finalizar",
    response_model=AssembleiaResponse,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def finalizar_assembleia_route(
    assembleia_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> AssembleiaResponse:
    return finalizar_assembleia(db, assembleia_id)

