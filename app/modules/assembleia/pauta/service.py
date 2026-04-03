from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.assembleia.assembleia.service import get_assembleia_by_id
from app.modules.assembleia.votacao.models import OpcaoVotacao, Pauta
from app.modules.assembleia.pauta.schemas import PautaCreate


def create_pauta(db: Session, payload: PautaCreate) -> Pauta:
    assembleia = get_assembleia_by_id(db, payload.assembleia_id)
    if (assembleia.status or "criada") == "finalizada":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nao e possivel adicionar pautas em uma assembleia finalizada.",
        )

    ordem = payload.ordem
    if ordem is None:
        ordem = int(
            db.scalar(
                select(func.coalesce(func.max(Pauta.ordem), 0)).where(
                    Pauta.assembleia_id == payload.assembleia_id
                )
            )
            or 0
        ) + 1

    pauta = Pauta(
        id=uuid.uuid4(),
        assembleia_id=payload.assembleia_id,
        titulo=payload.titulo,
        descricao=payload.descricao,
        tipo_votacao=payload.tipo_votacao,
        regra_votacao=payload.regra_votacao,
        ordem=ordem,
        status="aguardando",
        versao=1,
        bloqueada=False,
        modo_votacao=payload.modo_votacao,
    )
    db.add(pauta)
    db.commit()
    db.refresh(pauta)
    return pauta


def list_pautas_by_assembleia(db: Session, assembleia_id: uuid.UUID) -> list[Pauta]:
    get_assembleia_by_id(db, assembleia_id)
    statement = (
        select(Pauta)
        .where(Pauta.assembleia_id == assembleia_id)
        .order_by(Pauta.ordem.asc(), Pauta.created_at.asc())
    )
    return list(db.scalars(statement).all())


def get_pauta_by_id(db: Session, pauta_id: uuid.UUID) -> Pauta:
    pauta = db.scalar(select(Pauta).where(Pauta.id == pauta_id))
    if pauta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pauta not found.",
        )
    return pauta


def list_opcoes_votacao(db: Session, pauta_id: uuid.UUID) -> list[OpcaoVotacao]:
    get_pauta_by_id(db, pauta_id)
    statement = (
        select(OpcaoVotacao)
        .where(OpcaoVotacao.pauta_id == pauta_id)
        .order_by(OpcaoVotacao.codigo.asc())
    )
    return list(db.scalars(statement).all())


def iniciar_votacao_pauta(db: Session, pauta_id: uuid.UUID) -> Pauta:
    pauta = get_pauta_by_id(db, pauta_id)
    assembleia = get_assembleia_by_id(db, pauta.assembleia_id)
    if assembleia.status != "em_andamento":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A assembleia precisa estar em andamento para iniciar a votacao.",
        )
    if pauta.status != "aguardando":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Apenas pautas aguardando podem iniciar votacao.",
        )

    active_pauta = db.scalar(
        select(Pauta).where(
            Pauta.assembleia_id == pauta.assembleia_id,
            Pauta.status == "em_votacao",
            Pauta.id != pauta.id,
        )
    )
    if active_pauta is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ja existe outra pauta em votacao nesta assembleia.",
        )

    pauta.status = "em_votacao"
    db.commit()
    db.refresh(pauta)
    return pauta


def encerrar_votacao_pauta(db: Session, pauta_id: uuid.UUID) -> Pauta:
    pauta = get_pauta_by_id(db, pauta_id)
    if pauta.status != "em_votacao":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Apenas pautas em votacao podem ser encerradas.",
        )

    pauta.status = "encerrada"
    db.commit()
    db.refresh(pauta)
    return pauta
