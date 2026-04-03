from __future__ import annotations


def validate_voto_import_row(
    mapped_row: dict,
    seen_identificadores: set[str],
) -> list[str]:
    errors: list[str] = []

    identificador = mapped_row.get("identificador_externo")
    if not identificador:
        errors.append("identificador_externo is required.")
    elif identificador.lower() in seen_identificadores:
        errors.append("Duplicate unidade inside CSV.")

    if mapped_row.get("codigo_opcao") is None:
        errors.append("codigo_opcao is required.")

    if not mapped_row.get("descricao_opcao") and mapped_row.get("codigo_opcao") is None:
        errors.append("descricao_opcao is required when codigo_opcao is missing.")

    if mapped_row.get("tipo_voto") is None:
        mapped_row["tipo_voto"] = "direto"

    return errors


