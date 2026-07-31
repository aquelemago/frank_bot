# TODO.md — Tarefas do Agente de Documentação

Única fonte de ordem do agente. Uma tarefa por vez.

## Tarefas em aberto

- [ ] Validar com o operador se o default de `EMAIL_SOLICITANTE_RELATORIO`
  em `app/config/loader.py:121` deve ser corrigido de `lcabra570@gmail.com`
  (typo) para `lcabral570@gmail.com` — mudança de configuração funcional;
  `.env` já define o valor correto, então o runtime não é afetado.

## Resolvidas (2026-07-31)

Sessão de documentação com a skill `documentation` (commit pendente):

- [x] `codex-context/01-overview.md`: entrypoints `--solicitante`, escopo do
  solicitante, regras de negócio e saídas.
- [x] `codex-context/02-architecture.md`: Main Flow dos dois serviços,
  dispatcher `run(dry_run, solicitante)`, módulos `app/soft4/api.py` e
  `app/requester/*`, `RequesterReportSettings`, mailer 5 funções/5 templates,
  Configuration Surface e Side Effects do solicitante.
- [x] `codex-context/03-operations.md`: comandos do solicitante, dry-run sem
  envio e falhas comuns da API Softdesk.
- [x] `codex-context/04-decisions.md`: `requests` anotado como usado; decisão
  do feature do solicitante registrada.
- [x] `codex-context/05-backlog.md`: item de `requests` resolvido removido.
- [x] `codex-context/06-inventory.md`: re-verificado na branch atual;
  arquivos do solicitante/API e observação de `requests` atualizados.
- [x] `.ai/VALIDATION.md`: baseline 27 testes, checagem de imports sem
  `app.mailer`, 5 HTMLs.
- [x] `.ai/RULES.md`: 27 testes, 5 e-mails, formato de commit
  `refactor:`/`feat:`.
- [x] `.ai/relatorio-solicitante/AGENT.md`: 12 → 27 testes.
- [x] `.ai/PROGRESS.md`: tabela do feature (etapas 1-13) e validação real da
  API.
- [x] `.ai/DECISIONS.md`: Divergencia 2 (`requests`) resolvida; decisões das
  etapas 10-13 registradas.
- [x] `.ai/ARCHITECTURE.md`: anotado como histórico; `api.py`/`requester/`
  no alvo.
- [x] `.ai/CONTEXT.md`: nota de atualização pós-snapshot.
- [x] `README.md`: observação de `requests` atualizada.

## Regras de validação

- A cada tarefa: `python -m compileall app tests tools` +
  `python tests/run_unittest_discovery.py` (27 OK) + `git status` limpo
  somente após commit.
- Documentação pura → commit `docs: ...`; alterar loader.py → validar com
  operador (configuração funcional).
