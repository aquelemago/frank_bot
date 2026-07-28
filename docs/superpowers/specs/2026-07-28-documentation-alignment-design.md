# Design: Documentation Alignment

## Goal

Update the project documentation so it matches the code as the source of truth
and gives a new AI agent a reliable path to understand the project from zero.

## Scope

- Keep `README.md` as the human operational guide.
- Keep `CODEX_START_HERE.md` as the first document for AI agents.
- Reorganize `codex-context/` into a small technical documentation set:
  - `01-overview.md`
  - `02-architecture.md`
  - `03-operations.md`
  - `04-decisions.md`
  - `05-backlog.md`
  - `06-inventory.md`
- Correct known divergences against the current code, especially repository
  state, dry-run behavior, tests, runtime artifacts, dependencies, and public
  entry points.
- Preserve the security rule that `.env`, `config/*.env`, browser profile data,
  cookies, and tokens must not be opened, printed, summarized, or committed.

## Source Of Truth

The Python code, tests, `requirements.txt`, and current Git state are the source
of truth. Documentation must describe observed behavior, not historical intent.

## Validation

After documentation changes, run:

```powershell
python -m compileall app tests
python tests/run_unittest_discovery.py
```

Do not run `python main.py` against Soft4 or SMTP without explicit operational
approval.

