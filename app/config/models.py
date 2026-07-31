from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Soft4Settings:
    base_url: str
    queue_path: str
    csv_path: str
    listing_type: str
    no_interaction_attendant_days: int
    requester_listing_type: str
    no_interaction_requester_days: int
    additional_holidays: str
    api_key: str
    api_path: str
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
class RequesterReportSettings:
    recipient: str
    name: str
    last_interaction_column: str
    id_column: str
    full_report_recipient: str


@dataclass(frozen=True)
class AppSettings:
    soft4: Soft4Settings
    email: EmailSettings
    email_queue: EmailQueueSettings
    manager_report: ManagerReportSettings
    requester_report: RequesterReportSettings
    downloads_dir: Path
    requester_downloads_dir: Path
