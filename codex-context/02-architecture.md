# Architecture

## Main Flow

The CLI dispatches `run()` to one of two independent service flows.

Attendant report (`run(dry_run, solicitante=False)`):

```text
main.py
  -> app.main.main()
     -> parse --dry-run / --solicitante
     -> app.main.run -> app.orchestrator.run.run(dry_run, solicitante)
        -> _run_attendant_report(dry_run)
           -> setup_logging()
           -> cleanup_runtime_residue()
           -> load_settings()
           -> Soft4Browser.ensure_authenticated()
           -> download_csv()
           -> filtrar_csv_por_dias_uteis_sem_interacao()
           -> build_attendant_email_queue()
           -> dry-run branch OR real SMTP branch
           -> cleanup_runtime_residue()
```

Requester report (`run(dry_run, solicitante=True)`):

```text
main.py
  -> app.main.main()
     -> app.orchestrator.run.run(dry_run, solicitante=True)
        -> _run_requester_report(dry_run)
           -> setup_logging()
           -> cleanup_runtime_residue()
           -> load_settings()
           -> Soft4Browser.ensure_authenticated()
           -> download_csv_as(prefix="solicitante")
           -> filtrar_csv_por_dias_uteis_sem_interacao() (solicitante)
           -> if SOFTDESK_API_KEY: _dispatch_requester_reports()
                build_requester_deliveries() via API -> per-requester sends
                + full report to EMAIL_SOLICITANTE_TODOS_CHAMADOS
              else: single legacy report to EMAIL_SOLICITANTE_RELATORIO
           -> dry-run branch (no e-mails) OR real SMTP branch
           -> cleanup_runtime_residue()
```

## Modules

- `main.py`: public script entrypoint; disables bytecode writes and returns
  `app.main.main()` as the process exit code.
- `app/main.py`: CLI parsing only (`argparse` + `--dry-run` + `--solicitante`);
  reexports `run` from `app.orchestrator.run` for backwards compatibility.
- `app/orchestrator/__init__.py`: package marker for orchestration.
- `app/orchestrator/run.py`: dispatcher `run(dry_run=False, solicitante=False)`
  selecting between `_run_attendant_report(dry_run)` and
  `_run_requester_report(dry_run)`, the `_dispatch_requester_reports` helper
  for per-requester deliveries, the dry-run plan logging helper, hardcoded
  `DRY_RUN_NOTIFICATION_RECIPIENT`, and exit-code handling (0/1/2). Imports its
  service layer from `app.services` and its lower-level dependencies from the
  new package layout (`app.config.loader`, `app.csv.filter`, `app.infra.*`,
  `app.soft4.browser`, `app.soft4.downloader`). Sets
  `sys.dont_write_bytecode = True`.
- `app/services/__init__.py`: facade reexporting the public mailer send
  functions (`send_attendant_csv_email`, `send_test_email`,
  `send_dry_run_success_email`, `send_manager_report_email`,
  `send_requester_report_email`, `EmailSendError`) and the queue domain symbols
  (`build_attendant_email_queue`, `mark_queue_item_sent`,
  `mark_queue_item_failed`, `EmailQueue`, `EmailQueueItem`,
  `EmailQueueError`). `app/orchestrator/run.py` imports its service
  layer from here.
- `app/config/__init__.py`: package marker for configuration.
- `app/config/models.py`: dataclasses (`Soft4Settings`, `EmailSettings`,
  `EmailQueueSettings`, `ManagerReportSettings`, `RequesterReportSettings`,
  `AppSettings`).
- `app/config/loader.py`: `PROJECT_ROOT` reexport, `ConfigError`,
  environment variable helpers `_env*`, `load_settings` (with the
  side effect of creating `downloads/`, `email_queue/`, `perfil_soft4/`),
  and `load_email_settings`.
- `app/infra/__init__.py`: package marker for cross-cutting infrastructure.
- `app/infra/fs.py`: `PROJECT_ROOT` and `remove_readonly` filesystem helper
  reused by `app/infra/cleanup` and `app/queue/repository`.
- `app/infra/logging_setup.py`: `setup_logging` with terminal stream and
  rotating file handler under `logs/frank_bot.log`.
- `app/infra/cleanup.py`: `cleanup_runtime_residue` removing `__pycache__`
  directories outside `.venv` and `perfil_soft4`.
- `app/soft4/__init__.py`: package marker for the Soft4 external
  integration (Playwright + Soft4 endpoints).
- `app/soft4/browser.py`: `Soft4Browser`, persistent Chromium context,
  login detection, login execution, session reuse, cookies, CSRF token
  extraction, and headers. (Formerly `app/auth.py`.)
- `app/soft4/downloader.py`: Soft4 queue payload, authenticated
  browser-side `fetch`, retry handling, previous CSV cleanup, and CSV
  validation. (Formerly `app/downloader.py`.)
- `app/soft4/api.py`: Softdesk API client for the requester report
  (`GET /api/api.php/chamado?codigo=<numero>` with `hash-api` header),
  `fetch_solicitante_email` (per chamado) and `fetch_solicitante_emails`
  (per CSV), HTTP 429 retry with `Retry-After`, `SoftdeskApiError`. Uses
  `requests`.
- `app/requester/__init__.py`: package marker for requester report delivery.
- `app/requester/delivery.py`: `build_requester_deliveries` — resolves each
  chamado's requester e-mail via the Softdesk API, groups chamados by
  recipient, ignores chamados without a resolvable e-mail, and builds
  `RequesterReportDelivery` objects (`RequesterDeliveryError` for missing
  rows, missing ID column, or no resolvable e-mails).
- `app/csv/__init__.py`: package marker for CSV concerns.
- `app/csv/io.py`: CSV delimiter detection, row reading, key normalization,
  and column resolution. (Formerly `app/csv_utils.py`.)
- `app/csv/filter.py`: business-day calculation, Brazilian national
  holidays, additional holidays, date parsing, and local CSV filtering.
  (Formerly `app/business_days.py`.)
- `app/queue/__init__.py`: package marker for the e-mail queue domain.
- `app/queue/grouping.py`: `group_by_attendant` (discards rows without
  attendant, preserving historical behavior).
- `app/queue/attendant_emails.py`: `load_attendant_emails`, reading
  `config/email_atendente.env` and `EMAIL_*` environment variables.
- `app/queue/repository.py`: `EmailQueue`, `EmailQueueItem`,
  `EmailQueueError`, `build_attendant_email_queue`, item status markers,
  `slugify`, and helpers for queue directory creation, previous-queue
  cleanup, attendant CSV/JSON writing, and queue summary. Uses
  `app.queue.grouping.group_by_attendant`,
  `app.queue.attendant_emails.load_attendant_emails`, and
  `app.infra.fs.remove_readonly`.
- `app/mailer/`: package providing e-mail transport, templates, and manager
  report assembly. The five public send functions live in
  `app/mailer/__init__.py`.
  - `app/mailer/smtp.py`: `EmailSendError`, `send_message` (SMTP TLS login),
    `parse_recipients`, `build_attachment`.
  - `app/mailer/templates.py`: pure `render_*` functions returning HTML for
    the attendant, test, dry-run, manager-report, and requester-report
    e-mails. HTML entities and styles preserved from the former
    `app/mailer.py`.
  - `app/mailer/reports.py`: `build_manager_report_sections` and helpers
    for reading the CSV and assembling per-attendant HTML tables. Keeps
    the historical `"Sem atendente"` fallback for rows without an attendant
    (intentionally different from `app.queue.grouping.group_by_attendant`,
    which discards rows without an attendant).
  - `app/mailer/__init__.py`: public send functions
    (`send_attendant_csv_email`, `send_test_email`,
    `send_dry_run_success_email`, `send_manager_report_email`,
    `send_requester_report_email`). Calls the transport via the module-local
    `_send_message` alias so test patches against `app.mailer._send_message`
    keep working.
- `tools/send_test_email.py`: operational SMTP test script (imports from
  `app.services` and `app.config.loader`).

## External System

- Default base URL: `https://mainhardt.soft4.com.br`.
- Queue page: `/chamado/fila-de-atendimento`.
- Search endpoint used inside browser JavaScript:
  `/chamado/fila-de-atendimento/json`.
- CSV endpoint used inside browser JavaScript:
  `/chamado/fila-de-atendimento/csv`.

`SOFT4_CSV_PATH` is loaded into settings, but the current browser-side fetch uses
the literal CSV path above.

## Configuration Surface

Soft4:

- `SOFT4_USUARIO`
- `SOFT4_SENHA`
- `SOFT4_BASE_URL`
- `SOFT4_FILA_PATH`
- `SOFT4_CSV_PATH`
- `SOFT4_TP_LISTAGEM`
- `SOFT4_DIAS_SEM_INTERACAO_ATENDENTE`
- `SOFT4_FERIADOS_ADICIONAIS`
- `SOFT4_TIMEOUT_SECONDS`
- `SOFT4_RETRIES`

Softdesk API (requester report):

- `SOFTDESK_API_KEY`
- `SOFT4_API_PATH` (default `/api/api.php`)

CSV and e-mail:

- `CSV_COLUNA_ATENDENTE`
- `CSV_COLUNA_ULTIMA_INTERACAO`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_USUARIO`
- `EMAIL_SENHA`
- `EMAIL_ATENDENTES_FILE`
- `EMAIL_FALHAR_SE_ATENDENTE_SEM_EMAIL`
- `EMAIL_GESTORA_RELATORIO`
- `NOME_GESTORA_RELATORIO`

Requester report:

- `SOFT4_TP_LISTAGEM_SOLICITANTE` (default `SEM_INTERACAO_SOLICITANTE`)
- `SOFT4_DIAS_SEM_INTERACAO_SOLICITANTE` (default `5`)
- `CSV_COLUNA_ULTIMA_INTERACAO_SOLICITANTE`
- `CSV_COLUNA_ID_CHAMADO`
- `EMAIL_SOLICITANTE_RELATORIO` (required)
- `NOME_SOLICITANTE_RELATORIO`
- `EMAIL_SOLICITANTE_TODOS_CHAMADOS` (full report copy; optional)

Legacy compatibility:

- `SMTP_HOST`
- `SMTP_PORT`
- `EMAIL_REMETENTE`
- `SENHA`

## Side Effects

- `setup_logging()` writes to terminal and to rotating logs under
  `logs/frank_bot.log`.
- `load_settings()` creates `downloads/`, `email_queue/`, and `perfil_soft4/`.
- `Soft4Browser` writes browser state to `perfil_soft4/`.
- `download_csv()` removes previous `downloads/fila_atendimento_*.csv` files
  before writing the new CSV; the requester flow uses `download_csv_as` with
  the `solicitante` prefix (`downloads/solicitante_*.csv`).
- `build_attendant_email_queue()` removes old queue directories before creating
  the current queue.
- Real execution sends SMTP e-mails to attendants and the manager.
- Real requester execution sends one SMTP report per requester e-mail and a
  full report to `EMAIL_SOLICITANTE_TODOS_CHAMADOS` when configured (or a
  single legacy report to `EMAIL_SOLICITANTE_RELATORIO` without a key).
- Dry-run execution still sends a success confirmation e-mail to Lucas Silva
  (attendant flow); requester dry-run sends no e-mails.
- Cleanup removes Python `__pycache__` directories outside `.venv` and
  `perfil_soft4`.

## Runtime Artifacts

Treat these as generated data, not documentation source:

- `.venv/`
- `.codex-audit/`
- `.agents/`
- `downloads/`
- `email_queue/`
- `logs/`
- `perfil_soft4/`
- `__pycache__/`

