from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class ConfigError(RuntimeError):
    """Erro de configuracao da aplicacao."""


@dataclass(frozen=True)
class Soft4Settings:
    base_url: str
    queue_path: str
    csv_path: str
    listing_type: str
    no_interaction_attendant_days: int
    additional_holidays: str
    usuario: str
    senha: str
    user_data_dir: Path
    timeout_seconds: int
    retries: int

    @property
    def queue_url(self) -> str:
        return f"{self.base_url}{self.queue_path}"

    @property
    def csv_url(self) -> str:
        return f"{self.base_url}{self.csv_path}"


@dataclass(frozen=True)
class EmailSettings:
    host: str
    port: int
    usuario: str
    senha: str


@dataclass(frozen=True)
class EmailQueueSettings:
    queue_dir: Path
    attendants_file: Path
    attendant_column: str
    last_interaction_column: str
    fail_on_missing_attendant_email: bool


@dataclass(frozen=True)
class ManagerReportSettings:
    recipient: str
    name: str


@dataclass(frozen=True)
class AppSettings:
    soft4: Soft4Settings
    email: EmailSettings
    email_queue: EmailQueueSettings
    manager_report: ManagerReportSettings
    downloads_dir: Path


def setup_logging(log_dir: Path | None = None) -> Path:
    target_dir = log_dir or PROJECT_ROOT / "logs"
    target_dir.mkdir(parents=True, exist_ok=True)
    log_path = target_dir / "frank_bot.log"

    logging.addLevelName(logging.ERROR, "ERRO")
    logging.addLevelName(logging.WARNING, "AVISO")
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if not any(getattr(handler, "_frank_bot_handler", False) for handler in root_logger.handlers):
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        setattr(stream_handler, "_frank_bot_handler", True)

        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        setattr(file_handler, "_frank_bot_handler", True)

        root_logger.addHandler(stream_handler)
        root_logger.addHandler(file_handler)

    return log_path


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
        downloads_dir=downloads_dir,
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
