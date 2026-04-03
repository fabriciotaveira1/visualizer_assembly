from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


TipoVotacaoPadrao = Literal["unidade", "fracao"]


class ConfiguracaoCondominioPayload(BaseModel):
    tipo_votacao_padrao: TipoVotacaoPadrao = "unidade"
    quorum_minimo: Decimal = Field(default=0, ge=0, le=100)
    tempo_votacao_padrao: int = Field(default=0, ge=0, le=1440)
    tempo_fala_padrao: int = Field(default=0, ge=0, le=3600)
    limite_procuracoes: int = Field(default=0, ge=0, le=1000)


class ConfiguracaoCondominioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    condominio_id: uuid.UUID | None
    tipo_votacao_padrao: str | None
    quorum_minimo: Decimal | None
    tempo_votacao_padrao: int | None
    tempo_fala_padrao: int | None
    limite_procuracoes: int | None
    created_at: datetime


class DashboardResponse(BaseModel):
    total_assembleias: int
    total_votos: int
    assembleias_ativas: int
    media_votos_por_assembleia: Decimal
    total_presencas: int


