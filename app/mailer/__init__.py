from __future__ import annotations

import html
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from app.config.models import EmailSettings
from app.csv.io import read_csv_rows
from app.mailer.reports import build_manager_report_sections, _build_report_table_row
from app.mailer.smtp import (
    EmailSendError,
    build_attachment,
    build_signature_image,
    parse_recipients,
    send_message as _send_message,
)
from app.mailer.templates import (
    render_attendant_email,
    render_dry_run_success_email,
    render_manager_report_email,
    render_requester_report_email,
    render_test_email,
)


LOGGER = logging.getLogger(__name__)


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

    recipients = parse_recipients(recipient)
    message = MIMEMultipart()
    message["From"] = settings.usuario
    message["To"] = ", ".join(recipients)
    message["Subject"] = (
        f"Chamados sem interacao ha {no_interaction_days} dias - {exported_at:%d/%m/%Y}"
    )

    html_body = render_attendant_email(
        attendant=attendant,
        exported_at=exported_at,
        row_count=row_count,
        no_interaction_days=no_interaction_days,
    )
    message.attach(MIMEText(html_body, "html", "utf-8"))
    message.attach(build_attachment(csv_path))

    try:
        _send_message(settings, message, recipients)
    except Exception as error:
        raise EmailSendError(f"Falha ao enviar e-mail para {attendant}: {error}") from error

    LOGGER.info("Email enviado para %s (%s)", attendant, recipient)


def send_test_email(
    settings: EmailSettings,
    recipient: str,
    sent_at: datetime | None = None,
    include_signature: bool = False,
) -> None:
    sent_at = sent_at or datetime.now()
    recipients = parse_recipients(recipient)

    # Create a multipart/related message for inline images
    message = MIMEMultipart('related')
    message["From"] = settings.usuario
    message["To"] = ", ".join(recipients)
    message["Subject"] = f"Teste de envio - Automacao Soft4 - {sent_at:%d/%m/%Y %H:%M}"

    html_body = render_test_email(sent_at=sent_at, include_signature=include_signature)
    
    # Create an alternative part for HTML content
    msg_alternative = MIMEMultipart('alternative')
    message.attach(msg_alternative)
    msg_alternative.attach(MIMEText(html_body, "html", "utf-8"))

    # Add signature image as inline if requested
    if include_signature:
        signature_path = Path("assinatura.png")
        if signature_path.exists():
            message.attach(build_signature_image(signature_path, "assinatura"))

    try:
        _send_message(settings, message, recipients)
    except Exception as error:
        raise EmailSendError(f"Falha ao enviar e-mail de teste: {error}") from error

    LOGGER.info("Email de teste enviado para %s", recipient)


def send_dry_run_success_email(
    settings: EmailSettings,
    recipient: str,
    exported_at: datetime,
    simulated_individual_emails: int,
    queue_dir: Path,
) -> None:
    recipients = parse_recipients(recipient)

    message = MIMEMultipart()
    message["From"] = settings.usuario
    message["To"] = ", ".join(recipients)
    message["Subject"] = f"Dry-run bem-sucedido - Automacao Soft4 - {exported_at:%d/%m/%Y}"

    html_body = render_dry_run_success_email(
        exported_at=exported_at,
        simulated_individual_emails=simulated_individual_emails,
        queue_dir=queue_dir,
    )
    message.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        _send_message(settings, message, recipients)
    except Exception as error:
        raise EmailSendError(f"Falha ao enviar confirmacao de dry-run: {error}") from error

    LOGGER.info("Confirmacao de dry-run enviada para %s", recipient)


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

    recipients = parse_recipients(recipient)
    sections, total_attendants, total_rows = build_manager_report_sections(
        source_csv,
        attendant_column,
    )

    message = MIMEMultipart()
    message["From"] = settings.usuario
    message["To"] = ", ".join(recipients)
    message["Subject"] = (
        f"Relatorio gerencial de chamados sem interacao - {exported_at:%d/%m/%Y}"
    )

    html_body = render_manager_report_email(
        manager_name=manager_name,
        exported_at=exported_at,
        no_interaction_days=no_interaction_days,
        total_attendants=total_attendants,
        total_rows=total_rows,
        sections=sections,
    )
    message.attach(MIMEText(html_body, "html", "utf-8"))
    message.attach(build_attachment(source_csv))

    try:
        _send_message(settings, message, recipients)
    except Exception as error:
        raise EmailSendError(f"Falha ao enviar relatorio para gestora: {error}") from error

    LOGGER.info("Relatorio gerencial enviado para %s", recipient)


def send_requester_report_email(
    settings: EmailSettings,
    recipient: str,
    requester_name: str,
    source_csv: Path,
    no_interaction_days: int,
    exported_at: datetime,
) -> None:
    if not source_csv.exists() or source_csv.stat().st_size == 0:
        raise EmailSendError(f"CSV de origem invalido ou vazio: {source_csv}")

    recipients = parse_recipients(recipient)
    rows, fieldnames, _dialect = read_csv_rows(source_csv)
    total_rows = len(rows)
    headers = "\n".join(
        (
            '<th style="border: 1px solid #d9e2ec; padding: 8px; '
            f'text-align: left; background: #f0f4f8;">{html.escape(fieldname)}</th>'
        )
        for fieldname in fieldnames
    )
    table_rows = "\n".join(
        _build_report_table_row(row, fieldnames) for row in rows
    )
    sections = f"""
    <table style="border-collapse: collapse; width: 100%; margin-bottom: 8px; font-size: 13px;">
      <thead>
        <tr>{headers}</tr>
      </thead>
      <tbody>
        {table_rows}
      </tbody>
    </table>
    """

    # Create a multipart/related message for inline images
    message = MIMEMultipart('related')
    message["From"] = settings.usuario
    message["To"] = ", ".join(recipients)
    message["Subject"] = (
        f"Relatorio de chamados sem interacao do solicitante - {exported_at:%d/%m/%Y}"
    )

    html_body = render_requester_report_email(
        requester_name=requester_name,
        exported_at=exported_at,
        no_interaction_days=no_interaction_days,
        total_rows=total_rows,
        sections=sections,
        include_signature=True,  # Always include signature for requester reports
    )
    
    # Create an alternative part for HTML content
    msg_alternative = MIMEMultipart('alternative')
    message.attach(msg_alternative)
    msg_alternative.attach(MIMEText(html_body, "html", "utf-8"))
    
    # Add signature image as inline
    signature_path = Path("assinatura.png")
    if signature_path.exists():
        message.attach(build_signature_image(signature_path, "assinatura"))
    
    # Add CSV attachment
    message.attach(build_attachment(source_csv))

    try:
        _send_message(settings, message, recipients)
    except Exception as error:
        raise EmailSendError(f"Falha ao enviar relatorio para solicitante: {error}") from error

    LOGGER.info("Relatorio do solicitante enviado para %s", recipient)


__all__ = [
    "EmailSendError",
    "send_attendant_csv_email",
    "send_dry_run_success_email",
    "send_manager_report_email",
    "send_requester_report_email",
    "send_test_email",
]
