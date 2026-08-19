from __future__ import annotations

import unittest
from pathlib import Path

from app.config.models import Soft4Settings
from app.soft4.downloader import _build_queue_payload


def _settings() -> Soft4Settings:
    return Soft4Settings(
        base_url="https://soft4.example.com",
        queue_path="/chamado/fila-de-atendimento",
        csv_path="/chamado/fila-de-atendimento/csv",
        listing_type="SEM_INTERACAO_ATENDENTE",
        no_interaction_attendant_days=3,
        requester_listing_type="SEM_INTERACAO_SOLICITANTE",
        no_interaction_requester_days=3,
        additional_holidays="",
        api_key="",
        api_path="/api/api.php",
        usuario="usuario-teste",
        senha="senha-teste",
        user_data_dir=Path("perfil-teste"),
        timeout_seconds=60,
        retries=3,
    )


class Soft4DownloaderPayloadTests(unittest.TestCase):
    def test_requester_payload_uses_filters_confirmed_in_soft4(self) -> None:
        settings = _settings()

        payload = _build_queue_payload(
            settings,
            include_status_chamado=True,
            listing_type=settings.requester_listing_type,
            no_interaction_days=settings.no_interaction_requester_days,
        )

        self.assertEqual(payload["cd_grupo_solucao_fila_atendimento"], [118, 257])
        self.assertEqual(payload["st_chamado"], [8])
        self.assertEqual(payload["tp_listagem"], "SEM_INTERACAO_SOLICITANTE")
        self.assertEqual(payload["quantidade_dias_sem_interacao_solicitante"], 3)

    def test_attendant_payload_preserves_existing_status_filters(self) -> None:
        settings = _settings()

        payload = _build_queue_payload(
            settings,
            include_status_chamado=True,
            listing_type=settings.listing_type,
            no_interaction_days=settings.no_interaction_attendant_days,
        )

        self.assertEqual(payload["cd_grupo_solucao_fila_atendimento"], [118, 257])
        self.assertEqual(payload["st_chamado"], [5, 1, 12, 0])
        self.assertEqual(payload["tp_listagem"], "SEM_INTERACAO_ATENDENTE")
        self.assertEqual(payload["quantidade_dias_sem_interacao_atendente"], "3")


if __name__ == "__main__":
    unittest.main()
