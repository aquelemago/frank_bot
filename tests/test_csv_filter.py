from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

from app.csv.filter import (
    chamado_deve_ser_processado,
    contar_dias_uteis_sem_interacao,
    filtrar_csv_por_dias_uteis_sem_interacao,
)


class CsvFilterTests(unittest.TestCase):
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
