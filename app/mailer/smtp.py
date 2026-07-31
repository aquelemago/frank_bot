from __future__ import annotations

import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart


class EmailSendError(RuntimeError):
    """Erro ao enviar e-mail."""


def parse_recipients(value: str) -> list[str]:
    recipients = [
        item.strip()
        for chunk in value.split(";")
        for item in chunk.split(",")
        if item.strip()
    ]
    if not recipients:
        raise EmailSendError("Destinatario de e-mail invalido ou vazio.")
    return recipients


def build_attachment(csv_path) -> MIMEBase:
    attachment = MIMEBase("text", "csv")
    attachment.set_payload(csv_path.read_bytes())
    encoders.encode_base64(attachment)
    attachment.add_header(
        "Content-Disposition",
        "attachment",
        filename=csv_path.name,
    )
    return attachment


def send_message(settings, message: MIMEMultipart, recipients: list[str]) -> None:
    with smtplib.SMTP(settings.host, settings.port, timeout=60) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(settings.usuario, settings.senha)
        smtp.send_message(message, from_addr=settings.usuario, to_addrs=recipients)
