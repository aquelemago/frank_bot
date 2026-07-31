from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from app.config.models import (
    AppSettings,
    EmailQueueSettings,
    EmailSettings,
    ManagerReportSettings,
    RequesterReportSettings,
    Soft4Settings,
)
from app.infra.fs import PROJECT_ROOT


class ConfigError(RuntimeError):
    """Erro de configuracao da aplicacao."""


def _env(name: str, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(name, default)
    if required and not value:
        raise ConfigError(f"Variavel obrigatoria ausente: {name}")
    return value or ""


def _env_any(names: tuple[str, ...], default: str | None = None, required: bool = False) -> str:
    for name in names:
        value = os.getenv(name)
        if value:
            return value

    if required and not default:
        joined = ", ".join(names)
        raise ConfigError(f"Variavel obrigatoria ausente: {joined}")
    return default or ""


def _env_int(name: str, default: str) -> int:
    value = _env(name, default)
    try:
        parsed = int(value)
    except ValueError as error:
        raise ConfigError(f"Variavel {name} deve ser numerica. Valor recebido: {value}") from error
    if parsed <= 0:
        raise ConfigError(f"Variavel {name} deve ser maior que zero. Valor recebido: {value}")
    return parsed


def _env_any_int(names: tuple[str, ...], default: str) -> int:
    value = _env_any(names, default, required=True)
    try:
        parsed = int(value)
    except ValueError as error:
        joined = ", ".join(names)
        raise ConfigError(f"Variavel {joined} deve ser numerica. Valor recebido: {value}") from error
    if parsed <= 0:
        joined = ", ".join(names)
        raise ConfigError(f"Variavel {joined} deve ser maior que zero. Valor recebido: {value}")
    return parsed


def _env_bool(name: str, default: str) -> bool:
    value = _env(name, default).strip().lower()
    return value in {"1", "true", "sim", "yes", "y", "s"}


def load_settings() -> AppSettings:
    load_dotenv(PROJECT_ROOT / ".env")
    load_dotenv(PROJECT_ROOT / "config" / "email_bot.env", override=False)
    load_dotenv(PROJECT_ROOT / "config" / "email_atendente.env", override=False)

    downloads_dir = PROJECT_ROOT / "downloads"
    user_data_dir = PROJECT_ROOT / "perfil_soft4"
    email_queue_dir = PROJECT_ROOT / "email_queue"
    attendants_file = Path(
        _env("EMAIL_ATENDENTES_FILE", str(PROJECT_ROOT / "config" / "email_atendente.env"))
    )
    if not attendants_file.is_absolute():
        attendants_file = PROJECT_ROOT / attendants_file

    settings = AppSettings(
        soft4=Soft4Settings(
            base_url=_env("SOFT4_BASE_URL", "https://mainhardt.soft4.com.br").rstrip("/"),
            queue_path=_env("SOFT4_FILA_PATH", "/chamado/fila-de-atendimento"),
            csv_path=_env("SOFT4_CSV_PATH", "/chamado/fila-de-atendimento/csv"),
            listing_type=_env("SOFT4_TP_LISTAGEM", "SEM_INTERACAO_ATENDENTE"),
            no_interaction_attendant_days=_env_int("SOFT4_DIAS_SEM_INTERACAO_ATENDENTE", "3"),
            requester_listing_type=_env("SOFT4_TP_LISTAGEM_SOLICITANTE", "SEM_INTERACAO_SOLICITANTE"),
            no_interaction_requester_days=_env_int("SOFT4_DIAS_SEM_INTERACAO_SOLICITANTE", "5"),
            additional_holidays=_env("SOFT4_FERIADOS_ADICIONAIS", ""),
            usuario=_env("SOFT4_USUARIO", required=True),
            senha=_env("SOFT4_SENHA", required=True),
            user_data_dir=user_data_dir,
            timeout_seconds=_env_int("SOFT4_TIMEOUT_SECONDS", "60"),
            retries=_env_int("SOFT4_RETRIES", "3"),
        ),
        email=EmailSettings(
            host=_env_any(("EMAIL_HOST", "SMTP_HOST"), "smtp.office365.com", required=True),
            port=_env_any_int(("EMAIL_PORT", "SMTP_PORT"), "587"),
            usuario=_env_any(("EMAIL_USUARIO", "EMAIL_REMETENTE"), required=True),
            senha=_env_any(("EMAIL_SENHA", "SENHA"), required=True),
        ),
        email_queue=EmailQueueSettings(
            queue_dir=email_queue_dir,
            attendants_file=attendants_file,
            attendant_column=_env("CSV_COLUNA_ATENDENTE", "atendente"),
            last_interaction_column=_env("CSV_COLUNA_ULTIMA_INTERACAO", "ultima interacao"),
            fail_on_missing_attendant_email=_env_bool("EMAIL_FALHAR_SE_ATENDENTE_SEM_EMAIL", "true"),
        ),
        manager_report=ManagerReportSettings(
            recipient=_env("EMAIL_GESTORA_RELATORIO", "francieli.cazuni@unus.solutions"),
            name=_env("NOME_GESTORA_RELATORIO", "Francieli"),
        ),
        requester_report=RequesterReportSettings(
            recipient=_env("EMAIL_SOLICITANTE_RELATORIO", "lcabra570@gmail.com", required=True),
            name=_env("NOME_SOLICITANTE_RELATORIO", "Teste"),
            last_interaction_column=_env("CSV_COLUNA_ULTIMA_INTERACAO_SOLICITANTE", "ultima interacao solicitante"),
        ),
        downloads_dir=downloads_dir,
        requester_downloads_dir=downloads_dir,
    )

    settings.downloads_dir.mkdir(parents=True, exist_ok=True)
    settings.email_queue.queue_dir.mkdir(parents=True, exist_ok=True)
    settings.soft4.user_data_dir.mkdir(parents=True, exist_ok=True)
    return settings


def load_email_settings() -> EmailSettings:
    load_dotenv(PROJECT_ROOT / ".env")
    load_dotenv(PROJECT_ROOT / "config" / "email_bot.env", override=False)

    return EmailSettings(
        host=_env_any(("EMAIL_HOST", "SMTP_HOST"), "smtp.office365.com", required=True),
        port=_env_any_int(("EMAIL_PORT", "SMTP_PORT"), "587"),
        usuario=_env_any(("EMAIL_USUARIO", "EMAIL_REMETENTE"), required=True),
        senha=_env_any(("EMAIL_SENHA", "SENHA"), required=True),
    )
