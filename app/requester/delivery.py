from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from pathlib import Path

from app.config.models import Soft4Settings
from app.csv.io import CsvReadError, normalize_key, read_csv_rows, resolve_column
from app.soft4.api import fetch_solicitante_emails


LOGGER = logging.getLogger(__name__)


class RequesterDeliveryError(RuntimeError):
    """Erro ao montar entregas do relatorio por solicitante."""


@dataclass(frozen=True)
class RequesterDelivery:
    solicitante: str
    recipient: str
    csv_path: Path
    row_count: int


def build_requester_deliveries(
    source_csv: Path,
    api_settings: Soft4Settings,
    id_column: str,
    output_dir: Path,
) -> list[RequesterDelivery]:
    """Agrupa chamados por e-mail do solicitante via API Softdesk.

    Para cada chamado do CSV, busca o e-mail do solicitante pela API (usando o
    numero do chamado). Chamados sem e-mail sao ignorados. Gera um CSV por
    destinatario em ``output_dir``.
    """
    if not source_csv.exists() or source_csv.stat().st_size == 0:
        raise RequesterDeliveryError(f"CSV de origem invalido ou vazio: {source_csv}")

    try:
        rows, fieldnames, dialect = read_csv_rows(source_csv)
    except CsvReadError as error:
        raise RequesterDeliveryError(str(error)) from error

    if not rows:
        raise RequesterDeliveryError("CSV do solicitante sem registros.")

    id_col = _resolve_required_column(fieldnames, id_column, "ID")
    solicitante_col = _resolve_required_column(fieldnames, "Solicitante", "SOLICITANTE")

    codigos = [row[id_col].strip() for row in rows if row.get(id_col, "").strip()]
    if not codigos:
        raise RequesterDeliveryError("Nenhum numero de chamado encontrado no CSV do solicitante.")

    emails_by_codigo = fetch_solicitante_emails(api_settings, codigos)

    deliveries_by_email: dict[str, dict[str, object]] = {}
    skipped = 0
    for row in rows:
        codigo = row.get(id_col, "").strip()
        email = emails_by_codigo.get(codigo, "").strip()
        if not email:
            skipped += 1
            continue

        entry = deliveries_by_email.setdefault(email, {"solicitante": "", "rows": []})
        solicitante = row.get(solicitante_col, "").strip()
        if not entry["solicitante"] and solicitante:
            entry["solicitante"] = solicitante
        entry["rows"].append(row)

    if not deliveries_by_email:
        raise RequesterDeliveryError("Nenhum e-mail de solicitante obtido pela API Softdesk.")

    output_dir.mkdir(parents=True, exist_ok=True)
    deliveries: list[RequesterDelivery] = []
    for email, entry in sorted(deliveries_by_email.items()):
        solicitante = str(entry["solicitante"]) or email
        rows_by_recipient = entry["rows"]
        csv_path = output_dir / f"{_slug(email)}.csv"
        _write_delivery_csv(csv_path, fieldnames, rows_by_recipient, dialect)
        deliveries.append(
            RequesterDelivery(
                solicitante=solicitante,
                recipient=email,
                csv_path=csv_path,
                row_count=len(rows_by_recipient),
            )
        )

    if skipped:
        LOGGER.warning("Chamados ignorados sem e-mail de solicitante: %s", skipped)
    LOGGER.info("Entregas do relatorio do solicitante montadas: %s", len(deliveries))
    return deliveries


def _resolve_required_column(fieldnames: list[str], configured_name: str, fallback: str) -> str:
    try:
        return resolve_column(fieldnames, configured_name, fallback)
    except CsvReadError as error:
        available = ", ".join(fieldnames)
        raise RequesterDeliveryError(
            f"Coluna nao encontrada no CSV do solicitante. Configure CSV_COLUNA_ID_CHAMADO. "
            f"Colunas: {available}"
        ) from error


def _slug(value: str) -> str:
    slug = normalize_key(value).lower()
    return slug or "solicitante"


def _write_delivery_csv(
    path: Path,
    fieldnames: list[str],
    rows: list[dict[str, str]],
    dialect: csv.Dialect,
) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            delimiter=dialect.delimiter,
            quotechar=dialect.quotechar or '"',
            quoting=dialect.quoting,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
