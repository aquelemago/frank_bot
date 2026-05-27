from __future__ import annotations

import logging
import time
from datetime import datetime
from pathlib import Path

from app.auth import AuthenticatedSession
from app.settings import Soft4Settings


LOGGER = logging.getLogger(__name__)


class CsvDownloadError(RuntimeError):
    """Erro ao baixar o CSV do Soft4."""


class SessionExpiredError(CsvDownloadError):
    """Sessao invalida ou expirada durante o POST do CSV."""


def download_csv(
    settings: Soft4Settings,
    session_data: AuthenticatedSession,
    downloads_dir: Path,
) -> Path:
    content = _download_csv_with_browser_retries(settings, session_data)
    _clear_previous_downloads(downloads_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = downloads_dir / f"fila_atendimento_{timestamp}.csv"
    output_path.write_bytes(content)
    LOGGER.info("CSV baixado: %s", output_path)
    return output_path


def _clear_previous_downloads(downloads_dir: Path) -> None:
    downloads_dir.mkdir(parents=True, exist_ok=True)
    removed = 0
    for item in downloads_dir.glob("fila_atendimento_*.csv"):
        if item.is_file():
            item.unlink()
            removed += 1
    if removed:
        LOGGER.info("CSVs antigos removidos: %s", removed)


def _download_csv_with_browser_retries(
    settings: Soft4Settings,
    session_data: AuthenticatedSession,
) -> bytes:
    last_error: Exception | None = None

    for attempt in range(1, settings.retries + 1):
        try:
            LOGGER.info("Solicitando CSV filtrado via POST (tentativa %s/%s)", attempt, settings.retries)
            return _download_csv_from_page(settings, session_data)
        except SessionExpiredError:
            raise
        except Exception as error:
            last_error = error
            LOGGER.warning("Falha ao baixar CSV pela tela: %s", error)
            if attempt < settings.retries:
                time.sleep(min(2 * attempt, 8))

    raise CsvDownloadError(f"Falha ao baixar CSV apos {settings.retries} tentativas.") from last_error


def _download_csv_from_page(settings: Soft4Settings, session_data: AuthenticatedSession) -> bytes:
    page = session_data.page
    content = bytes(_download_filtered_csv_via_fetch(page, settings))
    LOGGER.info("CSV filtrado capturado via POST: %s bytes", len(content))
    return _validate_csv_content(content)


def _download_filtered_csv_via_fetch(page, settings: Soft4Settings) -> list[int]:
    payload = _build_queue_payload(settings, include_status_chamado=True)
    response = page.evaluate(
        """async ({ payload }) => {
            const csrf = document.querySelector('meta[name="csrf-token"]')?.content || "";
            const xsrfCookie = document.cookie
                .split("; ")
                .find((item) => item.startsWith("XSRF-TOKEN="));
            const xsrf = xsrfCookie ? decodeURIComponent(xsrfCookie.split("=").slice(1).join("=")) : "";
            const headers = {
                "accept": "application/json, text/plain, */*",
                "content-type": "application/json",
                "x-requested-with": "XMLHttpRequest",
            };
            if (csrf) {
                headers["x-csrf-token"] = csrf;
            }
            if (xsrf) {
                headers["x-xsrf-token"] = xsrf;
            }

            const searchPayload = {...payload};
            delete searchPayload.status_chamado;
            const searchResponse = await fetch("/chamado/fila-de-atendimento/json", {
                method: "POST",
                credentials: "include",
                headers,
                body: JSON.stringify(searchPayload),
            });
            if (!searchResponse.ok) {
                throw new Error(`Pesquisa HTTP ${searchResponse.status}`);
            }

            const csvResponse = await fetch("/chamado/fila-de-atendimento/csv", {
                method: "POST",
                credentials: "include",
                headers,
                body: JSON.stringify(payload),
            });
            if (!csvResponse.ok) {
                throw new Error(`CSV HTTP ${csvResponse.status}`);
            }

            const buffer = await csvResponse.arrayBuffer();
            return Array.from(new Uint8Array(buffer));
        }""",
        {"payload": payload},
    )
    LOGGER.info(
        "CSV solicitado com filtro: %s, dias sem interacao atendente=%s",
        settings.listing_type,
        settings.no_interaction_attendant_days,
    )
    return response


def _build_queue_payload(settings: Soft4Settings, include_status_chamado: bool) -> dict[str, object]:
    payload: dict[str, object] = {
        "cd_area": 0,
        "cd_cliente": 0,
        "cd_usuario": 0,
        "cd_prioridade": 0,
        "cd_grupo_solucao_fila_atendimento": [118, 257],
        "cd_campo_customizavel": [],
        "cd_atendente": [],
        "st_chamado": [5, 1, 12, 0],
        "cd_tipo_chamado": [],
        "rotulo": ["CHAMADO_FILHO", "CODIGO", "DESCRICAO", "CLIENTE", "USUARIO", "ATENDENTE"],
        "tamanho_fonte": "12",
        "tp_listagem": settings.listing_type,
        "quantidade_dias_sem_interacao_atendente": str(settings.no_interaction_attendant_days),
        "quantidade_dias_sem_interacao_solicitante": 5,
        "cd_grupo_solucao": [],
        "campo_customizavel": [],
    }
    if include_status_chamado:
        payload["status_chamado"] = [
            {"value": 0, "text": "Novo"},
            {"value": 1, "text": "Em atendimento"},
            {"value": 2, "text": "Encerrado"},
            {"value": 5, "text": "Contestado"},
            {"value": 7, "text": "Agendado"},
            {"value": 8, "text": "Aguardando solicitante"},
            {"value": 9, "text": "Fornecedor"},
            {"value": 10, "text": "Aguardando aprovacao"},
        ]
    return payload


def _validate_csv_content(content: bytes) -> bytes:
    text_preview = content.decode("utf-8-sig", errors="replace")
    if not text_preview.strip():
        raise CsvDownloadError(
            "CSV retornado pelo Soft4 nao contem cabecalho nem dados. "
            "Verifique se a pesquisa da fila encontrou registros ou se o endpoint CSV mudou."
        )

    return content
