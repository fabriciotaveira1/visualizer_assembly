from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.condominio.condominio.service import get_condominio_by_id
from app.modules.condominio.unidade.models import Unidade
from app.modules.condominio.unidade.schemas import UnidadeCreate


def create_unidade(db: Session, payload: UnidadeCreate) -> Unidade:
    get_condominio_by_id(db, payload.condominio_id)

    existing = db.scalar(
        select(Unidade).where(
            Unidade.condominio_id == payload.condominio_id,
            Unidade.identificador_externo == payload.identificador_externo,
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="identificador_externo already exists for this condominio.",
        )

    unidade = Unidade(
        condominio_id=payload.condominio_id,
        bloco=payload.bloco,
        numero=payload.numero,
        identificador_externo=payload.identificador_externo,
        fracao_ideal=payload.fracao_ideal,
        ativo=payload.ativo,
    )
    db.add(unidade)
    db.commit()
    db.refresh(unidade)
    return unidade


def list_unidades_by_condominio(db: Session, condominio_id: UUID) -> list[Unidade]:
    get_condominio_by_id(db, condominio_id)
    statement = (
        select(Unidade)
        .where(Unidade.condominio_id == condominio_id)
        .order_by(Unidade.created_at.desc())
    )
    return list(db.scalars(statement).all())


def get_unidade_by_id(db: Session, unidade_id: UUID) -> Unidade:
    statement = select(Unidade).where(Unidade.id == unidade_id)
    unidade = db.scalar(statement)
    if unidade is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidade not found.",
        )
    return unidade


