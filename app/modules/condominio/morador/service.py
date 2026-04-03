from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.condominio.condominio.service import get_condominio_by_id
from app.modules.condominio.morador.models import Morador
from app.modules.condominio.morador.schemas import MoradorCreate
from app.modules.condominio.unidade.service import get_unidade_by_id


def create_morador(db: Session, payload: MoradorCreate) -> Morador:
    get_condominio_by_id(db, payload.condominio_id)
    unidade = get_unidade_by_id(db, payload.unidade_id)

    if unidade.condominio_id != payload.condominio_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unidade does not belong to the provided condominio.",
        )

    morador = Morador(
        condominio_id=payload.condominio_id,
        unidade_id=payload.unidade_id,
        nome=payload.nome,
        cpf=payload.cpf,
        telefone=payload.telefone,
        email=payload.email,
        tipo=payload.tipo,
        ativo=payload.ativo,
    )
    db.add(morador)
    db.commit()
    db.refresh(morador)
    return morador


def list_moradores_by_unidade(db: Session, unidade_id: UUID) -> list[Morador]:
    get_unidade_by_id(db, unidade_id)
    statement = (
        select(Morador)
        .where(Morador.unidade_id == unidade_id)
        .order_by(Morador.created_at.desc())
    )
    return list(db.scalars(statement).all())


