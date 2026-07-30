from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path


class CsvReadError(RuntimeError):
    """Erro ao ler CSV da automacao."""


def normalize_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^A-Z0-9]+", "_", ascii_value.upper()).strip("_")


def read_csv_rows(path: Path) -> tuple[list[dict[str, str]], list[str], csv.Dialect]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    if not text.strip():
        raise CsvReadError("CSV esta vazio.")

    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;|\t")
    except csv.Error:
        dialect = csv.excel

    reader = csv.DictReader(text.splitlines(), dialect=dialect)
    if not reader.fieldnames:
        raise CsvReadError("CSV sem cabecalho.")

    rows = [dict(row) for row in reader if any(_cell_has_content(value) for value in row.values())]
    return rows, list(reader.fieldnames), dialect


def resolve_column(fieldnames: list[str], configured_name: str, fallback_contains: str) -> str:
    wanted = normalize_key(configured_name)
    for fieldname in fieldnames:
        if normalize_key(fieldname) == wanted:
            return fieldname

    fallback = normalize_key(fallback_contains)
    for fieldname in fieldnames:
        if fallback in normalize_key(fieldname):
            return fieldname

    available = ", ".join(fieldnames)
    raise CsvReadError(f"Coluna nao encontrada. Colunas: {available}")


def _cell_has_content(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, list):
        return any(_cell_has_content(item) for item in value)
    return bool(str(value).strip())
