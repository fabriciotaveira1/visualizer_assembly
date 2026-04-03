from __future__ import annotations

from app.integracoes.importador.parsers.csv_unidades import _parse_csv_rows


def parse_csv_votos(content: str) -> list[dict[str, str]]:
    return _parse_csv_rows(content)
