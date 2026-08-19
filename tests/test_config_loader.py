from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from app.config.loader import load_settings


REQUIRED_ENV = {
    "SOFT4_USUARIO": "usuario-teste",
    "SOFT4_SENHA": "senha-teste",
    "EMAIL_USUARIO": "remetente@example.com",
    "EMAIL_SENHA": "senha-email-teste",
}


class ConfigLoaderTests(unittest.TestCase):
    def test_loads_optional_second_full_requester_report_recipient(self) -> None:
        environ = {
            **REQUIRED_ENV,
            "EMAIL_SOLICITANTE_TODOS_CHAMADOS2": "gestor@example.com",
        }
        with (
            patch.dict("os.environ", environ, clear=True),
            patch("app.config.loader.PROJECT_ROOT", Path("config-loader-test")),
            patch("app.config.loader.load_dotenv"),
            patch("app.config.loader.Path.mkdir"),
        ):
            settings = load_settings()

        self.assertEqual(
            settings.requester_report.full_report_recipient2,
            "gestor@example.com",
        )

    def test_second_full_requester_report_recipient_defaults_to_empty(self) -> None:
        with (
            patch.dict("os.environ", REQUIRED_ENV, clear=True),
            patch("app.config.loader.PROJECT_ROOT", Path("config-loader-test")),
            patch("app.config.loader.load_dotenv"),
            patch("app.config.loader.Path.mkdir"),
        ):
            settings = load_settings()

        self.assertEqual(settings.requester_report.full_report_recipient2, "")

    def test_requester_days_default_to_three(self) -> None:
        with (
            patch.dict("os.environ", REQUIRED_ENV, clear=True),
            patch("app.config.loader.PROJECT_ROOT", Path("config-loader-test")),
            patch("app.config.loader.load_dotenv"),
            patch("app.config.loader.Path.mkdir"),
        ):
            settings = load_settings()

        self.assertEqual(settings.soft4.no_interaction_requester_days, 3)


if __name__ == "__main__":
    unittest.main()
