# Inventario Tecnico

Este arquivo concentra evidencias coletadas por auditoria segura. Use como indice
para manutencao; confirme no codigo antes de alterar comportamento.

## Auditoria Mais Recente

- Data: 2026-05-26 08:55:09.
- Comando:

```powershell
python C:\Users\lucas.silva\.codex\skills\project-context-auditor\scripts\audit_project_context.py .
```

- Saidas locais:
  - `.codex-audit/project-context-audit.json`
  - `.codex-audit/project-context-audit.md`
- Contagem: 24 arquivos considerados, 13 Python e 10 Markdown.
- Diretorios runtime detectados: `.codex-audit/`, `.venv/`, `downloads/`, `email_queue/`, `perfil_soft4/`.
- Arquivos sensiveis nao devem ser abertos nem resumidos: `.env`, `config/*.env`, cookies, tokens e perfil do navegador.

## Descoberta De Skills

- Skills usadas nesta organizacao: `find-skills`, `skill-installer`, `skill-creator`, `project-context-auditor` e `softdesk-docs-orientation`.
- Busca externa via `npx skills find project documentation` encontrou opcoes publicas com baixa instalacao para este caso.
- Busca externa via `npx skills find codebase audit` encontrou opcoes publicas genericas.
- Decisao: nao instalar skill externa nesta execucao; usar `project-context-auditor`, que ja e local, especifica para Python e adequada as regras de seguranca deste projeto.
- Skill local principal: `C:\Users\lucas.silva\.codex\skills\project-context-auditor`.

## Entradas Publicas

- `python main.py`: entrada publica operacional; chama `app.main.run()`.
- `app.main.run()`: orquestrador real do fluxo.
- `tests/run_unittest_discovery.py`: entrada de testes unittest.

## Modulos Python

- `main.py`: repassa codigo de saida de `app.main.run()`.
- `app/main.py`: setup de logs, limpeza, settings, autenticacao, download, filtro por dias uteis, fila, envio individual, relatorio gerencial e codigos de saida.
- `app/settings.py`: dataclasses de configuracao, leitura de `.env` e arquivos legados, criacao de diretorios runtime.
- `app/auth.py`: Playwright Chromium persistente, login, reaproveitamento de sessao, CSRF, cookies e headers.
- `app/downloader.py`: payload da fila, POST via `fetch` autenticado, validacao do CSV e remocao de CSVs antigos.
- `app/business_days.py`: dias uteis, feriados nacionais do Brasil, feriados adicionais e filtro local do CSV.
- `app/csv_utils.py`: leitura de CSV com sniffing de delimitador, normalizacao ASCII e resolucao de colunas.
- `app/email_queue.py`: carregamento de destinatarios, agrupamento por atendente, criacao de CSV/JSON por item e resumo da fila.
- `app/mailer.py`: e-mails HTML, anexos CSV, relatorio gerencial e SMTP TLS.
- `app/cleanup.py`: remocao de `__pycache__` fora de `.venv` e `perfil_soft4`.
- `app/__init__.py`: pacote Python.

## Configuracoes Referenciadas

Soft4:

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

CSV e e-mail:

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

## Dependencias

Declaradas em `requirements.txt`:

- `playwright>=1.44.0`
- `python-dotenv>=1.0.1`
- `requests>=2.31.0`

Observacao: a auditoria de 2026-05-26 nao encontrou import direto de `requests`
nos arquivos Python versionaveis. Confirmar necessidade antes de remover.

## Testes Existentes

- `tests/test_email_queue_and_mailer.py`
- Cobre agrupamento por atendente, destinatarios ausentes, e-mail individual, relatorio gerencial, normalizacao, dias uteis, datas invalidas e feriados configuraveis.

Comandos seguros:

```powershell
python -m compileall app tests
python tests/run_unittest_discovery.py
```

## Estado De Versionamento

- Em 2026-05-26, `git status --short` falhou porque esta pasta nao e um repositorio Git.
- Registre alteracoes relevantes em `05-historico.md` e mantenha backups externos quando necessario.
