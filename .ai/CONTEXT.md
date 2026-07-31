# CONTEXT.md — Contexto Tecnico do Projeto (Snapshot Inicial)

> Snapshot capturado em 2026-07-30, no inicio da refatoracao. O codigo e a
> fonte de verdade; este documento apenas congela o estado inicial para
> referencia.

## Identificacao do projeto

- Nome: `frank_bot`
- Finalidade: Automacao Soft4/Mainhardt que baixa o CSV de chamados sem
  interacao do atendente, filtra por dias uteis, separa por atendente e envia
  e-mails via SMTP.
- Branch de refatoracao: `feature/refatora-arquitetura`
- Commit base: `40677f2 Reorganiza documentacao tecnica`

## Stack

- Linguagem: Python 3.11+ (recurso de anotacoes `from __future__` amplamente
  usado; `tuple[...]`, `str | None` em use).
- Dependencias declaradas (`requirements.txt`):
  - `playwright>=1.44.0`
  - `python-dotenv>=1.0.1`
  - `requests>=2.31.0` (declarado, mas **sem uso direto** confirmado pela
    documentacao; preservar ate verificacao operacional — fora do escopo desta
    refatoracao).
- Plataforma: Windows + PowerShell.
- Sem framework web; aplicacao CLI de automacao.

## Estrutura de diretorios (inicial)

```text
frank_bot/
├── .gitignore
├── CODEX_START_HERE.md
├── README.md
├── main.py                      # entrypoint raiz
├── requirements.txt
├── skills-lock.json
├── .agents/
│   └── skills/find-skills/SKILL.md
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── business_days.py
│   ├── cleanup.py
│   ├── csv_utils.py
│   ├── downloader.py
│   ├── email_queue.py
│   ├── main.py
│   ├── mailer.py
│   └── settings.py
├── codex-context/
│   └── (01-overview ... 06-inventory)
├── config/
│   ├── email_atendente.env
│   └── email_bot.env
├── docs/
│   └── superpowers/specs/...
├── tests/
│   ├── run_unittest_discovery.py
│   ├── test_email_queue_and_mailer.py
│   └── test_main_and_logging.py
└── tools/
    └── send_test_email.py
```

## Modulos Python na estrutura inicial

| Arquivo | Linhas | Responsabilidades atuais |
|---|---|---|
| `app/main.py` | 176 | CLI (`main`), orquestracao (`run`), log de plano dry-run, tratamento de erros e codigos de saida 0/1/2. Hardcoded `DRY_RUN_NOTIFICATION_RECIPIENT`. |
| `app/settings.py` | 219 | Dataclasses de config + `PROJECT_ROOT` + `ConfigError` + helpers `_env*` + `load_settings` + `load_email_settings` + `setup_logging` (logging misturado com config). Efeito colateral: cria `downloads/`, `email_queue/`, `perfil_soft4/`. |
| `app/auth.py` | 174 | `Soft4Browser` (Playwright), `AuthenticatedSession`, login, deteccao de tela de login, CSRF, cookies, headers. |
| `app/downloader.py` | 173 | `download_csv`, payload Soft4 hardcoded (lists magicas), retry, validacao, limpeza de CSVs antigos. Excecoes `CsvDownloadError`, `SessionExpiredError`. |
| `app/business_days.py` | 279 | Feriados nacionais (Pascoa via Gauss), parse de feriados adicionais, contagem de dias uteis, **filtro do CSV + escrita do CSV** no mesmo modulo. |
| `app/csv_utils.py` | 58 | `normalize_key`, `read_csv_rows`, `resolve_column`, `CsvReadError`, `_cell_has_content`. |
| `app/email_queue.py` | 258 | `EmailQueueItem`, `EmailQueue`, `EmailQueueError`, `build_attendant_email_queue`, marcacao de status, `load_attendant_emails`, `slugify`, `_group_by_attendant`, escrita de CSV/JSON, sumario. Duplica `_remove_readonly`. |
| `app/mailer.py` | 354 | 4 funcoes de envio publicas + 4 templates HTML + `_send_message`, `_parse_recipients`, `_build_attachment`, **leitura do CSV e agrupamento por atendente** (`_build_manager_report_sections` e auxiliares). |
| `app/cleanup.py` | 35 | `cleanup_runtime_residue`, `_remove_pycache`, `_remove_readonly` (duplicado de email_queue). |
| `tools/send_test_email.py` | 53 | Script CLI de teste SMTP; insere `PROJECT_ROOT` em `sys.path` manualmente. |

## Duplicacoes identificadas

- `_remove_readonly(function, path, exc_info)` aparece em `app/cleanup.py:30`
  e em `app/email_queue.py:163` (implementacao identica).
- Logica de agrupamento por atendente (`group_by_attendant`): existe em
  `app/email_queue.py` (`_group_by_attendant`) e re-implementada em
  `app/mailer.py` (`_build_manager_report_sections` com comportamento
  ligeiramente diferente — usa `"Sem atendente"` como fallback; preservar
  esta diferenca).

## Divergencias documentacao vs codigo (registrar em DECISIONS.md)

1. **`SOFT4_CSV_PATH` carregado mas nao usado no fetch**.
   `app/settings.py:174` carrega `SOFT4_CSV_PATH` em `Soft4Settings.csv_path`
   e a dataclass expoe `csv_url`, porem `app/downloader.py:109` faz o POST
   literal para `/chamado/fila-de-atendimento/csv`. Divergencia ja
   documentada em `codex-context/02-architecture.md` linhas 56-57.
   **Tratamento**: nao corrigir nesta refatoracao (seria mudanca de
   comportamento). Apenas preservar o carregamento em `config/loader.py`.

2. **`requests` em `requirements.txt` sem import direto**.
   Ja alertado em `README.md:43-44` e `codex-context/06-inventory.md:60-61`.
   **Tratamento**: preservar a dependencia no `requirements.txt`. Fora do
   escopo.

## Testes (snapshot inicial)

Comando:

```powershell
python tests/run_unittest_discovery.py
# ou
python -m unittest discover -s tests -p "test_*.py" -v
```

Resultado do baseline (2026-07-30):

- **12 testes, todos OK**.
- `test_main_and_logging.py`: 3 testes (CLI dry-run, dry-run sem envio,
  setup_logging rotativo).
- `test_email_queue_and_mailer.py`: 9 testes.

Parallelismos de mock relevantes para futuras mudancas:

- `test_main_and_logging.py` faz `patch("app.main.run")` no CLI.
- `test_dry_run_builds_queue_without_sending_email` faz
  `patch("app.main.<simbolo>")` para **15 simbolos** (`setup_logging`,
  `cleanup_runtime_residue`, `load_settings`, `Soft4Browser`, `download_csv`,
  `montar_feriados`, `parse_feriados_adicionais`,
  `filtrar_csv_por_dias_uteis_sem_interacao`, `build_attendant_email_queue`,
  `send_attendant_csv_email`, `send_manager_report_email`,
  `send_dry_run_success_email`, `mark_queue_item_sent`,
  `mark_queue_item_failed`, `datetime`).
- Testes do mailer fazem `patch("app.mailer._send_message", ...)`.

## Configuracao

- Variaveis obrigatorias: `SOFT4_USUARIO`, `SOFT4_SENHA`, `EMAIL_USUARIO`
  (ou `EMAIL_REMETENTE`), `EMAIL_SENHA` (ou `SENHA`).
- Defaults relevantes: `SOFT4_DIAS_SEM_INTERACAO_ATENDENTE=3`,
  `EMAIL_FALHAR_SE_ATENDENTE_SEM_EMAIL=true`, dry-run envia confirmacao
  apenas para `lucas.silva@mainhardt.com.br`.

## Artefatos gerados em runtime (nao versionar)

- `downloads/`, `email_queue/`, `logs/`, `perfil_soft4/`, `__pycache__/`,
  `.venv/`, `.codex-audit/`, `.agents/` ja no `.gitignore`.

## Decisao sobre validacao

Confirmado com o operador: a **validacao de comportamento durante a
refatoracao** (cada etapa) usara apenas testes automatizados
(`python -m compileall app tests tools` + `python tests/run_unittest_discovery.py`).
O operador (humano) fica responsavel por rodar o `python main.py --dry-run`
real (que exige credenciais `.env`) ao final de cada etapa, se desejar
confirmar contra Soft4/SMTP.
