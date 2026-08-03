from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.config.models import Soft4Settings
from app.requester.delivery import (
    RequesterDeliveryError,
    build_requester_deliveries,
)


def _api_settings() -> Soft4Settings:
    return Soft4Settings(
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


class RequesterDeliveryTests(unittest.TestCase):
    def test_groups_chamados_by_solicitante_email(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_csv = root / "solicitante.csv"
            source_csv.write_text(
                "ID;Titulo;Cliente;Solicitante;Dias sem interacao\n"
                "77934;Falha A;GRUPO HARD;Bruna Martins;114\n"
                "78969;Falha B;AXA;Talita Gois;59\n"
                "78970;Falha C;AXA;Talita Gois;60\n",
                encoding="utf-8",
            )
            emails_by_codigo = {
                "77934": "bruna@example.com",
                "78969": "talita@example.com",
                "78970": "talita@example.com",
            }

            with patch(
                "app.requester.delivery.fetch_solicitante_emails",
                return_value=emails_by_codigo,
            ):
                deliveries = build_requester_deliveries(
                    source_csv=source_csv,
                    api_settings=_api_settings(),
                    id_column="ID",
                    output_dir=root / "entregas",
                )

            self.assertEqual(len(deliveries), 2)
            by_recipient = {delivery.recipient: delivery for delivery in deliveries}
            self.assertEqual(by_recipient["bruna@example.com"].solicitante, "Bruna Martins")
            self.assertEqual(by_recipient["bruna@example.com"].row_count, 1)
            self.assertEqual(by_recipient["talita@example.com"].row_count, 2)
            self.assertTrue(by_recipient["bruna@example.com"].csv_path.exists())
            self.assertTrue(by_recipient["talita@example.com"].csv_path.exists())

            bruna_csv = by_recipient["bruna@example.com"].csv_path.read_text(encoding="utf-8")
            self.assertIn("Falha A", bruna_csv)
            self.assertNotIn("Falha B", bruna_csv)

    def test_ignores_chamados_without_email(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_csv = root / "solicitante.csv"
            source_csv.write_text(
                "ID;Titulo;Solicitante\n"
                "1;Chamado sem email;Sem Email\n"
                "2;Chamado com email;Com Email\n",
                encoding="utf-8",
            )
            emails_by_codigo = {"2": "com@example.com"}

            with patch(
                "app.requester.delivery.fetch_solicitante_emails",
                return_value=emails_by_codigo,
            ):
                deliveries = build_requester_deliveries(
                    source_csv=source_csv,
                    api_settings=_api_settings(),
                    id_column="ID",
                    output_dir=root / "entregas",
                )

            self.assertEqual(len(deliveries), 1)
            self.assertEqual(deliveries[0].recipient, "com@example.com")

    def test_raises_when_no_emails_found(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_csv = root / "solicitante.csv"
            source_csv.write_text(
                "ID;Titulo;Solicitante\n1;Chamado A;Alguem\n",
                encoding="utf-8",
            )

            with patch("app.requester.delivery.fetch_solicitante_emails", return_value={}):
                with self.assertRaises(RequesterDeliveryError):
                    build_requester_deliveries(
                        source_csv=source_csv,
                        api_settings=_api_settings(),
                        id_column="ID",
                        output_dir=root / "entregas",
                    )

    def test_raises_when_id_column_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_csv = root / "solicitante.csv"
            source_csv.write_text("Titulo;Solicitante\nChamado A;Alguem\n", encoding="utf-8")

            with self.assertRaises(RequesterDeliveryError):
                build_requester_deliveries(
                    source_csv=source_csv,
                    api_settings=_api_settings(),
                    id_column="ID",
                    output_dir=root / "entregas",
                )


if __name__ == "__main__":
    unittest.main()
