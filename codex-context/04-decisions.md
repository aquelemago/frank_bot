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

