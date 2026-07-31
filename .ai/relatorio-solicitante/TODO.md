# Relatório de Chamados Sem Interação do Solicitante

Ordem obrigatória. 1 tarefa = ler código → editar → compileall → testes → commit → próximo.

---

## 1. `app/config/models.py` — Adicionar dataclasses

- Adicionar em `Soft4Settings`: `requester_listing_type: str`, `no_interaction_requester_days: int`
- Novo: `RequesterReportSettings` com `recipient`, `name`, `last_interaction_column`
- Adicionar em `AppSettings`: `requester_report: RequesterReportSettings`, `requester_downloads_dir: Path`

## 2. `app/config/loader.py` — Carregar env vars

5 novas: `SOFT4_TP_LISTAGEM_SOLICITANTE` (default `SEM_INTERACAO_SOLICITANTE`), `SOFT4_DIAS_SEM_INTERACAO_SOLICITANTE` (default `5`), `EMAIL_SOLICITANTE_RELATORIO` (required, default `lcabra570@gmail.com`), `NOME_SOLICITANTE_RELATORIO` (default `Teste`), `CSV_COLUNA_ULTIMA_INTERACAO_SOLICITANTE` (default `ultima interacao solicitante`).

## 3. `app/soft4/downloader.py` — Função parametrizada

Criar `download_csv_as(settings, session, downloads_dir, listing_type, no_interaction_days, prefix)`:
- Refatorar `_build_queue_payload` para aceitar parâmetros opcionais
- Cleanup seletivo por prefixo (ex: `solicitante_*.csv`)
- Salva como `{prefix}_YYYYMMDD_HHMMSS.csv`

## 4. `app/mailer/templates.py` — Template HTML

Adicionar `render_requester_report_email()`. Mesmo estilo visual. Texto adaptado para solicitante.

## 5. `app/mailer/__init__.py` — Função de envio

Adicionar `send_requester_report_email()` seguindo padrão de `send_manager_report_email()`. Adicionar em `__all__`.

## 6. `app/services/__init__.py` — Facade

Reexportar `send_requester_report_email`. Adicionar em `__all__`.

## 7. `app/orchestrator/run.py` — Orquestração

- Importar `download_csv_as` e `send_requester_report_email`
- Dentro do `with Soft4Browser`: segundo download com `prefix="solicitante"`
- Após filtro do atendente: filtrar CSV de solicitante com coluna `last_interaction_column`
- Em dry-run: log simulado do relatório de solicitante
- Após `send_manager_report_email`: chamar `send_requester_report_email` com tratamento de erro

## 8. `tests/test_requester_report.py` — Testes

Testar template HTML e função de envio (com `patch("app.mailer._send_message")` seguindo padrão dos testes existentes).

## 9. Documentação

Atualizar `README.md` com as novas env vars. Atualizar `CODEX_START_HERE.md` se necessário.