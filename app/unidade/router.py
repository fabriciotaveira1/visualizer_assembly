from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_active_user, require_roles
from app.unidade.schemas import UnidadeCreate, UnidadeResponse
from app.unidade.service import create_unidade, list_unidades_by_condominio


router = APIRouter(prefix="/unidades", tags=["unidades"])


@router.post(
    "",
    response_model=UnidadeResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def create_unidade_route(
    payload: UnidadeCreate,
    db: Annotated[Session, Depends(get_db)],
) -> UnidadeResponse:
    return create_unidade(db, payload)


@router.get(
    "",
    response_model=list[UnidadeResponse],
    dependencies=[Depends(get_current_active_user)],
)
def list_unidades_route(
    condominio_id: UUID = Query(...),
    db: Session = Depends(get_db),
) -> list[UnidadeResponse]:
    return list_unidades_by_condominio(db, condominio_id)
