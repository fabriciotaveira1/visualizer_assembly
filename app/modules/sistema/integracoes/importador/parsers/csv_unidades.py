from __future__ import annotations

import csv
from io import StringIO


def parse_csv_unidades(content: str) -> list[dict[str, str]]:
    return _parse_csv_rows(content)


def _parse_csv_rows(content: str) -> list[dict[str, str]]:
    if not content.strip():
        return []

    try:
        dialect = csv.Sniffer().sniff(content[:2048], delimiters=";,")
        reader = csv.DictReader(StringIO(content), dialect=dialect)
    except csv.Error:
        reader = csv.DictReader(StringIO(content), delimiter=";")

    rows: list[dict[str, str]] = []
    for row in reader:
        normalized_row: dict[str, str] = {}
        for key, value in row.items():
            if key is None:
                continue
            if isinstance(value, list):
                normalized_value = " | ".join(str(item).strip() for item in value if item)
            else:
                normalized_value = (value or "").strip()
            normalized_row[str(key).strip()] = normalized_value
        if not any(normalized_row.values()):
            continue
        rows.append(normalized_row)
    return rows


