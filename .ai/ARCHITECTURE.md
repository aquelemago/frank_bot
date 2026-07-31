# ARCHITECTURE.md — Arquitetura Atual e Arquitetura Alvo

> Nota: documento historico do plano de refatoracao de 10 etapas
> (concluida 2026-07-31). A arquitetura ALVO (secao 2) ja foi implementada
> e evoluiu: o feature do solicitante (etapas 1-12) adicionou
> `app/soft4/api.py` (cliente da API Softdesk) e `app/requester/delivery.py`,
> e o mailer passou a ter 5 funcoes de envio e 5 templates. Ver
> `codex-context/02-architecture.md` para o estado atual.

## 1. Arquitetura ATUAL (snapshot inicial)

### Fluxo principal

```text
main.py (raiz)
  -> app.main.main(argv)
     -> argparse --dry-run
     -> run(dry_run)
        -> setup_logging()
        -> cleanup_runtime_residue()
        try:
           load_settings()
           with Soft4Browser(settings.soft4):
              auth_session = browser.ensure_authenticated()
              try: download_csv(...)
              except SessionExpiredError:
                 auth_session = browser.ensure_authenticated()
                 download_csv(...)
           feriados = montar_feriados(...)
           filtrar_csv_por_dias_uteis_sem_interacao(...)   # grava por cima do CSV
           email_queue = build_attendant_email_queue(...)
           if dry_run:
              _log_dry_run_plan(...)
              send_dry_run_success_email(...) -> para lucas.silva@mainhardt.com.br
              return 0
           for item in email_queue.items:
              send_attendant_csv_email(...); mark_queue_item_sent(item, ...)
              ou mark_queue_item_failed(item, ...)
           try: send_manager_report_email(...)
           except: registra em failures
           if failures: raise RuntimeError
           return 0
        except ConfigError:       return 2
        except Exception:         return 1
        finally: cleanup_runtime_residue()
```

### Mapa de dependencias (imports de `app.main`)

- `app.auth.Soft4Browser`
- `app.business_days`: `filtrar_csv_por_dias_uteis_sem_interacao`,
  `montar_feriados`, `parse_feriados_adicionais`
- `app.cleanup.cleanup_runtime_residue`
- `app.downloader`: `SessionExpiredError`, `download_csv`
- `app.email_queue`: `build_attendant_email_queue`,
  `mark_queue_item_failed`, `mark_queue_item_sent`
- `app.mailer`: `send_attendant_csv_email`, `send_dry_run_success_email`,
  `send_manager_report_email`
- `app.settings`: `ConfigError`, `PROJECT_ROOT`, `load_settings`,
  `setup_logging`

Dependencias internas entre modulos:

- `app.auth` -> `app.settings.Soft4Settings`
- `app.downloader` -> `app.auth.AuthenticatedSession`,
  `app.settings.Soft4Settings`
- `app.business_days` -> `app.csv_utils`
- `app.email_queue` -> `app.csv_utils`, `app.settings.EmailQueueSettings`
- `app.mailer` -> `app.csv_utils`, `app.settings.EmailSettings`
- `app.cleanup` -> (somente stdlib)
- `app.settings` -> `python-dotenv`, `logging` (inclui `setup_logging`,
  misturado com config)

### Problemas estruturais identificados

1. **Baixa coesao em `settings.py`**: mistura modelos de config, carregamento
   de env e logging (preocupacao transversal).
2. **Baixa coesao em `mailer.py`**: mistura transporte SMTP, 4 templates HTML,
   parse de destinatarios, anexo e **leitura/agrupamento de CSV** (logica de
   dominio que pertence a fila).
3. **Baixa coesao em `email_queue.py`**: agrupa dominio (fila), I/O de
   filesystem, carga de destinatarios, sumario e marcacao de status.
4. **Baixa coesao em `business_days.py`**: calculo puro de dias uteis junto
   com escrita de CSV (filtros locais escrevem por cima do arquivo original).
5. **Codigo duplicado (`_remove_readonly`)**: em `cleanup.py:30` e
   `email_queue.py:163`.
6. **Codigo duplicado (group_by_attendant)**: conceitualmente repetido em
   `email_queue.py` e `mailer.py` (com comportamento diferente — preservar).
7. **Alto acoplamento do orquestrador**: `app.main` importa 6 modulos
   diretamente; qualquer mudanca de retorno ou assinatura propaga erro.
8. **Constante de negocio hardcoded fora de config**:
   `DRY_RUN_NOTIFICATION_RECIPIENT` em `app.main:32`.
9. **`tools/send_test_email.py`** duplica inicializacao de logging e
   `sys.path` hack.

## 2. Arquitetura ALVO

```text
frank_bot/
├── main.py                      (inalterado)
├── requirements.txt
├── README.md
├── CODEX_START_HERE.md
├── codex-context/
├── config/                      (sensiveis, inalterado)
├── docs/
│   └── refactoring-plan.md
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # apenas CLI + chamada ao orchestrator
│   │
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   └── run.py               # run() + tratamento de codigos de saida
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── models.py            # dataclasses
│   │   └── loader.py            # carga de env + helpers _env*
│   │
│   ├── infra/
│   │   ├── __init__.py
│   │   ├── logging_setup.py     # setup_logging
│   │   ├── cleanup.py           # cleanup_runtime_residue
│   │   └── fs.py                # _remove_readonly reutilizavel
│   │
│   ├── soft4/
│   │   ├── __init__.py
│   │   ├── browser.py           # Soft4Browser, login, CSRF, cookies
│   │   ├── downloader.py        # download_csv + payload + retry + validacao
│   │   └── api.py               # cliente da API Softdesk (etapa 10 do feature)
│   │
│   ├── requester/
│   │   ├── __init__.py
│   │   └── delivery.py          # build_requester_deliveries (etapas do feature)
│   │
│   ├── csv/
│   │   ├── __init__.py
│   │   ├── io.py                # read_csv_rows, resolve_column, normalize_key
│   │   └── filter.py            # dias uteis, feriados, filtrar_csv_*
│   │
│   ├── queue/
│   │   ├── __init__.py
│   │   ├── repository.py        # build_attendant_email_queue, escrita CSV/JSON
│   │   ├── attendant_emails.py  # load_attendant_emails
│   │   └── grouping.py          # group_by_attendant (reusada pelo mailer)
│   │
│   ├── mailer/
│   │   ├── __init__.py
│   │   ├── smtp.py              # _send_message, _parse_recipients, _build_attachment
│   │   ├── templates.py         # 4 corpos HTML (funcoes render puras)
│   │   └── reports.py           # _build_manager_report_sections (usa queue.grouping)
│   │
│   └── services/
│       └── __init__.py          # facade: send_*, mark_queue_item_*
│
├── tools/
│   └── send_test_email.py
└── tests/
    ├── run_unittest_discovery.py
    ├── test_csv_filter.py
    ├── test_email_queue.py
    ├── test_mailer.py
    └── test_main_run.py
```

### Justificativa resumida

- `infra/`: isola preocupacoes transversais (logging, cleanup, fs) e elimina
  a duplicacao de `_remove_readonly`.
- `config/`: separa modelos (o que e configuracao) de loader (como carregar).
- `csv/`: separa I/O de CSV da regra de dias uteis.
- `queue/`: separa dominio de fila de I/O de e-mail; expoe agrupamento
  reutilizavel.
- `mailer/`: separa transporte SMTP, templates HTML e relatorio (que usa
  `queue.grouping`). Sem HTML inline misturado com MIME.
- `soft4/`: isola dependencia externa (Playwright e endpoints Soft4).
- `orchestrator/`: separa fluxo de CLI; reduz acoplamento do ponto central.
- `services/`: facade para o orquestrador importar poucos simbolos.

### Visao de dependencias alvo

- `app.main` -> `app.orchestrator.run.run`
- `app.orchestrator.run` -> `app.services`, `app.infra.logging_setup`,
  `app.infra.cleanup`, `app.config.loader`, `app.soft4.browser`,
  `app.soft4.downloader`, `app.csv.filter`, `app.queue.repository`
- `app.services` -> `app.mailer`, `app.queue.repository`
- `app.mailer.reports` -> `app.queue.grouping`, `app.csv.io`
- `app.queue.repository` -> `app.queue.grouping`,
  `app.queue.attendant_emails`, `app.csv.io`, `app.config.models`,
  `app.infra.fs`
- `app.config.loader` -> `app.config.models`, `app.infra.logging_setup`
  (mantem efeito colateral de criar diretorios; logica preservada)

## 3. Inalterados

- Comportamento funcional.
- Codigos de saida (0/1/2).
- Templates HTML dos 4 e-mails (entidades, estilo, conteudo).
- Payload Soft4 (listas magicas) — fora do escopo.
- `requests` em `requirements.txt` — fora do escopo.
- `SOFT4_CSV_PATH` carregado mas nao usado no fetch — divergencia
  preservada (registrada em DECISIONS.md).

## 4. Ordem de execucao

A ordem completa esta em `docs/refactoring-plan.md` e em `TODO.md`.
Resumo:

1. `infra/` (logging + cleanup + fs)
2. `config/` (quebra de settings.py)
3. `csv/` (io + filter)
4. `queue/` (repository + attendant_emails + grouping)
5. `mailer/` (smtp + templates + reports)
6. `soft4/` (browser + downloader)
7. `orchestrator/` (isolamento de run)
8. `services/` (facade) + limpeza de shims
9. Reorganizacao de testes por tema (opcional)
10. Atualizacao de documentacao
