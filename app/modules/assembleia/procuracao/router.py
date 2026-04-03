from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import require_roles
from app.modules.assembleia.procuracao.schemas import ProcuracaoCreate, ProcuracaoResponse
from app.modules.assembleia.procuracao.service import create_procuracao, list_procuracoes


router = APIRouter(prefix="/procuracoes", tags=["procuracoes"])


@router.post(
    "",
    response_model=ProcuracaoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def create_procuracao_route(
    payload: ProcuracaoCreate,
    db: Annotated[Session, Depends(get_db)],
) -> ProcuracaoResponse:
    return create_procuracao(db, payload.assembleia_id, payload.unidade_origem_id, payload.unidade_destino_id)


@router.get(
    "/assembleia/{assembleia_id}",
    response_model=list[ProcuracaoResponse],
    dependencies=[Depends(require_roles("admin", "operador"))],
)
def list_procuracoes_route(
    assembleia_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> list[ProcuracaoResponse]:
    return list_procuracoes(db, assembleia_id)


