from __future__ import annotations

import logging
import sys
from datetime import datetime

from app.config.loader import ConfigError, PROJECT_ROOT, load_settings
from app.csv.filter import (
    filtrar_csv_por_dias_uteis_sem_interacao,
    montar_feriados,
    parse_feriados_adicionais,
)
from app.infra.cleanup import cleanup_runtime_residue
from app.infra.logging_setup import setup_logging
from app.requester.delivery import build_requester_deliveries
from app.services import (
    build_attendant_email_queue,
    mark_queue_item_failed,
    mark_queue_item_sent,
    send_attendant_csv_email,
    send_dry_run_success_email,
    send_manager_report_email,
    send_requester_report_email,
)
from app.soft4.browser import Soft4Browser
from app.soft4.downloader import SessionExpiredError, download_csv, download_csv_as


LOGGER = logging.getLogger(__name__)
sys.dont_write_bytecode = True
DRY_RUN_NOTIFICATION_RECIPIENT = "lucas.silva@mainhardt.com.br"


def _log_dry_run_plan(email_queue, manager_recipient: str) -> None:
    for item in email_queue.items:
        LOGGER.info(
            "Dry-run: email individual seria enviado para %s <%s> com %s chamado(s); "
            "anexo=%s",
            item.attendant,
            item.recipient,
            item.row_count,
            item.csv_path,
        )

    LOGGER.info(
        "Dry-run: relatorio gerencial seria enviado para %s com %s atendente(s)",
        manager_recipient,
        len(email_queue.items),
    )


def _dispatch_requester_reports(
    settings,
    requester_csv_path,
    exported_at,
    dry_run: bool,
    failures: list[str],
) -> None:
    api_key = getattr(settings.soft4, "api_key", "")
    if not api_key:
        if dry_run:
            LOGGER.info(
                "Dry-run: relatorio do solicitante seria enviado para %s",
                settings.requester_report.recipient,
            )
            return
        try:
            send_requester_report_email(
                settings=settings.email,
                recipient=settings.requester_report.recipient,
                requester_name=settings.requester_report.name,
                source_csv=requester_csv_path,
                no_interaction_days=settings.soft4.no_interaction_requester_days,
                exported_at=exported_at,
            )
        except Exception as error:
            failures.append(f"Relatorio solicitante: {error}")
        return

    id_column = getattr(settings.requester_report, "id_column", "ID")
    output_dir = (
        settings.requester_downloads_dir
        / f"relatorio_solicitante_{exported_at:%Y%m%d_%H%M%S}"
    )
    try:
        deliveries = build_requester_deliveries(
            source_csv=requester_csv_path,
            api_settings=settings.soft4,
            id_column=id_column,
            output_dir=output_dir,
        )
    except Exception as error:
        message = f"Relatorio solicitante: {error}"
        if dry_run:
            LOGGER.error("Dry-run: %s", message)
        else:
            failures.append(message)
        return

    for delivery in deliveries:
        if dry_run:
            LOGGER.info(
                "Dry-run: relatorio do solicitante seria enviado para %s <%s> "
                "com %s chamado(s); anexo=%s",
                delivery.solicitante,
                delivery.recipient,
                delivery.row_count,
                delivery.csv_path,
            )
            continue
        try:
            send_requester_report_email(
                settings=settings.email,
                recipient=delivery.recipient,
                requester_name=delivery.solicitante,
                source_csv=delivery.csv_path,
                no_interaction_days=settings.soft4.no_interaction_requester_days,
                exported_at=exported_at,
            )
        except Exception as error:
            failures.append(f"Relatorio solicitante {delivery.recipient}: {error}")


def run(dry_run: bool = False) -> int:
    setup_logging()
    LOGGER.info("Iniciando automacao")
    if dry_run:
        LOGGER.warning(
            "Modo dry-run ativo: emails de atendimento nao serao enviados; "
            "apenas a confirmacao de sucesso sera enviada para %s",
            DRY_RUN_NOTIFICATION_RECIPIENT,
        )
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

            try:
                requester_csv_path = download_csv_as(
                    settings.soft4,
                    auth_session,
                    settings.requester_downloads_dir,
                    settings.soft4.requester_listing_type,
                    settings.soft4.no_interaction_requester_days,
                    "solicitante",
                )
            except SessionExpiredError:
                LOGGER.info("Sessao expirou durante o download do solicitante; refazendo login")
                auth_session = browser.ensure_authenticated()
                requester_csv_path = download_csv_as(
                    settings.soft4,
                    auth_session,
                    settings.requester_downloads_dir,
                    settings.soft4.requester_listing_type,
                    settings.soft4.no_interaction_requester_days,
                    "solicitante",
                )

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

        filtrar_csv_por_dias_uteis_sem_interacao(
            source_csv=requester_csv_path,
            data_atual=data_atual,
            feriados=feriados,
            limite_dias_uteis=settings.soft4.no_interaction_requester_days,
            coluna_ultima_interacao=settings.requester_report.last_interaction_column,
        )

        email_queue = build_attendant_email_queue(
            source_csv=csv_path,
            settings=settings.email_queue,
            created_at=exported_at,
        )
        if not email_queue.items:
            raise RuntimeError(f"Fila de email sem itens enviaveis: {email_queue.queue_dir}")

        if dry_run:
            _log_dry_run_plan(email_queue, settings.manager_report.recipient)
            _dispatch_requester_reports(
                settings,
                requester_csv_path,
                exported_at,
                dry_run=True,
                failures=[],
            )
            LOGGER.info(
                "Dry-run bem-sucedido: %s email(s) individual(is), o relatorio gerencial "
                "e o relatorio do solicitante foram simulados, mas nao enviados. Fila mantida como pending em %s",
                len(email_queue.items),
                email_queue.queue_dir,
            )
            send_dry_run_success_email(
                settings=settings.email,
                recipient=DRY_RUN_NOTIFICATION_RECIPIENT,
                exported_at=exported_at,
                simulated_individual_emails=len(email_queue.items),
                queue_dir=email_queue.queue_dir,
            )
            LOGGER.info("Automacao finalizada")
            return 0

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

        _dispatch_requester_reports(
            settings,
            requester_csv_path,
            exported_at,
            dry_run=False,
            failures=failures,
        )

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
