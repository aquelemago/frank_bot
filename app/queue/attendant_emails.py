from __future__ import annotations

import logging
import os
from pathlib import Path

from app.csv.io import normalize_key


LOGGER = logging.getLogger(__name__)


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
