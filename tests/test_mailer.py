from __future__ import annotations

import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from app.config.models import EmailSettings
from app.mailer import (
    send_attendant_csv_email,
    send_dry_run_success_email,
    send_manager_report_email,
    send_test_email,
)


class MailerTests(unittest.TestCase):
    def test_manager_report_uses_full_csv_and_sends_structured_html(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_csv = Path(temp_dir) / "fila.csv"
            source_csv.write_text(
                "ID;Titulo;Atendente;Dias sem interacao\n"
                "1;Chamado A;Ana Silva;4\n"
                "2;Chamado B;Bruno Souza;7\n",
                encoding="utf-8",
            )
            sent: dict[str, object] = {}

            def capture_send(settings, message, recipients):
                sent["message"] = message
                sent["recipients"] = recipients

            with patch("app.mailer._send_message", capture_send):
                send_manager_report_email(
                    settings=EmailSettings("smtp.example.com", 587, "bot@example.com", "secret"),
                    recipient="gestora@example.com",
                    manager_name="Francieli",
                    source_csv=source_csv,
                    attendant_column="atendente",
                    exported_at=datetime(2026, 5, 21, 10, 0, 0),
                    no_interaction_days=3,
                )

            message = sent["message"]
            self.assertEqual(sent["recipients"], ["gestora@example.com"])
            self.assertEqual(
                message["Subject"],
                "Relatorio gerencial de chamados sem interacao - 21/05/2026",
            )
            payload = message.get_payload()
            html_body = payload[0].get_payload(decode=True).decode("utf-8")
            self.assertIn("Ana Silva - 1 chamado(s)", html_body)
            self.assertIn("Bruno Souza - 1 chamado(s)", html_body)
            self.assertIn("Total de chamados:</strong> 2", html_body)
            self.assertGreaterEqual(len(payload), 2)

    def test_attendant_email_uses_priority_review_template(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_csv = Path(temp_dir) / "ana.csv"
            source_csv.write_text("ID;Titulo\n1;Chamado A\n", encoding="utf-8")
            sent: dict[str, object] = {}

            def capture_send(settings, message, recipients):
                sent["message"] = message
                sent["recipients"] = recipients

            with patch("app.mailer._send_message", capture_send):
                send_attendant_csv_email(
                    settings=EmailSettings("smtp.example.com", 587, "bot@example.com", "secret"),
                    recipient="ana@example.com",
                    attendant="Ana Silva",
                    csv_path=source_csv,
                    exported_at=datetime(2026, 5, 21, 10, 0, 0),
                    row_count=1,
                    no_interaction_days=3,
                )

            message = sent["message"]
            self.assertEqual(sent["recipients"], ["ana@example.com"])
            self.assertEqual(
                message["Subject"],
                "Chamados sem interacao ha 3 dias - 21/05/2026",
            )
            payload = message.get_payload()
            html_body = payload[0].get_payload(decode=True).decode("utf-8")
            self.assertIn("Ol&aacute;, Ana Silva.", html_body)
            self.assertIn("sem qualquer intera&ccedil;&atilde;o h&aacute; 3", html_body)
            self.assertIn("Conforme observado, h&aacute; chamados pendentes", html_body)
            self.assertIn("necessitam de revis&atilde;o", html_body)
            self.assertIn("Total de chamados no anexo:</strong> 1", html_body)
            self.assertGreaterEqual(len(payload), 2)

    def test_test_email_uses_configured_sender_and_recipient(self) -> None:
        sent: dict[str, object] = {}

        def capture_send(settings, message, recipients):
            sent["message"] = message
            sent["recipients"] = recipients

        with patch("app.mailer._send_message", capture_send):
            send_test_email(
                settings=EmailSettings("smtp.example.com", 587, "bot@example.com", "secret"),
                recipient="lucas.silva@mainhardt.com.br",
                sent_at=datetime(2026, 6, 24, 9, 30, 0),
            )

        message = sent["message"]
        self.assertEqual(sent["recipients"], ["lucas.silva@mainhardt.com.br"])
        self.assertEqual(message["From"], "bot@example.com")
        self.assertEqual(message["To"], "lucas.silva@mainhardt.com.br")
        self.assertEqual(
            message["Subject"],
            "Teste de envio - Automacao Soft4 - 24/06/2026 09:30",
        )
        html_body = message.get_payload()[0].get_payload(decode=True).decode("utf-8")
        self.assertIn("e-mail de teste da automacao Soft4/Mainhardt", html_body)

    def test_dry_run_success_email_goes_only_to_lucas(self) -> None:
        sent: dict[str, object] = {}

        def capture_send(settings, message, recipients):
            sent["message"] = message
            sent["recipients"] = recipients

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("app.mailer._send_message", capture_send):
                send_dry_run_success_email(
                    settings=EmailSettings("smtp.example.com", 587, "bot@example.com", "secret"),
                    recipient="lucas.silva@mainhardt.com.br",
                    exported_at=datetime(2026, 6, 24, 9, 30, 0),
                    simulated_individual_emails=3,
                    queue_dir=Path(temp_dir) / "email_queue" / "20260624_093000",
                )

        message = sent["message"]
        self.assertEqual(sent["recipients"], ["lucas.silva@mainhardt.com.br"])
        self.assertEqual(message["To"], "lucas.silva@mainhardt.com.br")
        self.assertEqual(
            message["Subject"],
            "Dry-run bem-sucedido - Automacao Soft4 - 24/06/2026",
        )
        html_body = message.get_payload()[0].get_payload(decode=True).decode("utf-8")
        self.assertIn("E-mails individuais simulados:</strong> 3", html_body)
        self.assertIn("Nenhum e-mail de atendimento foi enviado", html_body)


if __name__ == "__main__":
    unittest.main()
