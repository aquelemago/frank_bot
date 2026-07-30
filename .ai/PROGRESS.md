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
| 4 | `app/queue/` (grouping + attendant_emails + repository) | concluida | `0399d47` | 2026-07-30 |
| 5 | `app/mailer/` (smtp + templates + reports) | concluida | `62e50c3` | 2026-07-30 |
| 6 | `app/soft4/` (browser + downloader) | concluida | `a9aaf59` | 2026-07-30 |
| 7 | `app/orchestrator/` (run isolado) | pendente | — | — |
| 8 | `app/services/` facade + limpeza de shims | pendente | — | — |
| 9 | Reorganizacao dos testes por tema | pendente | — | — |
| 10 | Sincronizar documentacao tecnica | pendente | — | — |

## Pendencias

- Nenhuma tecnica. Tarefas 0, 1, 2, 3, 4, 5 e 6 concluidas e validadas.
- Apenas operacional: o operador, se desejar, pode rodar `python main.py
  --dry-run` contra Soft4/SMTP para validacao adicional (opcional).

## Proxima acao

Commit da Tarefa 6 com a mensagem
`refactor: etapa 6 - app/soft4 (browser + downloader)`.
Encerrar a execucao e aguardar confirmacao do operador para iniciar a
Tarefa 7.

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

### Tarefa 5 — `app/mailer/`

Estrategia anti-colisao (registrada em DECISIONS.md):
- Criado pacote temporario `app/mailer_pkg/` com 4 modulos.
- Atualizados importadores para `app.mailer_pkg`.
- Validados testes (12 OK).
- Deletado `app/mailer.py`.
- Renomeado `app/mailer_pkg/` -> `app/mailer/`.
- Voltados imports para `app.mailer`.
- Validados testes novamente (12 OK).

Criados (4 modulos em `app/mailer/`):
- `app/mailer/__init__.py` — 4 funcoes publicas
  (`send_attendant_csv_email`, `send_test_email`,
  `send_dry_run_success_email`, `send_manager_report_email`) e o alias
  `_send_message` (preserva ponto de patch dos testes
  `patch("app.mailer._send_message", ...)`).
- `app/mailer/smtp.py` — `EmailSendError`, `send_message` (SMTP TLS),
  `parse_recipients`, `build_attachment`.
- `app/mailer/templates.py` — 4 funcoes `render_*` puras retornando HTML
  identico ao anterior (entidades `&aacute;`, `&ccedil;`, etc.
  preservadas).
- `app/mailer/reports.py` — `build_manager_report_sections` e helpers.
  **Preserva** o fallback `"Sem atendente"` (regra do mailer, diferente
  do `queue.grouping.group_by_attendant` que descarta vazios).
  Importa `read_csv_rows`, `CsvReadError`, `resolve_column` de
  `app.csv.io` (nao mais de `app.csv_utils`).

Deletado:
- `app/mailer.py` (substituido pelo pacote `app/mailer/`).

Importadores atualizados:
- `app/main.py`, `tools/send_test_email.py`,
  `tests/test_email_queue_and_mailer.py` agora importam de `app.mailer`
  (direto). Os patches de teste `patch("app.main.<X>")` continuam
  funcionando (simbolos ficam no namespace de `app.main`).
- Os 4 `patch("app.mailer._send_message")` voltaram ao ponto final
  `app.mailer._send_message` (alias no `__init__.py`).

Microdecisao registrada em DECISIONS.md: `reports.py` **não** usa
`app.queue.grouping.group_by_attendant` (que descarta linhas sem
atendente); manteve o loop local com fallback `"Sem atendente"` para
preservar exatamente o comportamento histórico do relatorio gerencial.
A unificacao dos agrupamentos ficaria como possivel backlog, mas
**fora do escopo** desta refatoracao (seria alteracao de comportamento
do relatorio).

Documentacao:
- `codex-context/02-architecture.md` atualizado com o pacote `app/mailer/`.
- `codex-context/06-inventory.md` inventario atualizado com os 4 novos
  arquivos.

Validacao:
- `python -m compileall app tests tools`: OK.
- `python tests/run_unittest_discovery.py`: **12 OK**.
- Os 4 testes de mailer (`test_attendant_email_*`, `test_manager_report_*`,
  `test_test_email_*`, `test_dry_run_success_*`) validam substrings dos
  HTMLs, subjects, `From`/`To` — todos verdes.

### Tarefa 6 — `app/soft4/`

Criados:
- `app/soft4/__init__.py` (vazio)
- `app/soft4/browser.py` — copia integral de `app/auth.py`
  (`Soft4Browser`, `AuthenticatedSession`, `AuthenticationError`,
  `extract_csrf_token`, `build_headers`). Importa `Soft4Settings` de
  `app.config.loader` (caminho novo, preservado via reexportacao
  em `loader`).
- `app/soft4/downloader.py` — copia integral de `app/downloader.py`
  (`CsvDownloadError`, `SessionExpiredError`, `download_csv` e helpers).
  Troca `from app.auth import AuthenticatedSession` por
  `from app.soft4.browser import AuthenticatedSession`.

Shims:
- `app/auth.py` reexporta `AuthenticationError`, `AuthenticatedSession`,
  `Soft4Browser`, `build_headers`, `extract_csrf_token` de
  `app.soft4.browser`.
- `app/downloader.py` reexporta `CsvDownloadError`, `SessionExpiredError`,
  `download_csv` de `app.soft4.downloader`.

Imports legados preservados (via shim):
- `app/main.py`: `from app.auth import Soft4Browser` e
  `from app.downloader import SessionExpiredError, download_csv`.

Patches de teste preservados:
- `test_dry_run_builds_queue_without_sending_email` faz
  `patch("app.main.Soft4Browser")` e `patch("app.main.download_csv")`,
  que continuam funcionando pois os simbolos permanecem no namespace
  de `app.main` (importados via shim).

Documentacao:
- `codex-context/02-architecture.md` atualizado com o pacote `app/soft4/`.
- `codex-context/06-inventory.md` inventario atualizado com os 3 novos
  arquivos (`app/soft4/__init__.py`, `app/soft4/browser.py`,
  `app/soft4/downloader.py`).

Validacao:
- `python -m compileall app tests tools`: OK.
- `python tests/run_unittest_discovery.py`: **12 OK**.


