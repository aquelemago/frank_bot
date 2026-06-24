from __future__ import annotations

import html
import logging
import smtplib
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from app.csv_utils import CsvReadError, read_csv_rows, resolve_column
from app.settings import EmailSettings


LOGGER = logging.getLogger(__name__)


class EmailSendError(RuntimeError):
    """Erro ao enviar e-mail."""


def send_attendant_csv_email(
    settings: EmailSettings,
    recipient: str,
    attendant: str,
    csv_path: Path,
    exported_at: datetime,
    row_count: int,
    no_interaction_days: int,
) -> None:
    if not csv_path.exists() or csv_path.stat().st_size == 0:
        raise EmailSendError(f"Anexo invalido ou vazio: {csv_path}")

    recipients = _parse_recipients(recipient)
    message = MIMEMultipart()
    message["From"] = settings.usuario
    message["To"] = ", ".join(recipients)
    message["Subject"] = (
        f"Chamados sem interacao ha {no_interaction_days} dias - {exported_at:%d/%m/%Y}"
    )

    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #1f2933; line-height: 1.5;">
        <p>Ol&aacute;, {html.escape(attendant)}.</p>

        <p>
          Segue em anexo a rela&ccedil;&atilde;o de chamados vinculados ao seu atendimento
          que est&atilde;o sem qualquer intera&ccedil;&atilde;o h&aacute; {no_interaction_days}
          dias ou mais.
        </p>

        <p>
          Conforme observado, h&aacute; chamados pendentes que necessitam de revis&atilde;o
          priorit&aacute;ria, principalmente nos casos em que o cliente aguarda retorno ou
          atualiza&ccedil;&atilde;o do andamento. Refor&ccedil;amos a import&acirc;ncia de avaliar
          os chamados listados o quanto antes, evitando impacto no atendimento.
        </p>

        <p>
          <strong>Total de chamados no anexo:</strong> {row_count}<br>
          <strong>Data e hora da exporta&ccedil;&atilde;o:</strong> {exported_at:%d/%m/%Y %H:%M:%S}
        </p>

        <p>
          Esta &eacute; uma mensagem autom&aacute;tica da rotina de apoio do Soft4.
        </p>
      </body>
    </html>
    """
    message.attach(MIMEText(html_body, "html", "utf-8"))
    message.attach(_build_attachment(csv_path))

    try:
        _send_message(settings, message, recipients)
    except Exception as error:
        raise EmailSendError(f"Falha ao enviar e-mail para {attendant}: {error}") from error

    LOGGER.info("Email enviado para %s (%s)", attendant, recipient)


def send_test_email(
    settings: EmailSettings,
    recipient: str,
    sent_at: datetime | None = None,
) -> None:
    sent_at = sent_at or datetime.now()
    recipients = _parse_recipients(recipient)

    message = MIMEMultipart()
    message["From"] = settings.usuario
    message["To"] = ", ".join(recipients)
    message["Subject"] = f"Teste de envio - Automacao Soft4 - {sent_at:%d/%m/%Y %H:%M}"

    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #1f2933; line-height: 1.5;">
        <p>Ola.</p>

        <p>
          Este e um e-mail de teste da automacao Soft4/Mainhardt.
        </p>

        <p>
          Se voce recebeu esta mensagem, as configuracoes SMTP estao funcionando
          para envio pela rotina.
        </p>

        <p>
          <strong>Data e hora do teste:</strong> {sent_at:%d/%m/%Y %H:%M:%S}
        </p>
      </body>
    </html>
    """
    message.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        _send_message(settings, message, recipients)
    except Exception as error:
        raise EmailSendError(f"Falha ao enviar e-mail de teste: {error}") from error

    LOGGER.info("Email de teste enviado para %s", recipient)


def send_manager_report_email(
    settings: EmailSettings,
    recipient: str,
    manager_name: str,
    source_csv: Path,
    attendant_column: str,
    exported_at: datetime,
    no_interaction_days: int,
) -> None:
    if not source_csv.exists() or source_csv.stat().st_size == 0:
        raise EmailSendError(f"CSV de origem invalido ou vazio: {source_csv}")

    recipients = _parse_recipients(recipient)
    sections, total_attendants, total_rows = _build_manager_report_sections(
        source_csv,
        attendant_column,
    )

    message = MIMEMultipart()
    message["From"] = settings.usuario
    message["To"] = ", ".join(recipients)
    message["Subject"] = (
        f"Relatorio gerencial de chamados sem interacao - {exported_at:%d/%m/%Y}"
    )

    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #1f2933; line-height: 1.5;">
        <p>Ola, {html.escape(manager_name)}.</p>

        <p>
          Segue o relatorio consolidado dos chamados sem interacao do atendente ha
          {no_interaction_days} dias ou mais, organizado por atendente.
        </p>

        <p>
          <strong>Total de atendentes no relatorio:</strong> {total_attendants}<br>
          <strong>Total de chamados:</strong> {total_rows}<br>
          <strong>Data e hora da exportacao:</strong> {exported_at:%d/%m/%Y %H:%M:%S}
        </p>

        {sections}

        <p>
          O CSV completo da exportacao tambem segue em anexo para conferencia ou filtro.
        </p>

        <p>
          Esta e uma mensagem automatica da rotina de apoio do Soft4.
        </p>
      </body>
    </html>
    """
    message.attach(MIMEText(html_body, "html", "utf-8"))
    message.attach(_build_attachment(source_csv))

    try:
        _send_message(settings, message, recipients)
    except Exception as error:
        raise EmailSendError(f"Falha ao enviar relatorio para gestora: {error}") from error

    LOGGER.info("Relatorio gerencial enviado para %s", recipient)


def _send_message(settings: EmailSettings, message: MIMEMultipart, recipients: list[str]) -> None:
    with smtplib.SMTP(settings.host, settings.port, timeout=60) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(settings.usuario, settings.senha)
        smtp.send_message(message, from_addr=settings.usuario, to_addrs=recipients)


def _parse_recipients(value: str) -> list[str]:
    recipients = [
        item.strip()
        for chunk in value.split(";")
        for item in chunk.split(",")
        if item.strip()
    ]
    if not recipients:
        raise EmailSendError("Destinatario de e-mail invalido ou vazio.")
    return recipients


def _build_manager_report_sections(
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


def _build_attachment(csv_path: Path) -> MIMEBase:
    attachment = MIMEBase("text", "csv")
    attachment.set_payload(csv_path.read_bytes())
    encoders.encode_base64(attachment)
    attachment.add_header(
        "Content-Disposition",
        "attachment",
        filename=csv_path.name,
    )
    return attachment
