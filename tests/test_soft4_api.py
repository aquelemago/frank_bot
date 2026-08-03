from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from app.config.models import Soft4Settings
from app.soft4.api import SoftdeskApiError, fetch_solicitante_email


def _settings(**overrides) -> Soft4Settings:
    base = dict(
        base_url="https://soft4.example.com",
        queue_path="/chamado/fila-de-atendimento",
        csv_path="/chamado/fila-de-atendimento/csv",
        listing_type="SEM_INTERACAO_ATENDENTE",
        no_interaction_attendant_days=3,
        requester_listing_type="SEM_INTERACAO_SOLICITANTE",
        no_interaction_requester_days=5,
        additional_holidays="",
        api_key="chave-secreta",
        api_path="/api/api.php",
        usuario="user",
        senha="pass",
        user_data_dir=Path("C:/tmp/perfil"),
        timeout_seconds=10,
        retries=2,
    )
    base.update(overrides)
    return Soft4Settings(**base)


class Soft4ApiTests(unittest.TestCase):
    def test_fetch_solicitante_email_returns_email(self) -> None:
        with patch("app.soft4.api.requests.get") as get_mock:
            get_mock.return_value.status_code = 200
            get_mock.return_value.json.return_value = {
                "objeto": {"usuario": {"codigo": 10, "nome": "Bruna", "email": "bruna@example.com"}}
            }

            email = fetch_solicitante_email(_settings(), "77934")

        self.assertEqual(email, "bruna@example.com")
        get_mock.assert_called_once()
        _args, _kwargs = get_mock.call_args
        self.assertIn("/api/api.php/chamado", _args[0])
        self.assertEqual(_kwargs["params"], {"codigo": "77934"})
        self.assertEqual(_kwargs["headers"]["hash-api"], "chave-secreta")

    def test_fetch_solicitante_email_returns_none_on_404(self) -> None:
        with patch("app.soft4.api.requests.get") as get_mock:
            get_mock.return_value.status_code = 404

            email = fetch_solicitante_email(_settings(), "99999")

        self.assertIsNone(email)

    def test_fetch_solicitante_email_retries_on_429_then_succeeds(self) -> None:
        first = unittest.mock.MagicMock()
        first.status_code = 429
        first.headers = {"Retry-After": "1"}
        second = unittest.mock.MagicMock()
        second.status_code = 200
        second.json.return_value = {"objeto": {"usuario": {"email": "talita@example.com"}}}

        with (
            patch("app.soft4.api.requests.get", side_effect=[first, second]) as get_mock,
            patch("app.soft4.api.time.sleep") as sleep_mock,
        ):
            email = fetch_solicitante_email(_settings(retries=3), "78969")

        self.assertEqual(email, "talita@example.com")
        self.assertEqual(get_mock.call_count, 2)
        sleep_mock.assert_called_once()

    def test_fetch_solicitante_email_raises_when_api_key_missing(self) -> None:
        with self.assertRaises(SoftdeskApiError):
            fetch_solicitante_email(_settings(api_key=""), "77934")

    def test_fetch_solicitante_email_raises_on_unexpected_status(self) -> None:
        with patch("app.soft4.api.requests.get") as get_mock:
            get_mock.return_value.status_code = 500
            get_mock.return_value.text = "erro interno"

            with self.assertRaises(SoftdeskApiError):
                fetch_solicitante_email(_settings(), "77934")

    def test_fetch_solicitante_email_raises_without_usuario_object(self) -> None:
        with patch("app.soft4.api.requests.get") as get_mock:
            get_mock.return_value.status_code = 200
            get_mock.return_value.json.return_value = {"objeto": {}}

            with self.assertRaises(SoftdeskApiError):
                fetch_solicitante_email(_settings(), "77934")


if __name__ == "__main__":
    unittest.main()
