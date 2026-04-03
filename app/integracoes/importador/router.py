from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import require_roles
from app.integracoes.importador.service import import_moradores_csv, import_unidades_csv


router = APIRouter(prefix="/importacoes", tags=["importacoes"])


@router.post(
    "/unidades",
    dependencies=[Depends(require_roles("admin", "operador"))],
)
async def import_unidades_route(
    condominio_id: Annotated[UUID, Form(...)],
    file: Annotated[UploadFile, File(...)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    return await import_unidades_csv(db, condominio_id, file)


@router.post(
    "/moradores",
    dependencies=[Depends(require_roles("admin", "operador"))],
)
async def import_moradores_route(
    condominio_id: Annotated[UUID, Form(...)],
    file: Annotated[UploadFile, File(...)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    return await import_moradores_csv(db, condominio_id, file)
