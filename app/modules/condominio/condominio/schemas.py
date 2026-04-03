from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CondominioCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=255)
    ativo: bool = True

    @field_validator("nome")
    @classmethod
    def normalize_nome(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Nome do condominio e obrigatorio.")
        return normalized


class CondominioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    ativo: bool
    created_at: datetime


