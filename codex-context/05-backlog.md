# Backlog

## Current Risks And Technical Debt

- Configure the attendant e-mail mapping for Rafaela Zen; her rows are skipped
  while missing-attendant mappings are allowed.
- Validate exactly one occurrence of each newly installed Windows Task
  Scheduler job in the next natural production windows, using task history and
  new application log entries without a manual resend.
- Confirm the exact attendant column name in the production Soft4 CSV.
- Confirm the exact last-interaction column name in the production Soft4 CSV.
- Confirm whether `SOFT4_CSV_PATH` should be used by `app/soft4/downloader.py`;
  the current browser-side fetch uses the literal
  `/chamado/fila-de-atendimento/csv` path.
- Test headless login with real credentials after any change to
  `app/soft4/browser.py`.
- Test SMTP with a controlled Office365 account before releasing mailer changes.
- Unify the two attendant-grouping rules: `app/queue/grouping.group_by_attendant`
  discards rows without an attendant, while `app/mailer/reports.py` keeps a
  `"Sem atendente"` fallback. Unifying requires choosing one behavior and is
  intentionally out of scope of the architecture refactor.
- Add tests for settings validation and configuration errors.
- Add tests for CSV delimiter variations.
- Add tests for multiple recipients parsed by comma and semicolon.
- Add a resend command for failed queue items without downloading a new CSV.
- Add CI for `compileall` and `unittest`.

## Resolved Risks

- 2026-08-19: authenticated observation confirmed solution groups `118` and
  `257`, requester status `8`, listing type `SEM_INTERACAO_SOLICITANTE`, and 3
  days for both search and CSV requests. Requester and attendant status filters
  are now covered independently by unit tests.

## Documentation Maintenance

- Update `CODEX_START_HERE.md` whenever the AI onboarding path changes.
- Update `README.md` when human setup, configuration, execution, or validation
  changes.
- Update `01-overview.md` when business rules, scope, inputs, or outputs change.
- Update `02-architecture.md` when modules, data flow, configuration, or side
  effects change.
- Update `03-operations.md` when commands, validation, troubleshooting, or
  safety rules change.
- Add or update `04-decisions.md` for behavior or architecture decisions.
- Update `06-inventory.md` after meaningful audits.

## Safe Change Rules

- Read `CODEX_START_HERE.md`, `README.md`, and the relevant `codex-context/`
  file before changing behavior.
- Read the affected code before changing documentation.
- Keep `python main.py` and `app.main.run()` as stable public entrypoints.
- Do not expose secrets or operational data from `.env`, `config/*.env`,
  `downloads/`, `email_queue/`, `logs/`, or `perfil_soft4/`.
- Do not run real Soft4/SMTP operations without explicit approval.

