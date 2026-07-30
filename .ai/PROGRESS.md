# PROGRESS.md — Estado Corrente da Refatoracao

## Snapshot inicial

- Data: 2026-07-30.
- Branch: `feature/refatora-arquitetura`.
- Commit base: `40677f2 Reorganiza documentacao tecnica`.
- Testes baseline: **12 OK** (`python tests/run_unittest_discovery.py`).
- `compileall`: OK.

## Status por tarefa

| Tarefa | Titulo | Status | Commit | Validado em |
|---|---|---|---|---|
| 0 | Estabelecer memoria `.ai/` e `docs/refactoring-plan.md` | concluida | `e489113` | 2026-07-30 |
| 1 | `app/infra/` (logging + cleanup + fs) | concluida | `1eb47ef` | 2026-07-30 |
| 2 | `app/config/` (models + loader) | concluida | `5d83761` | 2026-07-30 |
| 3 | `app/csv/` (io + filter) | pendente | — | — |
| 4 | `app/queue/` (grouping + attendant_emails + repository) | pendente | — | — |
| 5 | `app/mailer/` (smtp + templates + reports) | pendente | — | — |
| 6 | `app/soft4/` (browser + downloader) | pendente | — | — |
| 7 | `app/orchestrator/` (run isolado) | pendente | — | — |
| 8 | `app/services/` facade + limpeza de shims | pendente | — | — |
| 9 | Reorganizacao dos testes por tema | pendente | — | — |
| 10 | Sincronizar documentacao tecnica | pendente | — | — |

## Pendencias

- Nenhuma tecnica. Tarefas 0, 1 e 2 concluidas e validadas.
- Apenas operacional: o operador, se desejar, pode rodar `python main.py
  --dry-run` contra Soft4/SMTP para validacao adicional (opcional).

## Proxima acao

Commit da Tarefa 2 com a mensagem
`refactor: etapa 2 - app/config (models + loader)`. Encerrar a execucao
e aguardar confirmacao do operador para iniciar a Tarefa 3.

## Log de alteracoes da etapa

### Tarefa 2 — `app/config/`

Criados:
- `app/config/__init__.py` (vazio)
- `app/config/models.py` — 5 dataclasses (`Soft4Settings`,
  `EmailSettings`, `EmailQueueSettings`, `ManagerReportSettings`,
  `AppSettings`) com as `@property queue_url` e `csv_url` preservadas.
- `app/config/loader.py` — `ConfigError`, helpers `_env*`,
  `load_settings` (efeito colateral de criar `downloads/`,
  `email_queue/`, `perfil_soft4/` preservado) e `load_email_settings`.
  Importa `PROJECT_ROOT` de `app.infra.fs` e as dataclasses de
  `app.config.models`.

Editados:
- `app/settings.py` reescrito como shim puro, reexportando tudo de
  `app.config.loader`, `app.config.models` e
  `app.infra.logging_setup`.

Documentacao:
- `codex-context/02-architecture.md` atualizado.
- `codex-context/06-inventory.md` inventario atualizado.

Validacao:
- `python -m compileall app tests tools`: OK.
- `python tests/run_unittest_discovery.py`: **12 OK**.

Observacao sobre a microdecisao da Tarefa 1:
- A Tarefa 1 ja tinha movido `PROJECT_ROOT` para `app/infra/fs.py`.
  Conforme registrado em DECISIONS.md, na Tarefa 2 nao foi necessario
  mover `PROJECT_ROOT` novamente. `app/config/loader` apenas o
  reexporta a partir de `app.infra.fs`, e `app/settings.py` o
  reexporta de `app.config.loader`.


