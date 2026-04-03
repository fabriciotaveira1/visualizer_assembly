from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.condominio.service import get_condominio_by_id


def validate_unidades_context(db: Session, condominio_id: UUID) -> None:
    get_condominio_by_id(db, condominio_id)


def validate_unidade_row(
    mapped_row: dict,
    seen_identificadores: set[str],
) -> list[str]:
    errors: list[str] = []

    identificador = mapped_row.get("identificador_externo")
    if not identificador:
        errors.append("identificador_externo is required.")
    elif identificador.lower() in seen_identificadores:
        errors.append("Duplicate identificador_externo inside CSV.")

    return errors
