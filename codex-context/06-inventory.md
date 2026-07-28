# Inventory

## Audit Snapshot

- Date: 2026-07-28.
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
- `app/auth.py`
- `app/business_days.py`
- `app/cleanup.py`
- `app/csv_utils.py`
- `app/downloader.py`
- `app/email_queue.py`
- `app/mailer.py`
- `app/main.py`
- `app/settings.py`

Tests:

- `tests/run_unittest_discovery.py`
- `tests/test_email_queue_and_mailer.py`
- `tests/test_main_and_logging.py`

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

Observation: no direct `requests` import was found in the current Python project
files during documentation review. Keep it until operational impact is checked.

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
