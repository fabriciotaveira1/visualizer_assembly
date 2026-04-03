from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.assembleia.presenca.models import Presenca
from app.modules.assembleia.presenca.schemas import PresencaCreate, QuorumResponse, StatusUnidadesResponse, UnidadeStatusItem
from app.modules.assembleia.procuracao.models import Procuracao
from app.modules.condominio.unidade.models import Unidade
from app.modules.assembleia.votacao.models import Assembleia, Pauta, Voto


def register_presenca(db: Session, payload: PresencaCreate) -> Presenca:
    if payload.tipo == "procuracao":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use /procuracoes to register represented attendance.",
        )

    assembleia = get_assembleia_by_id(db, payload.assembleia_id)
    unidade = get_unidade_for_assembleia(db, payload.unidade_id, assembleia)

    existing = get_presenca_record(db, payload.assembleia_id, payload.unidade_id)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unidade already has a presence record for this assembleia.",
        )

    has_procuracao_as_origem = db.scalar(
        select(Procuracao).where(
            Procuracao.assembleia_id == payload.assembleia_id,
            Procuracao.unidade_origem_id == payload.unidade_id,
        )
    )
    if has_procuracao_as_origem is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unidade represented by procuracao cannot also be marked as presente.",
        )

    presenca = Presenca(
        assembleia_id=payload.assembleia_id,
        unidade_id=unidade.id,
        tipo=payload.tipo,
    )
    db.add(presenca)
    db.commit()
    db.refresh(presenca)
    return presenca


def list_presencas_by_assembleia(db: Session, assembleia_id: UUID) -> list[Presenca]:
    get_assembleia_by_id(db, assembleia_id)
    return list(
        db.scalars(
            select(Presenca)
            .where(Presenca.assembleia_id == assembleia_id)
            .order_by(Presenca.created_at.asc())
        ).all()
    )


def list_absent_units(db: Session, assembleia_id: UUID) -> list[Unidade]:
    status_data = get_status_unidades(db, assembleia_id)
    absent_ids = {item.unidade_id for item in status_data.ausentes}
    if not absent_ids:
        return []
    return list(
        db.scalars(
            select(Unidade)
            .where(Unidade.id.in_(absent_ids))
            .order_by(Unidade.bloco.asc(), Unidade.numero.asc(), Unidade.identificador_externo.asc())
        ).all()
    )


def get_quorum(db: Session, assembleia_id: UUID) -> QuorumResponse:
    assembleia = get_assembleia_by_id(db, assembleia_id)
    total_unidades, total_fracao = _get_unidades_totals(db, assembleia.condominio_id)
    presencas = list_presencas_by_assembleia(db, assembleia_id)

    total_presentes = sum(1 for presenca in presencas if presenca.tipo == "presente")
    total_por_procuracao = sum(1 for presenca in presencas if presenca.tipo == "procuracao")
    total_representadas = total_presentes + total_por_procuracao

    presentes_ids = [presenca.unidade_id for presenca in presencas if presenca.unidade_id is not None]
    represented_units = []
    if presentes_ids:
        represented_units = list(
            db.scalars(select(Unidade).where(Unidade.id.in_(presentes_ids))).all()
        )

    fracao_representada = sum(
        (_resolve_fracao(unidade.fracao_ideal) for unidade in represented_units),
        start=Decimal("0"),
    )

    percentual_presenca = Decimal("0")
    if total_unidades > 0:
        percentual_presenca = (Decimal(total_representadas) / Decimal(total_unidades)) * Decimal("100")

    percentual_fracao_ideal = Decimal("0")
    if total_fracao > 0:
        percentual_fracao_ideal = (fracao_representada / total_fracao) * Decimal("100")
    elif total_unidades > 0:
        percentual_fracao_ideal = percentual_presenca

    return QuorumResponse(
        assembleia_id=assembleia_id,
        total_unidades=total_unidades,
        total_presentes=total_presentes,
        total_por_procuracao=total_por_procuracao,
        percentual_presenca=percentual_presenca.quantize(Decimal("0.01")),
        percentual_fracao_ideal=percentual_fracao_ideal.quantize(Decimal("0.01")),
    )


def get_status_unidades(db: Session, assembleia_id: UUID) -> StatusUnidadesResponse:
    assembleia = get_assembleia_by_id(db, assembleia_id)
    unidades = list(
        db.scalars(
            select(Unidade)
            .where(Unidade.condominio_id == assembleia.condominio_id)
            .order_by(Unidade.bloco.asc(), Unidade.numero.asc(), Unidade.identificador_externo.asc())
        ).all()
    )
    presencas = list_presencas_by_assembleia(db, assembleia_id)
    presence_map = {presenca.unidade_id: presenca.tipo for presenca in presencas if presenca.unidade_id is not None}

    represented_ids = {unidade_id for unidade_id, tipo in presence_map.items() if tipo == "procuracao"}
    present_ids = {unidade_id for unidade_id, tipo in presence_map.items() if tipo == "presente"}
    absent_ids = {unidade.id for unidade in unidades} - represented_ids - present_ids

    pending_vote_ids = _get_pending_vote_ids(db, assembleia_id, present_ids | represented_ids)

    return StatusUnidadesResponse(
        assembleia_id=assembleia_id,
        presentes=[_build_unidade_status(unit) for unit in unidades if unit.id in present_ids],
        ausentes=[_build_unidade_status(unit) for unit in unidades if unit.id in absent_ids],
        representados=[_build_unidade_status(unit) for unit in unidades if unit.id in represented_ids],
        pendentes_voto=[_build_unidade_status(unit) for unit in unidades if unit.id in pending_vote_ids],
    )


def get_assembleia_by_id(db: Session, assembleia_id: UUID) -> Assembleia:
    assembleia = db.scalar(select(Assembleia).where(Assembleia.id == assembleia_id))
    if assembleia is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assembleia not found.")
    if assembleia.condominio_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assembleia is not linked to a condominio.",
        )
    return assembleia


def get_unidade_for_assembleia(db: Session, unidade_id: UUID, assembleia: Assembleia) -> Unidade:
    unidade = db.scalar(select(Unidade).where(Unidade.id == unidade_id))
    if unidade is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidade not found.")
    if unidade.condominio_id != assembleia.condominio_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unidade does not belong to the assembleia condominio.",
        )
    return unidade


def get_presenca_record(db: Session, assembleia_id: UUID, unidade_id: UUID) -> Presenca | None:
    return db.scalar(
        select(Presenca).where(
            Presenca.assembleia_id == assembleia_id,
            Presenca.unidade_id == unidade_id,
        )
    )


def _build_unidade_status(unidade: Unidade) -> UnidadeStatusItem:
    return UnidadeStatusItem(
        unidade_id=unidade.id,
        identificador_externo=unidade.identificador_externo,
        bloco=unidade.bloco,
        numero=unidade.numero,
        fracao_ideal=unidade.fracao_ideal,
    )


def _get_unidades_totals(db: Session, condominio_id: UUID) -> tuple[int, Decimal]:
    unidades = list(
        db.scalars(select(Unidade).where(Unidade.condominio_id == condominio_id)).all()
    )
    total_fracao = sum((_resolve_fracao(unidade.fracao_ideal) for unidade in unidades), start=Decimal("0"))
    return len(unidades), total_fracao


def _resolve_fracao(fracao: Decimal | None) -> Decimal:
    if fracao is None:
        return Decimal("1")
    decimal_value = Decimal(str(fracao))
    return decimal_value if decimal_value > 0 else Decimal("1")


def _get_pending_vote_ids(db: Session, assembleia_id: UUID, represented_ids: set[UUID]) -> set[UUID]:
    if not represented_ids:
        return set()

    pautas_abertas = list(
        db.scalars(
            select(Pauta.id).where(
                Pauta.assembleia_id == assembleia_id,
                Pauta.status == "em_votacao",
                Pauta.modo_votacao.in_(["manual", "importado"]),
            )
        ).all()
    )
    if not pautas_abertas:
        return set()

    voted_ids = {
        unidade_id
        for unidade_id in db.scalars(
            select(Voto.unidade_id)
            .where(
                Voto.pauta_id.in_(pautas_abertas),
                Voto.unidade_id.in_(represented_ids),
            )
        ).all()
        if unidade_id is not None
    }
    return represented_ids - voted_ids


