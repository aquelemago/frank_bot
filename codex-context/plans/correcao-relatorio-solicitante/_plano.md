# Plano: correcao da coleta do relatorio de solicitantes

Estado: **VALIDACAO OPERACIONAL CONCLUIDA**

## Painel de progresso

**Estagio atual:** `Plano concluido`

**Situacao atual:** `CONCLUIDA`

**Proxima acao:** decidir separadamente quando restaurar o scheduler, que
permanece parado; nenhuma acao adicional pertence a este plano.

| Milestone | Descricao | Estado | Evidencia necessaria |
|---|---|---|---|
| 0 | Confirmar baseline e contrato atual | ✅ Concluida | 12/12 direcionados, 54/54 completos e payload atual comprovado |
| 1 | Confirmar a requisicao correta do Soft4 | ✅ Concluida | Pesquisa e CSV confirmaram grupos 118/257, status 8, tipo e 3 dias |
| 2 | Criar testes do payload de solicitantes | ✅ Concluida | Dois testes falharam por status e default divergentes |
| 3 | Implementar filtros especificos do solicitante | ✅ Concluida | 5/5 testes verdes, incluindo preservacao do atendente |
| 4 | Validar download e filtro local offline | ✅ Concluida | 17/17 testes comprovaram propagacao e ordem do fluxo |
| 5 | Atualizar documentacao | ✅ Concluida | README e contexto coerentes com o comportamento testado |
| 6 | Executar regressao final e revisar diff | ✅ Concluida | Compilacao, 57/57 testes e diff verdes |
| 7 | Validar no Soft4 sem envio | ✅ Concluida | 25 registros, filtros agregados validos e SMTP ausente |
| 8 | Validar um envio controlado | ✅ Concluida | SMTP aceitou uma mensagem e responsavel confirmou o relatorio |

Legenda:

- `⬜ Nao iniciada`: nenhuma evidencia aceita foi produzida;
- `🟨 Em andamento`: milestone iniciada, ainda sem toda a evidencia;
- `🟥 Bloqueada`: impedimento concreto registrado em **Bloqueios**;
- `✅ Concluida`: criterio demonstrado por validacao reproduzivel ou evidencia
  operacional aprovada.

Somente uma milestone pode ficar `🟨 Em andamento` por vez. Uma milestone nao
pode ser concluida apenas por inspecao visual.

## Objetivo

Fazer o fluxo de solicitantes coletar do Soft4 somente os chamados que atendam
aos filtros operacionais aprovados:

```text
Grupo de solucao: Suporte, Suporte
Status: Aguardando solicitante
Listar: Sem interacao do solicitante
Periodo: 3 dias
```

A correcao deve preservar:

- o fluxo de atendentes;
- a autenticacao atual no Soft4;
- o filtro local por dias uteis e feriados;
- a consulta individual a API Softdesk para descobrir o e-mail;
- o agrupamento por solicitante;
- os destinatarios principal e secundario do relatorio completo;
- templates, anexos e transporte SMTP;
- entrypoints publicos;
- scheduler e horarios.

## Diagnostico inicial confirmado

O comportamento atual usa os endpoints autenticados da fila do Soft4:

```text
POST /chamado/fila-de-atendimento/json
POST /chamado/fila-de-atendimento/csv
```

O payload atual em `app/soft4/downloader.py` contem:

```text
cd_grupo_solucao_fila_atendimento = [118, 257]
st_chamado = [5, 1, 12, 0]
tp_listagem = SEM_INTERACAO_SOLICITANTE
quantidade_dias_sem_interacao_solicitante = 5 por padrao
```

Divergencias ja identificadas:

1. o status desejado e `Aguardando solicitante`, mapeado no proprio payload
   como valor `8`, mas `st_chamado` atualmente nao contem `8`;
2. o periodo desejado e 3 dias, enquanto
   `SOFT4_DIAS_SEM_INTERACAO_SOLICITANTE` usa default `5`;
3. os IDs `[118, 257]` podem representar os dois grupos chamados `Suporte`, mas
   o repositorio nao contem evidencia que associe esses IDs aos nomes;
4. a API Softdesk conhecida (`GET /api/api.php/chamado?codigo=<numero>`) apenas
   resolve o e-mail do solicitante; ela nao escolhe nem gera o relatorio;
5. nao foi encontrada no repositorio ou em busca publica uma API documentada
   que substitua os endpoints de pesquisa e CSV da fila.

Essas descobertas orientam o trabalho, mas os IDs de grupo e o formato final do
payload devem ser confirmados pela requisicao real da tela correta antes da
mudanca de producao.

## Fonte de verdade e ordem de leitura

Antes de trabalhar:

1. ler `AGENTS.md` e `CODEX_START_HERE.md`;
2. ler este plano integralmente;
3. conferir o comportamento real em:
   - `app/soft4/downloader.py`;
   - `app/config/models.py`;
   - `app/config/loader.py`;
   - `app/orchestrator/run.py`;
   - `app/csv/filter.py`;
   - `app/soft4/api.py`;
4. localizar testes existentes relacionados ao downloader, configuracao,
   orquestrador e filtro CSV;
5. consultar `README.md`, `codex-context/01-overview.md`,
   `codex-context/02-architecture.md`, `codex-context/03-operations.md` e
   `codex-context/05-backlog.md`;
6. em caso de divergencia, usar codigo e testes como evidencia primaria e
   registrar a decisao neste plano antes de editar.

## Escopo

### Dentro do escopo

- confirmar endpoint e payload produzidos pela tela correta do Soft4;
- separar, se necessario, filtros do solicitante dos filtros do atendente;
- fazer o solicitante usar somente o status `Aguardando solicitante`;
- fazer o limite do solicitante ser 3 dias no pre-filtro e no filtro local;
- confirmar e preservar os dois grupos de solucao `Suporte`;
- criar testes unitarios deterministas para o payload;
- validar o download com navegador somente mediante autorizacao;
- validar envio real somente em milestone separada e mediante autorizacao;
- atualizar documentacao relacionada.

### Fora do escopo

- alterar o relatorio dos atendentes;
- mudar destinatarios, remetente ou credenciais;
- alterar templates, assuntos ou anexos;
- alterar a API de consulta individual de chamado sem evidencia de necessidade;
- instalar dependencias;
- refatorar modulos nao relacionados;
- abrir ou registrar conteudo de CSVs operacionais;
- executar scheduler durante a validacao;
- enviar relatorios a solicitantes reais durante a validacao de coleta;
- testar repetidamente em producao sem diagnostico entre tentativas;
- assumir que `[118, 257]` sao os IDs corretos sem evidencia da tela/requisicao.

## Arquivos inicialmente permitidos

- `app/soft4/downloader.py`;
- `app/config/models.py`, somente se forem necessarios campos especificos;
- `app/config/loader.py`, somente se a configuracao precisar ser representada;
- `app/orchestrator/run.py`, somente se a propagacao dos filtros estiver errada;
- testes existentes ou novo teste direcionado em `tests/`;
- `README.md`;
- `codex-context/01-overview.md`;
- `codex-context/02-architecture.md`;
- `codex-context/03-operations.md`, se o procedimento operacional mudar;
- `codex-context/04-decisions.md`, para registrar decisao arquitetural;
- `codex-context/05-backlog.md`, para encerrar ou atualizar riscos existentes;
- este plano.

Qualquer necessidade de editar outro arquivo deve ser registrada em
**Descobertas e decisoes** antes da mudanca.

## Regras de seguranca

- Nao abrir, imprimir, resumir ou modificar `.env` ou `config/*.env`.
- Nao expor cookies, tokens, cabecalhos de autenticacao ou chaves de API.
- Nao imprimir resposta JSON, CSV ou dados de chamados reais.
- Na captura de rede, registrar somente endpoint, metodo e nomes/valores de
  filtros nao sensiveis.
- Soft4, Playwright e Chromium exigem autorizacao explicita para a milestone
  operacional correspondente.
- SMTP e qualquer envio real exigem uma segunda autorizacao explicita,
  independente da autorizacao de coleta.
- Durante validacoes operacionais, confirmar que o scheduler esta parado para
  evitar duplicidade.
- Mockar todas as integracoes externas nos testes automatizados.
- Preservar mudancas preexistentes do worktree.
- Nao apagar artefatos operacionais sem solicitacao explicita.

## Contrato funcional pretendido

O payload de solicitantes deve representar, depois de confirmacao no Soft4:

```text
cd_grupo_solucao_fila_atendimento = [IDs confirmados de Suporte, Suporte]
st_chamado = [8]
tp_listagem = SEM_INTERACAO_SOLICITANTE
quantidade_dias_sem_interacao_solicitante = 3
```

O filtro local deve receber o mesmo limite de 3 dias:

```text
limite_dias_uteis = 3
```

O fluxo de atendentes deve continuar usando seus filtros atuais. A implementacao
nao deve obter o relatorio pela API Softdesk individual; essa API continua sendo
usada apenas depois do CSV para resolver e-mails.

## Estrategia de desenvolvimento com harness

O trabalho deve ser dirigido por evidencias e testes:

```text
OBSERVAR CONTRATO REAL
        |
CODIFICAR EXPECTATIVA EM TESTE
        |
EXECUTAR TESTE -> DEVE FALHAR PELA DIVERGENCIA ESPERADA
        |
IMPLEMENTAR A MENOR CORRECAO
        |
REPETIR TESTE -> DEVE PASSAR
        |
EXECUTAR REGRESSAO ACUMULADA
        |
ATUALIZAR PLANO E DOCUMENTACAO
```

O agente deve manter o contexto recuperavel neste arquivo: estado, proxima
acao, comandos, resultados, descobertas, decisoes e bloqueios.

### Protocolo de falha

Quando um teste ou validacao falhar:

1. parar a milestone atual;
2. classificar a causa;
3. registrar evidencia sanitizada;
4. corrigir implementacao ou teste conforme a causa comprovada;
5. repetir exatamente o teste que falhou;
6. executar regressao acumulada depois do sucesso;
7. nao avancar enquanto houver falha.

Classificacoes permitidas:

1. bug no payload de producao;
2. default de configuracao incorreto;
3. teste ausente, incorreto ou desatualizado;
4. IDs ou contrato do Soft4 ainda nao confirmados;
5. falha de autenticacao ou sessao;
6. divergencia entre pesquisa JSON e exportacao CSV;
7. problema no filtro local;
8. limitacao do ambiente;
9. problema preexistente fora do escopo.

## Milestone 0 — confirmar baseline e contrato atual

### Objetivo

Provar que o baseline atual esta verde e registrar a divergencia sem alterar a
implementacao.

### Procedimento

1. conferir `git status --short`;
2. localizar todos os testes do downloader e filtro;
3. executar testes direcionados existentes;
4. executar a suite completa;
5. registrar que o payload atual usa status diferentes de `8` e default de 5
   dias por inspecao programatica ou teste.

### Validacao prevista

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_csv_filter tests.test_main_run -v
.\.venv\Scripts\python.exe tests\run_unittest_discovery.py
```

### Criterio de conclusao

Baseline verde e divergencias atuais registradas com arquivo e campo exatos.

## Milestone 1 — confirmar a requisicao correta do Soft4

### Gate obrigatorio

Esta milestone acessa o Soft4 e deve ser executada somente com autorizacao
explicita para ambiente e perfil do navegador. Ela nao autoriza SMTP.

### Procedimento preferido

1. garantir que o scheduler e execucoes manuais estejam parados;
2. abrir a fila do Soft4 com o perfil autorizado;
3. selecionar manualmente:
   - grupo `Suporte` e o segundo grupo `Suporte`;
   - status `Aguardando solicitante`;
   - listar `Sem interacao do solicitante`;
   - periodo `3` dias;
4. observar a requisicao de pesquisa e a de exportacao;
5. registrar de forma sanitizada:
   - endpoint;
   - metodo;
   - IDs dos dois grupos;
   - `st_chamado`;
   - `tp_listagem`;
   - quantidade de dias;
   - diferencas entre payload JSON e CSV;
6. nao baixar, abrir ou imprimir o conteudo do CSV alem do estritamente
   necessario para confirmar que a exportacao foi produzida.

### Criterio de conclusao

Endpoint e payload corretos confirmados por evidencia observavel, sem segredo ou
dado de chamado no plano. Se os IDs nao forem `[118, 257]`, registrar os IDs
corretos antes de qualquer implementacao.

## Milestone 2 — criar testes do payload de solicitantes

### Objetivo

Transformar o contrato confirmado em testes unitarios antes da correcao.

### Casos obrigatorios

- payload do solicitante usa somente `st_chamado = [8]`;
- payload usa os dois IDs de grupo confirmados;
- `tp_listagem` e `SEM_INTERACAO_SOLICITANTE`;
- quantidade de dias do solicitante e `3`;
- payload do atendente permanece inalterado;
- pesquisa JSON e exportacao CSV recebem os campos esperados;
- `status_chamado`, quando necessario apenas para a exportacao, nao mascara o
  filtro efetivo de `st_chamado`.

### Validacao

Executar primeiro o novo teste contra o codigo atual e confirmar que ele falha
pelas divergencias esperadas. Nao afrouxar assertions para obter sucesso.

### Criterio de conclusao

Teste falhando de forma controlada pelo status e/ou periodo incorretos, sem
chamar navegador, rede ou SMTP.

## Milestone 3 — implementar filtros especificos do solicitante

### Objetivo

Corrigir a menor superficie possivel sem alterar o atendente.

### Direcao tecnica

- separar filtros de status por tipo de relatorio, se hoje forem compartilhados;
- usar somente o status confirmado de `Aguardando solicitante` no solicitante;
- usar os IDs confirmados dos dois grupos `Suporte`;
- adotar 3 dias como contrato do solicitante;
- preservar o formato esperado pelo endpoint real;
- evitar duplicar toda a funcao de payload quando parametros claros forem
  suficientes;
- nao criar abstracao generica alem do necessario.

### Validacao

```powershell
.\.venv\Scripts\python.exe -m unittest <teste_direcionado_do_payload> -v
```

### Criterio de conclusao

Teste do payload verde e teste equivalente do atendente demonstrando ausencia de
regressao.

## Milestone 4 — validar download e filtro local offline

### Objetivo

Comprovar que os 3 dias percorrem todo o fluxo e que o filtro local permanece
coerente.

### Casos obrigatorios

- loader produz limite 3 conforme contrato aprovado;
- orquestrador passa 3 ao downloader;
- payload envia 3 ao Soft4;
- filtro local recebe 3 dias uteis;
- fins de semana e feriados continuam excluidos;
- API Softdesk nao e chamada antes de o CSV estar filtrado;
- testes nao acessam integracoes externas.

### Validacao prevista

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_csv_filter tests.test_main_run <teste_do_loader> -v
```

### Criterio de conclusao

Propagacao de 3 dias demonstrada de configuracao ate filtro local, com regressao
acumulada verde.

## Milestone 5 — atualizar documentacao

### Objetivo

Alinhar documentacao ao contrato comprovado, sem documentar suposicoes.

### Atualizacoes previstas

- README: filtros corretos e forma de coleta;
- overview: regra de negocio de 3 dias;
- arquitetura: endpoint, payload e separacao Soft4/Softdesk;
- operacoes: validacao e troubleshooting de relatorio incorreto;
- decisoes: motivo para separar filtros de solicitante e atendente;
- backlog: resolver ou atualizar a pendencia de grupos e status fixos;
- este plano: comandos e resultados reais.

### Validacao

```powershell
rg -n "Aguardando solicitante|SEM_INTERACAO_SOLICITANTE|3 dias|st_chamado" README.md codex-context app tests
```

### Criterio de conclusao

Codigo, testes e documentacao descrevem o mesmo comportamento.

## Milestone 6 — regressao final e revisao de diff

### Validacao obrigatoria

```powershell
.\.venv\Scripts\python.exe -m compileall service.py app tests tools
.\.venv\Scripts\python.exe tests\run_unittest_discovery.py
git diff --check
git status --short
git diff -- app tests README.md codex-context
```

### Criterio de conclusao

- testes direcionados verdes;
- suite completa verde;
- compilacao com codigo `0`;
- `git diff --check` sem erros;
- nenhuma dependencia adicionada;
- nenhum segredo ou dado operacional no diff;
- alteracoes restritas ao escopo;
- mudancas preexistentes preservadas.

## Milestone 7 — validar no Soft4 sem envio

### Gate obrigatorio

Solicitar autorizacao explicita para Soft4, Playwright, perfil operacional e
download real. Essa autorizacao nao inclui SMTP.

### Estrategia

Usar um harness de validacao que execute autenticacao, pesquisa, download e
filtro, mas substitua todo transporte SMTP por mocks ou por um ponto de parada
antes do despacho. O comando normal `--dry-run` nao deve ser usado cegamente no
fluxo de atendentes, pois possui efeito de e-mail documentado; para solicitantes,
confirmar por teste que nenhum SMTP e chamado antes da execucao.

### Evidencias sanitizadas

- endpoint e filtros usados;
- codigo de saida;
- CSV produzido e nao vazio, sem imprimir caminho completo ou conteudo;
- todos os registros resultantes atendem aos criterios, validados por um
  verificador que produza somente contagens booleanas/agregadas;
- nenhum SMTP chamado;
- navegador encerrado.

### Criterio de conclusao

Coleta correta demonstrada no ambiente real sem envio de e-mail e sem exposicao
de chamados.

## Milestone 8 — validar um envio controlado

### Gate independente

Solicitar nova autorizacao explicita para SMTP, remetente, destinatario e janela.
Confirmar novamente que o scheduler esta parado.

### Estrategia segura

- nao enviar aos solicitantes individuais durante o primeiro teste;
- enviar uma unica copia do relatorio completo para o destinatario de teste
  aprovado;
- reutilizar o CSV ja validado na Milestone 7;
- nao coletar novamente nem repetir o envio automaticamente;
- registrar somente sucesso/falha e confirmacao humana, sem endereco ou dados do
  relatorio.

### Criterio de conclusao

SMTP aceita uma unica mensagem e o responsavel confirma que os chamados do
relatorio correspondem aos filtros aprovados.

## Criterio objetivo de DONE

Este plano so pode ser marcado como concluido quando:

- endpoint e payload corretos forem confirmados;
- IDs dos dois grupos `Suporte` forem comprovados;
- status efetivo for exclusivamente `Aguardando solicitante`;
- tipo de listagem for `SEM_INTERACAO_SOLICITANTE`;
- limite for 3 dias no pre-filtro e no filtro local;
- fluxo de atendentes permanecer inalterado;
- testes direcionados, compilacao e suite completa passarem;
- documentacao estiver coerente;
- coleta real sem SMTP demonstrar o relatorio correto;
- um envio controlado for realizado somente com autorizacao e confirmado pelo
  responsavel;
- nenhum segredo, dado de chamado ou destinatario real for registrado.

## Regra de atualizacao do progresso

Ao iniciar ou concluir uma milestone, atualizar na mesma mudanca:

1. `Estado`;
2. `Estagio atual`, `Situacao atual` e `Proxima acao`;
3. a linha correspondente da tabela;
4. **Evidencias de execucao** com comando, resultado e quantidade de testes;
5. **Descobertas e decisoes**;
6. **Bloqueios**, se aplicavel.

Uma milestone somente recebe `✅ Concluida` depois que seu criterio de conclusao
e a regressao acumulada passarem. Falhas devem permanecer visiveis no historico,
mesmo depois de corrigidas.

## Evidencias de execucao

- 2026-08-19 — Milestone 0: testes direcionados passaram com 12/12 e a suite
  completa passou com 54/54. Nenhuma integracao externa foi executada.
- 2026-08-19 — Verificacao programatica offline de
  `_build_queue_payload()` confirmou grupos `[118, 257]`, status efetivos
  `[5, 1, 12, 0]`, tipo `SEM_INTERACAO_SOLICITANTE`, limite `5` e ausencia do
  status efetivo `8` (`Aguardando solicitante`).
- 2026-08-19 — Milestone 1: observacao autorizada da tela confirmou
  `118 = Suporte [MAINHARDT]`, `257 = Suporte [UNUS]` e
  `8 = Aguardando solicitante`. O POST real de pesquisa para
  `/chamado/fila-de-atendimento/json` enviou grupos `[118, 257]`, status `[8]`,
  tipo `SEM_INTERACAO_SOLICITANTE` e 3 dias.
- 2026-08-19 — A exportacao real foi interceptada e abortada antes do download.
  O POST para `/chamado/fila-de-atendimento/csv` confirmou o mesmo payload da
  pesquisa. Nenhum CSV foi lido e nenhum SMTP foi chamado.
- 2026-08-19 — Milestone 2: os testes novos falharam de forma controlada. O
  payload retornou `[5, 1, 12, 0]` onde o contrato exige `[8]`; o loader retornou
  default `5` onde o contrato exige `3`. Classificacao: bugs no payload de
  producao e no default de configuracao.
- 2026-08-19 — Milestone 3: `tests.test_soft4_downloader` e
  `tests.test_config_loader` passaram com 5/5. O solicitante usa status `[8]`,
  grupos `[118, 257]`, tipo aprovado e 3 dias; o atendente preserva
  `[5, 1, 12, 0]`.
- 2026-08-19 — Milestone 4: regressao acumulada de configuracao, payload,
  filtro e orquestrador passou com 17/17. O teste do fluxo comprova 3 dias no
  downloader e no filtro local e a ordem `filtrar -> despachar`.
- 2026-08-19 — Milestone 5: README, overview, arquitetura, operacoes, decisoes,
  backlog e guia de execucao foram alinhados ao contrato confirmado. A busca
  cruzada e `git diff --check` passaram.
- 2026-08-19 — Milestone 6: compilacao passou, suite completa passou com 57/57
  e `git diff --check` passou. O diff foi revisado; nenhuma dependencia, segredo
  ou chamada externa foi adicionada.
- 2026-08-19 — Preflight da Milestone 7: a configuracao efetiva foi carregada
  sem imprimir valores e reportou que o limite do solicitante nao e 3. Nenhum
  download ou SMTP foi executado.
- 2026-08-19 — Repeticao do preflight da Milestone 7: a configuracao efetiva
  passou a resolver o limite do solicitante para 3 dias. Nenhum valor sensivel
  foi exibido e nenhuma integracao foi executada nesta repeticao.
- 2026-08-19 — Milestone 7: harness isolado acessou Soft4/Playwright sem
  importar ou chamar mailer e API Softdesk. Pesquisa e CSV enviaram grupos
  `[118, 257]`, status `[8]`, tipo `SEM_INTERACAO_SOLICITANTE` e 3 dias. O CSV
  temporario foi baixado, filtrado e removido ao final; permaneceu nao vazio com
  25 registros.
- 2026-08-19 — Como o CSV nao exporta colunas de status ou grupo, a verificacao
  agregada usou a resposta JSON da mesma pesquisa: todos os 25 registros tinham
  status numerico `8`; o resumo confirmou duas entradas `Suporte`, status
  `Aguardando solicitante` e listagem sem interacao do solicitante. Nenhum valor
  de chamado foi exibido e `SMTP_CALLED=NAO`.
- 2026-08-19 — Milestone 8: apos autorizacao explicita, o scheduler foi
  confirmado parado. O harness coletou novamente com o contrato de 3 dias,
  filtrou 25 registros e enviou uma unica mensagem ao destinatario principal
  configurado. O SMTP aceitou o envio; entregas individuais e a copia completa
  secundaria nao foram chamadas. O CSV temporario foi removido ao final.
- 2026-08-19 — O responsavel confirmou o recebimento e informou que o relatorio
  funcionou corretamente. A Milestone 8 e o plano foram concluidos.

## Descobertas e decisoes

- O relatorio e coletado pelos endpoints autenticados da fila do Soft4, nao pela
  API Softdesk individual.
- O status `Aguardando solicitante` aparece no payload como valor `8`.
- Antes da correcao, o filtro efetivo do solicitante usava
  `st_chamado = [5, 1, 12, 0]` e default de 5 dias.
- A implementacao agora seleciona status `[8]` para solicitantes e preserva
  `[5, 1, 12, 0]` para atendentes; o default do solicitante passou a 3 dias.
- Os IDs `[118, 257]` foram associados aos dois grupos `Suporte` pela
  requisicao real.
- O scheduler estava parado na ultima verificacao e deve permanecer assim ate
  uma decisao operacional explicita de restauracao.
- Nenhum arquivo de implementacao foi alterado por este planejamento.

## Bloqueios

- A autorizacao e a confirmacao exigidas pela Milestone 1 foram obtidas.
- Os IDs `[118, 257]` foram confirmados como os dois grupos `Suporte`.
- As Milestones 7 e 8 possuem gates independentes para coleta real e SMTP.
- O bloqueio de configuracao e o gate de coleta da Milestone 7 foram resolvidos.
- A coleta real e o envio controlado foram concluidos sem bloqueios restantes.
- O scheduler permanece parado e sua restauracao exige uma decisao operacional
  separada deste plano.
