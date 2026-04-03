from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


StatusAssembleia = Literal["criada", "aberta", "em_andamento", "encerrada", "finalizada"]


class AssembleiaCreate(BaseModel):
    condominio_id: uuid.UUID
    titulo: str = Field(min_length=1, max_length=255)
    data: date

    @field_validator("titulo")
    @classmethod
    def normalize_titulo(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Titulo da assembleia e obrigatorio.")
        return normalized


class AssembleiaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    condominio_id: uuid.UUID | None
    titulo: str | None
    data: date | None
    status: str | None
    created_at: datetime
