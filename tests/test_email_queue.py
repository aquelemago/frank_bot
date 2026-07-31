from __future__ import annotations

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from app.config.models import EmailQueueSettings
from app.csv.io import normalize_key
from app.queue.repository import build_attendant_email_queue


class EmailQueueTests(unittest.TestCase):
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

    def test_normalize_key_removes_accents_and_symbols(self) -> None:
        self.assertEqual(normalize_key("Patrícia König Costa"), "PATRICIA_KONIG_COSTA")


if __name__ == "__main__":
    unittest.main()
