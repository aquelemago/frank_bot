# Plano: migracao profissional para o Agendador de Tarefas do Windows

Estado: **INSTALADO — MILESTONE 6 AGUARDANDO PROXIMA JANELA**

## Painel de progresso

| Milestone | Entrega | Estado | Evidencia de aceite |
|---|---|---|---|
| 0 | Auditar implantacao atual | ✅ Concluida | Atalho de Inicializar e scheduler Python identificados |
| 1 | Criar instalador seguro e idempotente | ✅ Concluida | Validacao offline e parser PowerShell verdes |
| 2 | Criar procedimento de remocao e rollback | ✅ Concluida | Remocao limitada aos nomes gerenciados |
| 3 | Atualizar documentacao | ✅ Concluida | Arquitetura, operacao e decisao coerentes |
| 4 | Executar regressao | ✅ Concluida | Testes Python, scripts e diff verdes |
| 5 | Instalar no Windows | ✅ Concluida | Duas tarefas validadas e atalho legado removido sem executar fluxos |
| 6 | Validar proxima execucao | ⬜ Nao iniciada | Historico, codigo de saida e log aprovados sem envio duplicado |

## Objetivo

Substituir o processo permanente iniciado por atalho no login por duas tarefas
diarias independentes no Agendador do Windows:

- `Frank Bot - Solicitantes`, executando `main.py --solicitante`;
- `Frank Bot - Atendentes`, executando `main.py`.

As tarefas devem usar o Python da `.venv`, a raiz do projeto como diretorio de
trabalho, uma conta operacional informada de forma interativa e a politica de
nao iniciar uma segunda instancia. Nao deve haver repeticao automatica, pois
uma repeticao depois de falha parcial pode duplicar e-mails.

## Guardrails

- Nunca registrar senha em arquivo, argumento documentado, log ou Git.
- Solicitar a credencial diretamente pelo prompt seguro do Windows.
- Nao executar as tarefas como parte da instalacao.
- Nao acessar Soft4, Softdesk ou SMTP durante validacao/instalacao.
- Nao usar `SYSTEM`, devido ao privilegio excessivo e ao perfil persistente do
  Chromium; usar uma conta tecnica com acesso minimo necessario.
- Nao habilitar `StartWhenAvailable`: uma maquina religada horas depois nao
  deve disparar e-mails atrasados.
- Nao habilitar repeticao automatica.
- Remover o atalho legado somente depois de as duas tarefas terem sido
  registradas e validadas, e apenas quando seu destino for confirmado como o
  `service.py` deste projeto.
- Preservar `service.py` como fallback ate a validacao operacional final.

## Milestone 0 — auditoria

Evidencia em 2026-08-19:

- o runbook registra `Frank Bot Scheduler.lnk` na pasta Inicializar;
- o atalho inicia `.venv\Scripts\pythonw.exe service.py`;
- a aplicacao ja oferece os entrypoints independentes necessarios;
- `service.py` usa mutex via `kernel32`, portanto nao e portavel diretamente
  para container Linux;
- nenhuma integracao externa foi executada nesta auditoria.

## Milestone 1 — instalador

Criar `tools/install_windows_scheduled_tasks.ps1` com:

- modo `-ValidateOnly` sem credencial e sem mutacao;
- horarios parametrizaveis, com defaults `08:00` e `09:00`;
- validacao de Python, `main.py`, horarios e conta informada;
- solicitacao interativa de `PSCredential` apenas no modo de instalacao;
- registro idempotente das duas tarefas;
- diretorio de trabalho explicito;
- `MultipleInstances=IgnoreNew`;
- limite de execucao de uma hora;
- execucao em background mesmo sem login, usando logon por senha;
- verificacao programatica das acoes e dos gatilhos registrados;
- opcao controlada para remover o atalho legado depois do sucesso.

## Milestone 2 — rollback

Criar `tools/uninstall_windows_scheduled_tasks.ps1` com modo de validacao e
remocao somente das duas tarefas e da pasta gerenciada, sem tocar em outras
tarefas nem reiniciar o scheduler legado.

## Milestone 3 — documentacao

Atualizar README e `codex-context` para:

- declarar o Agendador do Windows como implantacao recomendada;
- documentar instalacao, verificacao, troca segura e rollback;
- explicar a necessidade de uma maquina sempre ligada e conta tecnica;
- manter `service.py` documentado como fallback, nao como implantacao padrao;
- registrar a decisao arquitetural.

## Milestone 4 — regressao

Validar programaticamente:

```powershell
powershell -NoProfile -Command { parser dos scripts }
.\tools\install_windows_scheduled_tasks.ps1 -ValidateOnly
.\tools\uninstall_windows_scheduled_tasks.ps1 -ValidateOnly
.\.venv\Scripts\python.exe tests\run_unittest_discovery.py
git diff --check
```

## Milestone 5 — instalacao

Requer prompt interativo local para a credencial da conta tecnica. Depois do
registro, validar as duas definicoes sem executa-las. Remover o atalho legado
somente pela opcao segura do instalador. Se a conta tecnica ainda nao existir,
esta milestone fica bloqueada sem improvisar uma identidade privilegiada.

## Milestone 6 — validacao operacional

Na proxima janela real, confirmar uma unica execucao de cada tarefa pelo
Historico do Agendador e por novas linhas do log. Nao disparar manualmente como
substituto sem gate de envio, pois os comandos enviam e-mails reais.

## Descobertas e decisoes

- O Agendador do Windows e mais adequado que um processo Python permanente
  para dois jobs diarios.
- Docker foi adiado: exigiria adaptar o mutex Windows, persistencia do perfil
  Playwright, volumes, segredos e agendamento externo.
- A instalacao nao pode ser concluida de forma segura sem uma conta operacional
  e sua credencial fornecida diretamente ao Windows.
- O instalador e o rollback passaram no parser do PowerShell sem erros. Os dois
  modos `-ValidateOnly` passaram sem registrar, executar ou remover tarefas.
- A regressao passou com 57/57 testes Python e `git diff --check` sem erros; o
  instalador tambem rejeitou programaticamente um horario fora de `HH:mm`.
- O preflight do Windows encontrou zero tarefas em `\FrankBot\`, confirmou o
  atalho legado presente e mostrou que o processo atual nao esta elevado.
- O responsavel executou o instalador em PowerShell elevado. A saida registrou
  `TASK_VALIDATED` para solicitantes e atendentes, confirmou a remocao do atalho
  legado, terminou com `INSTALLATION=PASSOU` e confirmou
  `TASKS_EXECUTED=NAO`. Nenhuma credencial foi copiada para a documentacao.
- Uma consulta independente posterior recebeu `Acesso negado` porque o processo
  do agente nao esta elevado. A falha foi classificada como limitacao de
  permissao da sessao de verificacao; ela nao contradiz a validacao elevada e
  reproduzivel feita pelo proprio instalador.

## Bloqueios

Nenhum bloqueio de instalacao. A Milestone 6 depende da passagem natural da
proxima janela aprovada: 08:00 para solicitantes e 09:00 para atendentes. Nao
executar manualmente apenas para antecipar essa evidencia, pois isso enviaria
e-mails reais.
