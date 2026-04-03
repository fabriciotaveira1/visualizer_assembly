from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.condominio.condominio.service import get_condominio_by_id
from app.modules.assembleia.votacao.models import Assembleia
from app.modules.assembleia.assembleia.schemas import AssembleiaCreate


def create_assembleia(db: Session, payload: AssembleiaCreate) -> Assembleia:
    get_condominio_by_id(db, payload.condominio_id)

    assembleia = Assembleia(
        id=uuid.uuid4(),
        condominio_id=payload.condominio_id,
        titulo=payload.titulo,
        data=payload.data,
        status="criada",
    )
    db.add(assembleia)
    db.commit()
    db.refresh(assembleia)
    return assembleia


def list_assembleias(db: Session) -> list[Assembleia]:
    statement = select(Assembleia).order_by(Assembleia.data.desc(), Assembleia.created_at.desc())
    return list(db.scalars(statement).all())


def get_assembleia_by_id(db: Session, assembleia_id: uuid.UUID) -> Assembleia:
    assembleia = db.scalar(select(Assembleia).where(Assembleia.id == assembleia_id))
    if assembleia is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assembleia not found.",
        )
    return assembleia


def abrir_assembleia(db: Session, assembleia_id: uuid.UUID) -> Assembleia:
    return _transition_assembleia_status(
        db,
        assembleia_id,
        expected_status={"criada"},
        new_status="aberta",
    )


def iniciar_assembleia(db: Session, assembleia_id: uuid.UUID) -> Assembleia:
    return _transition_assembleia_status(
        db,
        assembleia_id,
        expected_status={"aberta"},
        new_status="em_andamento",
    )


def encerrar_assembleia(db: Session, assembleia_id: uuid.UUID) -> Assembleia:
    return _transition_assembleia_status(
        db,
        assembleia_id,
        expected_status={"em_andamento"},
        new_status="encerrada",
    )


def finalizar_assembleia(db: Session, assembleia_id: uuid.UUID) -> Assembleia:
    return _transition_assembleia_status(
        db,
        assembleia_id,
        expected_status={"encerrada"},
        new_status="finalizada",
    )


def _transition_assembleia_status(
    db: Session,
    assembleia_id: uuid.UUID,
    *,
    expected_status: set[str],
    new_status: str,
) -> Assembleia:
    assembleia = get_assembleia_by_id(db, assembleia_id)
    current_status = assembleia.status or "criada"
    if current_status not in expected_status:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Assembleia cannot transition from {current_status} to {new_status}.",
        )

    assembleia.status = new_status
    db.commit()
    db.refresh(assembleia)
    return assembleia
