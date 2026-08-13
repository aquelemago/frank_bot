# Plano filho: prontidao para producao do scheduler

Estado: **IMPLEMENTACAO OFFLINE CONCLUIDA — VALIDACAO OPERACIONAL PENDENTE**

## Relacao com o plano pai

Este plano e subordinado a
[`scheduler-service.md`](./scheduler-service.md) e existe para eliminar as
pendencias que impedem a conclusao objetiva daquele plano.

O plano pai continua sendo a fonte de verdade para a arquitetura e o
comportamento do scheduler. Este documento nao autoriza mudar horarios, fluxos,
entrypoints ou regras ja aprovadas. Em caso de conflito, prevalece o plano pai.

## Objetivo

Levar a implementacao atual do scheduler de **IMPLEMENTATION COMPLETE — BASELINE
PREEXISTENTE PENDENTE** para uma condicao verificavel de prontidao, com:

- os 20 testes do scheduler passando;
- compilacao sem erros;
- os 47 testes da suite completa passando;
- lock de instancia que nao bloqueie permanentemente uma reinicializacao apos
  encerramento forcado do processo no Windows;
- validacoes operacionais executadas somente com autorizacao explicita;
- forma de inicializacao apos login definida e validada separadamente.

## Estado confirmado antes da execucao

- `service.py` existe e chama `app.main.run()` diretamente.
- Os fluxos sao sincronos e sequenciais.
- Os defaults atuais sao solicitantes `08:00` e atendentes `09:00`.
- Os horarios sao lidos de `FRANK_BOT_REQUESTER_TIME` e
  `FRANK_BOT_ATTENDANT_TIME` no ambiente do processo, nao do `.env`.
- Os 20 testes de `tests.test_service` passam.
- `compileall` passa.
- A suite completa encontra 47 testes e atualmente termina com 43 sucessos,
  duas falhas e dois erros.
- As quatro pendencias estao relacionadas a expectativas de templates e a
  leitura da estrutura MIME dos e-mails nos testes antigos.
- O lock atual usa arquivo criado com `O_CREAT | O_EXCL`; encerramento forcado
  pode deixar um lock orfao.
- Nenhum fluxo real, Soft4, Softdesk, Playwright, Chromium ou SMTP foi executado
  durante essa validacao.

## Escopo

### Dentro do escopo

- diagnosticar e corrigir as quatro falhas antigas da suite;
- corrigir codigo de producao ou teste conforme a causa comprovada;
- tornar a exclusividade de instancia segura contra lock orfao no Windows;
- preservar mensagens de log claras para inicio, execucao, retorno e
  encerramento;
- adicionar ou ajustar testes offline deterministas;
- executar compilacao e suites automatizadas;
- preparar o roteiro de validacao operacional;
- documentar decisoes e resultados neste plano e, se estritamente necessario,
  no runbook operacional.

### Fora do escopo sem nova autorizacao

- executar `main.py`, `service.py` ou `pythonw.exe` contra o ambiente real;
- acessar Soft4 ou Softdesk;
- abrir Playwright/Chromium com o perfil operacional;
- enviar e-mails reais ou testar SMTP real;
- revisar ou alterar destinatarios operacionais;
- criar atalho na pasta Inicializar;
- instalar servico do Windows ou tarefa agendada;
- adicionar dependencia externa;
- alterar a regra dos horarios ou a janela de atraso de cinco minutos;
- refatorar partes nao relacionadas da aplicacao.

## Arquivos inicialmente permitidos

- `service.py`;
- `tests/test_service.py`;
- `app/mailer/templates.py`, somente se o diagnostico comprovar defeito no
  comportamento de producao;
- modulos de montagem MIME em `app/mailer/`, somente se o diagnostico comprovar
  defeito no comportamento de producao;
- `tests/test_mailer.py` e `tests/test_requester_report.py`, somente se a
  expectativa estiver comprovadamente desatualizada ou a leitura MIME do teste
  estiver incorreta;
- este plano;
- `codex-context/03-operations.md`, apenas depois da validacao automatizada e se
  houver mudanca operacional material.

Qualquer necessidade de alterar outro arquivo deve ser registrada em
**Decisoes** antes da mudanca.

## Regras de seguranca

- Ler `AGENTS.md`, `CODEX_START_HERE.md`, o plano pai e este plano antes de
  implementar.
- Nunca imprimir ou inspecionar valores de `.env` ou arquivos de credenciais.
- Nunca executar automacao externa real sem autorizacao explicita para ambiente,
  credenciais e destinatarios.
- Em testes, mockar obrigatoriamente `app.main.run`, SMTP, Soft4 e qualquer
  integracao externa.
- Nao alterar assertions apenas para obter resultado verde.
- Classificar toda falha antes de corrigi-la.
- Fazer mudancas pequenas e revisar o diff depois de cada milestone.

## Protocolo obrigatorio de falha

Para cada milestone:

```text
DIAGNOSTICAR
    |
IMPLEMENTAR A MENOR CORRECAO LEGITIMA
    |
EXECUTAR O TESTE DIRECIONADO
    |
PASSOU?
  SIM -> executar regressao acumulada -> registrar resultado -> seguir
  NAO -> classificar causa -> corrigir -> repetir o mesmo teste
```

Classificacoes permitidas:

1. bug no codigo de producao;
2. teste incorreto ou desatualizado;
3. premissa incompatível com o comportamento aprovado;
4. problema preexistente fora do escopo;
5. limitacao do ambiente de execucao.

## Progresso

- [x] Milestone 0 — reproduzir e classificar as quatro falhas
- [x] Milestone 1 — corrigir as duas divergencias de template
- [x] Milestone 2 — corrigir os dois erros de estrutura MIME
- [x] Milestone 3 — eliminar lock orfao no encerramento forcado
- [x] Milestone 4 — validar encerramento e exclusividade de instancia offline
- [x] Milestone 5 — obter todos os testes do scheduler, compilacao limpa e suite completa verde
- [x] Milestone 6 — revisar diff e atualizar documentacao operacional
- [x] Milestone 7 — validar os fluxos reais, mediante autorizacao explicita
- [x] Milestone 8 — validar scheduler visivel e `pythonw.exe`, mediante autorizacao
- [ ] Milestone 9 — definir e validar inicializacao apos login, mediante autorizacao

Nenhum checkbox pode ser marcado sem evidencia programatica ou, nas milestones
operacionais, evidencia observavel registrada no log.

## Milestone 0 — Reproducao e classificacao

### Objetivo

Reproduzir isoladamente cada uma das quatro falhas e determinar se a causa esta
no codigo ou no teste.

### Procedimento

1. Executar isoladamente os testes afetados.
2. Inspecionar os templates e a montagem MIME correspondentes.
3. Comparar o comportamento com README, runbook, decisoes registradas e testes
   de negocio relacionados.
4. Registrar a classificacao individual em **Descobertas**.

### Validacao

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_mailer -v
.\.venv\Scripts\python.exe -m unittest tests.test_requester_report -v
```

### Criterio de conclusao

As quatro falhas estao reproduzidas e cada uma possui causa e arquivo-alvo
identificados. Nenhuma correcao deve ser feita antes dessa classificacao.

## Milestone 1 — Divergencias de template

### Objetivo

Alinhar os templates de atendentes e solicitantes ao texto operacional aprovado.

### Regras

- Se o template atual estiver errado, corrigir o template.
- Se o texto atual estiver aprovado e o teste estiver desatualizado, corrigir a
  expectativa do teste e registrar a evidencia.
- Preservar escape HTML e dados dinamicos.
- Nao modificar destinatarios ou regras de envio.

### Validacao

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_mailer.MailerTests.test_attendant_email_uses_priority_review_template -v
.\.venv\Scripts\python.exe -m unittest tests.test_requester_report.RequesterReportTests.test_requester_report_template_renders_with_rows -v
```

### Criterio de conclusao

Os dois testes passam e o texto resultante corresponde ao comportamento
operacional documentado.

## Milestone 2 — Estrutura MIME

### Objetivo

Fazer os testes validarem corretamente a parte HTML das mensagens e corrigir o
codigo somente se a mensagem gerada estiver estruturalmente incorreta.

### Procedimento

1. Inspecionar `Content-Type`, multipartes e payloads sem enviar mensagens.
2. Verificar se o consumidor SMTP recebe uma mensagem MIME valida.
3. Corrigir a montagem em producao se ela estiver invalida.
4. Caso a mensagem esteja valida, corrigir o helper/assertion do teste para
   localizar a parte `text/html` de forma robusta.

### Validacao

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_mailer.MailerTests.test_test_email_uses_configured_sender_and_recipient -v
.\.venv\Scripts\python.exe -m unittest tests.test_requester_report.RequesterReportTests.test_requester_report_uses_full_csv_and_sends_structured_html -v
```

### Criterio de conclusao

Os dois testes passam, a mensagem contem parte HTML decodificavel e nenhum SMTP
real e acessado.

## Milestone 3 — Lock sem bloqueio orfao

### Objetivo

Impedir duas instancias simultaneas sem impedir uma nova inicializacao depois que
o Windows encerra o processo abruptamente.

### Direcao tecnica preferida

Usar um bloqueio mantido pelo sistema operacional e liberado automaticamente no
fim do processo, com biblioteca padrao do Python. No Windows, avaliar primeiro
um lock de arquivo mantido por handle com `msvcrt`; se isso nao atender aos
criterios de atomicidade e testes, usar um mutex nomeado via APIs nativas.

O arquivo informativo pode continuar existindo, mas sua mera existencia nao deve
ser a fonte de verdade sobre uma instancia ativa.

### Criterios funcionais

- primeira instancia adquire o lock;
- segunda instancia falha antes de chamar qualquer fluxo;
- liberacao normal permite nova aquisicao;
- fim abrupto do processo libera o bloqueio do sistema;
- arquivo residual, se existir, nao causa bloqueio permanente;
- uma instancia nunca remove ou invalida o lock ativo de outra;
- mensagem de erro permanece clara no log.

### Testes

- teste unitario de exclusividade no mesmo caminho;
- teste de reacquisicao apos liberacao;
- subprocesso curto que adquire o lock e termina sem cleanup normal;
- nova instancia deve adquirir o lock depois do fim desse subprocesso;
- mock deve provar que a instancia rejeitada nao chamou `app.main.run`.

### Validacao

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_service.InstanceLockTests -v
```

### Criterio de conclusao

Todos os cenarios passam de forma deterministica, sem processos permanentes e
sem apagar lock ativo de outra instancia.

## Milestone 4 — Encerramento e exclusividade offline

### Objetivo

Validar o ciclo de vida do scheduler sem esperar horarios reais e sem executar a
aplicacao.

### Casos obrigatorios

- stop ja marcado encerra sem executar;
- stop durante a espera impede execucao posterior;
- `KeyboardInterrupt` registra encerramento e libera recursos;
- excecao inesperada nao transforma uma segunda instancia em valida;
- retorno `0`, `1` ou `2` continua registrado corretamente;
- nenhuma chamada concorrente ou duplicada ocorre.

### Validacao

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_service.ControlledShutdownTests -v
.\.venv\Scripts\python.exe -m unittest tests.test_service.InstanceLockTests -v
.\.venv\Scripts\python.exe -m unittest tests.test_service.SequentialExecutionTests -v
```

### Criterio de conclusao

Todas as classes passam e `app.main.run` permanece mockado.

## Milestone 5 — Regressao completa

### Objetivo

Demonstrar que as correcoes eliminam a pendencia do baseline sem introduzir
regressoes.

### Validacao obrigatoria

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_service -v
.\.venv\Scripts\python.exe -m compileall service.py app tests tools
.\.venv\Scripts\python.exe tests\run_unittest_discovery.py
```

### Resultado exigido

- scheduler: todos os testes passando;
- compilacao: exit code `0`;
- suite completa: **47/47**, exit code `0`;
- nenhuma integracao externa executada.

Se a suite falhar por permissao da pasta temporaria do ambiente isolado, repetir
o mesmo comando com a permissao estritamente necessaria. Falhas de permissao nao
podem ser contabilizadas como sucesso do projeto.

## Milestone 6 — Revisao e documentacao

### Objetivo

Garantir que a solucao final seja pequena, compreensivel e operacionalmente
segura.

### Procedimento

1. Revisar `git diff` e separar mudancas preexistentes das realizadas por este
   plano.
2. Confirmar que nenhum segredo, destinatario ou dado operacional foi incluido.
3. Confirmar que nao foram adicionadas dependencias.
4. Atualizar este plano com comandos, resultados e decisoes.
5. Atualizar o plano pai para concluir a Milestone 0 somente depois de 47/47.
6. Atualizar o runbook apenas se o novo lock exigir orientacao operacional.

### Criterio de conclusao

Diff revisado, resultados registrados e plano pai coerente com a evidencia.

## Milestone 7 — Fluxos reais com autorizacao

### Gate obrigatorio

Esta milestone deve parar e solicitar autorizacao explicita antes da execucao.
A autorizacao deve confirmar ambiente, credenciais e destinatarios.

### Comandos previstos

```powershell
.\.venv\Scripts\python.exe main.py --solicitante
.\.venv\Scripts\python.exe main.py
```

### Verificacoes

- destinatarios revisados;
- Soft4 acessado corretamente;
- CSV e fila gerados conforme esperado;
- e-mails enviados apenas aos destinatarios aprovados;
- Chromium encerrado;
- retorno `0` e resultado registrados em `logs/frank_bot.log`.

### Criterio de conclusao

Os dois fluxos passam separadamente com evidencia no log. Falha real deve ser
diagnosticada antes de prosseguir.

## Milestone 8 — Scheduler visivel e sem janela

### Gate obrigatorio

Executar somente depois da Milestone 7 e com autorizacao explicita, pois o
scheduler pode alcançar o horario real e enviar e-mails.

### Procedimento previsto

1. Iniciar `service.py` com Python visivel.
2. Conferir proximo evento e horario no log.
3. Tentar uma segunda instancia e confirmar rejeicao.
4. Encerrar com `Ctrl+C` e confirmar cleanup.
5. Iniciar novamente e confirmar reacquisicao do lock.
6. Iniciar com `pythonw.exe` e acompanhar pelo log.
7. Encerrar o processo de forma controlada quando possivel e comprovar que uma
   nova instancia pode iniciar.

### Criterio de conclusao

Sem duplicidade, agendamento correto, encerramento registrado e reinicializacao
possivel mesmo depois do encerramento do processo anterior.

## Milestone 9 — Inicializacao apos login

### Gate obrigatorio

Criar atalho somente com autorizacao explicita, pois isso altera a inicializacao
da conta do Windows.

### Procedimento previsto

1. Definir executavel, argumento e diretorio de trabalho absolutos.
2. Configurar as variaveis de horario no contexto que iniciara o processo, se os
   defaults nao forem os aprovados.
3. Criar o atalho na pasta Inicializar do usuario.
4. Reiniciar ou realizar logout/login em janela autorizada.
5. Confirmar uma unica instancia, lock ativo e proximo horario correto no log.

### Criterio de conclusao

O scheduler inicia depois do login sem console, nao duplica e registra o proximo
evento correto.

## Criterio objetivo de DONE deste plano filho

Este plano so pode ser marcado como concluido quando:

- todas as milestones automatizadas 0–6 estiverem concluidas;
- os 47 testes passarem;
- o lock nao deixar bloqueio permanente depois do fim forcado do processo;
- o diff estiver revisado e documentado;
- as milestones 7–9 forem concluidas com autorizacao, ou forem explicitamente
  aceitas pelo responsavel como gates operacionais pendentes fora da entrega de
  codigo;
- o plano pai for atualizado com os resultados reais.

## Descobertas

- Milestone 0 reproduziu exatamente duas falhas e dois erros nos seis testes de
  `tests.test_mailer` e `tests.test_requester_report`.
- O template de atendentes recebe `no_interaction_days`, mas nao usava o valor;
  classificacao: bug no codigo de producao.
- O template de solicitantes atual contem texto operacional detalhado sobre
  retorno e encerramento apos sete dias; as assertions ainda esperavam o modelo
  antigo; classificacao: testes desatualizados.
- E-mails de teste e de solicitante usam `multipart/related` com uma parte
  `multipart/alternative`, conforme a arquitetura documentada para assinatura
  inline. As mensagens sao MIME validas; os testes acessavam apenas o primeiro
  nivel; classificacao: testes incorretos para a estrutura aprovada.
- O teste direcionado das quatro correcoes passou: 4/4.
- O lock passou a usar mutex nomeado do Windows derivado do caminho absoluto do
  arquivo. O arquivo contem apenas o PID para diagnostico.
- Um fixture inicial do subprocesso passou `str` em vez de `Path` e falhou antes
  de testar o lock; o fixture foi corrigido sem afrouxar as assertions.
- Exclusividade, reacquisicao, `KeyboardInterrupt` e encerramento abrupto via
  `os._exit(0)` passaram em 6/6 testes direcionados.
- A suite do scheduler cresceu de 20 para 22 testes e passou integralmente.
- `compileall service.py app tests tools` passou.
- A suite completa cresceu de 47 para 49 testes e passou integralmente: 49/49.
- O diff foi revisado; nao foram adicionadas dependencias, destinatarios,
  credenciais ou chamadas externas.
- Validacao operacional de 2026-08-13: o fluxo real de solicitantes concluiu
  com codigo `0`, enviou o relatorio consolidado configurado e montou/enviou
  cinco entregas individuais por e-mail obtido da API Softdesk.
- Na mesma validacao, o fluxo real de atendentes baixou e filtrou sete registros,
  mas terminou com codigo `1`: todos os seis atendentes encontrados estavam sem
  mapeamento de e-mail, a fila ficou com zero itens e nenhum relatorio de
  atendente ou da gestora foi enviado.
- A repeticao autorizada do fluxo de atendentes em 2026-08-13 concluiu com codigo
  `0`: quatro relatorios individuais e o relatorio gerencial foram enviados.
  Um registro de Rafaela Zen foi ignorado porque ainda nao possui mapeamento de
  e-mail; a configuracao atual permite continuar nessa situacao.
- A validacao operacional do scheduler confirmou proximo evento em
  `2026-08-14T08:00:00`, descarte dos eventos antigos, rejeicao da segunda
  instancia com codigo `1` e reinicio depois do encerramento forcado.
- `pythonw.exe` foi validado sem console; a segunda instancia foi rejeitada e a
  primeira foi encerrada usando seu PID exato.
- O atalho `Frank Bot Scheduler.lnk` foi criado na pasta Inicializar com target,
  argumento e diretorio de trabalho absolutos validados.
- O scheduler foi iniciado pelo proprio atalho e permanece ativo como `pythonw`
  PID `19488`. Falta somente confirmar a inicializacao em um login real para
  concluir a Milestone 9.

## Decisoes

- Este documento e plano filho de `scheduler-service.md`.
- A implementacao deve continuar sem dependencia externa.
- A existencia de um arquivo residual nao deve, sozinha, representar uma
  instancia ativa.
- Testes automatizados nunca podem acessar Soft4, SMTP ou destinatarios reais.
- Validacoes operacionais e criacao de inicializacao automatica possuem gates de
  autorizacao separados.
- O texto atual do e-mail de solicitantes e o comportamento aprovado; os testes
  antigos foram alinhados a ele.
- O parametro `no_interaction_days` do template de atendentes deve aparecer no
  corpo, assim como ja aparece no assunto.
- O mutex do Windows, e nao a existencia do arquivo de PID, e a fonte de verdade
  sobre uma instancia ativa.

## Proximo passo

No proximo login ou reinicio autorizado, confirmar que o atalho inicia uma unica
instancia de `pythonw.exe` e que o log registra o proximo evento correto. Essa e
a unica evidencia restante para concluir a **Milestone 9**. Como melhoria
operacional separada, configurar o e-mail de Rafaela Zen para que os chamados
dela nao sejam ignorados.
