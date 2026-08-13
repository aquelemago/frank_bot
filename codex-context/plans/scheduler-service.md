# Plano operacional: scheduler Python permanente

Estado: **IMPLEMENTATION COMPLETE — BASELINE RESOLVIDA**

Este arquivo é a fonte de verdade exclusiva para implementar o scheduler. Uma
nova sessão deve ler `CODEX_START_HERE.md`, `AGENTS.md`, este plano e o código
afetado antes de começar. O scheduler ainda não está implementado.

## Contexto confirmado no código

- `app.orchestrator.run.run(dry_run: bool = False, solicitante: bool = False) -> int`
  é a definição real; `app.main` a reexporta.
- `solicitante=False` chama o relatório de atendentes; `solicitante=True` chama
  o relatório de solicitantes. Os fluxos são síncronos.
- Ambos retornam `0` em sucesso, `1` em falha geral e `2` em configuração inválida.
- `setup_logging()` configura console e `RotatingFileHandler` em
  `logs/frank_bot.log`, sem duplicar handlers marcados.
- `run()` pode carregar `.env`, criar diretórios, limpar `__pycache__`, abrir
  Playwright/Chromium persistente, acessar Soft4/Softdesk, gravar CSV/fila e
  enviar SMTP. Portanto, em testes, `app.main.run` deve ser sempre mockado.
- Testes existentes usam `unittest` e `unittest.mock`; pytest não faz parte do
  projeto. Não adicionar dependência de scheduler nem de teste.

## Escopo e arquitetura-alvo

Criar somente `service.py` e `tests/test_service.py`, preservando os entrypoints
e o código de produção existentes:

```text
service.py
    +--> app.main.run(solicitante=False)
    +--> app.main.run(solicitante=True)
```

Um único processo Python deve calcular horários pelo relógio, executar os fluxos
sequencialmente, registrar retornos, continuar após falhas e encerrar de forma
controlada. Deve ser compatível com `pythonw.exe` e usar somente a biblioteca
padrão. Fora de escopo: serviço do Windows, inicialização automática, web,
Celery, Redis, banco, Docker, processos permanentes iniciados pelos testes e
qualquer refatoração da aplicação.

## Segurança de desenvolvimento

Toda validação do scheduler deve ser offline e determinística. Nunca chamar o
`run()` real, `python main.py`, Soft4, Softdesk, Playwright/Chromium ou SMTP.
Usar `unittest.mock`, funções substitutas, eventos e relógio/sleep injetados ou
controlados. Nenhum teste pode depender de rede, credenciais, produção ou espera
real. Importar `service` não pode iniciar o loop.

## Configuração prevista

Na Milestone 2, definir em `service.py` horários diários com defaults explícitos
e simples, sobrescrevíveis por variáveis de ambiente documentadas no próprio
módulo. Antes de fixar nomes/defaults, confirmar com o responsável operacional;
essa escolha não pode alterar `app/config/`. Formato recomendado: `HH:MM`, uma
variável para atendentes e outra para solicitantes. Valores inválidos devem
falhar antes do loop com mensagem clara.

## Protocolo obrigatório de falha

```text
IMPLEMENTAR
   |
EXECUTAR TESTE DA MILESTONE
   |
PASSOU?
  SIM -> executar regressão acumulada -> atualizar plano -> seguir
  NÃO -> identificar causa -> corrigir -> executar o mesmo teste -> repetir
```

Antes de corrigir, classificar a causa como: (1) bug na implementação; (2) teste
incorreto; (3) premissa do plano incompatível com o código real; (4) problema
preexistente; ou (5) limitação real do ambiente. Se o teste estiver correto,
corrigir o código. Se estiver objetivamente errado, corrigir o teste e registrar
a justificativa em **Decisões**. Se a arquitetura estiver errada, atualizar
**Decisões** antes de continuar. Nunca mascarar teste, remover assertion para
obter sucesso ou adaptar teste a comportamento incorreto.

## Regra de regressão

Após uma milestone passar: (1) repetir seu teste; (2) executar todos os testes
do scheduler até ela; (3) executar os testes preexistentes relevantes. Para M1,
rodar M1; para M2, M1+M2; e assim por diante. Se houver regressão, parar,
diagnosticar, corrigir e repetir a suíte acumulada. Falhas registradas no baseline
devem ser comparadas por identidade; uma falha nova ou uma piora é regressão.

## Progresso

- [x] Milestone 0 — Baseline
- [x] Milestone 1 — Estrutura mínima do `service.py`
- [x] Milestone 2 — Cálculo do próximo horário
- [x] Milestone 3 — Execução correta do tipo de fluxo
- [x] Milestone 4 — Execução sequencial e sem sobreposição
- [x] Milestone 5 — Tratamento dos códigos retornados por `run()`
- [x] Milestone 6 — Falha não encerra scheduler
- [x] Milestone 7 — Suspensão / execução atrasada
- [x] Milestone 8 — Proteção contra duplicidade
- [x] Milestone 9 — Encerramento controlado
- [x] Milestone 10 — Validação integrada segura

Nenhum checkbox vira `[x]` antes do teste correspondente passar.

## Milestone 0 — Baseline

### Objetivo

Estabelecer o estado conhecido anterior ao scheduler e distinguir falhas antigas
de regressões futuras.

### Mudança esperada

Nenhuma mudança de produção; registrar aqui os resultados reais.

### Arquivos permitidos

`codex-context/plans/scheduler-service.md`.

### Arquivos que não devem ser alterados

Todo código em `app/`, `main.py`, testes existentes e configuração.

### Critério de aceitação

Imports requeridos funcionam, compilação passa e a suíte preexistente passa. Se
o ambiente impedir a suíte, a milestone permanece aberta e a causa é registrada.

### Teste programático

AST confirma assinatura/retornos; `compileall` verifica sintaxe; discovery roda
a suíte existente sem chamar entrypoints operacionais.

### Comando de validação

```powershell
C:\Python313\python.exe -m compileall app tests tools
C:\Python313\python.exe tests\run_unittest_discovery.py
```

### Resultado esperado

Exit code `0` nos dois comandos; imports e todos os testes verdes.

### Procedimento se falhar

Classificar como ambiente, falha preexistente ou regressão. Registrar detalhes;
não corrigir dívida antiga fora do escopo. Antes de M1, assegurar que
`tests/test_service.py` possa rodar isoladamente mesmo se o baseline continuar
documentadamente vermelho.

## Milestone 1 — Estrutura mínima do `service.py`

### Objetivo

Criar um módulo importável que não inicie o loop nem a automação ao importar.

### Mudança esperada

Adicionar `service.py` com funções/constantes mínimas e guard
`if __name__ == "__main__"`; iniciar `tests/test_service.py`.

### Arquivos permitidos

`service.py`, `tests/test_service.py`, este plano.

### Arquivos que não devem ser alterados

`main.py`, `app/**`, demais testes, requisitos e configuração.

### Critério de aceitação

Importar `service` termina imediatamente, não chama `app.main.run`, não inicia
loop, navegador, rede, SMTP nem cria artefatos do scheduler.

### Teste programático

Subprocesso curto injeta `app.main.run` mockado antes do import e afirma zero
chamadas; teste normal importa o módulo e comprova ausência de autoexecução.

### Comando de validação

```powershell
C:\Python313\python.exe -m unittest tests.test_service.ServiceImportTests -v
```

### Resultado esperado

Exit code `0`; todos os testes da classe passam sem efeitos externos.

### Procedimento se falhar

Aplicar o protocolo obrigatório, priorizando remover efeitos de import e manter
o guard de execução; repetir a mesma classe antes da regressão.

## Milestone 2 — Cálculo do próximo horário

### Objetivo

Separar uma função pura que selecione o próximo evento diário pelo relógio.

### Mudança esperada

Representar eventos simples e calcular o menor datetime elegível, sem
`sleep(86400)` e sem ler o relógio dentro da função pura.

### Arquivos permitidos

`service.py`, `tests/test_service.py`, este plano.

### Arquivos que não devem ser alterados

`main.py`, `app/**`, requisitos e demais testes.

### Critério de aceitação

Antes e exatamente no horário selecionam o evento do dia; depois seleciona o
dia seguinte; múltiplos horários escolhem o primeiro cronologicamente.

### Teste programático

Testes com `datetime` fixo cobrem antes, igualdade, depois, virada de dia,
múltiplos eventos e desempate determinístico, sem espera real.

### Comando de validação

```powershell
C:\Python313\python.exe -m unittest tests.test_service.ScheduleCalculationTests -v
```

### Resultado esperado

Exit code `0`; datetimes e tipos de fluxo coincidem exatamente com os fixtures.

### Procedimento se falhar

Classificar erro de fronteira/ordenação/configuração, corrigir a função pura e
repetir a classe; depois rodar M1+M2.

## Milestone 3 — Execução correta do tipo de fluxo

### Objetivo

Provar o despacho correto para `app.main.run()`.

### Mudança esperada

Adicionar executor de um evento que aceite/internamente use função substituível.

### Arquivos permitidos

`service.py`, `tests/test_service.py`, este plano.

### Arquivos que não devem ser alterados

`main.py`, `app/**`, requisitos e demais testes.

### Critério de aceitação

Evento atendente gera exatamente `run(solicitante=False)`; solicitante gera
exatamente `run(solicitante=True)`.

### Teste programático

`Mock` verifica argumentos e número de chamadas para ambos os eventos; o
`app.main.run` real nunca é executado.

### Comando de validação

```powershell
C:\Python313\python.exe -m unittest tests.test_service.FlowDispatchTests -v
```

### Resultado esperado

Exit code `0` e chamadas mockadas exatas.

### Procedimento se falhar

Corrigir o mapeamento/evento, não afrouxar `assert_called_once_with`; repetir e
rodar M1–M3.

## Milestone 4 — Execução sequencial e sem sobreposição

### Objetivo

Garantir que o mesmo loop nunca inicie dois fluxos simultaneamente.

### Mudança esperada

Manter execução síncrona em um único thread e serializar eventos vencidos em
ordem determinística.

### Arquivos permitidos

`service.py`, `tests/test_service.py`, este plano.

### Arquivos que não devem ser alterados

`main.py`, `app/**`, requisitos e demais testes.

### Critério de aceitação

Ordem observada é `inicio atendente`, `fim atendente`, `inicio solicitante`,
`fim solicitante`; a segunda chamada nunca ocorre durante a primeira.

### Teste programático

Fake runner/spies registram início/fim e uma flag detecta reentrada; dois eventos
prontos são processados sem threads reais nem tempo real.

### Comando de validação

```powershell
C:\Python313\python.exe -m unittest tests.test_service.SequentialExecutionTests -v
```

### Resultado esperado

Exit code `0`, ordem exata e nenhuma reentrada.

### Procedimento se falhar

Remover concorrência ou corrigir fila/ordenação; não alterar a ordem esperada
para esconder sobreposição; repetir e rodar M1–M4.

## Milestone 5 — Tratamento dos códigos retornados por `run()`

### Objetivo

Registrar os retornos reais `0`, `1` e `2` sem encerrar o loop por retorno não zero.

### Mudança esperada

Executor registra fluxo e código, distinguindo sucesso, falha geral e configuração.

### Arquivos permitidos

`service.py`, `tests/test_service.py`, este plano.

### Arquivos que não devem ser alterados

`main.py`, `app/**`, requisitos e demais testes.

### Critério de aceitação

Cada código `0`, `1`, `2` aparece no log com fluxo correto; o executor devolve
ou representa o código sem converter erro em sucesso.

### Teste programático

`assertLogs` e runner mockado parametrizado por `subTest` validam os três códigos.

### Comando de validação

```powershell
C:\Python313\python.exe -m unittest tests.test_service.ReturnCodeTests -v
```

### Resultado esperado

Exit code `0`; mensagens contêm fluxo e código exato para cada caso.

### Procedimento se falhar

Corrigir classificação/logging sem alterar os códigos do aplicativo; repetir e
rodar M1–M5.

## Milestone 6 — Falha não encerra scheduler

### Objetivo

Garantir que retorno de erro ou exceção em uma execução não mate o agendamento.

### Mudança esperada

Capturar exceções no limite de uma execução, registrar e voltar ao loop.

### Arquivos permitidos

`service.py`, `tests/test_service.py`, este plano.

### Arquivos que não devem ser alterados

`main.py`, `app/**`, requisitos e demais testes.

### Critério de aceitação

Após primeira chamada retornar erro e, em cenário separado, lançar exceção, uma
segunda execução ainda ocorre.

### Teste programático

Runner com `side_effect=[RuntimeError(...), 0]` e runner com retornos `[1, 0]`;
loop limitado por contador/stop fake; verificar duas chamadas e log de falha.

### Comando de validação

```powershell
C:\Python313\python.exe -m unittest tests.test_service.FailureRecoveryTests -v
```

### Resultado esperado

Exit code `0`; duas chamadas em cada cenário, sem exceção escapar do loop.

### Procedimento se falhar

Corrigir o limite de captura sem engolir `KeyboardInterrupt`/pedido de parada;
repetir e rodar M1–M6.

## Milestone 7 — Suspensão / execução atrasada

### Objetivo

Evitar duplicidade ou rajada após suspensão/retorno tardio.

### Mudança esperada

Política: executar um evento atrasado somente se tiver até 5 minutos de atraso;
descartar eventos mais antigos, registrar o descarte e calcular o próximo evento.
Cada ocorrência diária pode ser consumida no máximo uma vez.

### Arquivos permitidos

`service.py`, `tests/test_service.py`, este plano.

### Arquivos que não devem ser alterados

`main.py`, `app/**`, requisitos e demais testes.

### Critério de aceitação

Atraso de 0–5 minutos executa uma vez; atraso maior que 5 minutos não executa;
retorno muito posterior não dispara backlog; próximo evento é futuro.

### Teste programático

Relógio fake salta no tempo e verifica limites de 5 minutos, descarte, ausência
de duplicação e próxima seleção, sem suspender a máquina.

### Comando de validação

```powershell
C:\Python313\python.exe -m unittest tests.test_service.LateEventPolicyTests -v
```

### Resultado esperado

Exit code `0`; chamadas e descartes correspondem exatamente à política.

### Procedimento se falhar

Diagnosticar fronteira temporal/estado consumido, corrigir sem aumentar a janela
para satisfazer teste e rodar M1–M7.

## Milestone 8 — Proteção contra duplicidade

### Objetivo

Impedir duas instâncias do scheduler no Windows sem dependência externa.

### Mudança esperada

Implementar lock exclusivo simples por arquivo usando criação atômica
`os.open(..., O_CREAT | O_EXCL)`, com PID informativo, liberação em `finally` e
mensagem clara. Não remover lock de outra instância automaticamente na v1;
lock órfão exige decisão operacional explícita.

### Arquivos permitidos

`service.py`, `tests/test_service.py`, este plano.

### Arquivos que não devem ser alterados

`main.py`, `app/**`, requisitos e demais testes.

### Critério de aceitação

Primeiro lock é adquirido; segundo lock lógico no mesmo caminho falha; após
liberação, nova aquisição funciona. Nenhum fluxo é chamado pelo perdedor.

### Teste programático

Diretório temporário controlado e duas instâncias da classe/função de lock no
mesmo processo validam exclusividade e liberação, sem processos permanentes.

### Comando de validação

```powershell
C:\Python313\python.exe -m unittest tests.test_service.InstanceLockTests -v
```

### Resultado esperado

Exit code `0`; exclusividade e reacquisição comprovadas.

### Procedimento se falhar

Corrigir atomicidade/cleanup; se permissões do ambiente impedirem arquivo
temporário, classificar e usar pasta temporária explicitamente gravável, sem
desabilitar a proteção; rodar M1–M8.

## Milestone 9 — Encerramento controlado

### Objetivo

Permitir que o loop pare limpo sem iniciar nova tarefa.

### Mudança esperada

Usar `threading.Event` (ou equivalente padrão) para parada e espera
interrompível; `KeyboardInterrupt` no entrypoint solicita parada e libera lock.

### Arquivos permitidos

`service.py`, `tests/test_service.py`, este plano.

### Arquivos que não devem ser alterados

`main.py`, `app/**`, requisitos e demais testes.

### Critério de aceitação

Stop fake/event já marcado encerra o loop sem chamar `run`; stop durante espera
impede execução posterior e libera recursos.

### Teste programático

Event/fake wait determinístico aciona parada sem sinais reais e afirma término,
zero chamadas posteriores e cleanup do lock.

### Comando de validação

```powershell
C:\Python313\python.exe -m unittest tests.test_service.ControlledShutdownTests -v
```

### Resultado esperado

Exit code `0`; loop termina rapidamente e recursos são liberados.

### Procedimento se falhar

Corrigir checagem/espera/finally; manter verificação manual de Ctrl+C/pythonw
separada e não usá-la como substituta do teste; rodar M1–M9.

## Milestone 10 — Validação integrada segura

### Objetivo

Comprovar o ciclo completo sem sistemas externos.

### Mudança esperada

Adicionar cenário integrado somente em `tests/test_service.py` e finalizar
documentação operacional estritamente necessária após o teste passar.

### Arquivos permitidos

`service.py`, `tests/test_service.py`, este plano e, somente após aprovação do
comportamento, `README.md`/`codex-context/03-operations.md`.

### Arquivos que não devem ser alterados

`main.py`, `app/**`, requisitos e demais testes.

### Critério de aceitação

Com relógio controlado e `app.main.run` mockado, o scheduler seleciona eventos,
despacha argumentos corretos em sequência, registra `0/1/2`, sobrevive a
exceção, descarta atraso fora da janela e escolhe evento posterior.

### Teste programático

Teste integrado simula múltiplos dias/eventos, retornos e exceção; spies validam
ordem, logs, continuidade, deduplicação e próxima ocorrência. Patch explícito
faz o teste falhar se o `run` real for alcançado.

### Comando de validação

```powershell
C:\Python313\python.exe -m unittest tests.test_service.SchedulerIntegrationTests -v
C:\Python313\python.exe -m unittest tests.test_service -v
C:\Python313\python.exe -m compileall service.py app tests tools
C:\Python313\python.exe tests\run_unittest_discovery.py
```

### Resultado esperado

Testes do scheduler e compilação com exit code `0`; suíte preexistente sem novas
falhas em relação ao baseline. Nenhuma rede, navegador ou mensagem real.

### Procedimento se falhar

Classificar cada falha, corrigir a menor causa legítima e repetir primeiro o
teste integrado, depois toda a regressão M1–M10 e os testes relevantes. Não
declarar DONE enquanto houver regressão do scheduler.

## Critério objetivo de DONE

Marcar o plano concluído somente quando todas as milestones obrigatórias estão
`[x]`; todas as validações do scheduler passam; testes preexistentes relevantes
não têm regressão (e falhas antigas estão resolvidas ou explicitamente aceitas
pelo responsável); nenhum Soft4/Softdesk/Playwright/SMTP/e-mail real foi usado;
`git diff` foi revisado; não há mudança fora do escopo sem justificativa; e este
documento reflete o estado final. Inspeção visual complementa, nunca substitui,
os testes.

## Estado atual

IMPLEMENTATION COMPLETE — BASELINE RESOLVIDA. O scheduler, seus testes e a
documentação operacional foram implementados. As quatro falhas preexistentes
foram diagnosticadas e corrigidas pelo plano filho
`scheduler-production-readiness.md`; a suíte completa está verde.

## Última milestone concluída

Milestone 0, após a conclusão offline do plano filho de prontidão.

## Validações realizadas

- Validação final de prontidão: 22/22 testes do scheduler passaram.
- `compileall service.py app tests tools`: passou.
- Suíte completa final: 49/49 testes passaram (47 anteriores mais dois novos
  testes de ciclo de vida do lock).
- Nenhuma automação real, navegador ou SMTP foi executado nessa validação.

- `C:\Python313\python.exe -m compileall app tests tools`: passou.
- `C:\Python313\python.exe tests\run_unittest_discovery.py`: falhou; 14 testes
  descobertos, 2 passaram, 1 falhou e 11 tiveram erro no primeiro registro.
- Repetição com `TEMP`/`TMP` dentro do workspace: mesma classe de falhas de
  permissão e dependências; o diretório temporário de validação foi removido.
- Nenhuma automação real, navegador ou SMTP foi executado.
- Milestone 1: `ServiceImportTests` passou duas vezes; `compileall` acumulado passou.
- Milestone 2: `ScheduleCalculationTests` passou duas vezes; regressão M1+M2 passou.
- Milestone 3: `FlowDispatchTests` passou duas vezes; regressão M1–M3 passou.
- Milestone 4: após correção justificada do fixture, `SequentialExecutionTests`
  passou duas vezes e a regressão M1–M4 passou.
- Milestone 5: `ReturnCodeTests` passou duas vezes; regressão M1–M5 passou.
- Milestone 6: após correção justificada dos fixtures, `FailureRecoveryTests`
  passou duas vezes; regressão M1–M6 passou.
- Milestone 7: `LateEventPolicyTests` passou duas vezes; regressão M1–M7 passou.
- Milestone 8: após contornar somente a ACL do fixture, `InstanceLockTests`
  passou duas vezes; regressão M1–M8 passou.
- Milestone 9: `ControlledShutdownTests` passou duas vezes; regressão M1–M9 passou.
- Milestone 10: `SchedulerIntegrationTests` passou duas vezes; os 20 testes de
  `tests.test_service` e `compileall` passaram. O discovery total encontrou 34
  testes: todos os 20 novos passaram e permaneceram 11 erros e 1 falha
  preexistentes, nas mesmas categorias registradas no baseline.

## Descobertas

- Python disponível: `C:\Python313\python.exe`, versão 3.13.7.
- Dependências declaradas `python-dotenv` e `requests` não estão instaladas nesse
  interpretador; imports de testes relacionados falham.
- `tempfile.TemporaryDirectory()` sofre `PermissionError` neste ambiente mesmo
  quando `TEMP`/`TMP` aponta para o workspace.
- `test_requester_report_template_renders_with_rows` diverge do template atual
  (`Ola, Teste.` esperado versus `Ol&aacute;, Teste!` produzido), falha preexistente.
- A suíte documentada historicamente menciona 27 testes, mas o discovery atual
  registrou 14 devido a módulos que falharam durante importação.

## Decisões

- Usar `unittest`/`unittest.mock` e somente biblioteca padrão.
- Preservar `app/**`, `main.py` e os entrypoints existentes.
- Política de atraso da v1: janela inclusiva de 5 minutos; depois disso,
  descartar a ocorrência e calcular a próxima.
- Incluir lock simples de instância na v1 porque duas inicializações manuais ou
  por pasta Inicializar podem concorrer pelo mesmo perfil Chromium.
- Falhas da baseline não serão corrigidas como parte da preparação documental.
- Horários default adotados dos exemplos do guia existente: solicitantes 08:00
  e atendentes 09:00, sobrescrevíveis por `FRANK_BOT_REQUESTER_TIME` e
  `FRANK_BOT_ATTENDANT_TIME` no formato `HH:MM`.
- Na primeira validação M4, o fixture usava solicitante às 08:00 avaliado às
  09:00 e foi corretamente descartado pela política de atraso. O teste foi
  corrigido para dois eventos às 09:00; o desempate determinístico por nome
  resulta em atendente antes de solicitante. A implementação não foi afrouxada.
- A primeira validação M6 repetia o mesmo fixture vencido de M4, portanto apenas
  um runner era elegível. Os dois cenários foram corrigidos para eventos às
  09:00; as assertions de duas chamadas permaneceram estritas.
- A primeira validação M8 não alcançou o lock: `TemporaryDirectory` recebeu ACL
  sem escrita neste ambiente, conforme a limitação já registrada no baseline.
  O fixture passou a usar `.test-service-lock` explicitamente no workspace e
  removê-lo em `finally`; as assertions de exclusividade não foram alteradas.

## Problemas conhecidos

- As limitações antigas da Milestone 0 foram resolvidas; a suíte final está verde.
- Horários default foram definidos a partir do guia existente; se a operação
  desejar outros horários, usar as variáveis documentadas.
- O mutex nomeado do Windows é a fonte de exclusividade; o arquivo de PID
  residual não bloqueia uma nova instância.
- O e-mail de Rafaela Zen ainda não está mapeado no fluxo de atendentes.

## Próximo passo

O plano pai e as validações operacionais dos fluxos e de `pythonw.exe` estão
concluídos. O atalho de inicialização foi criado e validado diretamente. Resta
confirmar, após o próximo login ou reinício real, que somente uma instância é
iniciada e que o próximo evento registrado no log está correto.
