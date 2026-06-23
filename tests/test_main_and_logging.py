from __future__ import annotations

import logging
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.email_queue import EmailQueue, EmailQueueItem
from app.main import main, run
from app.settings import setup_logging


class MainAndLoggingTests(unittest.TestCase):
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
        run_mock.assert_called_once_with(dry_run=True)

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
                ),
                email_queue=SimpleNamespace(last_interaction_column="ultima interacao"),
                downloads_dir=root / "downloads",
            )
            browser = MagicMock()
            browser.__enter__.return_value.ensure_authenticated.return_value = object()

            with (
                patch("app.main.setup_logging"),
                patch("app.main.cleanup_runtime_residue"),
                patch("app.main.load_settings", return_value=settings),
                patch("app.main.Soft4Browser", return_value=browser),
                patch("app.main.download_csv", return_value=csv_path),
                patch("app.main.montar_feriados", return_value=set()),
                patch("app.main.parse_feriados_adicionais", return_value=set()),
                patch("app.main.filtrar_csv_por_dias_uteis_sem_interacao"),
                patch("app.main.build_attendant_email_queue", return_value=queue),
                patch("app.main.send_attendant_csv_email") as attendant_send,
                patch("app.main.send_manager_report_email") as manager_send,
                patch("app.main.mark_queue_item_sent") as mark_sent,
                patch("app.main.mark_queue_item_failed") as mark_failed,
                patch("app.main.datetime") as datetime_mock,
            ):
                datetime_mock.now.return_value = datetime(2026, 6, 23, 8, 0, 0)
                exit_code = run(dry_run=True)

            self.assertEqual(exit_code, 0)
            attendant_send.assert_not_called()
            manager_send.assert_not_called()
            mark_sent.assert_not_called()
            mark_failed.assert_not_called()

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
