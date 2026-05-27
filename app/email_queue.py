from __future__ import annotations

import csv
import json
import logging
import os
import shutil
import stat
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from app.csv_utils import CsvReadError, normalize_key, read_csv_rows, resolve_column
from app.settings import EmailQueueSettings


LOGGER = logging.getLogger(__name__)


class EmailQueueError(RuntimeError):
    """Erro ao criar fila de e-mail por atendente."""


@dataclass(frozen=True)
class EmailQueueItem:
    attendant: str
    recipient: str
    csv_path: Path
    metadata_path: Path
    row_count: int


@dataclass(frozen=True)
class EmailQueue:
    queue_dir: Path
    items: list[EmailQueueItem]
    missing_recipients: list[str]


def build_attendant_email_queue(
    source_csv: Path,
    settings: EmailQueueSettings,
    created_at: datetime,
) -> EmailQueue:
    if not source_csv.exists() or source_csv.stat().st_size == 0:
        raise EmailQueueError(f"CSV de origem invalido ou vazio: {source_csv}")

    attendant_emails = load_attendant_emails(settings.attendants_file)
    _clear_previous_queue_dirs(settings.queue_dir)
    run_dir = _create_unique_queue_dir(settings.queue_dir, created_at)

    try:
        rows, fieldnames, dialect = read_csv_rows(source_csv)
    except CsvReadError as error:
        raise EmailQueueError(str(error)) from error
    attendant_column = _resolve_attendant_column(fieldnames, settings.attendant_column)
    grouped = _group_by_attendant(rows, attendant_column)

    if not grouped:
        raise EmailQueueError("Nenhum registro com atendente foi encontrado no CSV.")

    items: list[EmailQueueItem] = []
    missing: list[str] = []

    for attendant, attendant_rows in sorted(grouped.items()):
        recipient = attendant_emails.get(normalize_key(attendant), "")
        if not recipient:
            missing.append(attendant)
            continue

        slug = slugify(attendant)
        csv_path = run_dir / f"{slug}.csv"
        metadata_path = run_dir / f"{slug}.json"

        _write_attendant_csv(csv_path, fieldnames, attendant_rows, dialect)
        item = EmailQueueItem(
            attendant=attendant,
            recipient=recipient,
            csv_path=csv_path,
            metadata_path=metadata_path,
            row_count=len(attendant_rows),
        )
        _write_metadata(item, "pending", created_at)
        items.append(item)

    _write_queue_summary(run_dir, source_csv, items, missing, created_at)

    if missing and settings.fail_on_missing_attendant_email:
        names = ", ".join(missing)
        raise EmailQueueError(f"Atendentes sem e-mail configurado: {names}")
    if missing:
        LOGGER.warning("Atendentes sem e-mail configurado: %s", ", ".join(missing))

    LOGGER.info("Fila de email criada: %s", run_dir)
    LOGGER.info("Itens na fila: %s", len(items))
    return EmailQueue(queue_dir=run_dir, items=items, missing_recipients=missing)


def mark_queue_item_sent(item: EmailQueueItem, sent_at: datetime) -> None:
    _write_metadata(item, "sent", sent_at)


def mark_queue_item_failed(item: EmailQueueItem, failed_at: datetime, error: Exception) -> None:
    _write_metadata(item, "failed", failed_at, str(error))


def load_attendant_emails(path: Path) -> dict[str, str]:
    emails: dict[str, str] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.startswith("EMAIL_") and value.strip():
                emails[normalize_key(key.removeprefix("EMAIL_"))] = value.strip().strip('"').strip("'")

    reserved = {
        "EMAIL_HOST",
        "EMAIL_PORT",
        "EMAIL_USUARIO",
        "EMAIL_SENHA",
        "EMAIL_ATENDENTES_FILE",
        "EMAIL_FALHAR_SE_ATENDENTE_SEM_EMAIL",
        "EMAIL_REMETENTE",
        "EMAIL_GESTORA_RELATORIO",
        "NOME_GESTORA_RELATORIO",
    }
    for key, value in os.environ.items():
        if key.startswith("EMAIL_") and key not in reserved and value.strip():
            emails[normalize_key(key.removeprefix("EMAIL_"))] = value.strip()

    return emails


def slugify(value: str) -> str:
    slug = normalize_key(value).lower()
    return slug or "atendente"


def _create_unique_queue_dir(base_dir: Path, created_at: datetime) -> Path:
    stem = created_at.strftime("%Y%m%d_%H%M%S")
    candidate = base_dir / stem
    index = 2
    while candidate.exists():
        candidate = base_dir / f"{stem}_{index}"
        index += 1
    candidate.mkdir(parents=True)
    return candidate


def _clear_previous_queue_dirs(base_dir: Path) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    removed = 0
    for item in base_dir.iterdir():
        if item.is_dir():
            shutil.rmtree(item, onerror=_remove_readonly)
            removed += 1
    if removed:
        LOGGER.info("Filas antigas removidas: %s", removed)


def _remove_readonly(function, path, exc_info) -> None:
    try:
        os.chmod(path, stat.S_IWRITE)
        function(path)
    except Exception:
        raise exc_info[1]


def _resolve_attendant_column(fieldnames: list[str], configured_name: str) -> str:
    try:
        return resolve_column(fieldnames, configured_name, "ATENDENTE")
    except CsvReadError as error:
        available = ", ".join(fieldnames)
        raise EmailQueueError(
            f"Coluna de atendente nao encontrada. Configure CSV_COLUNA_ATENDENTE. Colunas: {available}"
        ) from error


def _group_by_attendant(rows: list[dict[str, str]], attendant_column: str) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        attendant = (row.get(attendant_column) or "").strip()
        if not attendant:
            continue
        grouped.setdefault(attendant, []).append(row)
    return grouped


def _write_attendant_csv(
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


def _write_metadata(
    item: EmailQueueItem,
    status: str,
    timestamp: datetime,
    error: str | None = None,
) -> None:
    data = {
        "atendente": item.attendant,
        "destinatario": item.recipient,
        "csv": str(item.csv_path),
        "registros": item.row_count,
        "status": status,
        "atualizado_em": timestamp.isoformat(timespec="seconds"),
    }
    if error:
        data["erro"] = error

    item.metadata_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_queue_summary(
    queue_dir: Path,
    source_csv: Path,
    items: list[EmailQueueItem],
    missing: list[str],
    created_at: datetime,
) -> None:
    summary = {
        "criado_em": created_at.isoformat(timespec="seconds"),
        "csv_origem": str(source_csv),
        "total_itens": len(items),
        "itens": [
            {
                "atendente": item.attendant,
                "destinatario": item.recipient,
                "csv": str(item.csv_path),
                "registros": item.row_count,
            }
            for item in items
        ],
        "atendentes_sem_email": missing,
    }
    (queue_dir / "queue.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
