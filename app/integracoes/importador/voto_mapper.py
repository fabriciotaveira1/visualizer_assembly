from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any
import unicodedata


COLUMN_ALIASES = {
    "unidade": "identificador_externo",
    "apartamento": "identificador_externo",
    "unidade id": "identificador_externo",
    "codigo opcao": "codigo_opcao",
    "codigo_opcao": "codigo_opcao",
    "opcao": "descricao_opcao",
    "opcao voto": "descricao_opcao",
    "descricao opcao": "descricao_opcao",
    "descricao_opcao": "descricao_opcao",
    "peso": "peso",
    "tipo voto": "tipo_voto",
    "tipo_voto": "tipo_voto",
}


def map_voto_row(row: dict[str, Any]) -> dict[str, Any]:
    mapped: dict[str, Any] = {}
    for source_key, value in row.items():
        target_key = COLUMN_ALIASES.get(_normalize_key(source_key))
        if target_key is None:
            continue

        if target_key == "codigo_opcao":
            mapped[target_key] = _parse_int(value)
        elif target_key == "peso":
            mapped[target_key] = _parse_decimal(value)
        elif target_key == "tipo_voto":
            mapped[target_key] = _normalize_tipo_voto(value)
        else:
            mapped[target_key] = _normalize_text(value)

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


def _parse_int(value: Any) -> int | None:
    normalized = _normalize_text(value)
    if normalized is None:
        return None
    try:
        return int(normalized)
    except ValueError:
        return None


def _parse_decimal(value: Any) -> Decimal | None:
    normalized = _normalize_text(value)
    if normalized in {None, ""}:
        return None
    if "," in normalized and "." in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")
    elif "," in normalized:
        normalized = normalized.replace(",", ".")
    try:
        return Decimal(normalized)
    except (InvalidOperation, ValueError):
        return None


def _normalize_tipo_voto(value: Any) -> str | None:
    normalized = (_normalize_text(value) or "").lower()
    if normalized in {"direto", "procuracao", "procuração"}:
        return "procuracao" if normalized != "direto" else "direto"
    return None
