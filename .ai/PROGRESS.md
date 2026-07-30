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
| 3 | `app/csv/` (io + filter) | concluida | pendente | 2026-07-30 |
| 4 | `app/queue/` (grouping + attendant_emails + repository) | pendente | — | — |
| 5 | `app/mailer/` (smtp + templates + reports) | pendente | — | — |
| 6 | `app/soft4/` (browser + downloader) | pendente | — | — |
| 7 | `app/orchestrator/` (run isolado) | pendente | — | — |
| 8 | `app/services/` facade + limpeza de shims | pendente | — | — |
| 9 | Reorganizacao dos testes por tema | pendente | — | — |
| 10 | Sincronizar documentacao tecnica | pendente | — | — |

## Pendencias

- Nenhuma tecnica. Tarefas 0, 1, 2 e 3 concluidas e validadas.
- Apenas operacional: o operador, se desejar, pode rodar `python main.py
  --dry-run` contra Soft4/SMTP para validacao adicional (opcional).

## Proxima acao

Commit da Tarefa 3 com a mensagem
`refactor: etapa 3 - app/csv (io + filter)`. Encerrar a execucao
e aguardar confirmacao do operador para iniciar a Tarefa 4.

## Log de alteracoes da etapa

### Tarefa 3 — `app/csv/`

Criados:
- `app/csv/__init__.py` (vazio)
- `app/csv/io.py` — copia integral de `app/csv_utils.py` (`CsvReadError`,
  `normalize_key`, `read_csv_rows`, `resolve_column`, `_cell_has_content`).
- `app/csv/filter.py` — copia integral de `app/business_days.py`, trocando
  `from app.csv_utils import ...` por `from app.csv.io import ...`.
  (`BusinessDayFilterError`, `eh_dia_util`,
  `contar_dias_uteis_sem_interacao`, `chamado_deve_ser_processado`,
  `feriados_nacionais_brasil`, `montar_feriados`,
  `parse_feriados_adicionais`,
  `filtrar_csv_por_dias_uteis_sem_interacao`, e helpers privados).

Shims:
- `app/csv_utils.py` reexporta `CsvReadError`, `normalize_key`,
  `read_csv_rows`, `resolve_column` de `app.csv.io`.
- `app/business_days.py` reexporta os 8 simbolos publicos de
  `app.csv.filter`.

Imports legados preservados:
- `app/email_queue.py` e `app/mailer.py` continuam
  `from app.csv_utils import` (via shim).
- `app/main.py` continua `from app.business_days import` (via shim).
- `tests/test_email_queue_and_mailer.py` continua
  `from app.business_days import` (via shim).

Documentacao:
- `codex-context/02-architecture.md` atualizado.
- `codex-context/06-inventory.md` inventario atualizado com os 3 novos
  arquivos (`app/csv/__init__.py`, `app/csv/io.py`, `app/csv/filter.py`).

Validacao:
- `python -m compileall app tests tools`: OK.
- `python tests/run_unittest_discovery.py`: **12 OK**.


