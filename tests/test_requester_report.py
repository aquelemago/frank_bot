from __future__ import annotations

import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from app.config.models import EmailSettings
from app.mailer import send_requester_report_email
from app.mailer.templates import render_requester_report_email


class RequesterReportTests(unittest.TestCase):
    def test_requester_report_uses_full_csv_and_sends_structured_html(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_csv = Path(temp_dir) / "fila_solicitante.csv"
            source_csv.write_text(
                "ID;Titulo;Solicitante;Dias sem interacao\n"
                "1;Chamado A;Cliente X;6\n"
                "2;Chamado B;Cliente Y;7\n",
                encoding="utf-8",
            )
            sent: dict[str, object] = {}

            def capture_send(settings, message, recipients):
                sent["message"] = message
                sent["recipients"] = recipients

            with patch("app.mailer._send_message", capture_send):
                send_requester_report_email(
                    settings=EmailSettings("smtp.example.com", 587, "bot@example.com", "secret"),
                    recipient="solicitante@example.com",
                    requester_name="Solicitante",
                    source_csv=source_csv,
                    no_interaction_days=5,
                    exported_at=datetime(2026, 6, 23, 8, 0, 0),
                )

            message = sent["message"]
            self.assertEqual(sent["recipients"], ["solicitante@example.com"])
            self.assertEqual(
                message["Subject"],
                "Relatorio de chamados sem interacao do solicitante - 23/06/2026",
            )
            payload = message.get_payload()
            html_body = payload[0].get_payload(decode=True).decode("utf-8")
            self.assertIn("Ola, Solicitante.", html_body)
            self.assertIn("sem interacao do solicitante ha", html_body)
            self.assertIn("5 dias ou mais", html_body)
            self.assertIn("Total de chamados:</strong> 2", html_body)
            self.assertIn("Chamado A", html_body)
            self.assertIn("Cliente X", html_body)
            self.assertGreaterEqual(len(payload), 2)

    def test_requester_report_template_renders_with_rows(self) -> None:
        sections = "<table><thead><tr><th>ID</th></tr></thead><tbody><tr><td>99</td></tr></tbody></table>"
        html_body = render_requester_report_email(
            requester_name="Teste",
            exported_at=datetime(2026, 6, 23, 8, 0, 0),
            no_interaction_days=5,
            total_rows=1,
            sections=sections,
        )

        self.assertIn("Ola, Teste.", html_body)
        self.assertIn("sem interacao do solicitante ha", html_body)
        self.assertIn("5 dias ou mais", html_body)
        self.assertIn("Total de chamados:</strong> 1", html_body)
        self.assertIn("<td>99</td>", html_body)
        self.assertIn("O CSV completo da exportacao tambem segue em anexo", html_body)


if __name__ == "__main__":
    unittest.main()
