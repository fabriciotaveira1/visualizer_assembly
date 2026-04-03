from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.condominio.schemas import CondominioCreate, CondominioResponse
from app.condominio.service import (
    create_condominio,
    get_condominio_by_id,
    list_condominios,
)
from app.core.security import get_current_active_user, require_roles


router = APIRouter(prefix="/condominios", tags=["condominios"])


@router.post(
    "",
    response_model=CondominioResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def create_condominio_route(
    payload: CondominioCreate,
    db: Annotated[Session, Depends(get_db)],
) -> CondominioResponse:
    return create_condominio(db, payload)


@router.get(
    "",
    response_model=list[CondominioResponse],
    dependencies=[Depends(get_current_active_user)],
)
def list_condominios_route(
    db: Annotated[Session, Depends(get_db)],
) -> list[CondominioResponse]:
    return list_condominios(db)


@router.get(
    "/{condominio_id}",
    response_model=CondominioResponse,
    dependencies=[Depends(get_current_active_user)],
)
def get_condominio_route(
    condominio_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> CondominioResponse:
    return get_condominio_by_id(db, condominio_id)
