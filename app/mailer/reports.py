from __future__ import annotations

import html
from pathlib import Path

from app.csv.io import CsvReadError, read_csv_rows, resolve_column
from app.mailer.smtp import EmailSendError


def build_manager_report_sections(
    source_csv: Path,
    attendant_column: str,
) -> tuple[str, int, int]:
    fieldnames, rows = _read_csv_for_report(source_csv)
    resolved_attendant_column = _resolve_report_attendant_column(fieldnames, attendant_column)
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        attendant = (row.get(resolved_attendant_column) or "").strip()
        if not attendant:
            attendant = "Sem atendente"
        grouped.setdefault(attendant, []).append(row)

    sections = "\n".join(
        _build_manager_attendant_section(attendant, attendant_rows, fieldnames)
        for attendant, attendant_rows in sorted(grouped.items())
    )
    return sections, len(grouped), len(rows)


def _build_manager_attendant_section(
    attendant: str,
    rows: list[dict[str, str]],
    fieldnames: list[str],
) -> str:
    table_rows = "\n".join(_build_report_table_row(row, fieldnames) for row in rows)
    headers = "\n".join(
        (
            '<th style="border: 1px solid #d9e2ec; padding: 8px; '
            f'text-align: left; background: #f0f4f8;">{html.escape(fieldname)}</th>'
        )
        for fieldname in fieldnames
    )
    if not table_rows:
        table_rows = f"""
        <tr>
          <td colspan="{len(fieldnames)}" style="border: 1px solid #d9e2ec; padding: 8px;">
            Nenhum chamado encontrado no arquivo do atendente.
          </td>
        </tr>
        """

    return f"""
    <h3 style="margin: 24px 0 8px; color: #102a43;">
      {html.escape(attendant)} - {len(rows)} chamado(s)
    </h3>
    <table style="border-collapse: collapse; width: 100%; margin-bottom: 8px; font-size: 13px;">
      <thead>
        <tr>{headers}</tr>
      </thead>
      <tbody>
        {table_rows}
      </tbody>
    </table>
    """


def _build_report_table_row(row: dict[str, str], fieldnames: list[str]) -> str:
    cells = "\n".join(
        (
            '<td style="border: 1px solid #d9e2ec; padding: 8px; '
            f'vertical-align: top;">{html.escape(row.get(fieldname, ""))}</td>'
        )
        for fieldname in fieldnames
    )
    return f"<tr>{cells}</tr>"


def _read_csv_for_report(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    try:
        rows, fieldnames, _dialect = read_csv_rows(path)
    except CsvReadError as error:
        raise EmailSendError(str(error)) from error
    return fieldnames, rows


def _resolve_report_attendant_column(fieldnames: list[str], configured_name: str) -> str:
    try:
        return resolve_column(fieldnames, configured_name, "ATENDENTE")
    except CsvReadError as error:
        available = ", ".join(fieldnames)
        raise EmailSendError(
            f"Coluna de atendente nao encontrada para relatorio da gestora. Colunas: {available}"
        ) from error
