# Technical Documentation Index

This directory is the technical memory for the project. It is written for AI
agents and maintainers who need to understand or update the system without
guessing.

The code remains the source of truth. When documentation and code disagree,
trust the code and update the documentation.

## Map

- `01-overview.md`: what the system does, scope, business rules, inputs, and
  outputs.
- `02-architecture.md`: how the system works, modules, configuration surface,
  and side effects.
- `03-operations.md`: setup, execution, validation, troubleshooting, and safety.
- `04-decisions.md`: dated behavior and architecture decisions.
- `05-backlog.md`: known risks, technical debt, and future improvements.
- `06-inventory.md`: audit snapshot, reviewed files, dependencies, tests, and
  generated paths.

## Update Rules

- Changed product behavior or business rule: update `01-overview.md`.
- Changed flow, module responsibility, configuration, or side effect: update
  `02-architecture.md`.
- Changed commands, setup, validation, logs, or troubleshooting: update
  `03-operations.md`.
- Made an important behavior or architecture decision: update `04-decisions.md`.
- Found a risk, debt, or future improvement: update `05-backlog.md`.
- Ran a meaningful audit or changed the reviewed surface: update
  `06-inventory.md`.
- Changed human setup or operating instructions: update `README.md`.
- Changed AI onboarding or safety rules: update `CODEX_START_HERE.md`.

## Security Rules

- Do not include secrets or real credential values.
- Do not read or summarize `.env`, `config/*.env`, cookies, tokens, browser
  profile data, operational CSVs, or generated queue data.
- Treat `downloads/`, `email_queue/`, `logs/`, `perfil_soft4/`, `.agents/`,
  `.codex-audit/`, `.venv/`, and `__pycache__/` as generated/runtime paths.

