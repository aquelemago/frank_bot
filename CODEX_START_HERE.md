# Comece Aqui

Este e o ponto de entrada unico para agentes de IA neste projeto.
Leia este arquivo antes de qualquer outro contexto.

## Ordem De Leitura

1. `CODEX_START_HERE.md`: regras criticas, estado curto e comandos seguros.
2. `README.md`: guia humano para instalar, configurar e operar.
3. `codex-context/README.md`: indice tecnico oficial.
4. Arquivo especifico em `codex-context/`, conforme a tarefa:
   - `01-projeto.md`: objetivo, escopo, regras de negocio, entradas e saidas.
   - `02-arquitetura.md`: fluxo, modulos, configuracao, efeitos colaterais.
   - `03-runbook.md`: setup, execucao, validacao, troubleshooting.
   - `04-backlog.md`: riscos, pendencias e melhorias.
   - `05-historico.md`: decisoes e mudancas datadas.
   - `06-inventario.md`: inventario detalhado de modulos, dependencias, testes e auditorias.

Arquivos que nao sao ponto de partida:

- `.codex-audit/`: artefatos gerados por auditoria; podem ser recriados e nao sao memoria oficial.

## Regras Criticas

- Nao abrir, imprimir, resumir ou versionar valores de `.env` ou `config/*.env`.
- Nao expor credenciais SMTP, usuarios, senhas, cookies, tokens ou perfil do navegador.
- Nao remover `downloads/`, `email_queue/` ou `perfil_soft4/` sem pedido explicito.
- Preservar `python main.py` e `app.main.run()` como entradas publicas.
- Documentar comportamento observado no codigo, nao suposicoes.
- Nao rodar automacao real contra Soft4/SMTP sem confirmacao de ambiente, credenciais e destinatarios.

## Estado Atual

- Automacao Python para exportar CSV da fila Soft4/Mainhardt.
- Codigo principal em `app/`.
- CSV baixado em `downloads/fila_atendimento_YYYYMMDD_HHMMSS.csv`.
- Fila de e-mail por execucao em `email_queue/YYYYMMDD_HHMMSS/`.
- Cada atendente recebe CSV filtrado.
- A gestora recebe relatorio consolidado.
- Chamados entram na automacao com 3 ou mais dias uteis sem interacao.
- A pasta atual nao esta inicializada como repositorio Git; rastreie alteracoes manualmente ou inicialize Git antes de mudancas amplas.

## Validacao Segura

```powershell
python -m compileall app tests
python tests/run_unittest_discovery.py
```

## Auditoria De Contexto

Quando precisar atualizar a memoria tecnica do projeto, rode:

```powershell
python C:\Users\lucas.silva\.codex\skills\project-context-auditor\scripts\audit_project_context.py .
```

Use os arquivos gerados em `.codex-audit/` apenas como apoio para atualizar
`codex-context/`. O codigo continua sendo a fonte de verdade.

Nao execute `python main.py` contra Soft4/SMTP real sem aprovacao explicita.
