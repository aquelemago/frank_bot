from __future__ import annotations

import logging
import sys
from datetime import datetime

from app.auth import Soft4Browser
from app.business_days import (
    filtrar_csv_por_dias_uteis_sem_interacao,
    montar_feriados,
    parse_feriados_adicionais,
)
from app.cleanup import cleanup_runtime_residue
from app.downloader import SessionExpiredError, download_csv
from app.email_queue import (
    build_attendant_email_queue,
    mark_queue_item_failed,
    mark_queue_item_sent,
)
from app.mailer import send_attendant_csv_email, send_manager_report_email
from app.settings import ConfigError, PROJECT_ROOT, load_settings, setup_logging


LOGGER = logging.getLogger(__name__)
sys.dont_write_bytecode = True


def run() -> int:
    setup_logging()
    LOGGER.info("Iniciando automacao")
    cleanup_runtime_residue(PROJECT_ROOT)

    try:
        settings = load_settings()
        exported_at = datetime.now()

        with Soft4Browser(settings.soft4) as browser:
            auth_session = browser.ensure_authenticated()
            try:
                csv_path = download_csv(settings.soft4, auth_session, settings.downloads_dir)
            except SessionExpiredError:
                LOGGER.info("Sessao expirou durante o download; refazendo login")
                auth_session = browser.ensure_authenticated()
                csv_path = download_csv(settings.soft4, auth_session, settings.downloads_dir)

        data_atual = exported_at.date()
        feriados = montar_feriados(
            data_atual=data_atual,
            feriados_adicionais=parse_feriados_adicionais(settings.soft4.additional_holidays),
        )
        filtrar_csv_por_dias_uteis_sem_interacao(
            source_csv=csv_path,
            data_atual=data_atual,
            feriados=feriados,
            limite_dias_uteis=settings.soft4.no_interaction_attendant_days,
            coluna_ultima_interacao=settings.email_queue.last_interaction_column,
        )

        email_queue = build_attendant_email_queue(
            source_csv=csv_path,
            settings=settings.email_queue,
            created_at=exported_at,
        )
        if not email_queue.items:
            raise RuntimeError(f"Fila de email sem itens enviaveis: {email_queue.queue_dir}")

        failures: list[str] = []
        for item in email_queue.items:
            try:
                send_attendant_csv_email(
                    settings=settings.email,
                    recipient=item.recipient,
                    attendant=item.attendant,
                    csv_path=item.csv_path,
                    exported_at=exported_at,
                    row_count=item.row_count,
                    no_interaction_days=settings.soft4.no_interaction_attendant_days,
                )
                mark_queue_item_sent(item, datetime.now())
            except Exception as error:
                mark_queue_item_failed(item, datetime.now(), error)
                failures.append(f"{item.attendant}: {error}")

        try:
            send_manager_report_email(
                settings=settings.email,
                recipient=settings.manager_report.recipient,
                manager_name=settings.manager_report.name,
                source_csv=csv_path,
                attendant_column=settings.email_queue.attendant_column,
                exported_at=exported_at,
                no_interaction_days=settings.soft4.no_interaction_attendant_days,
            )
        except Exception as error:
            failures.append(f"Relatorio gestora: {error}")

        if failures:
            joined = "; ".join(failures)
            raise RuntimeError(f"Falha ao enviar alguns itens da fila: {joined}")

        LOGGER.info("Automacao finalizada")
        return 0
    except ConfigError as error:
        LOGGER.error("Falha de configuracao: %s", error)
        return 2
    except Exception as error:
        LOGGER.exception("Falha na automacao: %s", error)
        return 1
    finally:
        cleanup_runtime_residue(PROJECT_ROOT)


if __name__ == "__main__":
    raise SystemExit(run())
