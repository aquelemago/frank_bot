# Plano: validacao operacional do segundo destinatario de solicitantes

Estado: **VALIDACAO OPERACIONAL CONCLUIDA**

## Painel de progresso

**Estagio atual:** `Concluido`

**Situacao atual:** `CONCLUIDO`

**Proxima acao:** nenhuma. Uma nova execucao real exige novo gate operacional.

| Milestone | Descricao | Estado | Evidencia necessaria |
|---|---|---|---|
| 0 | Confirmar baseline offline | ✅ Concluida | 14/14 direcionados, 57/57 completos, compilacao e diff verdes |
| 1 | Preflight seguro da configuracao | ✅ Concluida | Configuracoes presentes, validas e destinatarios distintos |
| 2 | Confirmar autorizacao operacional | ✅ Concluida | Nova confirmacao imediatamente antes da execucao real |
| 3 | Executar fluxo real de solicitantes | ✅ Concluida | Execucao unica terminou com codigo 0 e log tecnico coerente |
| 4 | Verificar evidencias do envio | ✅ Concluida | Log aprovado e recebimentos confirmados pelo responsavel |
| 5 | Encerrar e documentar resultado | ✅ Concluida | Resultado, validacoes e limitacao de inspecao registrados sem dados sensiveis |

Legenda:

- `⬜ Nao iniciada`: nenhuma evidencia aceita foi produzida;
- `🟨 Em andamento`: milestone iniciada, mas ainda sem toda a evidencia;
- `🟥 Bloqueada`: impedimento concreto registrado em **Bloqueios**;
- `✅ Concluida`: criterio demonstrado por validacao reproduzivel ou evidencia
  operacional aprovada.

Somente uma milestone pode ficar `🟨 Em andamento` por vez. A milestone atual
deve passar antes do inicio da proxima.

## Objetivo

Validar de forma controlada que, em uma execucao real do fluxo de solicitantes:

- `EMAIL_SOLICITANTE_TODOS_CHAMADOS` continua recebendo o relatorio completo;
- `EMAIL_SOLICITANTE_TODOS_CHAMADOS2` recebe uma segunda copia do mesmo relatorio
  completo;
- cada solicitante continua recebendo somente seus chamados;
- nenhum destinatario inesperado recebe e-mail;
- o fluxo conclui com o codigo e os registros esperados.

Este plano valida a implementacao entregue em
`requester-full-report-secondary-recipient.md`. Ele nao autoriza novas mudancas
de comportamento.

## Fonte de verdade e ordem de leitura

Antes de executar:

1. ler `AGENTS.md` e `CODEX_START_HERE.md`;
2. ler este plano integralmente;
3. ler `requester-full-report-secondary-recipient.md`;
4. conferir os entrypoints em `main.py`, `app/main.py` e
   `app/orchestrator/run.py`;
5. consultar `README.md` e `codex-context/03-operations.md` para o runbook;
6. tratar codigo e testes como fonte primaria quando houver divergencia.

## Escopo

### Dentro do escopo

- repetir validacoes offline;
- verificar somente presenca, ausencia e formato basico das variaveis
  necessarias, sem imprimir valores;
- confirmar com o responsavel o ambiente e os destinatarios antes do envio;
- executar uma unica vez o fluxo real de solicitantes;
- acompanhar codigo de saida e novas linhas do log;
- obter confirmacao humana de recebimento da copia adicional;
- registrar resultado e diagnosticar eventual falha;
- aplicar correcao somente se uma causa comprovada estiver dentro do escopo da
  implementacao do segundo destinatario e houver autorizacao para editar.

### Fora do escopo

- executar o fluxo de atendentes;
- iniciar ou reiniciar o scheduler;
- alterar horarios do scheduler;
- executar dry-run como substituto da validacao real, pois ele acessa Soft4 mas
  nao envia e-mail do solicitante;
- imprimir ou copiar valores de `.env` e `config/*.env`;
- abrir CSVs, filas geradas ou dados de chamados para inspecao manual;
- modificar destinatarios, credenciais, templates, filtros ou regras de negocio;
- repetir envios reais sem novo diagnostico e nova confirmacao dos
  destinatarios;
- enviar e-mail de teste por `tools/send_test_email.py`, pois ele nao valida o
  relatorio completo de solicitantes;
- executar Soft4, Softdesk, Playwright, Chromium ou SMTP antes do gate da
  Milestone 2.

## Regras de seguranca operacional

- Nunca exibir o endereco contido nas variaveis de destinatario.
- O preflight deve retornar apenas estados como `PRESENTE`, `AUSENTE`,
  `FORMATO_VALIDO` ou `FORMATO_INVALIDO`.
- Nunca exibir credenciais, tokens, cookies, cabecalhos, conteudo do CSV ou nomes
  de solicitantes.
- Antes do envio, o responsavel deve confirmar fora da saida tecnica que os dois
  destinatarios completos e os destinatarios individuais sao os esperados.
- Capturar a posicao ou o horario inicial do log antes da execucao para analisar
  apenas os registros novos, sem despejar o historico operacional.
- Nao iniciar o comando se outra execucao do fluxo ou scheduler puder produzir
  envio concorrente na mesma janela.
- Uma falha real deve ser diagnosticada antes de qualquer repeticao.
- Nao remover arquivos operacionais gerados pela validacao sem solicitacao
  explicita.

## Protocolo obrigatorio de falha

```text
EXECUTAR UMA ETAPA
       |
VALIDAR A EVIDENCIA
       |
PASSOU?
  SIM -> REGISTRAR RESULTADO -> SEGUIR
  NAO -> PARAR -> CLASSIFICAR CAUSA -> DIAGNOSTICAR
         -> CORRIGIR SOMENTE SE AUTORIZADO -> REPETIR APENAS A ETAPA NECESSARIA
```

Classificacoes permitidas:

1. configuracao ausente ou invalida;
2. falha de autenticacao Soft4 ou Softdesk;
3. falha de download ou filtro;
4. falha de SMTP;
5. bug no segundo destinatario;
6. destinatarios nao aprovados;
7. execucao concorrente ou risco de duplicidade;
8. limitacao do ambiente;
9. problema preexistente fora do escopo.

Nao repetir o fluxo completo apenas para obter um resultado verde: uma repeticao
pode duplicar e-mails para todos os solicitantes.

## Milestone 0 — confirmar baseline offline

### Objetivo

Garantir que o codigo que sera executado ainda corresponde a implementacao
validada.

### Validacao

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_config_loader tests.test_main_run -v
.\.venv\Scripts\python.exe -m compileall service.py app tests tools
.\.venv\Scripts\python.exe tests\run_unittest_discovery.py
git diff --check
```

### Criterio de conclusao

- testes direcionados verdes;
- compilacao com codigo `0`;
- suite completa verde;
- `git diff --check` sem erros;
- nenhuma integracao externa executada.

## Milestone 1 — preflight seguro da configuracao

### Objetivo

Confirmar que o processo consegue carregar a configuracao necessaria sem expor
valores e sem iniciar navegador ou SMTP.

### Verificacoes obrigatorias

- `SOFT4_USUARIO`: presente;
- `SOFT4_SENHA`: presente;
- `SOFTDESK_API_KEY`: presente, pois a segunda copia pertence ao ramo da API;
- configuracao SMTP obrigatoria: presente;
- `EMAIL_SOLICITANTE_TODOS_CHAMADOS`: presente e com formato basico valido;
- `EMAIL_SOLICITANTE_TODOS_CHAMADOS2`: presente e com formato basico valido;
- os dois destinatarios completos nao sao iguais;
- horarios ou scheduler nao sao alterados por esta verificacao.

### Forma segura prevista

Usar um pequeno comando offline que carregue as variaveis no mesmo processo da
aplicacao e imprima somente nomes logicos e estados booleanos. O comando nao pode
imprimir `repr(settings)`, dicionarios de ambiente, valores ou mensagens de erro
que contenham segredos.

### Criterio de conclusao

Todas as configuracoes necessarias reportam estado valido e os dois
destinatarios completos sao distintos, sem qualquer valor sensivel na saida.

Se houver ausencia ou formato invalido, marcar esta milestone como bloqueada e
solicitar que o responsavel corrija a configuracao. Nao modificar `.env`.

## Milestone 2 — confirmar autorizacao operacional

### Gate obrigatorio

Parar e obter autorizacao explicita imediatamente antes da execucao real. A
autorizacao deve confirmar:

- que o ambiente Soft4/Softdesk e o ambiente operacional correto;
- que o remetente SMTP e o esperado;
- que `EMAIL_SOLICITANTE_TODOS_CHAMADOS` aponta para o destinatario principal
  aprovado;
- que `EMAIL_SOLICITANTE_TODOS_CHAMADOS2` aponta para o gestor de teste aprovado;
- que os e-mails individuais para os solicitantes reais estao autorizados;
- que a execucao pode ocorrer na janela atual;
- que nao existe scheduler ou execucao manual concorrente;
- que o responsavel aceita uma unica execucao real do fluxo.

### Criterio de conclusao

Autorizacao explicita registrada em **Evidencias de execucao**, sem copiar os
enderecos reais para o plano.

Sem essa confirmacao, o plano deve permanecer bloqueado e nenhum comando real
deve ser executado.

## Milestone 3 — executar fluxo real de solicitantes

### Precondicoes

- Milestones 0, 1 e 2 concluidas;
- nenhuma instancia concorrente identificada;
- ponto inicial do log registrado sem expor seu conteudo historico;
- destinatarios confirmados pelo responsavel;
- nenhuma alteracao pendente desde a regressao offline.

### Comando autorizado pelo gate

```powershell
.\.venv\Scripts\python.exe main.py --solicitante
```

Executar exatamente uma vez. Nao usar `service.py`, `pythonw.exe`, `--dry-run`
ou o script SMTP para esta validacao.

### Evidencias a registrar

- data e hora da execucao;
- comando executado;
- codigo de saida;
- indicacao de que somente novas linhas do log foram analisadas;
- quantidade de categorias de envio observadas, sem nomes, enderecos ou dados de
  chamados;
- qualquer excecao, classificada sem revelar informacao sensivel.

### Criterio de conclusao

O comando termina com codigo `0` e as novas linhas do log indicam conclusao do
fluxo e envios esperados. Codigo `1` ou `2` interrompe o plano para diagnostico;
nao repetir automaticamente.

## Milestone 4 — verificar evidencias do envio

### Objetivo

Demonstrar que a nova copia funcionou sem depender apenas do codigo de saida.

### Verificacoes

- o log novo registra envio do relatorio completo principal;
- o log novo registra envio da copia adicional;
- nao ha falha acumulada para a copia adicional;
- o responsavel confirma recebimento no destinatario principal;
- o gestor de teste confirma recebimento da segunda copia;
- quando aplicavel, os solicitantes receberam seus relatorios individuais;
- assunto, anexo e conteudo da copia adicional correspondem ao relatorio
  completo esperado, sem registrar seu conteudo neste plano;
- nenhum destinatario inesperado e identificado.

### Criterio de conclusao

Evidencia tecnica no log e confirmacao humana de recebimento concordam. Se o
SMTP aceitar a mensagem mas ela nao chegar, classificar como problema de
entrega/quarentena e nao reenviar antes de verificar a infraestrutura de e-mail.

## Milestone 5 — encerrar e documentar resultado

### Procedimento

1. Registrar resultados das Milestones 0–4.
2. Atualizar o painel e o estado deste documento.
3. Registrar falhas, diagnosticos e decisoes sem dados sensiveis.
4. Confirmar que nenhum processo de teste permaneceu ativo.
5. Revisar `git status --short` e distinguir documentacao desta tarefa de
   artefatos operacionais preexistentes ou gerados.
6. Nao apagar CSVs, logs ou relatorios sem autorizacao.

### Estados finais permitidos

- **VALIDACAO OPERACIONAL CONCLUIDA**: envio principal e copia adicional
  comprovados;
- **BLOQUEADO ANTES DO ENVIO**: configuracao ou autorizacao insuficiente;
- **FALHA OPERACIONAL DIAGNOSTICADA**: execucao ocorreu, falhou e nao foi
  repetida sem controle;
- **RESULTADO INCONCLUSIVO**: log ou confirmacao humana insuficiente, sem
  afirmar sucesso.

## Criterio objetivo de DONE

Este plano somente pode ser marcado como concluido quando:

- o baseline offline estiver verde;
- o preflight seguro comprovar a configuracao sem expor valores;
- houver autorizacao operacional explicita;
- uma unica execucao real terminar com codigo `0`;
- o log novo comprovar o envio principal e a copia adicional;
- o destinatario principal e o gestor de teste confirmarem recebimento;
- nao houver evidencia de destinatario inesperado;
- o resultado final estiver documentado sem segredos ou dados operacionais.

## Regra de atualizacao do progresso

Ao iniciar ou concluir qualquer milestone, atualizar na mesma mudanca:

1. `Estado`;
2. `Estagio atual`, `Situacao atual` e `Proxima acao`;
3. a linha da milestone na tabela;
4. **Evidencias de execucao**;
5. **Descobertas e decisoes**;
6. **Bloqueios**, quando aplicavel.

Nenhuma milestone pode ser marcada como concluida apenas por inspecao visual ou
por expectativa. A evidencia deve ser reproduzivel, exceto a confirmacao de
recebimento, que deve ser registrada como verificacao humana.

## Evidencias de execucao

- 2026-08-19 — Retomada controlada: o baseline anterior foi considerado
  historico porque a implementacao dos filtros do relatorio de solicitantes foi
  alterada depois dos 54 testes registrados. A Milestone 0 foi reaberta para
  validacao do codigo atual. Nenhuma integracao externa foi executada.
- 2026-08-19 — Revalidacao da Milestone 0: 14/14 testes direcionados passaram,
  incluindo configuracao, orquestracao e payload Soft4; compilacao passou com
  codigo `0`; suite completa passou com 57/57; `git diff --check` passou apenas
  com avisos informativos de conversao LF/CRLF. Nenhuma integracao externa foi
  executada.
- 2026-08-19 — Milestone 1 revalidada: o preflight terminou com codigo `0` e
  confirmou, somente por indicadores `SIM/NAO`, credenciais Soft4, chave
  Softdesk, SMTP, os dois destinatarios presentes e com formato valido,
  destinatarios distintos e regra de solicitante configurada para tres dias.
  Duas tentativas anteriores do comando falharam com `SyntaxError` antes de
  carregar a configuracao; a causa foi a interpretacao de aspas pelo shell e a
  validacao foi repetida por script temporario removido em seguida. Nenhuma
  integracao externa foi executada.
- 2026-08-19 — Pre-gate da Milestone 2: o processo registrado no arquivo de
  lock nao esta ativo; `SCHEDULER_RUNNING=NAO`. Nenhum processo foi alterado.
- 2026-08-19 — Milestone 2 revalidada: o responsavel declarou "autorizo" em
  resposta ao gate completo, aprovando o ambiente, remetente, os dois
  destinatarios completos, os e-mails individuais reais, a janela atual e uma
  unica execucao de `main.py --solicitante`.
- 2026-08-19 — Milestone 3: o ponto inicial do log foi registrado por tamanho,
  e `main.py --solicitante` foi executado exatamente uma vez. O processo
  terminou com codigo `0`. A analise exclusiva do trecho novo encontrou 21
  entregas individuais esperadas e 23 marcadores de envio, quantidade igual as
  entregas individuais mais os dois relatorios completos; houve um marcador de
  conclusao e nenhum marcador de falha do fluxo ou do envio. Nenhum endereco,
  nome ou conteudo de chamado foi exibido.
- 2026-08-19 — Milestone 4: o responsavel respondeu "sim para tudo" e confirmou
  o recebimento correto do relatorio completo no destinatario principal e no
  gestor de teste, incluindo assunto, conteudo e anexo. A confirmacao humana e
  a evidencia tecnica concordam.
- 2026-08-19 — Milestone 5: a regressao final passou com 14/14 testes
  direcionados e 57/57 testes completos; `git diff --check` passou apenas com
  avisos informativos LF/CRLF. A sessao da execucao real terminou e o processo
  registrado no lock do scheduler permanece inativo. A consulta ampla das
  linhas de comando dos processos foi negada pelo Windows e foi registrada como
  limitacao de observabilidade, sem invalidar as evidencias anteriores. O
  `git status --short` foi revisado; artefatos operacionais e alteracoes alheias
  preexistentes foram preservados, sem exclusao ou restauracao.

- 2026-08-19 — Milestone 0: testes direcionados passaram com 11/11;
  compilacao passou com codigo `0`; suite completa passou com 54/54;
  `git diff --check` passou. Nenhuma integracao externa foi executada.
- 2026-08-19 — Milestone 1: preflight carregou a configuracao com sucesso e
  confirmou credenciais Soft4, chave Softdesk, SMTP e destinatario completo
  principal presentes. `EMAIL_SOLICITANTE_TODOS_CHAMADOS2` foi reportada como
  ausente pela configuracao efetiva. Nenhum valor foi exibido e nenhuma
  integracao externa foi executada.
- 2026-08-19 — Repeticao da Milestone 1: configuracao carregada com sucesso;
  credenciais Soft4, chave Softdesk, SMTP e os dois destinatarios completos
  foram reportados como presentes; ambos os destinatarios possuem formato
  valido e sao distintos. Nenhum valor foi exibido.
- 2026-08-19 — Pre-gate da Milestone 2: o arquivo informativo de lock existe e o
  processo registrado esta ativo como `pythonw`. Nenhum processo foi encerrado
  ou alterado.
- 2026-08-19 — Milestone 2: o responsavel respondeu "sim pra tudo", aprovando o
  ambiente, remetente, os dois destinatarios completos, os envios individuais
  reais, uma unica execucao na janela atual e a interrupcao temporaria do
  scheduler para evitar concorrencia.

## Descobertas e decisoes

- A autorizacao operacional registrada anteriormente precede a correcao dos
  filtros e uma execucao controlada posterior. Por seguranca contra duplicidade,
  o gate da Milestone 2 devera ser renovado imediatamente antes de uma nova
  execucao completa.

- O responsavel informou que `EMAIL_SOLICITANTE_TODOS_CHAMADOS2` ja esta
  preenchida. O valor nao foi lido nem registrado.
- A validacao real precisa usar `python main.py --solicitante`; o dry-run nao
  envia e-mail de solicitante e, portanto, nao comprova a entrega.
- A execucao real tambem pode enviar relatorios aos solicitantes obtidos pela
  API Softdesk. Esse efeito exige confirmacao explicita antes do comando.
- Uma repeticao indiscriminada pode duplicar mensagens; por isso o plano exige
  diagnostico antes de qualquer nova tentativa.

## Bloqueios

Nenhum bloqueio conhecido. Nenhuma nova execucao real esta autorizada ou
prevista.
