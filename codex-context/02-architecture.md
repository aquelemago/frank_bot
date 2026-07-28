# Architecture

## Main Flow

```text
main.py
  -> app.main.main()
    -> parse --dry-run
    -> app.main.run(dry_run)
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

## Modules

- `main.py`: public script entrypoint; disables bytecode writes and returns
  `app.main.main()` as the process exit code.
- `app/main.py`: CLI parsing, orchestration, logging setup, cleanup,
  authentication, CSV download, local filtering, queue creation, dry-run branch,
  real e-mail branch, and exit-code handling.
- `app/settings.py`: dataclasses, environment loading, legacy configuration
  compatibility, runtime directory creation, and rotating file logging.
- `app/auth.py`: `Soft4Browser`, persistent Chromium context, login detection,
  login execution, session reuse, cookies, CSRF token extraction, and headers.
- `app/downloader.py`: Soft4 queue payload, authenticated browser-side `fetch`,
  retry handling, previous CSV cleanup, and CSV validation.
- `app/business_days.py`: business-day calculation, Brazilian national
  holidays, additional holidays, date parsing, and local CSV filtering.
- `app/csv_utils.py`: CSV delimiter detection, row reading, key normalization,
  and column resolution.
- `app/email_queue.py`: attendant e-mail loading, grouping, old queue cleanup,
  per-attendant CSV/JSON creation, queue summary, and item status updates.
- `app/mailer.py`: HTML e-mail bodies, CSV attachments, multiple recipient
  parsing by comma or semicolon, SMTP TLS login, attendant e-mails, manager
  report, dry-run confirmation, and SMTP test e-mail.
- `app/cleanup.py`: removal of `__pycache__` directories outside `.venv` and
  `perfil_soft4`.
- `tools/send_test_email.py`: operational SMTP test script.

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
  before writing the new CSV.
- `build_attendant_email_queue()` removes old queue directories before creating
  the current queue.
- Real execution sends SMTP e-mails to attendants and the manager.
- Dry-run execution still sends a success confirmation e-mail to Lucas Silva.
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

