from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


MoradorTipo = Literal["proprietario", "inquilino"]


class MoradorCreate(BaseModel):
    condominio_id: uuid.UUID
    unidade_id: uuid.UUID
    nome: str = Field(min_length=1, max_length=255)
    cpf: str | None = Field(default=None, max_length=20)
    telefone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    tipo: MoradorTipo
    ativo: bool = True

    @field_validator("nome", "cpf", "telefone", "email")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("Field cannot be blank.")
        return normalized

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.lower()
        if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
            raise ValueError("Invalid email.")
        return normalized


class MoradorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    condominio_id: uuid.UUID
    unidade_id: uuid.UUID
    nome: str
    cpf: str | None
    telefone: str | None
    email: str | None
    tipo: MoradorTipo
    ativo: bool
    created_at: datetime


