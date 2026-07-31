# TODO.md — Backlog Oficial da Refatoracao

> Cada tarefa e uma unidade independente de trabalho. Executar UMA por vez.
> Ordem obrigatoria. Apos cada tarefa, atualizar `PROGRESS.md` e encerrar a
> execucao (nao continuar automaticamente).

## Tarefa 1 — Extrair logging e helpers de filesystem em `app/infra/`

### Objetivo

Separar preocupacoes transversais (logging e cleanup/fs) da configuracao de
negocio. Eliminar a duplicacao de `_remove_readonly`.

### Arquivos envolvidos

- Novos:
  - `app/infra/__init__.py`
  - `app/infra/logging_setup.py`
  - `app/infra/fs.py`
  - `app/infra/cleanup.py`
- Editados:
  - `app/settings.py` (tornar shim: reexportar `setup_logging`)
  - `app/email_queue.py` (importar `_remove_readonly` de `app.infra.fs`,
    remover copia local)
- Shims mantidos temporariamente:
  - `app/cleanup.py` reexporta `cleanup_runtime_residue` de `app.infra.cleanup`
- Imports atualizados (aplicacao):
  - `app/main.py`: `setup_logging` continua importando de `app.settings`
    (nao alterar nesta tarefa — usa-se o shim de settings).
    `cleanup_runtime_residue` tambem continua importando de `app.cleanup`
    (shim) OU ponto direto — escolher manter o import legado minimizando
    scope. **Decisao**: nesta tarefa, atualizar os imports para os novos
    caminhos so em `app/main.py` e `tools/send_test_email.py` para validar
    os novos modulos. O shim de `app/cleanup.py` garante compatibilidade
    tardia.
  - `tools/send_test_email.py`: importar `setup_logging` de
    `app.infra.logging_setup`.

### Checklist

- [ ] Criar `app/infra/__init__.py` vazio.
- [ ] Criar `app/infra/logging_setup.py` com `setup_logging` movido de
      `app/settings.py` (copia integral, sem alterar logica).
- [ ] Criar `app/infra/fs.py` com `remove_readonly` (nome sem underscore
      inicial; interna do pacote) unica implementacao.
- [ ] Criar `app/infra/cleanup.py` com `cleanup_runtime_residue` e
      `_remove_pycache`, usando `from app.infra.fs import remove_readonly`.
- [ ] `app/settings.py`: remover `setup_logging` e `RotatingFileHandler`
      daqui, mas manter reexportacao:
      `from app.infra.logging_setup import setup_logging` no final do
      arquivo (preserva `from app.settings import setup_logging`).
- [ ] `app/email_queue.py`: substituir a funcao local
      `_remove_readonly` por `from app.infra.fs import remove_readonly`
      e atualizar chamadas.
- [ ] `app/cleanup.py` torna-se shim:
      `from app.infra.cleanup import cleanup_runtime_residue` (exporta o
      nome antigo).
- [ ] `app/main.py`: alterar
      `from app.settings import ... setup_logging ...` para importar
      `setup_logging` de `app.infra.logging_setup` e
      `cleanup_runtime_residue` de `app.infra.cleanup`. **Preservar** o
      `from app.main import main` externo (sem mudanca).
- [ ] `tools/send_test_email.py`: usar
      `from app.infra.logging_setup import setup_logging`.
- [ ] Atualizar `codex-context/02-architecture.md` (modulo `infra/`).
- [ ] Atualizar `codex-context/06-inventory.md` (lista de arquivos
      Python).

### Validacoes

- `python -m compileall app tests tools` sem erros.
- `python tests/run_unittest_discovery.py` 12 testes OK.
- `test_setup_logging_writes_to_rotating_file` verde (importa de
  `app.settings`).

### Risco

Baixo. Apenas move funcoes; shims preservam todos os caminhos legados.

### Criterio de conclusao

Compila, testes verdes, docs de modulos atualizadas, PROGRESS.md
preenchido, commit unico com mensagem
`refactor: etapa 1 - infra (logging, cleanup, fs)`.

---

## Tarefa 2 — Quebrar `settings.py` em `app/config/`

### Objetivo

Separar modelos de dados de configuracao (`models.py`) do carregamento de
variaveis de ambiente (`loader.py`). Logging ja isolado na Tarefa 1.

### Arquivos envolvidos

- Novos:
  - `app/config/__init__.py`
  - `app/config/models.py`
  - `app/config/loader.py`
- Editados:
  - `app/settings.py` torna-se shim reexportando todos os simbolos
    publicos das duas novas pastas (preserva `from app.settings import X`).

### Checklist

- [ ] Criar `app/config/__init__.py` vazio.
- [ ] Criar `app/config/models.py` com: `Soft4Settings`, `EmailSettings`,
      `EmailQueueSettings`, `ManagerReportSettings`, `AppSettings`.
      Manter as `@property queue_url` e `csv_url`.
- [ ] Criar `app/config/loader.py` com: `PROJECT_ROOT`, `ConfigError`,
      `_env`, `_env_any`, `_env_int`, `_env_any_int`, `_env_bool`,
      `load_settings`, `load_email_settings`.
      - `load_settings` mantem o efeito colateral de criar
        `downloads/`, `email_queue/`, `perfil_soft4/` (preservar).
      - Importar o caminho correto para as dataclasses
        (`from app.config.models import Soft4Settings, ...`).
- [ ] `models.py` reexporta `ConfigError`:
      `from app.config.loader import ConfigError` (compat para testes
      que importem `from app.config.models import ConfigError`).
- [ ] `app/settings.py` reescrito como shim explicito:
      ```python
      from app.config.loader import (
          PROJECT_ROOT, ConfigError, load_settings, load_email_settings,
      )
      from app.config.models import (
          Soft4Settings, EmailSettings, EmailQueueSettings,
          ManagerReportSettings, AppSettings,
      )
      from app.infra.logging_setup import setup_logging
      ```
- [ ] Atualizar `codex-context/02-architecture.md` (modulo config).
- [ ] Atualizar `codex-context/06-inventory.md`.

### Validacoes

- `python -m compileall app tests tools`.
- `python tests/run_unittest_discovery.py` 12 OK.
- Teste do main usa `from app.settings import setup_logging`,
  `ConfigError`, etc. — preservado via shim.

### Risco

Baixo. Shim mantem compatibilidade.

### Criterio de conclusao

Compila, testes verdes, docs atualizadas, PROGRESS.md atualizado,
commit `refactor: etapa 2 - app/config (models + loader)`.

---

## Tarefa 3 — Reorganizar CSV em `app/csv/`

### Objetivo

Separar I/O de CSV (`io.py`) da regra de dias uteis e feriados
(`filter.py`). Movimentacao pura.

### Arquivos envolvidos

- Novos:
  - `app/csv/__init__.py`
  - `app/csv/io.py`
  - `app/csv/filter.py`
- Editados:
  - `app/csv_utils.py` -> shim
  - `app/business_days.py` -> shim

### Checklist

- [ ] Criar `app/csv/__init__.py` vazio.
- [ ] Criar `app/csv/io.py` com conteudo integral de `app/csv_utils.py`.
- [ ] Criar `app/csv/filter.py` com conteudo integral de
      `app/business_days.py`, trocando
      `from app.csv_utils import ...` por `from app.csv.io import ...`.
- [ ] `app/csv_utils.py` vira shim:
      `from app.csv.io import *` (ou reexportacao explicita).
- [ ] `app/business_days.py` vira shim:
      `from app.csv.filter import *`.
- [ ] Atualizar imports diretos em `app/email_queue.py` e `app/mailer.py`
      para apontar a `app.csv.io` (opcional nesta tarefa; shims cobrem;
      decidir pela clareza — escolher apontar direto para reduzir
      transitoriedade desde ja).
- [ ] Atualizar `codex-context/02-architecture.md` e `06-inventory.md`.

### Validacoes

- `python -m compileall app tests tools`.
- `python tests/run_unittest_discovery.py` 12 OK.

### Risco

Baixo.

### Criterio de conclusao

Compila, testes verdes, docs atualizadas, PROGRESS.md atualizado,
commit `refactor: etapa 3 - app/csv (io + filter)`.

---

## Tarefa 4 — Quebrar `email_queue.py` em `app/queue/`

### Objetivo

Separar dominio de fila de e-mail do I/O de arquivos; expor
`group_by_attendant` reutilizavel para o mailer (que ainda sera refactor na
Tarefa 5). Eliminar a duplicacao de `_remove_readonly` (ja feita na Tarefa
1).

### Arquivos envolvidos

- Novos:
  - `app/queue/__init__.py`
  - `app/queue/grouping.py`
  - `app/queue/attendant_emails.py`
  - `app/queue/repository.py`
- Editados:
  - `app/email_queue.py` -> shim

### Checklist

- [ ] Criar `app/queue/__init__.py` vazio.
- [ ] `app/queue/grouping.py`: mover `_group_by_attendant` renomeada para
      `group_by_attendant(rows, attendant_column)` (sem alterar logica).
- [ ] `app/queue/attendant_emails.py`: mover `load_attendant_emails`
      (import `normalize_key` de `app.csv.io`).
- [ ] `app/queue/repository.py`: mover `EmailQueue`, `EmailQueueItem`,
      `EmailQueueError`, `build_attendant_email_queue`,
      `mark_queue_item_sent`, `mark_queue_item_failed`, `slugify`,
      `_create_unique_queue_dir`, `_clear_previous_queue_dirs`,
      `_resolve_attendant_column`, `_write_attendant_csv`,
      `_write_metadata`, `_write_queue_summary`.
      - Importar `_remove_readonly`... continuaremos usando nome
        `remove_readonly` de `app.infra.fs`.
      - Importar `group_by_attendant` de `app.queue.grouping`
        (substituir a chamada local).
      - Importar `load_attendant_emails` de `app.queue.attendant_emails`.
      - Importar `normalize_key` de `app.csv.io`.
- [ ] `app/email_queue.py` vira shim reexportando:
      `EmailQueue`, `EmailQueueItem`, `EmailQueueError`,
      `build_attendant_email_queue`, `mark_queue_item_failed`,
      `mark_queue_item_sent`, `slugify`, `load_attendant_emails`,
      `group_by_attendant`, **e `normalize_key`** (teste
      `test_normalize_key_removes_accents_and_symbols` faz
      `from app.email_queue import normalize_key`).
- [ ] Atualizar `app/mailer.py`: ainda NAO usar `group_by_attendant` da
      queue (preservar comportamento atual). Apenas atualizar imports de
      `app.csv_utils` para `app.csv.io` se Tarefa 3 nao o fez.
- [ ] Atualizar `codex-context/02-architecture.md` e `06-inventory.md`.

### Validacoes

- `python -m compileall app tests tools`.
- `python tests/run_unittest_discovery.py` 12 OK.
- `test_build_queue_groups_by_attendant_and_tracks_missing_email` verde.
- Dry-run real (operador) opcional: queue.json identico ao baseline.

### Risco

Medio. Toca a construcao da fila, que mantem estado `pending/sent/failed`
e escreve arquivos.

### Criterio de conclusao

Compila, testes verdes, docs atualizadas, PROGRESS.md atualizado,
commit `refactor: etapa 4 - app/queue (grouping + attendant_emails + repository)`.

---

## Tarefa 5 — Quebrar `mailer.py` em `app/mailer/` (pacote)

### Objetivo

Separar transporte SMTP, templates HTML e relatorio. Extrair templates para
funcoes `render_*` puras sem dependencia de MIME. Fazer `reports.py` usar
`app.queue.grouping`.

### Pontos de atencao

Existe colisao entre o arquivo `app/mailer.py` (atual) e o pacote
`app/mailer/` (alvo). Estrategia anti-colisao:

1. Criar pacote `app/mailer_pkg/` (temporario) com
   `__init__.py`, `smtp.py`, `templates.py`, `reports.py`.
2. Atualizar imports dos importadores para `app.mailer_pkg.
3. Ap validar (compila + testes), deletar `app/mailer.py`.
4. Renomear `app/mailer_pkg/` -> `app/mailer/`.
5. Atualizar imports de volta para `app.mailer`.

### Arquivos envolvidos

- Novos:
  - `app/mailer_pkg/__init__.py`
  - `app/mailer_pkg/smtp.py`
  - `app/mailer_pkg/templates.py`
  - `app/mailer_pkg/reports.py`
- Editados:
  - `app/mailer.py` (deletado ap os testes)
  - `app/main.py` (`from app.mailer import ...` -> `app.mailer_pkg` -> `app.mailer`)
  - `tools/send_test_email.py`
  - `tests/test_email_queue_and_mailer.py` (`patch("app.mailer._send_message")`
    -> precisara apontar para `app.mailer.smtp._send_message`).

### Checklist

- [ ] Criar `app/mailer_pkg/__init__.py` com as 4 funcoes publicas
      (`send_attendant_csv_email`, `send_test_email`,
      `send_dry_run_success_email`, `send_manager_report_email`) reusando
      `templates.render_*` + `smtp._send_message`/`_parse_recipients`/
      `_build_attachment`.
      Reexportar tambem `EmailSendError`.
- [ ] Criar `app/mailer_pkg/smtp.py` com `_send_message`,
      `_parse_recipients`, `_build_attachment`.
      Import `EmailSettings` de `app.config.models`. Import `EmailSendError`.
- [ ] Criar `app/mailer_pkg/templates.py` com 4 funcoes render puras que
      retornam string HTML. Reproduzir ENTIDADES E ESTILOS EXATAMENTE.
- [ ] Criar `app/mailer_pkg/reports.py` com
      `_build_manager_report_sections`, `_build_manager_attendant_section`,
      `_build_report_table_row`, `_read_csv_for_report`,
      `_resolve_report_attendant_column`.
      Usar `group_by_attendant` de `app.queue.grouping`.
      PRESERVAR o fallback `"Sem atendente"` (diferente do repository que
      descarta linhas sem atendente).
- [ ] Atualizar `app/main.py`: import `from app.mailer import ...` ->
      `from app.mailer_pkg import ...`.
- [ ] Atualizar `tools/send_test_email.py` similarly.
- [ ] Atualizar `tests/test_email_queue_and_mailer.py`:
      `patch("app.mailer._send_message", ...)` ->
      `patch("app.mailer_pkg.smtp._send_message", ...)`.
      Atentar que 3 testes fazem este patch. Ap os testes passarem na
      primeira fase, trocar imports para `app.mailer` final.
- [ ] Fase 1: rodar `compileall` + testes com `app.mailer_pkg`.
- [ ] Fase 2: deletar `app/mailer.py`, renomear `app/mailer_pkg/` ->
      `app/mailer/`.
- [ ] Fase 3: atualizar imports `app.mailer_pkg` -> `app.mailer` em todo
      lugar (incluindo o patch de teste ->
      `patch("app.mailer.smtp._send_message", ...)`).
- [ ] Recriar `app/mailer.py` como shim? **NAO**. Pacote efetiva o nome.
- [ ] Atualizar `codex-context/02-architecture.md` e `06-inventory.md`.

### Validacoes

- `python -m compileall app tests tools`.
- `python tests/run_unittest_discovery.py` 12 OK.
- Os 4 testes de mailer (`test_manager_report_*`,
  `test_attendant_email_*`, `test_test_email_*`, `test_dry_run_success_*`)
  validam `assertIn` de substrings do HTML — todos verdes.

### Risco

Medio-alto. Montagem MIME e HTML sensivel. Testes validam apenas substrings.

### Criterio de conclusao

Compila, testes verdes, HTML templates preservados (entidades intactas),
docs atualizadas, PROGRESS.md atualizado,
commit `refactor: etapa 5 - app/mailer (smtp + templates + reports)`.

---

## Tarefa 6 — Mover Soft4 para `app/soft4/`

### Objetivo

Isolar integracao externa (Playwright e endpoints Soft4) num unico pacote.

### Arquivos envolvidos

- Novos:
  - `app/soft4/__init__.py`
  - `app/soft4/browser.py` (conteudo de `app/auth.py`)
  - `app/soft4/downloader.py` (conteudo de `app/downloader.py`)
- Editados:
  - `app/auth.py` -> shim
  - `app/downloader.py` -> shim
  - `app/main.py` (imports)

### Checklist

- [ ] Criar `app/soft4/__init__.py` vazio.
- [ ] Mover `app/auth.py` -> `app/soft4/browser.py` integralmente.
- [ ] Mover `app/downloader.py` -> `app/soft4/downloader.py`,
      trocar `from app.auth import AuthenticatedSession` ->
      `from app.soft4.browser import AuthenticatedSession`.
- [ ] Atualizar imports em `app/main.py`: `Soft4Browser`,
      `SessionExpiredError`, `download_csv` -> `app.soft4.browser` /
      `app.soft4.downloader`.
- [ ] Criar shims `app/auth.py` e `app/downloader.py` reexportando
      tudo o que antes era importado diretamente:
      `app/auth.py`: `from app.soft4.browser import *` com explicitos
      (`AuthenticationError`, `AuthenticatedSession`, `Soft4Browser`,
      `extract_csrf_token`, `build_headers`).
      `app/downloader.py`: `CsvDownloadError`, `SessionExpiredError`,
      `download_csv`.
- [ ] Atualizar `codex-context/02-architecture.md` e `06-inventory.md`.

### Validacoes

- `python -m compileall app tests tools`.
- `python tests/run_unittest_discovery.py` 12 OK.
- `test_dry_run_builds_queue_without_sending_email` faz
  `patch("app.main.Soft4Browser")` e `patch("app.main.download_csv")`
  (preservados, ja que os imports dentro de `app.main` apontarao para
  `app.soft4.*` configurados via `from app.soft4.browser import
  Soft4Browser`).

### Risco

Baixo.

### Criterio de conclusao

Compila, testes verdes, docs atualizadas, PROGRESS.md atualizado,
commit `refactor: etapa 6 - app/soft4 (browser + downloader)`.

---

## Tarefa 7 — Isolar orquestracao em `app/orchestrator/`

### Objetivo

Separar CLI de fluxo. Mover `run`, `_log_dry_run_plan`,
`DRY_RUN_NOTIFICATION_RECIPIENT` para `app/orchestrator/run.py`.
`app/main.py` fica apenas com `argparse`.

### Arquivos envolvidos

- Novos:
  - `app/orchestrator/__init__.py`
  - `app/orchestrator/run.py`
- Editados:
  - `app/main.py`
  - `tests/test_main_and_logging.py` (atualizar alvos de patch)

### Checklist

- [ ] Criar `app/orchestrator/__init__.py` vazio.
- [ ] Criar `app/orchestrator/run.py` movendo:
      `run`, `_log_dry_run_plan`, `DRY_RUN_NOTIFICATION_RECIPIENT`,
      `LOGGER`, `sys.dont_write_bytecode = True` (manter fora? decidir:
      manter `sys.dont_write_bytecode` no `main.py` raiz, que e o
      entrypoint). Imports ortodoxos para os novos caminhos:
      - `from app.infra.logging_setup import setup_logging`
      - `from app.infra.cleanup import cleanup_runtime_residue`
      - `from app.config.loader import load_settings, ConfigError,
         PROJECT_ROOT`
      - `from app.soft4.browser import Soft4Browser`
      - `from app.soft4.downloader import SessionExpiredError, download_csv`
      - `from app.csv.filter import filtrar_csv_por_dias_uteis_sem_interacao,
         montar_feriados, parse_feriados_adicionais`
      - `from app.queue.repository import build_attendant_email_queue,
         mark_queue_item_failed, mark_queue_item_sent`
      - `from app.mailer import send_attendant_csv_email,
         send_dry_run_success_email, send_manager_report_email`
- [ ] `app/main.py` (CLI) reescrito:
      ```python
      from __future__ import annotations
      import argparse, sys
      sys.dont_write_bytecode = True
      from app.orchestrator.run import run
      def main(argv=None) -> int:
          parser = argparse.ArgumentParser(...)
          parser.add_argument("--dry-run", ...)
          return run(dry_run=parser.parse_args(argv).dry_run)
      if __name__ == "__main__":
          raise SystemExit(main())
      ```
      Tambem reexporta `run`:
      `from app.orchestrator.run import run` (para `from app.main import
      run` continuar funcionando).
- [ ] Atualizar `tests/test_main_and_logging.py`:
      - `from app.main import main, run` ->
        `from app.main import main`
        `from app.orchestrator.run import run`.
      - `patch("app.main.run", return_value=0)` no
        `test_cli_enables_dry_run`: como `app.main` reexporta `run`,
        **o patch continua funcionando** (validar; se nao funcionar, trocar
        para `patch("app.orchestrator.run.run", ...)`). Preferir manter
        `patch("app.main.run", ...)` se possivel.
      - `test_dry_run_builds_queue_without_sending_email`: trocar todos os
        `patch("app.main.<X>")` por `patch("app.orchestrator.run.<X>")`
        para os 15 simbolos listados em `CONTEXT.md`.
      - `self.assertLogs("app.main", ...)` ->
        `self.assertLogs("app.orchestrator.run", ...)`.
- [ ] Atualizar `codex-context/02-architecture.md` (modulo orchestrator,
      fluxo).

### Validacoes

- `python -m compileall app tests tools`.
- `python tests/run_unittest_discovery.py` 12 OK.
- `test_cli_enables_dry_run` valida que `main(["--dry-run"])` chama
  `run(dry_run=True)`.
- `test_dry_run_builds_queue_without_sending_email` verde com os novos
  pontos de patch.

### Risco

Medio-alto. Ponto central da aplicacao e alvo dos patches de teste.

### Criterio de conclusao

Compila, testes verdes, docs atualizadas, PROGRESS.md atualizado,
commit `refactor: etapa 7 - app/orchestrator (isolado run)`.

---

## Tarefa 8 — Criar facade `app/services/` e limpar shims

### Objetivo

Centralizar ponto de entrada (services facade) e remover toda a
compatibilidade legada (shims). Orquestrador importa de `app.services`.

### Arquivos envolvidos

- Novos:
  - `app/services/__init__.py`
- Deletados (shims):
  - `app/settings.py`
  - `app/cleanup.py`
  - `app/csv_utils.py`
  - `app/business_days.py`
  - `app/email_queue.py`
  - `app/auth.py`
  - `app/downloader.py`
- Editados:
  - `app/orchestrator/run.py` (importar `send_*` e `mark_queue_item_*`
    de `app.services`)
  - `tools/send_test_email.py` (importar de `app.services` e
    `app.config.loader`)
  - `tests/test_main_and_logging.py` (checar que nenhum test faz import
    removido; se sim, atualizar)
  - `tests/test_email_queue_and_mailer.py`:
    `from app.email_queue import normalize_key` ->
    `from app.csv.io import normalize_key` (e outros imports que apontam
    a shims).

### Checklist

- [ ] Criar `app/services/__init__.py` expondo funcoes publicas:
      ```python
      from app.mailer import (
          EmailSendError, send_attendant_csv_email, send_test_email,
          send_dry_run_success_email, send_manager_report_email,
      )
      from app.queue.repository import (
          EmailQueue, EmailQueueItem, EmailQueueError,
          build_attendant_email_queue, mark_queue_item_failed,
          mark_queue_item_sent,
      )
      ```
- [ ] `app/orchestrator/run.py`: importa `send_*` e `mark_queue_item_*`
      de `app.services`. **Manter** os imports de
      `setup_logging`, `cleanup_runtime_residue`, `load_settings`,
      `Soft4Browser`, `download_csv`, `montar_feriados`,
      `parse_feriados_adicionais`, `filtrar_csv_por_dias_uteis_sem_interacao`,
      `build_attendant_email_queue` (este pode vir de services tambem),
      `ConfigError`, `PROJECT_ROOT`.
- [ ] Atualizar `tools/send_test_email.py`: importar de `app.services`
      e `app.config.loader` (nao mais de `app.settings`).
- [ ] Atualizar tests que importavam via shims:
      `from app.email_queue import normalize_key` -> `from app.csv.io`, etc.
- [ ] Verificar via grep que nenhum import legado permanece:
      `rg "from app\.settings import|from app\.cleanup import|from app\.csv_utils import|from app\.business_days import|from app\.email_queue import|from app\.auth import|from app\.downloader import|from app\.mailer import send|import app\.mailer" app tests tools`
      deve retornar vazio.
      (Excecao: `from app.mailer import` e permitido dentro de
      `app/services/__init__.py`).
- [ ] Deletar os 7 shims.
- [ ] Atualizar `codex-context/02-architecture.md`, `06-inventory.md`,
      `README.md` (estrutura).

### Validacoes

- `python -m compileall app tests tools`.
- `python tests/run_unittest_discovery.py` 12 OK.
- Grep de imports legados retorna vazio.

### Risco

Medio. Remocao de shims pode expor imports esquecidos.

### Criterio de conclusao

Compila, testes verdes, nenhum shim legado, docs atualizadas,
PROGRESS.md atualizado,
commit `refactor: etapa 8 - app/services facade + limpa shims`.

---

## Tarefa 9 — Reorganizar testes por tema (opcional)

### Objetivo

Dividir os 12 testes em arquivos pequenos por tema.

### Arquivos envolvidos

- Novos:
  - `tests/test_csv_filter.py`
  - `tests/test_email_queue.py`
  - `tests/test_mailer.py`
  - `tests/test_main_run.py`
- Deletados:
  - `tests/test_email_queue_and_mailer.py`
  - `tests/test_main_and_logging.py`

### Checklist

- [ ] `tests/test_csv_filter.py` com:
      `test_business_day_counter_ignores_weekend_and_starts_next_day`,
      `test_filter_csv_uses_last_interaction_date_and_skips_invalid_dates`,
      `test_filter_csv_uses_configurable_holidays`.
      Imports: `from app.csv.filter import ...`,
      `from app.csv.io import normalize_key`.
- [ ] `tests/test_email_queue.py` com:
      `test_build_queue_groups_by_attendant_and_tracks_missing_email`,
      `test_normalize_key_removes_accents_and_symbols`.
      Imports: `from app.queue.repository import ...`,
      `from app.csv.io import normalize_key`,
      `from app.config.models import EmailQueueSettings`.
- [ ] `tests/test_mailer.py` com os 4 testes de mailer:
      `test_manager_report_uses_full_csv_and_sends_structured_html`,
      `test_attendant_email_uses_priority_review_template`,
      `test_test_email_uses_configured_sender_and_recipient`,
      `test_dry_run_success_email_goes_only_to_lucas`.
      Patch: `patch("app.mailer.smtp._send_message", ...)`.
- [ ] `tests/test_main_run.py` com os 3 testes finais:
      `test_cli_enables_dry_run`, `test_setup_logging_writes_to_rotating_file`,
      `test_dry_run_builds_queue_without_sending_email`.
      Imports atualizados para nova arquitetura.
- [ ] Deletar arquivos antigos.
- [ ] Confirmar que `tests/run_unittest_discovery.py` descobre os novos
      (padrao `test_*.py`).

### Validacoes

- `python -m unittest discover -s tests -p "test_*.py" -v` — 12 OK.

### Risco

Nulo (apenas move).

### Criterio de conclusao

Compila, 12 testes OK, docs atualizadas, PROGRESS.md atualizado,
commit `refactor: etapa 9 - tests organizados por tema`.

---

## Tarefa 10 — Atualizar documentacao tecnica

### Objetivo

Sincronizar toda a documentacao com a estrutura final. Nao altera codigo.

### Arquivos envolvidos

- `README.md` (bloco "Estrutura")
- `CODEX_START_HERE.md` (ponteiro de arquivos Python)
- `codex-context/02-architecture.md` (modulos e fluxo)
- `codex-context/06-inventory.md` (inventario de arquivos)
- `codex-context/03-operations.md` (se referir a caminhos)
- `codex-context/04-decisions.md` (registrar decisoes de refatoracao)
- `codex-context/05-backlog.md` (registrar eventuais classicos
  remanescentes — nao necessario por padr)

### Checklist

- [ ] README.md: atualizar arvore de diretorios sob "Estrutura".
- [ ] CODEX_START_HERE.md: atualizar lista de arquivos Python.
- [ ] codex-context/02-architecture.md: reescrever "Modules",
      "Main Flow" (referir `app.orchestrator.run.run`),
      "Side Effects" (idem).
- [ ] codex-context/06-inventory.md: atualizar lista de "Project Files
      Reviewed".
- [ ] codex-context/04-decisions.md: append entry sobre a refatoracao
      arquitetural (data, motivo, escopo), preservando itens anteriores.

### Validacoes

- Revisao manual de consistencia entre docs e arvore final.
- `python -m compileall app tests tools` continua verde (docs nao afetam).
- `python tests/run_unittest_discovery.py` 12 OK.

### Risco

Nulo.

### Criterio de conclusao

Docs sincronizadas com codigo, PROGRESS.md atualizado,
commit `docs: etapa 10 - sincroniza documentacao pós refatoracao`.

---

## Ordem de execucao

1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9 -> 10

Nao alterar a ordem sem registrar justificativa em `DECISIONS.md`.

