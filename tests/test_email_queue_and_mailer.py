from __future__ import annotations

import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

from app.business_days import (
    chamado_deve_ser_processado,
    contar_dias_uteis_sem_interacao,
    filtrar_csv_por_dias_uteis_sem_interacao,
)
from app.email_queue import build_attendant_email_queue, normalize_key
from app.mailer import (
    send_attendant_csv_email,
    send_dry_run_success_email,
    send_manager_report_email,
    send_test_email,
)
from app.settings import EmailQueueSettings, EmailSettings


class EmailQueueAndMailerTests(unittest.TestCase):
    def test_build_queue_groups_by_attendant_and_tracks_missing_email(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_csv = root / "fila.csv"
            source_csv.write_text(
                "ID;Titulo;Atendente\n"
                "1;Chamado A;Ana Silva\n"
                "2;Chamado B;Ana Silva\n"
                "3;Chamado C;Bruno Souza\n",
                encoding="utf-8",
            )
            attendants_file = root / "email_atendente.env"
            attendants_file.write_text("EMAIL_ANA_SILVA=ana@example.com\n", encoding="utf-8")

            queue = build_attendant_email_queue(
                source_csv=source_csv,
                settings=EmailQueueSettings(
                    queue_dir=root / "email_queue",
                    attendants_file=attendants_file,
                    attendant_column="atendente",
                    last_interaction_column="ultima interacao",
                    fail_on_missing_attendant_email=False,
                ),
                created_at=datetime(2026, 5, 21, 10, 0, 0),
            )

            self.assertEqual(len(queue.items), 1)
            self.assertEqual(queue.items[0].attendant, "Ana Silva")
            self.assertEqual(queue.items[0].row_count, 2)
            self.assertEqual(queue.missing_recipients, ["Bruno Souza"])
            self.assertTrue(queue.items[0].csv_path.exists())

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

    def test_normalize_key_removes_accents_and_symbols(self) -> None:
        self.assertEqual(normalize_key("Patrícia König Costa"), "PATRICIA_KONIG_COSTA")


    def test_business_day_counter_ignores_weekend_and_starts_next_day(self) -> None:
        feriados: set[date] = set()

        self.assertEqual(
            contar_dias_uteis_sem_interacao(
                data_ultima_interacao=date(2026, 5, 22),
                data_atual=date(2026, 5, 26),
                feriados=feriados,
            ),
            2,
        )
        self.assertFalse(
            chamado_deve_ser_processado(
                data_ultima_interacao=date(2026, 5, 22),
                data_atual=date(2026, 5, 26),
                feriados=feriados,
            )
        )
        self.assertTrue(
            chamado_deve_ser_processado(
                data_ultima_interacao=date(2026, 5, 22),
                data_atual=date(2026, 5, 27),
                feriados=feriados,
            )
        )

    def test_filter_csv_uses_last_interaction_date_and_skips_invalid_dates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_csv = Path(temp_dir) / "fila.csv"
            source_csv.write_text(
                "ID;Titulo;Atendente;Ultima interacao\n"
                "1;Chamado A;Ana Silva;22/05/2026\n"
                "2;Chamado B;Ana Silva;25/05/2026\n"
                "3;Chamado C;Ana Silva;data invalida\n",
                encoding="utf-8",
            )

            kept = filtrar_csv_por_dias_uteis_sem_interacao(
                source_csv=source_csv,
                data_atual=date(2026, 5, 27),
                feriados=set(),
                limite_dias_uteis=3,
                coluna_ultima_interacao="ultima interacao",
            )

            self.assertEqual(kept, 1)
            filtered = source_csv.read_text(encoding="utf-8-sig")
            self.assertIn("Chamado A", filtered)
            self.assertNotIn("Chamado B", filtered)
            self.assertNotIn("Chamado C", filtered)

    def test_filter_csv_uses_configurable_holidays(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_csv = Path(temp_dir) / "fila.csv"
            source_csv.write_text(
                "ID;Titulo;Atendente;Ultima interacao\n"
                "1;Chamado A;Ana Silva;22/05/2026\n",
                encoding="utf-8",
            )

            kept = filtrar_csv_por_dias_uteis_sem_interacao(
                source_csv=source_csv,
                data_atual=date(2026, 5, 27),
                feriados={date(2026, 5, 25)},
                limite_dias_uteis=3,
                coluna_ultima_interacao="ultima interacao",
            )

            self.assertEqual(kept, 0)


if __name__ == "__main__":
    unittest.main()
