# Decisions

This file keeps lightweight architecture decision records. Add a dated entry
when a change affects behavior, structure, operations, or long-term maintenance.

## 2026-07-28 - Documentation Structure For AI Orientation

Decision: keep `CODEX_START_HERE.md` as the first AI entrypoint, keep
`README.md` as the human operational guide, and organize `codex-context/` into
overview, architecture, operations, decisions, backlog, and inventory.

Reason: a new AI agent needs a short safe start, then a predictable technical
map. Splitting documents by purpose reduces stale duplication and makes future
updates easier to target.

## 2026-06-23 - Dry-Run Sends Only Confirmation

Decision: `python main.py --dry-run` downloads and processes real Soft4 data,
creates the queue, keeps items as `pending`, skips attendant and manager sends,
and sends only a success confirmation to Lucas Silva.

Reason: dry-run validates the operational path while limiting the blast radius of
test e-mails.

## 2026-05-26 - Local Business-Day Filter

Decision: after downloading the Soft4 CSV, filter rows locally using business
days, Brazilian national holidays, and optional configured holidays.

Reason: the Soft4 pre-filter is not enough to express the business-day rule with
the needed precision.

## 2026-05-21 - CSV-Based Automation

Decision: use authenticated CSV export through the Soft4 page instead of the old
JSON/table extraction flow.

Reason: the CSV export is the operational artifact needed for attendant-specific
attachments and the manager report.

## 2026-05-21 - Persistent Headless Browser Session

Decision: use Playwright Chromium with persistent profile data under
`perfil_soft4/` and `headless=True`.

Reason: this allows session reuse and avoids interactive browser operation for
the routine.

## 2026-07-30 - 10-Step Architectural Refactor (Structure Only)

Decision: reorganize the codebase into layered packages without changing
behavior, in 10 incremental steps tracked in `.ai/` (plan, TODO, PROGRESS,
DECISIONS) and `docs/refactoring-plan.md`.

Scope and outcome:

- `app/config/` (settings dataclasses + env loading), `app/csv/` (IO + business
  day filter), `app/queue/` (e-mail queue domain), `app/mailer/` (SMTP,
  templates, manager report), `app/soft4/` (Playwright browser + CSV download),
  `app/infra/` (logging, cleanup, fs), `app/orchestrator/` (isolated `run()`),
  and `app/services/` (facade).
- `app/main.py` is CLI-only and reexports `run` from `app.orchestrator.run`.
- All legacy shims (`app/settings.py`, `app/cleanup.py`, `app/csv_utils.py`,
  `app/business_days.py`, `app/email_queue.py`, `app/auth.py`,
  `app/downloader.py`) were removed after imports were migrated.
- Tests were reorganized by theme into `tests/test_csv_filter.py`,
  `tests/test_email_queue.py`, `tests/test_mailer.py`, and
  `tests/test_main_run.py` (same 12 tests, all green).
- Divergences preserved (see `codex-context/02-architecture.md` and
  `codex-context/05-backlog.md`): `requests` still declared without direct
  import; `SOFT4_CSV_PATH` loaded but not used by the fetch; the two
  attendant-grouping rules (queue discards empty; manager report uses
  `"Sem atendente"`) intentionally not unified.

Reason: the original flat modules mixed concerns (config + logging, CSV filter +
file writes, SMTP + templates + report) and duplicated helpers (e.g.
`_remove_readonly`); layering makes the automation easier to maintain and test
without altering its observable behavior.

Status: accepted. Completed 2026-07-31. Validated at each step with
`python -m compileall app tests tools` and `python tests/run_unittest_discovery.py`
(12/12 OK).

