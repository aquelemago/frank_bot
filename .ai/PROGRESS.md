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
| 1 | `app/infra/` (logging + cleanup + fs) | concluida | pendente | 2026-07-30 |
| 2 | `app/config/` (models + loader) | pendente | — | — |
| 3 | `app/csv/` (io + filter) | pendente | — | — |
| 4 | `app/queue/` (grouping + attendant_emails + repository) | pendente | — | — |
| 5 | `app/mailer/` (smtp + templates + reports) | pendente | — | — |
| 6 | `app/soft4/` (browser + downloader) | pendente | — | — |
| 7 | `app/orchestrator/` (run isolado) | pendente | — | — |
| 8 | `app/services/` facade + limpeza de shims | pendente | — | — |
| 9 | Reorganizacao dos testes por tema | pendente | — | — |
| 10 | Sincronizar documentacao tecnica | pendente | — | — |

## Pendencias

- Nenhuma tecnica. Tarefa 1 concluida e validada.
- Apenas operacional: o operador, se desejar, pode rodar `python main.py
  --dry-run` contra Soft4/SMTP para validacao adicional (opcional).

## Proxima acao

Commit da Tarefa 1 com a mensagem
`refactor: etapa 1 - app/infra (logging, cleanup, fs)`. Encerrar a execucao
e aguardar confirmacao do operador para iniciar a Tarefa 2.

## Log de alteracoes da etapa

### Tarefa 1 — `app/infra/`

Criados:
- `app/infra/__init__.py` (vazio)
- `app/infra/fs.py` — `PROJECT_ROOT` + `remove_readonly`
- `app/infra/logging_setup.py` — `setup_logging` (movido de settings)
- `app/infra/cleanup.py` — `cleanup_runtime_residue` + `_remove_pycache`

Editados (shims/imports):
- `app/settings.py` — reexporta `PROJECT_ROOT` e `setup_logging` de `app.infra`;
  removidos `import logging`, `RotatingFileHandler` e a definicao local.
- `app/cleanup.py` — shim reexportando `cleanup_runtime_residue`.
- `app/email_queue.py` — substitui a copia local de `_remove_readonly` por
  `from app.infra.fs import remove_readonly`; removidos `import stat` e a
  definicao duplicada.
- `app/main.py` — imports diretos de
  `app.infra.cleanup.cleanup_runtime_residue` e
  `app.infra.logging_setup.setup_logging` (para validar os novos modulos);
  os patches `patch("app.main.<X>")` nos testes permanecem funcionando.
- `tools/send_test_email.py` — import direto de
  `app.infra.logging_setup.setup_logging`.

Documentacao:
- `codex-context/02-architecture.md` atualizado com modulos `app/infra/*`.
- `codex-context/06-inventory.md` inventario atualizado com os 4 novos
  arquivos.

Validacao:
- `python -m compileall app tests tools`: OK.
- `python tests/run_unittest_discovery.py`: **12 OK**.

Microdecisao registrada em DECISIONS.md: `PROJECT_ROOT` foi movido para
`app/infra/fs.py` (antecipacao parcial da Tarefa 2) e reexportado por
`app/settings.py` para evitar dependencia circular entre `settings` e
`logging_setup`.
