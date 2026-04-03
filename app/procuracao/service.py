from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.presenca.models import Presenca
from app.presenca.service import get_assembleia_by_id, get_presenca_record, get_unidade_for_assembleia
from app.procuracao.models import Procuracao


def create_procuracao(
    db: Session,
    assembleia_id: UUID,
    unidade_origem_id: UUID,
    unidade_destino_id: UUID,
) -> Procuracao:
    assembleia = get_assembleia_by_id(db, assembleia_id)
    origem = get_unidade_for_assembleia(db, unidade_origem_id, assembleia)
    destino = get_unidade_for_assembleia(db, unidade_destino_id, assembleia)

    if origem.id == destino.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="unidade_origem_id and unidade_destino_id must be different.",
        )

    presenca_origem = get_presenca_record(db, assembleia_id, origem.id)
    if presenca_origem is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unidade origem cannot already be present or represented.",
        )

    presenca_destino = get_presenca_record(db, assembleia_id, destino.id)
    if presenca_destino is None or presenca_destino.tipo != "presente":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unidade destino must have presencial attendance.",
        )

    existing = db.scalar(
        select(Procuracao).where(
            Procuracao.assembleia_id == assembleia_id,
            Procuracao.unidade_origem_id == origem.id,
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Procuracao already exists for this unidade origem.",
        )

    reverse_existing = db.scalar(
        select(Procuracao).where(
            Procuracao.assembleia_id == assembleia_id,
            Procuracao.unidade_destino_id == origem.id,
            Procuracao.unidade_origem_id == destino.id,
        )
    )
    if reverse_existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Reverse procuracao is not allowed.",
        )

    _validate_procuracao_limit(db, assembleia.condominio_id, assembleia_id, destino.id)

    procuracao = Procuracao(
        assembleia_id=assembleia_id,
        unidade_origem_id=origem.id,
        unidade_destino_id=destino.id,
    )
    db.add(procuracao)
    db.flush()

    db.add(
        Presenca(
            assembleia_id=assembleia_id,
            unidade_id=origem.id,
            tipo="procuracao",
        )
    )
    db.commit()
    db.refresh(procuracao)
    return procuracao


def list_procuracoes(db: Session, assembleia_id: UUID) -> list[Procuracao]:
    get_assembleia_by_id(db, assembleia_id)
    return list(
        db.scalars(
            select(Procuracao)
            .where(Procuracao.assembleia_id == assembleia_id)
            .order_by(Procuracao.created_at.asc())
        ).all()
    )


def _validate_procuracao_limit(
    db: Session,
    condominio_id: UUID,
    assembleia_id: UUID,
    unidade_destino_id: UUID,
) -> None:
    limite = db.execute(
        _select_limit_query(),
        {"condominio_id": str(condominio_id)},
    ).scalar_one_or_none()
    if limite is None:
        return

    total_count = int(
        db.scalar(
            select(func.count())
            .select_from(Procuracao)
            .where(
                Procuracao.assembleia_id == assembleia_id,
                Procuracao.unidade_destino_id == unidade_destino_id,
            )
        )
        or 0
    )
    if total_count >= int(limite):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Procuracao limit reached for unidade destino.",
        )


def _select_limit_query():
    return text(
        """
        SELECT limite_procuracoes
        FROM configuracoes_condominio
        WHERE condominio_id = CAST(:condominio_id AS UUID)
        ORDER BY created_at DESC
        LIMIT 1
        """
    )
