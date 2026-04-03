from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


TipoPresenca = Literal["presente", "procuracao"]


class PresencaCreate(BaseModel):
    assembleia_id: uuid.UUID
    unidade_id: uuid.UUID
    tipo: TipoPresenca = "presente"


class UnidadeStatusItem(BaseModel):
    unidade_id: uuid.UUID
    identificador_externo: str
    bloco: str | None
    numero: str | None
    fracao_ideal: Decimal | None


class PresencaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    assembleia_id: uuid.UUID | None
    unidade_id: uuid.UUID | None
    tipo: str | None
    created_at: datetime


class QuorumResponse(BaseModel):
    assembleia_id: uuid.UUID
    total_unidades: int
    total_presentes: int
    total_por_procuracao: int
    percentual_presenca: Decimal
    percentual_fracao_ideal: Decimal


class StatusUnidadesResponse(BaseModel):
    assembleia_id: uuid.UUID
    presentes: list[UnidadeStatusItem]
    ausentes: list[UnidadeStatusItem]
    representados: list[UnidadeStatusItem]
    pendentes_voto: list[UnidadeStatusItem]


