# Arquitetura

## Fluxo Principal

```text
main.py
  -> app.main.main()
    -> parse de --dry-run
    -> app.main.run(dry_run)
    -> setup_logging()
    -> cleanup_runtime_residue()
    -> load_settings()
    -> Soft4Browser.ensure_authenticated()
    -> download_csv()
    -> filtrar_csv_por_dias_uteis_sem_interacao()
    -> build_attendant_email_queue()
    -> send_attendant_csv_email() para cada item
    -> send_manager_report_email()
    -> cleanup_runtime_residue()
```

## Modulos

- `main.py`: entrada publica; importa `app.main.main()` e repassa o codigo de saida.
- `app/main.py`: interpreta `--dry-run` e orquestra setup, limpeza, autenticacao, download, filtro local, fila, envio e tratamento de erros.
- `app/settings.py`: define dataclasses `Soft4Settings`, `EmailSettings`, `EmailQueueSettings`, `ManagerReportSettings` e `AppSettings`; carrega `.env`, arquivos legados, variaveis e diretorios; configura log rotativo em `logs/frank_bot.log`.
- `app/auth.py`: define `Soft4Browser` e `AuthenticatedSession`; abre Chromium persistente, autentica no Soft4, detecta login, coleta cookies, CSRF e headers.
- `app/business_days.py`: define `eh_dia_util`, `contar_dias_uteis_sem_interacao`, `chamado_deve_ser_processado`, feriados nacionais, feriados adicionais e filtro local do CSV.
- `app/downloader.py`: monta payload da fila, executa POST autenticado via `page.evaluate(fetch)`, valida conteudo e salva CSV completo.
- `app/csv_utils.py`: normaliza chaves, detecta delimitador, le CSV e resolve colunas por nome configurado/fallback.
- `app/email_queue.py`: carrega mapa de e-mails, agrupa CSV por atendente, cria arquivos por atendente e grava metadados `pending`, `sent` ou `failed`.
- `app/mailer.py`: monta e-mails HTML, anexos CSV, relatorio gerencial e envio SMTP com TLS.
- `app/cleanup.py`: remove `__pycache__` fora de `.venv` e `perfil_soft4`.

## Testes

- `tests/run_unittest_discovery.py`: wrapper para descoberta unittest.
- `tests/test_email_queue_and_mailer.py`: cobre agrupamento por atendente, destinatarios ausentes, e-mail individual, relatorio gerencial, normalizacao, contador de dias uteis, datas invalidas e feriados configuraveis.

## Dependencias Python

- `playwright>=1.44.0`
- `python-dotenv>=1.0.1`
- `requests>=2.31.0`

## Dados E Saidas

- CSV completo: `downloads/fila_atendimento_YYYYMMDD_HHMMSS.csv`.
- Fila de e-mail: `email_queue/YYYYMMDD_HHMMSS/`.
- Resumo da fila: `email_queue/YYYYMMDD_HHMMSS/queue.json`.
- Item por atendente: `<atendente>.csv` e `<atendente>.json`.

## Efeitos Colaterais

- Browser persistente grava dados em `perfil_soft4/`.
- Download remove CSVs antigos em `downloads/`.
- Criacao de fila remove filas antigas em `email_queue/`.
- Envio SMTP envia e-mail real quando nao mockado.
- Cleanup remove `__pycache__` fora de `.venv` e `perfil_soft4`.
- Auditorias de contexto podem criar `.codex-audit/` com JSON/Markdown sanitizados.

## Artefatos Runtime

- `.venv/`: ambiente local, nao documentar como fonte de verdade.
- `downloads/`: CSVs baixados, podem conter dados operacionais.
- `email_queue/`: filas e anexos gerados, podem conter dados operacionais.
- `perfil_soft4/`: perfil persistente do Chromium, cookies e sessao.
- `.codex-audit/`: resumo local de auditoria para manutencao de contexto.

## Configuracao

Arquivos sensiveis:

- `.env`
- `config/email_bot.env`
- `config/email_atendente.env`

Variaveis Soft4:

- `SOFT4_USUARIO`
- `SOFT4_SENHA`
- `SOFT4_BASE_URL`
- `SOFT4_FILA_PATH`
- `SOFT4_CSV_PATH`
- `SOFT4_TP_LISTAGEM`
- `SOFT4_DIAS_SEM_INTERACAO_ATENDENTE`
- `SOFT4_FERIADOS_ADICIONAIS`
- `SOFT4_TIMEOUT_SECONDS`
- `SOFT4_RETRIES`

Variaveis CSV/e-mail:

- `CSV_COLUNA_ATENDENTE`
- `CSV_COLUNA_ULTIMA_INTERACAO`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_USUARIO`
- `EMAIL_SENHA`
- `EMAIL_ATENDENTES_FILE`
- `EMAIL_FALHAR_SE_ATENDENTE_SEM_EMAIL`
- `EMAIL_GESTORA_RELATORIO`
- `NOME_GESTORA_RELATORIO`

Compatibilidade legada:

- `SMTP_HOST`
- `SMTP_PORT`
- `EMAIL_REMETENTE`
- `SENHA`

## Legado Removido

Arquivos removidos em migracoes anteriores:

- `src/extrair_chamados.py`
- `data/chamados.json`
- `prompt.txt`
