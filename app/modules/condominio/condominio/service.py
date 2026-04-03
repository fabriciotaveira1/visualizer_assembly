from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.condominio.condominio.models import Condominio
from app.modules.condominio.condominio.schemas import CondominioCreate


def create_condominio(db: Session, payload: CondominioCreate) -> Condominio:
    condominio = Condominio(
        nome=payload.nome,
        ativo=payload.ativo,
    )
    db.add(condominio)
    db.commit()
    db.refresh(condominio)
    return condominio


def list_condominios(db: Session) -> list[Condominio]:
    statement = select(Condominio).order_by(Condominio.created_at.desc())
    return list(db.scalars(statement).all())


def get_condominio_by_id(db: Session, condominio_id: UUID) -> Condominio:
    statement = select(Condominio).where(Condominio.id == condominio_id)
    condominio = db.scalar(statement)
    if condominio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Condominio not found.",
        )
    return condominio


