from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.condominio.condominio.service import get_condominio_by_id


def validate_moradores_context(db: Session, condominio_id: UUID) -> None:
    get_condominio_by_id(db, condominio_id)


def validate_morador_row(mapped_row: dict) -> list[str]:
    errors: list[str] = []

    if not mapped_row.get("nome"):
        errors.append("nome is required.")
    if not mapped_row.get("identificador_externo"):
        errors.append("identificador_externo is required.")
    if not mapped_row.get("tipo"):
        errors.append("tipo must be proprietario or inquilino.")

    return errors


