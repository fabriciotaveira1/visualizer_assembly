from __future__ import annotations

from typing import Any
import unicodedata


COLUMN_ALIASES = {
    "nome": "nome",
    "bloco": "bloco",
    "unidade": "identificador_externo",
    "apartamento": "identificador_externo",
    "tipo": "tipo",
    "status": "ativo",
    "cpf": "cpf",
    "email": "email",
    "email 1": "email",
    "e-mail": "email",
    "celular": "telefone",
    "telefone": "telefone",
    "residencial": "telefone",
}

TIPO_ALIASES = {
    "proprietario": "proprietario",
    "proprietário": "proprietario",
    "inquilino": "inquilino",
    "locatario": "inquilino",
    "locatário": "inquilino",
}


def map_morador_row(row: dict[str, Any]) -> dict[str, Any]:
    mapped: dict[str, Any] = {}

    for source_key, value in row.items():
        target_key = COLUMN_ALIASES.get(_normalize_key(source_key))
        if target_key is None:
            continue

        if target_key == "ativo":
            mapped[target_key] = _map_status_to_active(value)
            continue
        if target_key == "tipo":
            mapped[target_key] = _map_tipo(value)
            continue
        if target_key == "email":
            mapped[target_key] = _normalize_email(value)
            continue
        mapped[target_key] = _normalize_text(value)

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


def _normalize_email(value: Any) -> str | None:
    normalized = _normalize_text(value)
    if normalized is None:
        return None
    normalized = normalized.lower()
    if "@" not in normalized:
        return None
    return normalized


def _map_status_to_active(value: Any) -> bool:
    normalized = (_normalize_text(value) or "").lower()
    return "inativ" not in normalized and "cancel" not in normalized


def _map_tipo(value: Any) -> str | None:
    normalized = unicodedata.normalize("NFKD", (_normalize_text(value) or "").lower())
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    return TIPO_ALIASES.get(normalized)


