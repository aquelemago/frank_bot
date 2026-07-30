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
| 3 | `app/csv/` (io + filter) | concluida | `7010b6b` | 2026-07-30 |
| 4 | `app/queue/` (grouping + attendant_emails + repository) | concluida | pendente | 2026-07-30 |
| 5 | `app/mailer/` (smtp + templates + reports) | pendente | — | — |
| 6 | `app/soft4/` (browser + downloader) | pendente | — | — |
| 7 | `app/orchestrator/` (run isolado) | pendente | — | — |
| 8 | `app/services/` facade + limpeza de shims | pendente | — | — |
| 9 | Reorganizacao dos testes por tema | pendente | — | — |
| 10 | Sincronizar documentacao tecnica | pendente | — | — |

## Pendencias

- Nenhuma tecnica. Tarefas 0, 1, 2, 3 e 4 concluidas e validadas.
- Apenas operacional: o operador, se desejar, pode rodar `python main.py
  --dry-run` contra Soft4/SMTP para validacao adicional (opcional).

## Proxima acao

Commit da Tarefa 4 com a mensagem
`refactor: etapa 4 - app/queue (grouping + attendant_emails + repository)`.
Encerrar a execucao e aguardar confirmacao do operador para iniciar a
Tarefa 5.

## Log de alteracoes da etapa

### Tarefa 4 — `app/queue/`

Criados:
- `app/queue/__init__.py` (vazio)
- `app/queue/grouping.py` — `group_by_attendant(rows, attendant_column)`.
  Preserva a regra do antigo `_group_by_attendant` do email_queue:
  **descarta** linhas com atendente vazio (diferente do mailer, que usa
  `"Sem atendente"` como fallback — preservado, nao tocado nesta tarefa).
- `app/queue/attendant_emails.py` — `load_attendant_emails` (movido do
  email_queue). Importa `normalize_key` de `app.csv.io`.
- `app/queue/repository.py` — `EmailQueue`, `EmailQueueItem`,
  `EmailQueueError`, `build_attendant_email_queue`,
  `mark_queue_item_sent`, `mark_queue_item_failed`, `slugify`, e os
  helpers privados (`_create_unique_queue_dir`, `_clear_previous_queue_dirs`,
  `_resolve_attendant_column`, `_write_attendant_csv`, `_write_metadata`,
  `_write_queue_summary`).
  Usa:
  - `group_by_attendant` de `app.queue.grouping`;
  - `load_attendant_emails` de `app.queue.attendant_emails`;
  - `remove_readonly` de `app.infra.fs`;
  - `normalize_key`, `read_csv_rows`, `resolve_column`, `CsvReadError`
    de `app.csv.io`;
  - `EmailQueueSettings` de `app.config.models`.

Shim:
- `app/email_queue.py` reexporta `EmailQueue`, `EmailQueueError`,
  `EmailQueueItem`, `EmailQueueSettings`, `build_attendant_email_queue`,
  `group_by_attendant`, `load_attendant_emails`,
  `mark_queue_item_failed`, `mark_queue_item_sent`, `normalize_key`,
  `slugify`.

Imports legados preservados (via shim):
- `app/main.py`: `build_attendant_email_queue`,
  `mark_queue_item_failed`, `mark_queue_item_sent`.
- `tests/test_main_and_logging.py`: `EmailQueue`, `EmailQueueItem`.
- `tests/test_email_queue_and_mailer.py`: `build_attendant_email_queue`,
  `normalize_key`.

Pontos de atencao (registrados em DECISIONS.md):
- Diferenca de comportamento entre os dois agrupamentos (email_queue
  descarta vazios; mailer usa "Sem atendente") — preservada. O mailer
  ainda NAO usa `group_by_attendant` ( fica para a Tarefa 5).

Documentacao:
- `codex-context/02-architecture.md` atualizado.
- `codex-context/06-inventory.md` inventario atualizado com os 4 novos
  arquivos (`app/queue/__init__.py`, `app/queue/grouping.py`,
  `app/queue/attendant_emails.py`, `app/queue/repository.py`).

Validacao:
- `python -m compileall app tests tools`: OK.
- `python tests/run_unittest_discovery.py`: **12 OK**.
- `test_build_queue_groups_by_attendant_and_tracks_missing_email` verde
  (confirma fila identica: Ana Silva com 2 chamados, Bruno Souza em
  `missing_recipients`).


