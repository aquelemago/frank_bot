from __future__ import annotations

import logging
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.infra.logging_setup import setup_logging
from app.main import main
from app.orchestrator.run import _dispatch_requester_reports, run
from app.queue.repository import EmailQueue, EmailQueueItem


class MainRunTests(unittest.TestCase):
    def tearDown(self) -> None:
        self._close_frank_bot_handlers()

    def _close_frank_bot_handlers(self) -> None:
        root_logger = logging.getLogger()
        for handler in list(root_logger.handlers):
            if getattr(handler, "_frank_bot_handler", False):
                root_logger.removeHandler(handler)
                handler.close()

    def test_cli_enables_dry_run(self) -> None:
        with patch("app.main.run", return_value=0) as run_mock:
            exit_code = main(["--dry-run"])

        self.assertEqual(exit_code, 0)
        run_mock.assert_called_once_with(dry_run=True, solicitante=False)

    def test_cli_enables_solicitante(self) -> None:
        with patch("app.main.run", return_value=0) as run_mock:
            exit_code = main(["--solicitante"])

        self.assertEqual(exit_code, 0)
        run_mock.assert_called_once_with(dry_run=False, solicitante=True)

    def test_dry_run_builds_queue_without_sending_email(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            csv_path = root / "fila.csv"
            csv_path.write_text("Atendente\nAna\n", encoding="utf-8")
            queue_dir = root / "email_queue" / "20260623_080000"
            queue_dir.mkdir(parents=True)
            item = EmailQueueItem(
                attendant="Ana",
                recipient="ana@example.com",
                csv_path=queue_dir / "ana.csv",
                metadata_path=queue_dir / "ana.json",
                row_count=1,
            )
            queue = EmailQueue(queue_dir=queue_dir, items=[item], missing_recipients=[])
            settings = SimpleNamespace(
                soft4=SimpleNamespace(
                    additional_holidays="",
                    no_interaction_attendant_days=3,
                    no_interaction_requester_days=5,
                    requester_listing_type="SEM_INTERACAO_SOLICITANTE",
                    api_key="",
                ),
                email=SimpleNamespace(),
                email_queue=SimpleNamespace(
                    last_interaction_column="ultima interacao",
                    attendant_column="Atendente",
                ),
                manager_report=SimpleNamespace(
                    recipient="gestora@example.com",
                    name="Gestora",
                ),
                requester_report=SimpleNamespace(
                    recipient="solicitante@example.com",
                    name="Solicitante",
                    last_interaction_column="ultima interacao",
                    id_column="ID",
                    full_report_recipient="",
                ),
                downloads_dir=root / "downloads",
                requester_downloads_dir=root / "downloads",
            )
            browser = MagicMock()
            browser.__enter__.return_value.ensure_authenticated.return_value = object()

            with (
                patch("app.orchestrator.run.setup_logging"),
                patch("app.orchestrator.run.cleanup_runtime_residue"),
                patch("app.orchestrator.run.load_settings", return_value=settings),
                patch("app.orchestrator.run.Soft4Browser", return_value=browser),
                patch("app.orchestrator.run.download_csv", return_value=csv_path),
                patch("app.orchestrator.run.download_csv_as", return_value=csv_path),
                patch("app.orchestrator.run.montar_feriados", return_value=set()),
                patch("app.orchestrator.run.parse_feriados_adicionais", return_value=set()),
                patch("app.orchestrator.run.filtrar_csv_por_dias_uteis_sem_interacao"),
                patch("app.orchestrator.run.build_attendant_email_queue", return_value=queue),
                patch("app.orchestrator.run.send_attendant_csv_email") as attendant_send,
                patch("app.orchestrator.run.send_manager_report_email") as manager_send,
                patch("app.orchestrator.run.send_requester_report_email") as requester_send,
                patch("app.orchestrator.run.send_dry_run_success_email") as dry_run_success_send,
                patch("app.orchestrator.run.mark_queue_item_sent") as mark_sent,
                patch("app.orchestrator.run.mark_queue_item_failed") as mark_failed,
                self.assertLogs("app.orchestrator.run", level="INFO") as captured_logs,
                patch("app.orchestrator.run.datetime") as datetime_mock,
            ):
                datetime_mock.now.return_value = datetime(2026, 6, 23, 8, 0, 0)
                exit_code = run(dry_run=True)

            self.assertEqual(exit_code, 0)
            attendant_send.assert_not_called()
            manager_send.assert_not_called()
            requester_send.assert_not_called()
            dry_run_success_send.assert_called_once_with(
                settings=settings.email,
                recipient="lucas.silva@mainhardt.com.br",
                exported_at=datetime(2026, 6, 23, 8, 0, 0),
                simulated_individual_emails=1,
                queue_dir=queue_dir,
            )
            mark_sent.assert_not_called()
            mark_failed.assert_not_called()
            logs = "\n".join(captured_logs.output)
            self.assertIn("Dry-run: email individual seria enviado para Ana", logs)
            self.assertIn("Dry-run bem-sucedido", logs)

    def test_dispatch_requester_reports_sends_full_report_to_copy_recipient(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_csv = root / "solicitante.csv"
            source_csv.write_text("ID\n1\n", encoding="utf-8")
            delivery_csv = root / "bruna.csv"
            delivery_csv.write_text("ID\n1\n", encoding="utf-8")
            settings = SimpleNamespace(
                soft4=SimpleNamespace(
                    api_key="chave",
                    no_interaction_requester_days=5,
                ),
                email=SimpleNamespace(),
                requester_report=SimpleNamespace(
                    recipient="solicitante@example.com",
                    name="Solicitante",
                    id_column="ID",
                    full_report_recipient="lcabral570@gmail.com",
                ),
                requester_downloads_dir=root / "entregas",
            )
            delivery = SimpleNamespace(
                solicitante="Bruna",
                recipient="bruna@example.com",
                csv_path=delivery_csv,
                row_count=1,
            )

            with (
                patch(
                    "app.orchestrator.run.build_requester_deliveries",
                    return_value=[delivery],
                ) as build_mock,
                patch("app.orchestrator.run.send_requester_report_email") as send_mock,
            ):
                failures: list[str] = []
                _dispatch_requester_reports(
                    settings,
                    source_csv,
                    datetime(2026, 6, 23, 8, 0, 0),
                    dry_run=False,
                    failures=failures,
                )

            self.assertEqual(failures, [])
            self.assertEqual(send_mock.call_count, 2)
            sent_recipients = [call.kwargs["recipient"] for call in send_mock.call_args_list]
            self.assertIn("bruna@example.com", sent_recipients)
            self.assertIn("lcabral570@gmail.com", sent_recipients)
            full_report_call = [
                call
                for call in send_mock.call_args_list
                if call.kwargs["recipient"] == "lcabral570@gmail.com"
            ][0]
            self.assertEqual(full_report_call.kwargs["source_csv"], source_csv)
            self.assertEqual(full_report_call.kwargs["requester_name"], "Solicitante")
            build_mock.assert_called_once()

    def test_requester_only_flow_does_not_touch_attendant_emails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            csv_path = root / "solicitante.csv"
            csv_path.write_text("ID\n1\n", encoding="utf-8")
            settings = SimpleNamespace(
                soft4=SimpleNamespace(
                    requester_listing_type="SEM_INTERACAO_SOLICITANTE",
                    no_interaction_requester_days=5,
                    additional_holidays="",
                ),
                email=SimpleNamespace(),
                requester_report=SimpleNamespace(
                    recipient="solicitante@example.com",
                    name="Solicitante",
                    last_interaction_column="ultima interacao",
                    id_column="ID",
                    full_report_recipient="",
                ),
                requester_downloads_dir=root / "downloads",
            )
            browser = MagicMock()
            browser.__enter__.return_value.ensure_authenticated.return_value = object()

            with (
                patch("app.orchestrator.run.setup_logging"),
                patch("app.orchestrator.run.cleanup_runtime_residue"),
                patch("app.orchestrator.run.load_settings", return_value=settings),
                patch("app.orchestrator.run.Soft4Browser", return_value=browser),
                patch("app.orchestrator.run.download_csv") as attendant_download,
                patch("app.orchestrator.run.download_csv_as", return_value=csv_path) as requester_download,
                patch("app.orchestrator.run.montar_feriados", return_value=set()),
                patch("app.orchestrator.run.parse_feriados_adicionais", return_value=set()),
                patch("app.orchestrator.run.filtrar_csv_por_dias_uteis_sem_interacao"),
                patch("app.orchestrator.run._dispatch_requester_reports") as dispatch_mock,
                patch("app.orchestrator.run.send_dry_run_success_email") as dry_run_success_send,
                patch("app.orchestrator.run.datetime") as datetime_mock,
            ):
                datetime_mock.now.return_value = datetime(2026, 6, 23, 8, 0, 0)
                exit_code = run(dry_run=True, solicitante=True)

            self.assertEqual(exit_code, 0)
            dispatch_mock.assert_called_once()
            self.assertTrue(dispatch_mock.call_args.kwargs["dry_run"])
            attendant_download.assert_not_called()
            requester_download.assert_called_once()
            dry_run_success_send.assert_not_called()

    def test_setup_logging_writes_to_rotating_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = setup_logging(Path(temp_dir))
            logging.getLogger("tests.logging").info("mensagem de teste")

            for handler in logging.getLogger().handlers:
                handler.flush()

            self.assertTrue(log_path.exists())
            self.assertIn("mensagem de teste", log_path.read_text(encoding="utf-8"))
            self._close_frank_bot_handlers()


if __name__ == "__main__":
    unittest.main()
