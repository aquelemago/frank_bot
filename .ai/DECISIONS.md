# DECISIONS.md — Decisoes e Divergencias Registradas

## Formato

Cada entrada contem: data, contexto, decisao, impacto, status.

---

## 2026-07-30 — Baseline de validacao por testes automatizados (nao dry-run real)

- **Contexto**: o plano de refatoracao original previa, a cada etapa, rodar
  `python main.py --dry-run` e comparar snapshots de `queue.json` e HTML dos
  4 templates contra um baseline.
- **Restricao**: o agente nao pode ler `.env` nem `config/*.env` (credenciais
  sensiveis), e a execucao real contra Soft4/SMTP exige aprovacao explicita.
- **Decisao**: confirmada com o operador. Durante a refatoracao (cada etapa),
  a **validacao de comportamento usara apenas testes automatizados**
  (`python -m compileall app tests tools` +
  `python tests/run_unittest_discovery.py`). O operador humano fica
  responsavel por rodar o dry-run real ao final de cada etapa, se desejar
  validar contra Soft4/SMTP.
- **Impacto**: acelera a refatoracao sem riscos de envio real de e-mails.
  Reduz a cobertura de validacao de "byte-a-byte" para "substrings
  validadas por testes" nos HTMLs e "estrutura do queue.json" implicita
  nos testes que constroem a fila.
- **Status**: aceito. Registrado em `VALIDATION.md` e `CONTEXT.md`.

---

## 2026-07-30 — Divergencia 1: `SOFT4_CSV_PATH` carregado mas nao usado no fetch

- **Contexto**: `app/settings.py:174` carrega a variavel `SOFT4_CSV_PATH`
  em `Soft4Settings.csv_path`. A dataclass expoe `csv_url` via
  `base_url + csv_path`. Porem `app/downloader.py:109` faz um POST literal
  para `/chamado/fila-de-atendimento/csv`, ignorando a configuracao.
- **Divergencia ja documentada**: `codex-context/02-architecture.md` linhas
  56-57 explica isso.
- **Decisao**: **Nao corrigir nesta refatoracao**. Corrigir seria alterar
  comportamento (passaria a usar `SOFT4_CSV_PATH` no fetch), o que esta
  fora do escopo da refatoracao arquitetural (que apenas reorganiza sem
  alterar comportamento).
- **Impacto**: a configuracao `SOFT4_CSV_PATH` continua carregada em
  `app/config/loader.py` apos a refatoracao (preservada), mas continua
  sem efeito pratico no fetch. E um classico pre-existente.
- **Status**: aceito como pre-existente. Fora do escopo. Registrado no
  backlog de divergencias conhecidas.

---

## 2026-07-30 — Divergencia 2: `requests` em `requirements.txt` sem uso direto

- **Contexto**: `requirements.txt` declara `requests>=2.31.0`, mas nao
  ha `import requests` nos arquivos Python do projeto (confirmado em
  `README.md:43-44` e `codex-context/06-inventory.md:60-61`).
- **Decisao**: **Nao remover `requests` nesta refatoracao**. Remocao e
  alteracao de dependencia e pode ter impacto operacional nao verificado.
- **Impacto**: `requirements.txt` permanece inalterado ao final da
  refatoracao.
- **Status**: aceito como pre-existente. Fora do escopo.

---

## 2026-07-30 — Diferenca de comportamento entre `group_by_attendant` em `email_queue` e `_build_manager_report_sections` em `mailer`

- **Contexto**: ambos agrupam linhas de CSV por atendente, mas:
  - `app/email_queue.py::_group_by_attendant` **descarta** linhas sem
    atendente (continue quando `attendant` vazio).
  - `app/mailer.py::_build_manager_report_sections` atribui
    `"Sem atendente"` como chave de agrupamento quando vazio.
- **Decisao**: **Preservar as duas regras** durante a refatoracao. A
  funcao unificada em `app/queue/grouping.py::group_by_attendant`
  exportada sera a regra que descarta vazios (equivalente ao
  email_queue). O `reports.py` do mailer continuara aplicando o
  fallback `"Sem atendente"` apos chamar `group_by_attendant` (ou
  mantendo logica local — definido na Tarefa 5).
- **Impacto**: dois comportamentos propositadamente diferentes seguem
  iguais antes/depois. Nenhuma regra de negocio alterada.
- **Status**: aceito. Registrado para protecao durante a Tarefa 5.

---

## 2026-07-30 — `DRY_RUN_NOTIFICATION_RECIPIENT` hardcoded permanece hardcoded

- **Contexto**: a constante `DRY_RUN_NOTIFICATION_RECIPIENT =
  "lucas.silva@mainhardt.com.br"` em `app/main.py:32` e uma regra de
  negocio (destinatario fixo do e-mail de confirmacao de dry-run).
- **Decisao**: **Nao mover para configuracao** nesta refatoracao.
  Migrar para `AppSettings` seria mudanca de configuracao funcional.
- **Impacto**: a constante sera movida para
  `app/orchestrator/run.py` (mesmo valor, mesmo nome) na Tarefa 7, sem
  tornar-la configuravel.
- **Status**: aceito. Fora do escopo.

---

## 2026-07-30 — Shims de compatibilidade em etapas intermediarias

- **Contexto**: para manter projeto compilando e testes verdes a cada
  etapa,Headers alguns arquivos antigos (`app/settings.py`,
  `app/cleanup.py`, `app/csv_utils.py`, `app/business_days.py`,
  `app/email_queue.py`, `app/auth.py`, `app/downloader.py`) serao
  convertidos em shims (reexportacao) em vez de deletados de imediato.
- **Decisao**: shims intermediarios sao permitidos; **todos** sao
  removidos na Tarefa 8 (limpeza). Nenhum shim deve sobreviver ao final
  da refatoracao.
- **Impacto**: o repostorio apresenta transitorio dual-path durante as
  etapas 1-7; nao deve representar aumento de complexidade permanente.
- **Status**: aceito. Registrado para governanca.

---

## 2026-07-30 — Colisao `app/mailer.py` vs `app/mailer/` (pacote)

- **Contexto**: o arquivo `app/mailer.py` (atual) tem o mesmo nome que o
  pacote `app/mailer/` (alvo). Python nao permite ambos no mesmo
  diretorio simultaneamente de forma limpa.
- **Decisao**: usar nome temporario `app/mailer_pkg/` na Tarefa 5; apos
  testes verdes, deletar `app/mailer.py` e renomear `app/mailer_pkg/`
  -> `app/mailer/`.
- **Impacto**: Tarefa 5 tem fase intermediaria explicita (criar
  `mailer_pkg` -> testar -> renomear).
- **Status**: aceito. Estrategia registrada no TODO Tarefa 5.

---

## Log de alteracoes

### 2026-07-30 — Microdecisao na Tarefa 1: `PROJECT_ROOT` movido para `app/infra/fs`

- **Contexto**: a Tarefa 1 planejava mover `setup_logging` de `app/settings.py`
  para `app/infra/logging_setup.py`, preservando `PROJECT_ROOT` em settings
  (pois `setup_logging` referencia `PROJECT_ROOT` para o caminho de logs).
  Porem, se `app/settings.py` importasse `setup_logging` de
  `app.infra.logging_setup`, e este importasse `PROJECT_ROOT` de
  `app.settings`, criaria dependencia circular.
- **Decisao**: `PROJECT_ROOT` foi movido para `app/infra/fs.py` (moduo sem
  dependencias do projeto), mantendo o MESMO valor
  (`Path(__file__).resolve().parent.parent` em `app/settings.py` ==
  `Path(__file__).resolve().parent.parent.parent` em `app/infra/fs.py` ==
  `.../frank_bot`). `app/settings.py` passou a importar e reexportar
  `PROJECT_ROOT` de `app.infra.fs` para preservar todos os imports legados
  (`from app.settings import PROJECT_ROOT`, `from app.settings import
  ConfigError, PROJECT_ROOT, load_settings` em `app/main.py`).
- **Impacto**: antecipacao parcial da Tarefa 2 (que moveria tambem
  `PROJECT_ROOT` para `app/config/loader.py`). Na Tarefa 2, `PROJECT_ROOT`
  sera reexportado por `app/config/loader` (a partir de `app.infra.fs`) e
  por `app/settings.py` (tambem a partir de `app.infra.fs`); ou seja, a
  Tarefa 2 nao remvera de mover `PROJECT_ROOT` novamente. Ajuste a ser
  registrado no PROGRESS da Tarefa 2.
- **Validacao**: `python -m compileall` e `python tests/run_unittest_discovery.py`
  passaram apos a movimentacao (12/12 OK).
- **Status**: aceito. Refletido em `app/infra/fs.py` e no shim de
  `app/settings.py`.

### 2026-07-30 — Microdecisao na Tarefa 5: `reports.py` nao usa `queue.grouping.group_by_attendant`

- **Contexto**: o plano original previa que `reports.py` (no novo pacote
  `app/mailer/`) usaria `app.queue.grouping.group_by_attendant` para
  agrupar atendentes no relatorio gerencial. Porem os dois
  agrupamentos historicos tinham comportamento **diferente**:
  - `email_queue._group_by_attendant` descarta linhas com atendente
    vazio (continue).
  - `mailer._build_manager_report_sections` atribui `"Sem atendente"`
    como chave quando vazio (preserva a linha).
- **Decisao**: `app/mailer/reports.py` **mantem o loop local** com
  fallback `"Sem atendente"` (copia fiel do `_build_manager_report_sections`
  original). **Nao** chama `queue.grouping.group_by_attendant`. Isso
  preserva exatamente o HTML e as contagens do relatorio gerencial.
- **Impacto**: o helper `group_by_attendant` em `queue.grouping`
  continua sendo usado apenas por `queue.repository` (fila de envio
  individual), como antes. A "unificacao" dos dois agrupamentos
  ficaria como backlog futuro — **fora do escopo** desta refatoracao,
  pois unifica-los exigiria escolher uma das duas regras, o que e
  alteracao de comportamento.
- **Status**: aceito. Registrado em `app/mailer/reports.py` e
  refletido tambem em `codex-context/02-architecture.md`.

### 2026-07-30 — Microdecisao na Tarefa 5: alias `_send_message` no `__init__.py` do mailer

- **Contexto**: o `mailer` original tinha a funcao local
  `_send_message` e os 4 testes de mailer fazem
  `patch("app.mailer._send_message", capture_send)`. No novo pacote,
  a funcao SMTP foi movida para `app/mailer/smtp.py` com nome publico
  `send_message` (sem underscore). Quebraria os patches.
- **Decisao**: `app/mailer/__init__.py` importa
  `from app.mailer.smtp import send_message as _send_message` e as 4
  funcoes publicas chamam `_send_message(...)`. Isso mantem o ponto
  de patch `app.mailer._send_message` funcionando identico, sem expor
  um nome publico indesejado fora do pacote.
- **Impacto**: os patches de teste continuam apontando para
  `app.mailer._send_message` (mesmo caminho apos o rename
  `mailer_pkg` -> `mailer`). Nenhum teste precisou trocar o alvo do
  patch entre a fase intermediaria e a final.
- **Status**: aceito. Implementado em `app/mailer/__init__.py`.

### 2026-07-30 — Microdecisao na Tarefa 7: logger name muda para `app.orchestrator.run` sem impacto na saida de log

- **Contexto**: o `run()` e o `_log_dry_run_plan` foram movidos de
  `app/main.py` para `app/orchestrator/run.py`, trocando o nome do
  logger de `app.main` para `app.orchestrator.run`.
- **Decisao**: aceita a mudanca de nome do logger. O formato de log
  (`%(asctime)s [%(levelname)s] %(message)s`) **nao inclui o nome do
  logger**, portanto a saida de log permanece identica antes/depois.
  `tests/test_main_and_logging.py` foi atualizado: `assertLogs` para
  `"app.orchestrator.run"` e os 15 patches movidos para
  `patch("app.orchestrator.run.<simbolo>")`.
- **Impacto**: nenhuma assertiva mudou (apenas alvos de patch); o output
  de log nao muda. `test_cli_enables_dry_run` mantem
  `patch("app.main.run", return_value=0)` pois `app/main.py` reexporta
  `run` de `app.orchestrator.run`.
- **Status**: aceito. Implementado em `app/orchestrator/run.py`.

### 2026-07-30 — Microdecisao na Tarefa 7: `sys.dont_write_bytecode` presente no entrypoint e na orquestracao

- **Contexto**: o `app/main.py` original definia `sys.dont_write_bytecode
  = True` no topo para evitar geracao de `__pycache__`. Com o
  desmembramento, a orquestracao passou a viver em
  `app/orchestrator/run.py`.
- **Decisao**: manter `sys.dont_write_bytecode = True` em
  `app/orchestrator/run.py` (ponto onde a pipeline e importada/executada
  em contexto de automacao) e tambem em `app/main.py` (entrypoint CLI).
  Duplicacao intencional e trivial, sem dependencia entre os modulos.
- **Impacto**: nenhum `__pycache__` e gerado quando o run.py e
  importado; comportamento identico ao original.
- **Status**: aceito. Implementado em `app/orchestrator/run.py:30` e
  `app/main.py:10`.


