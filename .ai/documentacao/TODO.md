# TODO.md — Tarefas do Agente de Documentação

Única fonte de ordem do agente. Uma tarefa por vez.

## Tarefas em aberto

- [ ] Corrigir `codex-context/01-overview.md` (etapas 10-12):
  - [ ] Documentar `python main.py --solicitante` e `--dry-run` como
    entrypoints.
  - [ ] Adicionar o relatório do solicitante ao escopo (agrupamento via API
    Softdesk, relatório completo para `EMAIL_SOLICITANTE_TODOS_CHAMADOS`).
  - [ ] Adicionar regras de negócio do solicitante
    (`SOFT4_DIAS_SEM_INTERACAO_SOLICITANTE=5`,
    `CSV_COLUNA_ULTIMA_INTERACAO_SOLICITANTE`).
  - [ ] Adicionar saídas: `downloads/solicitante_*.csv`, e-mails por
    solicitante.
- [ ] Corrigir `codex-context/02-architecture.md` (etapas 10-12):
  - [ ] Main Flow com `run(dry_run, solicitante)` e `_run_requester_report`.
  - [ ] Dataclass `RequesterReportSettings`.
  - [ ] Módulos `app/soft4/api.py` e `app/requester/delivery.py`.
  - [ ] Mailer: 5 funções públicas e 5 templates.
  - [ ] Configuration Surface com as vars do solicitante e da API.
  - [ ] Side Effects (CSV do solicitante, envios por solicitante, relatório
    completo).
- [ ] Corrigir `codex-context/03-operations.md`: documentar comandos do
  relatório do solicitante e validação.
- [ ] Corrigir `codex-context/04-decisions.md`: anotar que `requests` passou
  a ser usado por `app/soft4/api.py`.
- [ ] Corrigir `codex-context/05-backlog.md`: remover/atualizar o item
  "Confirm whether `requests` is still needed" (agora importado por
  `app/soft4/api.py`).
- [ ] Corrigir `codex-context/06-inventory.md`: re-verificar snapshot na
  branch atual (`feature/envia-email-para-solicitante`), incluir
  `app/soft4/api.py`, `app/requester/*`, `tests/test_soft4_api.py`,
  `tests/test_requester_report.py`, `tests/test_requester_delivery.py`, e o
  uso direto de `requests`.
- [ ] Corrigir `.ai/VALIDATION.md`: baseline de testes 12 → 27; remover o
  grep de `from app\.mailer import` da checagem de imports (agora legítimo);
  "4 HTMLs" → 5.
- [ ] Corrigir `.ai/RULES.md`: "(12 testes)" → 27; "HTML dos 4 e-mails" → 5;
  alinhar formato de commit (`refactor:` vs `feat:`).
- [ ] Corrigir `.ai/relatorio-solicitante/AGENT.md`: "(12 existentes...)" → 27.
- [ ] Corrigir `.ai/PROGRESS.md`: adicionar linhas das etapas do feature
  (API Softdesk, relatório completo, separação de serviços) e atualizar
  "Próxima ação".
- [ ] Corrigir `.ai/DECISIONS.md`: anotar a Divergência 2 (`requests`) como
  resolvida; registrar decisões das etapas 10-12.
- [ ] Corrigir `.ai/ARCHITECTURE.md`: anotar que é plano histórico; incluir
  `app/soft4/api.py` e `app/requester/` no alvo.
- [ ] Corrigir `README.md:43-44`: remover a observação de que `requests` não
  tem import direto (agora importado).
- [ ] Corrigir `app/config/loader.py:121`: default `lcabra570@gmail.com`
  (typo) para `lcabral570@gmail.com` — validar com operador antes (código).

## Resolvidas

- Nenhuma ainda.

## Regras de validação

- A cada tarefa: `python -m compileall app tests tools` +
  `python tests/run_unittest_discovery.py` (27 OK) + `git status` limpo
  somente após commit.
- Documentação pura → commit `docs: ...`; alterar loader.py → validar com
  operador (configuração funcional).
