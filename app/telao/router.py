from __future__ import annotations

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import require_roles
from app.telao.service import (
    enviar_mensagem,
    enviar_pauta_ativa,
    enviar_resultado,
    enviar_status_assembleia,
    validar_assembleia,
)
from app.votacao.service import get_pauta_by_id


class TelaoMensagemPayload(BaseModel):
    assembleia_id: UUID
    titulo: str | None = Field(default=None, max_length=255)
    mensagem: str = Field(min_length=1, max_length=2000)
    nivel: str | None = Field(default=None, max_length=50)


class TelaoStatusPayload(BaseModel):
    assembleia_id: UUID
    status: str = Field(min_length=1, max_length=100)
    descricao: str | None = Field(default=None, max_length=1000)
    metadata: dict[str, Any] | None = None


class TelaoPautaPayload(BaseModel):
    assembleia_id: UUID
    pauta_id: UUID
    titulo: str = Field(min_length=1, max_length=255)
    ordem: int | None = None
    status: str | None = Field(default=None, max_length=100)
    modo_votacao: str | None = Field(default=None, max_length=50)


class TelaoResultadoPayload(BaseModel):
    pauta_id: UUID


router = APIRouter(prefix="/telao", tags=["telao"])


@router.post(
    "/mensagem",
    dependencies=[Depends(require_roles("admin", "operador"))],
)
async def enviar_mensagem_route(
    payload: TelaoMensagemPayload,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    validar_assembleia(db, payload.assembleia_id)
    await enviar_mensagem(payload.assembleia_id, payload.model_dump(mode="json"))
    return {"status": "sent"}


@router.post(
    "/status",
    dependencies=[Depends(require_roles("admin", "operador"))],
)
async def enviar_status_route(
    payload: TelaoStatusPayload,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    validar_assembleia(db, payload.assembleia_id)
    await enviar_status_assembleia(payload.assembleia_id, payload.model_dump(mode="json"))
    return {"status": "sent"}


@router.post(
    "/pauta",
    dependencies=[Depends(require_roles("admin", "operador"))],
)
async def enviar_pauta_route(
    payload: TelaoPautaPayload,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    validar_assembleia(db, payload.assembleia_id)
    pauta = get_pauta_by_id(db, payload.pauta_id)
    if pauta.assembleia_id != payload.assembleia_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pauta does not belong to the provided assembleia.",
        )
    await enviar_pauta_ativa(payload.assembleia_id, payload.model_dump(mode="json"))
    return {"status": "sent"}


@router.post(
    "/resultado",
    dependencies=[Depends(require_roles("admin", "operador"))],
)
async def enviar_resultado_route(
    payload: TelaoResultadoPayload,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    await enviar_resultado(db, payload.pauta_id)
    return {"status": "sent"}
