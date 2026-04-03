from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_active_user, require_roles
from app.modules.condominio.morador.schemas import MoradorCreate, MoradorResponse
from app.modules.condominio.morador.service import create_morador, list_moradores_by_unidade


router = APIRouter(prefix="/moradores", tags=["moradores"])


@router.post(
    "",
    response_model=MoradorResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def create_morador_route(
    payload: MoradorCreate,
    db: Annotated[Session, Depends(get_db)],
) -> MoradorResponse:
    return create_morador(db, payload)


@router.get(
    "",
    response_model=list[MoradorResponse],
    dependencies=[Depends(get_current_active_user)],
)
def list_moradores_route(
    unidade_id: UUID = Query(...),
    db: Session = Depends(get_db),
) -> list[MoradorResponse]:
    return list_moradores_by_unidade(db, unidade_id)


