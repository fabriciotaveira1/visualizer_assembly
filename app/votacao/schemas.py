from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


ModoVotacao = Literal["manual", "importado", "resultado_manual"]
TipoVoto = Literal["direto", "procuracao"]
TipoOrigem = Literal["manual", "importado"]


class OpcaoVotacaoCreate(BaseModel):
    codigo: int = Field(ge=1)
    descricao: str = Field(min_length=1, max_length=255)

    @field_validator("descricao")
    @classmethod
    def normalize_descricao(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("descricao is required.")
        return normalized


class OpcaoVotacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    pauta_id: uuid.UUID
    codigo: int
    descricao: str
    created_at: datetime


class VotoCreate(BaseModel):
    pauta_id: uuid.UUID
    unidade_id: uuid.UUID
    tipo_voto: TipoVoto = "direto"
    codigo_opcao: int = Field(ge=1)
    descricao_opcao: str | None = Field(default=None, max_length=255)
    peso: Decimal | None = None

    @field_validator("descricao_opcao")
    @classmethod
    def normalize_descricao(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class VotoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    pauta_id: uuid.UUID | None
    unidade_id: uuid.UUID | None
    tipo_voto: str | None
    tipo_origem: str | None
    codigo_opcao: int | None
    descricao_opcao: str | None
    peso: Decimal | None
    ip: str | None
    data_voto: datetime | None
    registrado_por: uuid.UUID | None


class ResultadoManualItemCreate(BaseModel):
    codigo_opcao: int = Field(ge=1)
    descricao_opcao: str | None = Field(default=None, max_length=255)
    quantidade_votos: int = Field(ge=0)
    peso_total: Decimal = Field(ge=0)
    percentual: Decimal = Field(ge=0)

    @field_validator("descricao_opcao")
    @classmethod
    def normalize_descricao(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class ResultadoManualCreate(BaseModel):
    pauta_id: uuid.UUID
    resultados: list[ResultadoManualItemCreate] = Field(min_length=1)


class ResultadoManualResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    pauta_id: uuid.UUID
    codigo_opcao: int
    descricao_opcao: str
    quantidade_votos: int
    peso_total: Decimal
    percentual: Decimal
    created_at: datetime


class ResultadoPautaOpcao(BaseModel):
    codigo_opcao: int
    descricao_opcao: str
    quantidade_votos: int
    peso_total: Decimal
    percentual: Decimal


class ResultadoPautaResponse(BaseModel):
    pauta_id: uuid.UUID
    modo_votacao: ModoVotacao
    total_votos: int
    total_peso: Decimal
    opcoes: list[ResultadoPautaOpcao]
