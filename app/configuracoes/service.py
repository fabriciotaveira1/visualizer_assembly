from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.condominio.service import get_condominio_by_id
from app.configuracoes.models import ConfiguracaoCondominio
from app.configuracoes.schemas import ConfiguracaoCondominioPayload


def get_or_create_configuracao(db: Session, condominio_id: UUID) -> ConfiguracaoCondominio:
    get_condominio_by_id(db, condominio_id)
    configuracao = _get_latest_config(db, condominio_id)
    if configuracao is not None:
        return configuracao

    configuracao = ConfiguracaoCondominio(
        condominio_id=condominio_id,
        tipo_votacao_padrao="unidade",
        quorum_minimo=0,
        tempo_votacao_padrao=0,
        tempo_fala_padrao=0,
        limite_procuracoes=0,
    )
    db.add(configuracao)
    db.commit()
    db.refresh(configuracao)
    return configuracao


def upsert_configuracao(
    db: Session,
    condominio_id: UUID,
    payload: ConfiguracaoCondominioPayload,
) -> ConfiguracaoCondominio:
    configuracao = get_or_create_configuracao(db, condominio_id)
    configuracao.tipo_votacao_padrao = payload.tipo_votacao_padrao
    configuracao.quorum_minimo = payload.quorum_minimo
    configuracao.tempo_votacao_padrao = payload.tempo_votacao_padrao
    configuracao.tempo_fala_padrao = payload.tempo_fala_padrao
    configuracao.limite_procuracoes = payload.limite_procuracoes
    db.add(configuracao)
    db.commit()
    db.refresh(configuracao)
    return configuracao


def _get_latest_config(db: Session, condominio_id: UUID) -> ConfiguracaoCondominio | None:
    return db.scalar(
        select(ConfiguracaoCondominio)
        .where(ConfiguracaoCondominio.condominio_id == condominio_id)
        .order_by(desc(ConfiguracaoCondominio.created_at))
    )
