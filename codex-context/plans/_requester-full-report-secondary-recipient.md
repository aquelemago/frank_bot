# Plano: segundo destinatario do relatorio completo de solicitantes

Estado: **IMPLEMENTACAO OFFLINE CONCLUIDA — VALIDACAO EXTERNA NAO EXECUTADA**

## Painel de progresso

**Estagio atual:** `Implementacao offline concluida`

**Situacao atual:** `CONCLUIDA`

**Proxima acao:** preencher `EMAIL_SOLICITANTE_TODOS_CHAMADOS2` no ambiente
operacional e, somente com autorizacao explicita, executar uma validacao real.

| Milestone | Descricao | Estado | Evidencia necessaria |
|---|---|---|---|
| 0 | Baseline e contrato observavel | ✅ Concluida | 6/6 testes atuais verdes; contrato registrado |
| 1 | Modelo e carregamento da configuracao | ✅ Concluida | 2/2 testes do loader e 6/6 da regressao verdes |
| 2 | Segundo envio do relatorio completo | ✅ Concluida | 9/9 testes do orquestrador verdes |
| 3 | Dry-run e falhas | ✅ Concluida | Dry-run e falha adicional cobertos nos 9/9 testes |
| 4 | Documentacao | ✅ Concluida | Busca confirmou contrato em README, contexto, codigo e testes |
| 5 | Regressao final e revisao | ✅ Concluida | 54/54 testes, compilacao e `git diff --check` verdes |

Legenda:

- `⬜ Nao iniciada`: nenhum trabalho da milestone foi validado;
- `🟨 Em andamento`: implementacao ou diagnostico iniciado, ainda sem toda a
  evidencia exigida;
- `🟥 Bloqueada`: existe impedimento concreto registrado em **Bloqueios**;
- `✅ Concluida`: criterio de conclusao demonstrado por validacao reproduzivel.

### Regra de atualizacao do progresso

Ao iniciar ou encerrar uma milestone, o agente deve atualizar, na mesma mudanca:

1. `Estado` no inicio do documento;
2. `Estagio atual` e `Situacao atual` neste painel;
3. a linha correspondente da tabela;
4. **Evidencias de execucao**, com comando, resultado e quantidade de testes;
5. **Descobertas e decisoes**, quando houver informacao relevante;
6. **Bloqueios**, se a continuidade depender de autorizacao ou informacao
   externa.

Somente uma milestone pode ficar `🟨 Em andamento` por vez. Uma milestone so
pode receber `✅ Concluida` depois que seu criterio de conclusao passar e sua
regressao acumulada tambem estiver verde. A proxima milestone nao deve ser
iniciada enquanto a atual estiver falhando.

## Objetivo

Adicionar suporte opcional a `EMAIL_SOLICITANTE_TODOS_CHAMADOS2` para enviar ao
gestor de teste uma segunda copia do mesmo relatorio completo de chamados do
solicitante que atualmente e enviado a `EMAIL_SOLICITANTE_TODOS_CHAMADOS`.

A mudanca deve ser estritamente aditiva. O destinatario atual, os relatorios
individuais, o conteudo, o anexo, os filtros, a consulta a API Softdesk, o
scheduler e o fluxo de atendentes devem permanecer inalterados.

## Fonte de verdade e ordem de leitura

Antes de implementar:

1. ler `AGENTS.md` e `CODEX_START_HERE.md`;
2. ler este plano integralmente;
3. conferir o comportamento real em:
   - `app/config/models.py`;
   - `app/config/loader.py`;
   - `app/orchestrator/run.py`;
   - `tests/test_main_run.py`;
4. consultar `README.md`, `codex-context/01-overview.md` e
   `codex-context/02-architecture.md` somente para manter a documentacao
   coerente;
5. em caso de divergencia entre documentacao e implementacao, considerar o
   codigo e os testes de comportamento como evidencia primaria e registrar a
   divergencia neste plano antes de alterar qualquer arquivo.

## Comportamento aprovado

Quando o fluxo de solicitantes estiver no modo que usa a API Softdesk:

- `EMAIL_SOLICITANTE_TODOS_CHAMADOS` continua recebendo o relatorio completo;
- cada solicitante continua recebendo apenas seus proprios chamados;
- se `EMAIL_SOLICITANTE_TODOS_CHAMADOS2` estiver preenchida, seu destinatario
  recebe uma segunda copia do relatorio completo;
- a segunda copia usa o mesmo CSV completo, template, data de exportacao e
  limite de dias sem interacao usados pela copia principal;
- se a nova variavel estiver ausente ou vazia, o comportamento atual permanece
  exatamente igual;
- em `dry-run`, nenhum e-mail do fluxo de solicitantes e enviado; o envio
  adicional aparece apenas no plano registrado em log;
- uma falha no envio adicional participa do tratamento de falhas ja usado pelo
  fluxo e deve resultar no mesmo comportamento de erro das demais falhas de
  envio.

O comportamento legado usado quando nao existe chave da API Softdesk nao deve
ser ampliado ou alterado por esta tarefa.

## Fora do escopo

- substituir ou remover `EMAIL_SOLICITANTE_TODOS_CHAMADOS`;
- mudar destinatarios reais ou valores de `.env`;
- modificar textos, assunto, HTML ou anexos dos e-mails;
- alterar agrupamento de chamados ou descoberta do e-mail do solicitante;
- mudar filtros de dias uteis, feriados ou limites de inatividade;
- alterar o scheduler, horarios ou entrypoints;
- alterar o fluxo de atendentes ou o relatorio da gestora de atendentes;
- adicionar dependencias;
- refatorar o sistema de configuracao ou o orquestrador;
- executar Soft4, Softdesk, Playwright, Chromium, SMTP ou qualquer envio real;
- tratar multiplos destinatarios genericos alem das duas variaveis aprovadas.

## Arquivos inicialmente permitidos

- `app/config/models.py`;
- `app/config/loader.py`;
- `app/orchestrator/run.py`;
- `tests/test_main_run.py`;
- teste de configuracao ja existente, se houver; caso nao exista, um novo teste
  direcionado sob `tests/`;
- `README.md`;
- `codex-context/01-overview.md`;
- `codex-context/02-architecture.md`;
- este plano.

Qualquer necessidade de alterar outro arquivo deve ser explicada e registrada
em **Descobertas e decisoes** antes da mudanca.

## Regras de seguranca

- Nao abrir, imprimir, resumir ou modificar `.env` ou `config/*.env`.
- Nao registrar enderecos operacionais reais em testes ou documentacao.
- Usar enderecos reservados como `gestor@example.com` nos testes.
- Mockar obrigatoriamente o envio de e-mail e todas as integracoes externas.
- Nao executar `main.py`, `service.py`, `pythonw.exe` ou o script SMTP.
- Nao alterar artefatos em `downloads/`, `email_queue/`, `logs/` ou
  `perfil_soft4/`.
- Preservar mudancas preexistentes no worktree.
- Fazer mudancas pequenas e revisar o diff apos cada milestone.

## Estrategia tecnica prevista

1. Acrescentar a `RequesterReportSettings` um campo explicito para o segundo
   destinatario completo, preferencialmente `full_report_recipient2`.
2. Carregar esse campo a partir de `EMAIL_SOLICITANTE_TODOS_CHAMADOS2`, com
   string vazia como padrao e sem obrigatoriedade.
3. No despacho de relatorios de solicitantes, preservar o envio principal e
   realizar um segundo envio somente quando o novo campo estiver preenchido.
4. Reutilizar `send_requester_report_email` com o CSV completo original e os
   mesmos parametros usados pelo destinatario principal.
5. Preservar o acumulador de falhas existente e identificar no erro qual envio
   adicional falhou.
6. No `dry-run`, registrar o segundo envio planejado sem chamar o transporte
   SMTP.

A implementacao deve evitar uma abstracao ampla de listas de destinatarios se
ela nao for necessaria para satisfazer esses criterios. A menor mudanca clara e
testavel e preferida.

## Fluxo obrigatorio por milestone

```text
IMPLEMENTAR A MENOR MUDANCA
        |
EXECUTAR TESTE DIRECIONADO
        |
PASSOU?
  SIM -> EXECUTAR REGRESSAO ACUMULADA -> REGISTRAR EVIDENCIA -> SEGUIR
  NAO -> CLASSIFICAR CAUSA -> CORRIGIR -> REPETIR O MESMO TESTE
```

Classificacoes de falha permitidas:

1. bug na implementacao;
2. teste incorreto ou incompleto;
3. premissa do plano incompatível com o comportamento real aprovado;
4. regressao preexistente fora do escopo;
5. limitacao do ambiente de execucao.

Uma milestone nao pode ser concluida apenas por inspecao visual.

## Milestone 0 — baseline e contrato observavel

### Objetivo

Confirmar o baseline antes de qualquer mudanca e transformar o pedido em
assertions observaveis.

### Procedimento

1. Conferir `git status --short` e registrar arquivos preexistentes alterados.
2. Executar os testes atuais do orquestrador.
3. Confirmar por teste/codigo que o relatorio completo atual usa o CSV original.
4. Confirmar que `dry-run` nao envia e-mails de solicitantes.
5. Confirmar que a copia completa existe apenas no ramo atual com chave da API.

### Validacao

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_main_run -v
```

### Criterio de conclusao

Baseline verde e contrato atual registrado em **Evidencias de execucao**. Se o
baseline falhar, diagnosticar e resolver a causa conforme as regras permanentes
antes de iniciar a Milestone 1.

## Milestone 1 — modelo e carregamento da configuracao

### Objetivo

Representar e carregar a nova variavel opcional sem alterar configuracoes
existentes.

### Implementacao prevista

- adicionar `full_report_recipient2` ao modelo de configuracao;
- carregar `EMAIL_SOLICITANTE_TODOS_CHAMADOS2` com default vazio;
- ajustar fixtures tipadas ou `SimpleNamespace` afetados somente onde
  necessario.

### Casos de teste obrigatorios

- variavel preenchida resulta no valor esperado no modelo;
- variavel ausente resulta em string vazia;
- configuracao existente continua sendo carregada sem mudanca semantica;
- nenhum teste le o `.env` operacional.

### Validacao

Executar o teste direcionado do loader e depois:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_main_run -v
```

### Criterio de conclusao

Nova configuracao comprovadamente opcional e regressao acumulada verde.

## Milestone 2 — segundo envio do relatorio completo

### Objetivo

Enviar a segunda copia sem alterar os demais envios.

### Casos de teste obrigatorios

Com a nova configuracao preenchida, provar que:

- o destinatario principal recebe o relatorio completo;
- o segundo destinatario recebe o relatorio completo;
- o solicitante continua recebendo seu relatorio individual;
- os dois destinatarios completos recebem `source_csv=requester_csv_path`;
- o solicitante recebe seu CSV individual;
- template, data e limite de dias sao preservados;
- a montagem de entregas individuais ocorre uma unica vez.

Com a nova configuracao vazia, provar que:

- nao existe chamada adicional;
- a contagem e os destinatarios permanecem iguais ao comportamento anterior.

### Validacao

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_main_run -v
```

### Criterio de conclusao

Todos os envios esperados e somente eles estao demonstrados pelas chamadas ao
mailer mockado.

## Milestone 3 — dry-run e falhas

### Objetivo

Preservar a seguranca do dry-run e o contrato de erro do orquestrador.

### Casos de teste obrigatorios

- `dry-run` registra o segundo destinatario planejado e nao chama o mailer;
- falha apenas no segundo destinatario e acumulada em `failures`;
- a mensagem permite distinguir a falha do envio adicional;
- falha adicional nao impede a tentativa dos relatorios individuais, conforme
  o fluxo atual;
- ausencia da nova variavel nao gera log ou falha adicional.

### Validacao

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_main_run -v
```

### Criterio de conclusao

Dry-run sem efeitos externos e tratamento de falhas demonstrado
programaticamente.

## Milestone 4 — documentacao

### Objetivo

Documentar a nova configuracao sem divulgar valores reais.

### Atualizacoes previstas

- adicionar `EMAIL_SOLICITANTE_TODOS_CHAMADOS2=` ao exemplo do `README.md`;
- explicar que a variavel e opcional e recebe uma segunda copia completa;
- atualizar o comportamento em `codex-context/01-overview.md`;
- atualizar configuracao, fluxo e efeitos em `codex-context/02-architecture.md`;
- registrar descobertas e decisoes neste plano.

### Validacao

```powershell
rg -n "EMAIL_SOLICITANTE_TODOS_CHAMADOS2" README.md codex-context app tests
```

### Criterio de conclusao

Configuracao, implementacao, testes e documentacao descrevem o mesmo contrato.

## Milestone 5 — regressao final e revisao

### Validacao obrigatoria

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_main_run -v
.\.venv\Scripts\python.exe -m compileall service.py app tests tools
.\.venv\Scripts\python.exe tests\run_unittest_discovery.py
git diff --check
git diff -- app/config/models.py app/config/loader.py app/orchestrator/run.py tests README.md codex-context
```

### Criterio de conclusao

- testes direcionados passando;
- compilacao com codigo de saida `0`;
- suite completa passando sem regressao;
- `git diff --check` sem erros;
- nenhum segredo, destinatario real ou dado operacional adicionado;
- nenhuma dependencia adicionada;
- diff restrito ao escopo aprovado;
- evidencias registradas neste plano somente depois de cada validacao passar.

## Gate para validacao externa

Este plano nao autoriza validacao real. Qualquer execucao de Soft4, Softdesk,
Playwright, Chromium ou SMTP exige autorizacao explicita posterior, incluindo a
confirmacao do ambiente, das credenciais e dos destinatarios.

Uma eventual validacao real deve ocorrer somente depois de toda a suite offline
passar e deve comprovar pelo log, sem expor dados sensiveis, que:

- o destinatario atual continuou recebendo o relatorio completo;
- o gestor de teste recebeu a segunda copia;
- nenhum destinatario nao aprovado recebeu mensagens;
- o fluxo terminou com o codigo esperado.

## Criterio objetivo de DONE

Esta tarefa estara concluida somente quando:

- todas as milestones offline estiverem validadas programaticamente;
- a variavel nova for opcional;
- os dois destinatarios completos forem comprovados por testes com o mesmo CSV;
- os relatorios individuais e o destinatario atual permanecerem inalterados;
- dry-run e tratamento de falhas estiverem cobertos;
- compilacao e suite completa estiverem verdes;
- documentacao e codigo estiverem coerentes;
- o diff final estiver revisado e restrito ao escopo;
- qualquer validacao externa tiver sido executada apenas mediante autorizacao,
  ou permanecer registrada como gate operacional fora da entrega offline.

## Evidencias de execucao

- 2026-08-19 — Milestone 0: `.\.venv\Scripts\python.exe -m unittest
  tests.test_main_run -v` passou com 6/6 testes. O teste existente comprovou que
  a copia completa usa o CSV original; a inspecao do fluxo confirmou dry-run sem
  envio e copia completa restrita ao ramo com chave da API.
- 2026-08-19 — Milestone 1: `tests.test_config_loader` passou com 2/2 testes e
  comprovou valor preenchido e default vazio. `tests.test_main_run` passou com
  6/6 testes na regressao acumulada. Nenhuma integracao externa foi chamada.
- 2026-08-19 — Milestones 2 e 3: `tests.test_main_run` passou com 9/9 testes.
  Foram comprovados o destinatario principal, a copia adicional, o CSV completo
  compartilhado, o CSV individual preservado, a ausencia opcional, o dry-run
  sem mailer e a continuidade apos falha simulada da copia adicional.
- 2026-08-19 — Milestone 4: `rg -n
  "EMAIL_SOLICITANTE_TODOS_CHAMADOS2" README.md codex-context app tests`
  confirmou a nova configuracao no loader, teste, README, overview, arquitetura
  e plano, sem registrar um destinatario operacional real.
- 2026-08-19 — Milestone 5: testes direcionados passaram com 11/11;
  `.\.venv\Scripts\python.exe -m compileall service.py app tests tools` passou
  com codigo `0`; `tests\run_unittest_discovery.py` passou com 54/54 testes;
  `git diff --check` passou. Soft4, Softdesk, Playwright, Chromium e SMTP nao
  foram executados.

## Bloqueios

Nenhum bloqueio da implementacao offline. A validacao externa permanece
protegida pelo gate de autorizacao.

## Descobertas e decisoes

- O comportamento atual possui um unico campo `full_report_recipient`, carregado
  de `EMAIL_SOLICITANTE_TODOS_CHAMADOS`.
- O envio completo atual ocorre no ramo com chave da API Softdesk e reutiliza o
  CSV completo antes da criacao dos CSVs individuais.
- A nova variavel sera uma copia adicional; nao substituira o destinatario
  existente.
- O comportamento legado sem chave da API permanecera fora desta alteracao.
- Nenhum arquivo de implementacao foi modificado durante a elaboracao deste
  plano.
- A primeira execucao dos testes do loader falhou ao criar subdiretorios no
  TEMP isolado do Windows (`PermissionError`). Classificacao: limitacao do
  ambiente de execucao. Como a restricao persistiu em uma pasta temporaria no
  workspace, o fixture passou a mockar apenas `Path.mkdir`, efeito colateral
  fora do contrato testado, sem alterar assertions ou comportamento de producao.
- A revisao final encontrou delecoes de
  `codex-context/plans/scheduler-production-readiness.md` e
  `codex-context/plans/scheduler-service.md` que nao pertencem a esta tarefa e
  nao foram realizadas nem restauradas por esta implementacao.
