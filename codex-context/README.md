# Indice Tecnico Oficial

Esta pasta concentra a memoria tecnica oficial para agentes de IA.
O ponto de entrada do projeto continua sendo `CODEX_START_HERE.md`.

## Ordem Recomendada

1. `01-projeto.md`: entender produto, escopo, regras de negocio, entradas e saidas.
2. `02-arquitetura.md`: entender fluxo tecnico, modulos, configuracao e efeitos colaterais.
3. `03-runbook.md`: executar setup, validacao, troubleshooting e operacao.
4. `04-backlog.md`: consultar riscos, pendencias e melhorias antes de planejar mudancas.
5. `05-historico.md`: verificar decisoes e mudancas relevantes.
6. `06-inventario.md`: consultar inventario detalhado de modulos, dependencias, testes e auditorias.

## Responsabilidade De Cada Arquivo

- `README.md`: guia humano e operacional, fora desta pasta.
- `CODEX_START_HERE.md`: inicio unico para agentes de IA, fora desta pasta.
- `01-projeto.md`: o que o sistema faz.
- `02-arquitetura.md`: como o sistema faz.
- `03-runbook.md`: como rodar, validar e resolver falhas.
- `04-backlog.md`: o que ainda precisa ser tratado.
- `05-historico.md`: o que mudou e quando.
- `06-inventario.md`: evidencias detalhadas coletadas por auditoria.

## Como Atualizar

- Para coletar evidencias antes de editar, rode:

```powershell
python C:\Users\lucas.silva\.codex\skills\project-context-auditor\scripts\audit_project_context.py .
```

- Use `.codex-audit/project-context-audit.json` e `.codex-audit/project-context-audit.md` como apoio local.
- Confira o codigo antes de transformar qualquer item da auditoria em documentacao permanente.
- Mudou comportamento? Atualize `01-projeto.md`, `02-arquitetura.md` e, se afetar usuario, `README.md`.
- Mudou comando, dependencia, validacao ou operacao? Atualize `03-runbook.md` e `README.md`.
- Mudou risco, TODO ou plano futuro? Atualize `04-backlog.md`.
- Mudanca relevante concluida? Registre em `05-historico.md`.
- Inventario tecnico novo? Atualize `06-inventario.md` com data, comandos e fonte.

## Regras

- Nao incluir segredos nem valores reais de credenciais.
- Nao documentar suposicoes como fatos.
- Manter comandos compativeis com PowerShell.
- Tratar `downloads/`, `email_queue/`, `perfil_soft4/` e `__pycache__/` como artefatos de runtime.
