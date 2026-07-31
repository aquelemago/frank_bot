# INCONSISTENCIAS.md — Código (fonte de verdade) vs Documentação

Revisão realizada em 2026-07-31 pelo Agente de Documentação, após as etapas
10-12 do feature `feature/envia-email-para-solicitante` (API Softdesk,
relatório completo, separação dos serviços).

Convenções: evidência = `documento:linha` → `código real`.

## A. Requests agora é usado diretamente

1. `codex-context/05-backlog.md:7-8` — "Confirm whether `requests` is still
   needed; the current project files do not import it directly."
   → `app/soft4/api.py:7` faz `import requests` (e os testes mockam
   `app.soft4.api.requests.get` em `tests/test_soft4_api.py`). Item de
   backlog resolvido; deve ser removido/atualizado.
2. `codex-context/06-inventory.md:80-81` — "no direct `requests` import was
   found in the current Python project files during documentation review."
   → Falso desde a etapa 10; import direto existe.
3. `codex-context/04-decisions.md:70` — "requests still declared without
   direct use" → desatualizado; anotar como resolvido.
4. `.ai/DECISIONS.md:50-59` — "Divergencia 2: requests em requirements.txt
   sem uso direto" → desatualizada; `requests` agora tem uso direto
   (`app/soft4/api.py:7`). Anotar como resolvida.
5. `.ai/CONTEXT.md:23` e `:102` — "requests ... sem uso direto" → snapshot
   inicial (congelado), mas a afirmação factual mudou; anotar.
6. `README.md:43-44` — "Observacao: requests esta declarado, mas o codigo
   atual nao possui import direto dele. Confirme impacto operacional antes
   de remover." → desatualizada; remover a observação (requests agora é
   usado pela API Softdesk).

## B. Contagem de testes (baseline 12 → 27)

7. `.ai/VALIDATION.md:36-38` — "Quantidade de testes esperada (baseline
   2026-07-30): 12 testes" + "Etapa 9 ... o numero total permanece 12."
   → Suíte atual: **27 testes OK**
   (`tests/run_unittest_discovery.py`, 2026-07-31). Etapa 9 foi concluída e
   os testes cresceram nas etapas 10-12.
8. `.ai/RULES.md:83` — "(12 testes)" nos critérios de conclusão → 27.
9. `.ai/relatorio-solicitante/AGENT.md:8` — "(12 existentes devem continuar
   verdes)" → 27.
10. `.ai/PROGRESS.md:8` — "Testes baseline: 12 OK" (snapshot inicial);
    histórico OK, mas faltam as etapas 10-12 do feature.
11. `.ai/CONTEXT.md:119` — "12 testes, todos OK" → snapshot inicial
    congelado; anotar que o número evoluiu.

## C. Templates HTML e funções de envio (4 → 5)

12. `.ai/VALIDATION.md:56-57,65` — "os 4 HTMLs gerados pelo mailer" / "os 4
    HTMLs via um script" → `app/mailer/templates.py` tem **5** funções
    `render_*` (adicionada `render_requester_report_email`, linha 98).
13. `.ai/RULES.md:19` — "HTML dos 4 e-mails" → 5 e-mails.
14. `codex-context/02-architecture.md:84-85` — "The four public send
    functions live in app/mailer/__init__.py" → **5** funções
    (`app/mailer/__init__.py:31,68,92,121,165`; adicionada
    `send_requester_report_email`).
15. `codex-context/02-architecture.md:88-90` — templates listam "attendant,
    test, dry-run, and manager-report e-mails" → falta o requester.

## D. Orquestração: dispatcher de dois serviços

16. `codex-context/02-architecture.md:9` — `app.main.run -> app.orchestrator.run.run(dry_run)`
    → assinatura real `run(dry_run=False, solicitante=False)`
    (`app/orchestrator/run.py:144`).
17. `codex-context/02-architecture.md:28` — "app/orchestrator/run.py: full
    automation flow (`run()`)" → agora é dispatcher:
    `_run_attendant_report` (:152), `_run_requester_report` (:259) e
    `_dispatch_requester_reports` (:52).
18. `codex-context/02-architecture.md:3-19` (Main Flow) — só o fluxo do
    atendente; falta o fluxo do solicitante (download `solicitante_*.csv`,
    filtro, API, envios por solicitante + relatório completo).
19. `codex-context/01-overview.md:15-24` (Public Entrypoints) — falta
    `python main.py --solicitante` e `--solicitante --dry-run`
    (`app/main.py:23-28`).

## E. Novos módulos ausentes nas docs

20. `codex-context/06-inventory.md:19-51` (file list) — faltam
    `app/soft4/api.py`, `app/requester/__init__.py`,
    `app/requester/delivery.py`, `tests/test_soft4_api.py`,
    `tests/test_requester_report.py`, `tests/test_requester_delivery.py`.
21. `codex-context/06-inventory.md:5-7` — snapshot "re-verified 2026-07-31
    after the 10-step architecture refactor ... branch
    feature/refatora-arquitetura" → branch atual
    `feature/envia-email-para-solicitante`; faltam as etapas 10-12.
22. `codex-context/02-architecture.md:21-102` (Modules) — faltam os módulos
    `app/soft4/api.py` (client Softdesk) e `app/requester/delivery.py`.
23. `codex-context/02-architecture.md:44-45` (dataclasses) — falta
    `RequesterReportSettings` (`app/config/models.py`).

## F. Superfície de configuração incompleta

24. `codex-context/02-architecture.md:116-149` (Configuration Surface) —
    faltam as variáveis carregadas por `app/config/loader.py`:
    `SOFTDESK_API_KEY` (:95), `SOFT4_API_PATH` (:96),
    `CSV_COLUNA_ULTIMA_INTERACAO_SOLICITANTE` (:123),
    `SOFT4_TP_LISTAGEM_SOLICITANTE` e `SOFT4_DIAS_SEM_INTERACAO_SOLICITANTE`
    (modelos `RequesterReportSettings`), `CSV_COLUNA_ID_CHAMADO` (:124),
    `EMAIL_SOLICITANTE_RELATORIO` (:121), `NOME_SOLICITANTE_RELATORIO`
    (:122), `EMAIL_SOLICITANTE_TODOS_CHAMADOS` (:125).
25. `README.md` (bloco env) já cobre as vars; `02-architecture.md` e
    `01-overview.md` não.
26. `codex-context/02-architecture.md:151-164` (Side Effects) — faltam: CSV
    do solicitante (`downloads/solicitante_*.csv`), envios SMTP por
    solicitante e relatório completo para `EMAIL_SOLICITANTE_TODOS_CHAMADOS`.

## G. Docs operacionais sem o novo serviço

27. `codex-context/03-operations.md` — nenhuma menção a `--solicitante`,
    dry-run do solicitante ou `SOFTDESK_API_KEY` (grep vazio).
28. `codex-context/01-overview.md` (Purpose/Scope/Outputs) — descreve apenas
    o fluxo do atendente; faltam as saídas
    `downloads/solicitante_YYYYMMDD_HHMMSS.csv` e os e-mails por
    solicitante.

## H. Validação: comando de grep de imports legados (quebrado)

29. `.ai/VALIDATION.md:47-48` — o grep inclui `from app\.mailer import` com
    a instrução "Deve retornar VAZIO apos Etapa 8". `app/mailer/` agora é um
    pacote e `from app.mailer import ...` é **legítimo** (usado por
    `app/services/__init__.py` e testes). O comando, como escrito, gera
    falso positivo na árvore atual; remover o trecho `app.mailer`.

## I. Commits e formato de mensagem

30. `.ai/RULES.md:47-48` — formato exigido `refactor: etapa N - <resumo>`,
    mas o feature atual usa `feat: etapa N - <resumo>` (histórico
    `46b809c`, `c5a1abe`, `6dc9cce`). Alinhar.

## J. Defaults divergentes (código vs docs) — requer operador

31. `app/config/loader.py:121` — default de `EMAIL_SOLICITANTE_RELATORIO` é
    `lcabra570@gmail.com` (typo), enquanto `README.md:74` documenta
    `lcabral570@gmail.com`. `.env` define explicitamente
    `lcabral570@gmail.com`, então o runtime está correto; corrigir o default
    do loader é mudança de configuração funcional → validar com o operador.

## K. Planos históricos (revisar só se citarem o estado atual)

32. `.ai/ARCHITECTURE.md` — "Arquitetura ALVO" (seção 2) não inclui
    `app/soft4/api.py` nem `app/requester/`; menciona `smtp.py: _send_message`
    (real: `send_message`, decisão da Tarefa 5) e "4 corpos HTML"
    (real: 5). Documento de plano do refactor → anotar como histórico.
33. `docs/refactoring-plan.md:136` — "requests nao e removido" (plano do
    refactor) → manter; histórico.
34. `.ai/relatorio-solicitante/TODO.md` — reflete o plano das etapas 1-9 do
    feature; as etapas 10-12 (API, relatório completo, separação) foram além.
    Atualizar o checklist pendente.

## Estado do código (fonte de verdade confirmada)

- `app/orchestrator/run.py:144` `run(dry_run=False, solicitante=False)`;
  `_run_attendant_report`/`_run_requester_report`/`_dispatch_requester_reports`.
- `app/soft4/api.py:7` `import requests`; `fetch_solicitante_email`,
  `fetch_solicitante_emails`, `SoftdeskApiError`.
- `app/requester/delivery.py` `build_requester_deliveries`,
  `RequesterReportDelivery`, `RequesterDeliveryError`.
- `app/mailer/__init__.py` 5 funções `send_*`; `app/mailer/templates.py`
  5 funções `render_*`.
- `app/config/models.py` inclui `RequesterReportSettings` com
  `full_report_recipient`; `app/config/loader.py` carrega a superfície das
  vars do solicitante/API.
- `app/main.py:23-28` flag `--solicitante` → `run(dry_run, solicitante)`.
- Testes: **27 OK**; `python -m compileall app tests tools` OK.
