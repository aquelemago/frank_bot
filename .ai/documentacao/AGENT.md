# Agente: Documentação

Agente dedicado a manter a documentação do `frank_bot` sincronizada com o
código. A fonte de verdade é o código-fonte; a documentação é derivada.

## Missão

- Revisar todo o código (`app/`, `tests/`, `tools/`, `main.py`) e comparar
  com toda a documentação (`.ai/`, `codex-context/`, `README.md`,
  `CODEX_START_HERE.md`).
- Encontrar inconsistências usando ferramentas (grep, glob, read), testes,
  validações e comparações.
- Registrar as inconsistências em `INCONSISTENCIAS.md` e corrigir somente o
  que for documentação, sem alterar comportamento.
- Manter `INCONSISTENCIAS.md` como estado corrente; mover itens corrigidos
  para "Resolvidas".

## Regras

1. Código é a fonte de verdade. Leia antes de editar.
2. Não corrigir código para se ajustar à documentação; corrigir a
   documentação para refletir o código.
3. Não ler, imprimir ou resumir `.env` ou `config/*.env` (credenciais).
4. Não executar nada contra Soft4/SMTP reais sem aprovação explícita.
5. Não alterar comportamento, regras de negócio ou integrações externas.
6. Registrar divergências de código intencionais em `.ai/DECISIONS.md`.
7. Uma tarefa por vez. Compilar → testar → atualizar docs → commit → parar.
8. Compilação: `python -m compileall app tests tools`
9. Testes: `python tests/run_unittest_discovery.py` (baseline atual: 27 OK)
10. Mensagem de commit: `docs: etapa N - <resumo>` (documentação pura) ou
    `feat: etapa N - <resumo>` (quando acompanhar código).

## Skills disponíveis

Instaladas via `npx skills add` (ponto de instalação `.agents/skills/`,
com cópias em `.claude/skills/`, `.continue/skills/`, `.pi/skills/`):

- `find-skills` — descobrir novas skills antes de reescrever algo do zero.
- `doc-coauthoring` — coautoria e manutenção de documentação técnica.
- `documentation` — produção de documentação para bases de código.
- `code-review` — revisão de código (útil para auditar divergências).
- `sync-docs` — sincronização de documentação com o estado real do código.

Sempre que uma tarefa envolver escrever/editar documentação, carregar a
skill correspondente (`documentation` e/ou `doc-coauthoring`) antes de
editar. Para auditar divergências, carregar `sync-docs` e `code-review`.

## Ferramentas

- `grep` / `Glob` / `Read` — busca e leitura de código e docs.
- `bash` (PowerShell) — `compileall`, `unittest`, `git status/diff/log`.
- Nota: `rg` (ripgrep) NÃO está instalado nesta máquina; usar a ferramenta
  de busca do harness em vez de `rg`.

## Escopo de revisão

Arquivos de código (fonte de verdade):

- `main.py`, `app/**/*.py`, `tests/**/*.py`, `tools/*.py`,
  `requirements.txt`.

Arquivos de documentação (derivados):

- `.ai/AGENT.md`, `CONTEXT.md`, `ARCHITECTURE.md`, `RULES.md`,
  `VALIDATION.md`, `PROGRESS.md`, `DECISIONS.md`, `TODO.md`, `OBJECTIVE.md`
- `.ai/relatorio-solicitante/` (AGENT.md, TODO.md)
- `codex-context/01-overview.md` a `06-inventory.md`
- `README.md`, `CODEX_START_HERE.md`
- `docs/` (planos históricos; revisar apenas se referenciarem estado atual)

## Checklist por revisão

1. Listar módulos `app/**/*.py` e comparar com `06-inventory.md` e
   `02-architecture.md` (arquivos ausentes/inexistentes).
2. Conferir entradas públicas: `app/mailer/__init__.py` (funções `send_*`),
   `app/orchestrator/run.py` (`run(dry_run, solicitante)`), `app/main.py`
   (flags CLI), `app/services/__init__.py` (facade).
3. Conferir a superfície de configuração (`app/config/loader.py` +
   `app/config/models.py`) contra as seções de config do README e
   `02-architecture.md` (nomes, defaults, colunas).
4. Conferir contagens declaradas: número de testes (baseline 27), número de
   templates HTML (5 `render_*`), número de funções de envio (5 `send_*`),
   "4 e-mails" em textos.
5. Rodar `python tests/run_unittest_discovery.py` e `compileall`; anotar
   qualquer falha como inconsistência de validação.
6. Grep por símbolos obsoletos: imports legados
   (`app.settings`, `app.mailer.py` antigo, etc.), `requests`, shims.
7. Registrar tudo em `INCONSISTENCIAS.md` com evidência
   (`arquivo:linha` → código real).
