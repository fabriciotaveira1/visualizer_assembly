from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


TipoVotacao = Literal["unidade", "fracao"]
RegraVotacao = Literal["simples", "2_3", "unanimidade"]
ModoVotacao = Literal["manual", "importado", "resultado_manual"]


class PautaCreate(BaseModel):
    assembleia_id: uuid.UUID
    titulo: str = Field(min_length=1, max_length=255)
    descricao: str | None = None
    tipo_votacao: TipoVotacao = "unidade"
    regra_votacao: RegraVotacao = "simples"
    modo_votacao: ModoVotacao = "manual"
    ordem: int | None = Field(default=None, ge=1)

    @field_validator("titulo")
    @classmethod
    def normalize_titulo(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Titulo da pauta e obrigatorio.")
        return normalized

    @field_validator("descricao")
    @classmethod
    def normalize_descricao(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class PautaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    assembleia_id: uuid.UUID | None
    titulo: str | None
    descricao: str | None
    tipo_votacao: str | None
    regra_votacao: str | None
    ordem: int | None
    status: str | None
    versao: int | None
    bloqueada: bool | None
    modo_votacao: str | None
    created_at: datetime
