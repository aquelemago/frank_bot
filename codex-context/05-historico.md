# Historico

## 2026-05-07

- Analise inicial do projeto.
- Ponto de entrada antigo: `main.py`.
- Logica antiga: `src/extrair_chamados.py`.
- Saida antiga: `data/chamados.json`.
- Configuracoes sensiveis em `config/*.env`.
- Nao havia repositorio Git inicializado na pasta.

## 2026-05-21 - Migracao Para CSV

- Projeto migrado para exportacao CSV via POST autenticado.
- Adicionada arquitetura modular em `app/`.
- Adicionada autenticacao Playwright headless com perfil persistente.
- Adicionado download CSV via `fetch` autenticado na pagina.
- Adicionada fila de e-mails por atendente.
- Adicionado envio SMTP Office365 com anexo.
- Adicionado relatorio gerencial consolidado para a gestora.
- Adicionada limpeza de caches Python locais.
- Removido fluxo antigo de JSON/tabela.

Arquivos removidos:

- `src/extrair_chamados.py`
- `data/chamados.json`
- `prompt.txt`

## 2026-05-21 - Documentacao Para IA

- `README.md` expandido como guia humano e operacional.
- `CODEX_START_HERE.md` criado como ponto de entrada curto para agentes.
- `codex-context/` criado como memoria tecnica por topico.
- Criada a skill local `softdesk-docs-orientation`.

## 2026-05-21 - Validacao Oficial Da Skill

- Python ativo identificado como `3.14.5`.
- `PyYAML 6.0.3` instalado via `python -m pip install PyYAML`.
- Validador oficial executado em `~/.codex/skills/softdesk-docs-orientation`.
- Resultado: `Skill is valid!`.
- Validacoes: `compileall`, `unittest` e auditoria `softdesk-python-qa` com sucesso.

## 2026-05-25 - Texto Do E-mail Individual

- Atualizado o corpo do e-mail individual enviado ao atendente em `app/mailer.py`.
- Mensagem passou a pedir revisao prioritaria dos chamados listados.
- Adicionado teste unitario para validar o template HTML sem SMTP real.
- Validacoes: `compileall` com sucesso; `unittest` com 4 testes OK.

## 2026-05-25 - Unificacao Da Documentacao

- `CODEX_START_HERE.md` e `codex-context/` foram substituidos por `codex-context.md`.
- `README.md` permaneceu como guia humano e operacional.
- O contexto tecnico, protocolo para IA, backlog e historico foram consolidados em um arquivo unico.

## 2026-05-26 - Dias Uteis Sem Interacao

- Adicionado `app/business_days.py` para calcular dias uteis, feriados nacionais do Brasil e feriados adicionais.
- O CSV baixado passa a ser filtrado localmente antes da fila de e-mails e do relatorio gerencial.
- Novas configuracoes: `CSV_COLUNA_ULTIMA_INTERACAO` e `SOFT4_FERIADOS_ADICIONAIS`.
- Quando nao ha coluna de ultima interacao, a automacao usa `Dias sem interacao` como fallback para inferir a data.
- Adicionados testes unitarios para os exemplos de sexta para terca/quarta, datas invalidas e feriados configuraveis.

## 2026-05-26 - Reorganizacao Da Pasta De Contexto

- Restaurado `CODEX_START_HERE.md` como ponto de entrada curto para agentes.
- Recriada a pasta `codex-context/` com arquivos separados por projeto, arquitetura, runbook, backlog e historico.
- Mantido `codex-context.md` como ponte de compatibilidade para a nova estrutura.

## 2026-05-26 - Skill De Auditoria De Contexto

- Usadas as skills `find-skills`, `skill-installer` e `skill-creator` para avaliar e criar apoio de documentacao.
- Busca por skills de documentacao encontrou opcoes publicas, mas o projeto ja tinha `documentation-writer` e `softdesk-docs-orientation` locais.
- Criada a skill local `project-context-auditor` em `C:\Users\lucas.silva\.codex\skills\project-context-auditor`.
- A skill adiciona o script `scripts/audit_project_context.py`, que coleta inventario seguro sem abrir `.env` ou `config/*.env`.
- Auditoria executada gerou `.codex-audit/project-context-audit.json` e `.codex-audit/project-context-audit.md`.
- `codex-context/` foi enriquecido com inventario de modulos, testes, dependencias, runtime artifacts e workflow de auditoria.

## 2026-05-26 - Inventario Tecnico Detalhado

- Executada nova auditoria segura com `project-context-auditor`.
- Buscas externas por skills de documentacao e auditoria foram avaliadas, mas nenhuma skill externa foi instalada por ser menos especifica que a skill local existente.
- Adicionado `codex-context/06-inventario.md` como indice detalhado de auditoria, modulos, configuracoes, dependencias, testes e estado de versionamento.
- `README.md`, `CODEX_START_HERE.md`, `codex-context.md` e `codex-context/README.md` foram atualizados para apontar para o novo inventario.
- Registrado que a pasta atual nao esta inicializada como repositorio Git.

## 2026-05-26 - Ordem Clara Da Documentacao

- `CODEX_START_HERE.md` foi definido como ponto de entrada unico para agentes de IA.
- `codex-context/README.md` passou a ser o indice tecnico oficial da pasta de contexto.
- `codex-context.md` foi reduzido a ponte legada curta para evitar duplicacao de mapa e conteudo.
- `README.md` foi ajustado para apontar agentes de IA ao ponto de entrada unico sem repetir a estrutura tecnica.

## 2026-05-26 - Remocao De Contexto Redundante

- Removido `codex-context.md` da raiz por ser ponte legada redundante.
- Removidos artefatos gerados em `.codex-audit/`, pois podem ser recriados pela auditoria e nao sao memoria oficial.
- A memoria oficial ficou concentrada em `CODEX_START_HERE.md` e `codex-context/`.
