# Inventory

## Audit Snapshot

- Date: 2026-07-28 (original audit); re-verified 2026-07-31 after the 10-step
  architecture refactor and again after the requester-report feature (etapas
  1-13) on branch `feature/envia-email-para-solicitante`; requester queue
  filters and the 57-test suite re-verified on 2026-08-19.
- Source of truth: current Python code, tests, `requirements.txt`, and Git
  metadata.
- Repository state: this folder is a Git repository. During this audit,
  `.agents/` and `skills-lock.json` were untracked because project-local skills
  were installed for the documentation task.
- Versioning note: `.gitignore` no longer ignores `README.md`,
  `CODEX_START_HERE.md`, or `codex-context/`, so official documentation can be
  tracked normally.
- Sensitive files were not opened: `.env`, `config/*.env`, cookies, tokens, and
  browser profile data.

## Project Files Reviewed

Python entrypoints and modules:

- `main.py`
- `tools/send_test_email.py`
- `app/__init__.py`
- `app/csv/__init__.py`
- `app/csv/io.py`
- `app/csv/filter.py`
- `app/soft4/__init__.py`
- `app/soft4/browser.py`
- `app/soft4/downloader.py`
- `app/soft4/api.py`
- `app/requester/__init__.py`
- `app/requester/delivery.py`
- `app/queue/__init__.py`
- `app/queue/grouping.py`
- `app/queue/attendant_emails.py`
- `app/queue/repository.py`
- `app/main.py`
- `app/mailer/__init__.py` (was `app/mailer.py`: public send functions)
- `app/mailer/reports.py`
- `app/mailer/smtp.py`
- `app/mailer/templates.py`
- `app/orchestrator/__init__.py`
- `app/orchestrator/run.py`
- `app/services/__init__.py` (facade: mailer send functions + queue symbols)
- `app/config/__init__.py`
- `app/config/loader.py`
- `app/config/models.py`
- `app/infra/__init__.py`
- `app/infra/cleanup.py`
- `app/infra/fs.py`
- `app/infra/logging_setup.py`

Tests:

- `tests/run_unittest_discovery.py`
- `tests/test_config_loader.py`
- `tests/test_csv_filter.py`
- `tests/test_email_queue.py`
- `tests/test_mailer.py`
- `tests/test_main_run.py`
- `tests/test_soft4_api.py`
- `tests/test_soft4_downloader.py`
- `tests/test_requester_report.py`
- `tests/test_requester_delivery.py`

Documentation:

- `README.md`
- `CODEX_START_HERE.md`
- `codex-context/README.md`
- `codex-context/01-overview.md`
- `codex-context/02-architecture.md`
- `codex-context/03-operations.md`
- `codex-context/04-decisions.md`
- `codex-context/05-backlog.md`
- `codex-context/06-inventory.md`

## Dependencies

Declared in `requirements.txt`:

- `playwright>=1.44.0`
- `python-dotenv>=1.0.1`
- `requests>=2.31.0`

Observation: `requests` is imported directly by `app/soft4/api.py` (Softdesk
API client) and mocked in `tests/test_soft4_api.py`. It is required and must
stay in `requirements.txt`.

## Tests

Covered by current tests:

- CLI dry-run flag wiring.
- Dry-run branch avoids attendant and manager sends.
- Dry-run success confirmation arguments.
- Rotating log file creation.
- Queue grouping by attendant.
- Missing attendant recipient handling.
- Attendant e-mail HTML template.
- Manager report e-mail generation.
- Requester report e-mail generation (`render_requester_report_email`).
- Requester delivery grouping via the Softdesk API
  (`tests/test_requester_delivery.py`).
- Softdesk API fetch with 404/429/retry and missing-key handling
  (`tests/test_soft4_api.py`).
- CLI `--solicitante` flag and requester-only dry-run
  (`tests/test_main_run.py`).
- Requester configuration defaults and optional full-report copy settings
  (`tests/test_config_loader.py`).
- Independent requester/attendant queue payload filters, including requester
  groups `[118, 257]`, status `[8]`, listing type, and 3-day threshold
  (`tests/test_soft4_downloader.py`).
- Propagation of requester days from orchestration through download and local
  filter, including filter-before-dispatch ordering (`tests/test_main_run.py`).
- SMTP test e-mail generation.
- Dry-run confirmation e-mail generation.
- CSV key normalization.
- Business-day counting.
- Invalid last-interaction dates.
- Configured additional holidays.

Safe validation commands:

```powershell
python -m compileall app tests
python tests/run_unittest_discovery.py
```

Windows deployment tooling:

- `tools/install_windows_scheduled_tasks.ps1`: validates prerequisites and
  idempotently registers the two daily jobs using a securely prompted technical
  account; it never runs the jobs during installation.
- `tools/uninstall_windows_scheduled_tasks.ps1`: validates or removes only the
  two tasks managed under `\FrankBot\`.
- `service.py`: legacy/fallback in-process scheduler; not the recommended
  production deployment and unsafe to run concurrently with scheduled tasks.

## Generated And Sensitive Paths

Generated/runtime:

- `.agents/`
- `.codex-audit/`
- `.venv/`
- `downloads/`
- `email_queue/`
- `logs/`
- `perfil_soft4/`
- `__pycache__/`

Sensitive:

- `.env`
- `config/*.env`
- Browser cookies/session data under `perfil_soft4/`
- Operational CSV and queue contents under `downloads/` and `email_queue/`
