from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


RoleType = Literal["admin", "operador", "sindico"]


class UserCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=5, max_length=255)
    senha: str = Field(min_length=8, max_length=128)
    perfil: RoleType
    ativo: bool = True

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
            raise ValueError("Invalid email.")
        return normalized


class UserLogin(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    senha: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
            raise ValueError("Invalid email.")
        return normalized


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str | None
    email: str
    perfil: RoleType
    ativo: bool
    created_at: datetime


