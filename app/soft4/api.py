from __future__ import annotations

import logging
import time
from collections.abc import Iterable

import requests

from app.config.models import Soft4Settings


LOGGER = logging.getLogger(__name__)


class SoftdeskApiError(RuntimeError):
    """Erro ao consultar a API do Soft4/Softdesk."""


def fetch_solicitante_email(
    settings: Soft4Settings,
    chamado_codigo: str | int,
) -> str | None:
    """Busca o e-mail do solicitante de um chamado pela API Softdesk.

    Faz GET em ``<base_url><api_path>/chamado?codigo=<codigo>`` com o cabecalho
    ``hash-api``. Retorna ``None`` quando o chamado nao existe (HTTP 404) ou nao
    possui e-mail de usuario. Dispara ``SoftdeskApiError`` em demais falhas.
    """
    if not settings.api_key:
        raise SoftdeskApiError("SOFTDESK_API_KEY nao configurada.")

    url = f"{settings.base_url}{settings.api_path}/chamado"
    params = {"codigo": str(chamado_codigo).strip()}
    headers = {"hash-api": settings.api_key, "Accept": "application/json"}

    last_error: Exception | None = None
    for attempt in range(1, settings.retries + 1):
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=settings.timeout_seconds,
            )
        except requests.RequestException as error:
            last_error = error
            LOGGER.warning(
                "Falha de rede na API Softdesk (tentativa %s/%s): %s",
                attempt,
                settings.retries,
                error,
            )
        else:
            if response.status_code == 200:
                return _extract_solicitante_email(response.json(), chamado_codigo)

            if response.status_code == 404:
                LOGGER.warning("Chamado %s nao encontrado na API Softdesk", chamado_codigo)
                return None

            if response.status_code == 429:
                retry_after = _parse_retry_after(response.headers.get("Retry-After"))
                last_error = SoftdeskApiError(
                    f"Rate limit da API Softdesk (HTTP 429); aguardando {retry_after}s"
                )
                LOGGER.warning(
                    "Rate limit da API Softdesk (tentativa %s/%s); aguardando %ss",
                    attempt,
                    settings.retries,
                    retry_after,
                )
                time.sleep(retry_after)
                continue

            raise SoftdeskApiError(
                f"API Softdesk retornou HTTP {response.status_code} para o chamado "
                f"{chamado_codigo}: {response.text[:200]}"
            )

        if attempt < settings.retries:
            time.sleep(attempt)

    raise SoftdeskApiError(
        f"Falha ao consultar o chamado {chamado_codigo} na API Softdesk: {last_error}"
    )


def fetch_solicitante_emails(
    settings: Soft4Settings,
    chamado_codigos: Iterable[str | int],
) -> dict[str, str]:
    """Busca e-mails de solicitantes para uma lista de numeros de chamado."""
    emails: dict[str, str] = {}
    for codigo in sorted({str(codigo).strip() for codigo in chamado_codigos if str(codigo).strip()}):
        email = fetch_solicitante_email(settings, codigo)
        if email:
            emails[codigo] = email
    return emails


def _extract_solicitante_email(payload: object, chamado_codigo: str | int) -> str | None:
    if not isinstance(payload, dict):
        raise SoftdeskApiError(
            f"Resposta inesperada da API Softdesk para o chamado {chamado_codigo}"
        )
    objeto = payload.get("objeto")
    usuario = objeto.get("usuario") if isinstance(objeto, dict) else None
    if not isinstance(usuario, dict):
        raise SoftdeskApiError(
            f"Chamado {chamado_codigo} sem objeto usuario na resposta da API"
        )
    email = (usuario.get("email") or "").strip()
    if not email:
        LOGGER.warning("Chamado %s sem e-mail de solicitante na resposta", chamado_codigo)
        return None
    return email


def _parse_retry_after(value: str | None) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 1.0
