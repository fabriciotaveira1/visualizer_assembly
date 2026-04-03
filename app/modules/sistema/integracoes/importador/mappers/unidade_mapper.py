from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any
import unicodedata


COLUMN_ALIASES = {
    "bloco": "bloco",
    "torre": "bloco",
    "unidade": "identificador_externo",
    "apartamento": "identificador_externo",
    "numero": "numero",
    "número": "numero",
    "fracao": "fracao_ideal",
    "fração": "fracao_ideal",
    "fracao ideal": "fracao_ideal",
    "fração ideal": "fracao_ideal",
    "status": "ativo",
}


def map_unidade_row(row: dict[str, Any]) -> dict[str, Any]:
    mapped: dict[str, Any] = {}

    for source_key, value in row.items():
        target_key = COLUMN_ALIASES.get(_normalize_key(source_key))
        if target_key is None:
            continue

        if target_key == "ativo":
            mapped[target_key] = _map_status_to_active(value)
            continue
        if target_key == "fracao_ideal":
            mapped[target_key] = _parse_decimal(value)
            continue
        mapped[target_key] = _normalize_text(value)

    identificador = mapped.get("identificador_externo")
    if identificador and not mapped.get("numero"):
        mapped["numero"] = identificador

    mapped.setdefault("ativo", True)
    return mapped


def _normalize_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    return " ".join(normalized.strip().lower().replace("_", " ").split())


def _normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _parse_decimal(value: Any) -> Decimal | None:
    normalized = _normalize_text(value)
    if normalized in {None, "-", ""}:
        return None

    if "," in normalized and "." in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")
    elif "," in normalized:
        normalized = normalized.replace(",", ".")

    try:
        return Decimal(normalized)
    except (InvalidOperation, ValueError):
        return None


def _map_status_to_active(value: Any) -> bool:
    normalized = (_normalize_text(value) or "").lower()
    return "inativ" not in normalized and "cancel" not in normalized


