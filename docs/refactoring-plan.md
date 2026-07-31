# Plano de Refatoracao Arquitetural — frank_bot

> Documento de referencia oficial para a execucao da refatoracao. A
> rastraabilidade operacional fica em `.ai/TODO.md` (tarefas numeradas) e
> `.ai/PROGRESS.md` (estado corrente). Em caso de divergencia, o agente
> segue o `.ai/TODO.md` e registra a divergencia em `.ai/DECISIONS.md`.

## Sumario

Reorganizacao arquitetural incremental de um projeto Python de automacao
Soft4/SMTP, preservando integralmente o comportamento funcional. Sem
novas funcionalidades, sem mudanca de regras de negocio, sem alteracao
de integracoes.

## Arquitetura atual (snapshot)

Ver `.ai/ARCHITECTURE.md` secao 1 e `.ai/CONTEXT.md`.

Problemas chave:

1. `app/settings.py` mistura configuracao, env e logging.
2. `app/mailer.py` mistura transporte SMTP, templates HTML e leitura de
   CSV por atendente.
3. `app/email_queue.py` mistura dominio, I/O de arquivos e carga de
   destinatarios.
4. `app/business_days.py` mistura calculo puro de dias uteis com
   escrita de CSV.
5. Duplicacao de `_remove_readonly` em `app/cleanup.py` e
   `app/email_queue.py`.
6. Duplicacao conceitual de agrupamento por atendente em `email_queue`
   e `mailer` (com comportamento intencionalmente diferente — ver
   `.ai/DECISIONS.md`).
7. Alto acoplamento do orquestrador `app/main.py`.

## Arquitetura alvo

```text
frank_bot/
├── main.py
├── requirements.txt
├── README.md
├── CODEX_START_HERE.md
├── codex-context/
├── config/
├── docs/
│   └── refactoring-plan.md   (este arquivo)
│   └── .ai/
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # CLI leve
│   │
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   └── run.py               # run() + codigos de saida
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── loader.py
│   │
│   ├── infra/
│   │   ├── __init__.py
│   │   ├── logging_setup.py
│   │   ├── cleanup.py
│   │   └── fs.py
│   │
│   ├── soft4/
│   │   ├── __init__.py
│   │   ├── browser.py
│   │   └── downloader.py
│   │
│   ├── csv/
│   │   ├── __init__.py
│   │   ├── io.py
│   │   └── filter.py
│   │
│   ├── queue/
│   │   ├── __init__.py
│   │   ├── grouping.py
│   │   ├── attendant_emails.py
│   │   └── repository.py
│   │
│   ├── mailer/
│   │   ├── __init__.py
│   │   ├── smtp.py
│   │   ├── templates.py
│   │   └── reports.py
│   │
│   └── services/
│       └── __init__.py
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

## Estrategia

- Refatoracao incremental. Cada etapa deixa a aplicacao funcional.
- Shims de compatibilidade intermediarios sao permitidos; todos sao
  removidos na Tarefa 8.
- Cada tarefa = 1 commit.
- Validacao por testes automatizados (`compileall` + `unittest`).
  Dry-run real e responsabilidade do operador.

## Etapas (1:1 com `.ai/TODO.md`)

1. **`app/infra/`** — logging + cleanup + fs. Elimina duplicacao de
   `_remove_readonly`.
2. **`app/config/`** — quebra `settings.py` em `models.py` + `loader.py`.
3. **`app/csv/`** — `io.py` + `filter.py` (movimentacao pura).
4. **`app/queue/`** — `grouping.py` + `attendant_emails.py` +
   `repository.py`. Expoe agrupamento reutilizavel.
5. **`app/mailer/`** — `smtp.py` + `templates.py` + `reports.py`.
   Templates viram funcoes `render_*` puras; `reports.py` usa
   `queue.grouping` preservando o fallback `"Sem atendente"`.
6. **`app/soft4/`** — `browser.py` + `downloader.py` (isola integracao
   externa).
7. **`app/orchestrator/`** — isola `run` da CLI.
8. **`app/services/`** facade + limpeza de todos os shims.
9. **Reorganizacao dos testes por tema** (opcional, baixo risco).
10. **Sincronizacao da documentacao tecnica**.

## Inalterados

- Comportamento funcional.
- Codigos de saida `0/1/2`.
- Payload Soft4 (listas magicas) — fora do escopo.
- Templates HTML dos 4 e-mails.
- `requirements.txt` (`requests` nao e removido).
- `SOFT4_CSV_PATH` carregado mas nao usado (divergencia preservada —
  ver `DECISIONS.md`).
- `DRY_RUN_NOTIFICATION_RECIPIENT` continua hardcoded (apenas muda de
  arquivo na Tarefa 7).

## Riscos gerais

- Imports quebrados em runtime (mitigados por `compileall` por etapa).
- Patches de teste desatualizados (Tarefa 7 e reescrita coordenada de
  todos os `patch("app.main.X")`).
- HTML de templates so validado por substrings (Tarefa 5 — repina
  entidades `&aacute;` etc.).
- Efeito colateral de `load_settings` (criar diretorios) preservado.

## Criterio de conclusao da refatoracao

- Todas as 10 tarefas concluidas.
- `python -m compileall app tests tools` sem erros.
- `python tests/run_unittest_discovery.py` 12 OK.
- `README.md`, `CODEX_START_HERE.md`, `codex-context/02-architecture.md`,
  `codex-context/06-inventory.md` sincronizados.
- Nenhum shim remanescente.
- Aplicacao com mesmo comportamento funcional do inicio.
