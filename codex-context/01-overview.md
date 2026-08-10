# Overview

## Purpose

This project is a Python automation for the Soft4/Mainhardt support queue. It
opens a persistent Playwright Chromium session, exports the queue as CSV, applies
a local business-day filter for tickets without attendant interaction, splits
the filtered CSV by attendant, and sends e-mails through SMTP. It also produces
a requester report (tickets without requester interaction): in a real run with a
`SOFTDESK_API_KEY`, one e-mail per requester is sent with the requester's own
chamados plus a full report to `EMAIL_SOLICITANTE_TODOS_CHAMADOS`; without a key,
a single legacy e-mail goes to `EMAIL_SOLICITANTE_RELATORIO`.

The code is the source of truth. This document records the behavior observed in
the current codebase.

## Public Entrypoints

- `python main.py`: runs the attendant report (individual attendants + manager
  report).
- `python main.py --dry-run`: accesses Soft4, downloads and filters the
  attendant CSV, creates the e-mail queue, logs the planned sends, keeps queue
  items as `pending`, and sends only a dry-run confirmation to
  `lucas.silva@mainhardt.com.br`.
- `python main.py --solicitante`: runs the requester report only (individual
  e-mails per requester via the Softdesk API, plus the full report to
  `EMAIL_SOLICITANTE_TODOS_CHAMADOS` when configured).
- `python main.py --solicitante --dry-run`: accesses Soft4, downloads and
  filters the requester CSV, logs the planned sends, and sends no e-mails.
- `python tools/send_test_email.py`: sends a SMTP test e-mail without accessing
  Soft4 or downloading CSV.
- `app.main.run()`: programmatic orchestration entrypoint used by tests and the
  CLI (reexported from `app.orchestrator.run.run()`).
- `python tests/run_unittest_discovery.py`: unit-test discovery wrapper.

## In Scope

1. Load configuration from `.env` and legacy files under `config/`.
2. Create runtime directories when needed.
3. Open Playwright Chromium in `headless=True`.
4. Reuse the persistent browser profile in `perfil_soft4/`.
5. Detect the login page and log in when the session is missing or expired.
6. Capture page context, cookies, CSRF data, and browser headers.
7. Execute a queue search and CSV export by authenticated browser `fetch`.
8. Keep only the most recent full CSV under `downloads/`.
9. Filter the downloaded CSV locally by business days without attendant
   interaction.
10. Resolve CSV columns by configured name or normalized fallback.
11. Group rows by attendant.
12. Resolve attendant recipients from `config/email_atendente.env` and
    `EMAIL_*` environment variables.
13. Remove old queue directories and create a new
    `email_queue/YYYYMMDD_HHMMSS/` directory.
14. Write one CSV and one metadata JSON per attendant with a configured e-mail.
15. Write `queue.json` with the queue summary and attendants missing e-mail.
16. Send individual e-mails to attendants in a real run.
17. Send a consolidated manager report in a real run.
18. Mark individual queue items as `pending`, `sent`, or `failed`.
19. Return exit code `0`, `1`, or `2`.
20. Remove local Python cache directories at start and finish.
21. Download and filter the requester CSV
    (`downloads/solicitante_*.csv`) by business days without requester
    interaction.
22. Resolve requester e-mails per chamado through the Softdesk API (using the
    chamado number in `CSV_COLUNA_ID_CHAMADO`) and group chamados by requester
    e-mail.
23. Send one requester report per recipient and a full report to
    `EMAIL_SOLICITANTE_TODOS_CHAMADOS` in a real run.
24. Fall back to a single legacy report to `EMAIL_SOLICITANTE_RELATORIO` when
    no `SOFTDESK_API_KEY` is configured.

## Out Of Scope

- Updating tickets in Soft4.
- Native scheduling.
- Isolated resend of failed queue items.
- Long-term retention of previous `downloads/` or `email_queue/` runs.
- Selenium, PyAutoGUI, or visual desktop automation.

## Business Rules

- Default Soft4 listing type: `SEM_INTERACAO_ATENDENTE`.
- Default threshold: 3 business days without attendant interaction.
- The last interaction date is not counted; counting starts on the following
  day.
- The current date is counted when it is a business day.
- Business days exclude Saturdays, Sundays, Brazilian national holidays, and
  dates configured in `SOFT4_FERIADOS_ADICIONAIS`.
- Additional holidays accept comma or semicolon separated dates in `YYYY-MM-DD`
  or `DD/MM/YYYY` format.
- If the configured last-interaction column exists and a row has an empty or
  invalid date, that row is ignored and the count is logged.
- If the last-interaction column does not exist, the automation falls back to a
  column containing `Dias sem interacao` and infers an approximate date.
- If an attendant has no configured e-mail and
  `EMAIL_FALHAR_SE_ATENDENTE_SEM_EMAIL=true`, queue creation fails.
- If `EMAIL_FALHAR_SE_ATENDENTE_SEM_EMAIL=false`, attendants without e-mail are
  listed in `atendentes_sem_email` and skipped for individual e-mail sends.
- The manager report uses the locally filtered full CSV, not only the attendants
  with configured e-mail.
- Requester report default listing type: `SEM_INTERACAO_SOLICITANTE`.
- Requester threshold: 5 business days without requester interaction
  (`SOFT4_DIAS_SEM_INTERACAO_SOLICITANTE`), using
  `CSV_COLUNA_ULTIMA_INTERACAO_SOLICITANTE` when present.
- In a requester run with `SOFTDESK_API_KEY`, each chamado's requester e-mail is
  fetched from the Softdesk API; chamados without a resolvable e-mail are
  ignored and logged.
- A real requester run sends one report per requester and a full report to
  `EMAIL_SOLICITANTE_TODOS_CHAMADOS` when configured. Without a
  `SOFTDESK_API_KEY`, a single report goes to `EMAIL_SOLICITANTE_RELATORIO`.
- Requester dry-run sends no e-mails.

## Inputs And Outputs

Inputs:

- `.env` in the project root.
- `config/email_bot.env` for legacy SMTP settings.
- `config/email_atendente.env` for attendant recipient mapping.
- Persistent browser session under `perfil_soft4/`.
- CSV returned by Soft4 through authenticated POST.
- Softdesk API (`GET /api/api.php/chamado?codigo=<numero>`, header `hash-api`)
  when `SOFTDESK_API_KEY` is configured.
- `assinatura.png` in the project root for email signature (optional).

Outputs:

- `downloads/fila_atendimento_YYYYMMDD_HHMMSS.csv`.
- `downloads/solicitante_YYYYMMDD_HHMMSS.csv`.
- `email_queue/YYYYMMDD_HHMMSS/queue.json`.
- `email_queue/YYYYMMDD_HHMMSS/<atendente>.csv`.
- `email_queue/YYYYMMDD_HHMMSS/<atendente>.json`.
- `logs/frank_bot.log`.
- SMTP e-mails in real runs (attendants + manager report; requester reports per
  requester and the full report).

