from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UnidadeCreate(BaseModel):
    condominio_id: uuid.UUID
    bloco: str | None = Field(default=None, max_length=100)
    numero: str | None = Field(default=None, max_length=100)
    identificador_externo: str = Field(min_length=1, max_length=255)
    fracao_ideal: Decimal | None = None
    ativo: bool = True

    @field_validator("bloco", "numero", "identificador_externo")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("Field cannot be blank.")
        return normalized


class UnidadeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    condominio_id: uuid.UUID
    bloco: str | None
    numero: str | None
    identificador_externo: str
    fracao_ideal: Decimal | None
    ativo: bool
    created_at: datetime


