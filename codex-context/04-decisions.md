# Decisions

This file keeps lightweight architecture decision records. Add a dated entry
when a change affects behavior, structure, operations, or long-term maintenance.

## 2026-08-19 - Windows Task Scheduler For Production

Decision: deploy two independent daily Windows Task Scheduler jobs, one for
`main.py --solicitante` and one for `main.py`, under a dedicated technical
account. Use the project installer to configure explicit working directory,
`MultipleInstances=IgnoreNew`, a one-hour limit, no delayed start, and no
automatic retry.

Reason: these are two scheduled batch jobs, not a continuously served API. The
native scheduler removes the dependency on an interactive user login, exposes
task history and exit results, and avoids a permanently sleeping Python
process. Disabling retries and late starts reduces duplicate or out-of-window
e-mail risk.

Status: supersedes the Startup-shortcut deployment decision below. Offline
installer and rollback validation are complete; real registration requires the
technical account credential through the Windows secure prompt.

## 2026-08-13 - Permanent Scheduler Startup On Windows

Decision: run `service.py` with the virtual environment's `pythonw.exe` and
start it after user login through `Frank Bot Scheduler.lnk` in the current
user's Startup folder. Use a named Windows mutex as the source of truth for
single-instance protection; keep `frank_bot_service.lock` only as PID
diagnostic information.

Reason: this keeps deployment simple and dependency-free, prevents concurrent
use of the Chromium profile, and permits recovery after abrupt process exit
without manual deletion of an orphaned lock.

Status: shortcut configuration and direct startup were validated. Final
confirmation after a real login or reboot remains pending. Authorized
production validation completed both requester and attendant flows with exit
code `0`; one attendant mapping (Rafaela Zen) remains operationally pending.

Superseded on 2026-08-19 by the Windows Task Scheduler decision. `service.py`
is retained only as a fallback and must not run with the scheduled tasks.

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
  `tests/test_main_run.py` (12 tests green at the time; the suite later grew
  to 27 tests with the requester feature in etapas 1-12).
- Divergences preserved at the time (see `codex-context/02-architecture.md`
  and `codex-context/05-backlog.md`): `SOFT4_CSV_PATH` loaded but not used by
  the fetch; the two attendant-grouping rules (queue discards empty; manager
  report uses `"Sem atendente"`) intentionally not unified. The `requests`
  divergence was resolved in etapa 10 when `app/soft4/api.py` started using
  `requests` for the Softdesk API.

Reason: the original flat modules mixed concerns (config + logging, CSV filter +
file writes, SMTP + templates + report) and duplicated helpers (e.g.
`_remove_readonly`); layering makes the automation easier to maintain and test
without altering its observable behavior.

Status: accepted. Completed 2026-07-31. Validated at each step with
`python -m compileall app tests tools` and `python tests/run_unittest_discovery.py`
(12/12 OK at the time; 27/27 OK after the requester feature).

## 2026-07-31 - Requester Report Feature (Etapas 1-12)

Decision: add a requester report (chamados without requester interaction) as an
independent service, following the plan tracked in
`.ai/relatorio-solicitante/` (etapas 1-13 on branch
`feature/envia-email-para-solicitante`).

Scope and outcome:

- `SOFT4_TP_LISTAGEM_SOLICITANTE` (default `SEM_INTERACAO_SOLICITANTE`) and
  `SOFT4_DIAS_SEM_INTERACAO_SOLICITANTE` (default 5 at adoption; superseded by
  the 2026-08-19 decision below) drive the requester CSV download and local
  filter.
- `app/soft4/api.py` uses `requests` to fetch each chamado's requester e-mail
  from the Softdesk API (`GET /api/api.php/chamado`, `hash-api` header, HTTP
  429 retry); `app/requester/delivery.py` groups chamados by requester e-mail.
- Per-requester reports plus a full report to `EMAIL_SOLICITANTE_TODOS_CHAMADOS`
  are sent in a real run; without `SOFTDESK_API_KEY`, a single legacy report
  goes to `EMAIL_SOLICITANTE_RELATORIO`.
- The CLI gained `--solicitante`; `app.orchestrator.run.run(dry_run,
  solicitante)` dispatches to `_run_attendant_report` or `_run_requester_report`.
- Requester dry-run downloads and filters but sends no e-mails.

Reason: delivery per requester reduces message blast radius and keeps each
solicitante informed about their own chamados; the full-report copy preserves
the consolidated view.

Status: accepted. Completed 2026-07-31. Validated with `compileall` and 27/27
unit tests; real API validation of chamados 77934 and 78969 succeeded without
sending e-mails.

## 2026-08-19 - Requester Queue Filters Match The Soft4 Screen

Decision: requester and attendant status filters must be independent. The
requester queue uses solution groups `118` (`Suporte [MAINHARDT]`) and `257`
(`Suporte [UNUS]`), status `8` (`Aguardando solicitante`), listing type
`SEM_INTERACAO_SOLICITANTE`, and a default threshold of 3 days. The attendant
queue preserves its existing status filter `[5, 1, 12, 0]`.

Reason: authenticated observation of both the search and CSV requests produced
the requester contract above. The previous shared status list and 5-day default
selected chamados outside the approved requester report.

Status: accepted. The search payload was observed directly; the CSV request was
intercepted and aborted after its sanitized payload was captured, without
reading operational data or sending e-mail.

