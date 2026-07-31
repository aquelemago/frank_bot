# Start Here For AI Agents

This is the first file an AI agent should read in this project.

## Ground Rules

- The code is the source of truth.
- Describe observed behavior, not assumptions or outdated intent.
- Do not open, print, summarize, or commit values from `.env` or `config/*.env`.
- Do not expose SMTP credentials, Soft4 credentials, cookies, tokens, browser
  profile data, operational CSV contents, or generated queue data.
- Do not run the real automation against Soft4/SMTP without explicit approval of
  environment, credentials, and recipients.
- Preserve `python main.py` and `app.main.run()` as public entrypoints. The
  orchestration flow itself lives in `app.orchestrator.run.run()`.

## Reading Order

1. `CODEX_START_HERE.md`: safety rules and orientation.
2. `README.md`: human setup, configuration, execution, and validation guide.
3. `codex-context/README.md`: technical documentation index.
4. Relevant technical documents:
   - `codex-context/01-overview.md`: purpose, scope, business rules, inputs,
     and outputs.
   - `codex-context/02-architecture.md`: flow, modules, configuration, and side
     effects.
   - `codex-context/03-operations.md`: runbook, validation, troubleshooting, and
     operational safety.
   - `codex-context/04-decisions.md`: important architecture and behavior
     decisions.
   - `codex-context/05-backlog.md`: risks, technical debt, and future work.
   - `codex-context/06-inventory.md`: audit evidence from the current codebase.

## Current State

- Python automation for exporting the Soft4/Mainhardt support queue as CSV.
- Main code lives under `app/`:
  - `app/main.py`: CLI only (`argparse` + `--dry-run`); reexports `run`.
  - `app/orchestrator/run.py`: full automation flow (`run()`), dry-run plan
    logging, exit codes, hardcoded dry-run recipient.
  - `app/services/`: facade reexporting mailer send functions and queue
    symbols; the orchestrator imports its service layer from here.
  - `app/config/`: settings dataclasses (`models.py`) and env loading
    (`loader.py`).
  - `app/csv/`: CSV reading helpers (`io.py`) and business-day/holiday
    filter (`filter.py`).
  - `app/queue/`: e-mail queue domain (grouping, attendant e-mails,
    repository).
  - `app/mailer/`: SMTP transport (`smtp.py`), HTML templates
    (`templates.py`), manager report assembly (`reports.py`).
  - `app/soft4/`: external integration (Playwright browser session and CSV
    downloader).
  - `app/infra/`: cross-cutting infrastructure (logging, cleanup, fs).
- Public command: `python main.py`.
- Dry-run command: `python main.py --dry-run`.
- SMTP test command: `python tools/send_test_email.py`.
- CSVs output: `downloads/fila_atendimento_YYYYMMDD_HHMMSS.csv` (atendente) and
  `downloads/solicitante_YYYYMMDD_HHMMSS.csv` (solicitante).
- E-mail queue output: `email_queue/YYYYMMDD_HHMMSS/`.
- Rotating logs: `logs/frank_bot.log`.
- Persistent browser profile: `perfil_soft4/`.
- This folder is a Git repository.

## Safe Commands

```powershell
python -m compileall app tests tools
python tests/run_unittest_discovery.py
```

## Unsafe Without Explicit Approval

```powershell
python main.py
```

`python main.py --dry-run` is safer than a full run, but it still accesses Soft4,
downloads real data, creates runtime artifacts, and sends one confirmation e-mail
to `lucas.silva@mainhardt.com.br`.

