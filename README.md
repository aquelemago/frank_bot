# Automacao Soft4 - CSV Por Atendente

Automacao Python para acessar a fila de atendimento do Soft4/Mainhardt, baixar o
CSV de chamados sem interacao do atendente, aplicar filtro local por dias uteis,
separar a fila por atendente e enviar e-mails via SMTP com os anexos
correspondentes. Em execucao real, tambem envia um relatorio consolidado para a
gestora e um relatorio de chamados sem interacao do solicitante.

## Para Agentes De IA

Comece por `CODEX_START_HERE.md`.

Regras importantes:

- O codigo e a fonte de verdade.
- Nao leia, imprima ou resuma valores de `.env` ou `config/*.env`.
- Nao exponha credenciais, cookies, tokens, perfil do navegador, CSVs
  operacionais ou dados de fila gerada.
- Nao rode a automacao real contra Soft4/SMTP sem aprovacao explicita.

## Requisitos

- Windows com PowerShell.
- Python 3.11+.
- Playwright.
- Chromium instalado pelo Playwright.
- Acesso ao Soft4/Mainhardt.
- Conta SMTP com permissao de envio.

## Instalacao

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Dependencias declaradas:

- `playwright>=1.44.0`
- `python-dotenv>=1.0.1`
- `requests>=2.31.0`

Observacao: `requests` e usado pelo cliente da API Softdesk
(`app/soft4/api.py`) para o relatorio do solicitante.

## Configuracao

Crie ou preencha `.env` na raiz do projeto. Nao versionar este arquivo.

```env
SOFT4_USUARIO=
SOFT4_SENHA=

EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USUARIO=
EMAIL_SENHA=

CSV_COLUNA_ATENDENTE=atendente
CSV_COLUNA_ULTIMA_INTERACAO=ultima interacao
SOFT4_TP_LISTAGEM=SEM_INTERACAO_ATENDENTE
SOFT4_DIAS_SEM_INTERACAO_ATENDENTE=3
SOFT4_FERIADOS_ADICIONAIS=
EMAIL_ATENDENTES_FILE=config/email_atendente.env
EMAIL_FALHAR_SE_ATENDENTE_SEM_EMAIL=false
EMAIL_GESTORA_RELATORIO=francieli.cazuni@unus.solutions
NOME_GESTORA_RELATORIO=Francieli

CSV_COLUNA_ULTIMA_INTERACAO_SOLICITANTE=ultima interacao solicitante
SOFT4_TP_LISTAGEM_SOLICITANTE=SEM_INTERACAO_SOLICITANTE
SOFT4_DIAS_SEM_INTERACAO_SOLICITANTE=5
CSV_COLUNA_ID_CHAMADO=ID
SOFTDESK_API_KEY=
EMAIL_SOLICITANTE_RELATORIO=lcabral570@gmail.com
NOME_SOLICITANTE_RELATORIO=Teste
EMAIL_SOLICITANTE_TODOS_CHAMADOS=lcabral570@gmail.com
```

Quando `SOFTDESK_API_KEY` estiver preenchida, o relatorio do solicitante e
enviado individualmente para cada solicitante. A automacao consulta a API do
Softdesk (`GET /api/api.php/chamado?codigo=<numero do chamado>`, cabecalho
`hash-api`) para obter o e-mail do solicitante de cada chamado do CSV, agrupa os
chamados por e-mail e envia um relatorio por destinatario. `CSV_COLUNA_ID_CHAMADO`
indica a coluna com o numero do chamado. Alem dos solicitantes, o relatorio com
todos os chamados tambem e enviado para `EMAIL_SOLICITANTE_TODOS_CHAMADOS`
(quando preenchida). Sem a chave, mantem o comportamento legado de enviar um
unico relatorio para `EMAIL_SOLICITANTE_RELATORIO`.

Mapeie atendentes em `config/email_atendente.env`:

```env
EMAIL_NOME_DO_ATENDENTE=atendente@empresa.com.br
```

Exemplos de normalizacao:

```text
Lucas Cabral da Silva -> EMAIL_LUCAS_CABRAL_DA_SILVA
Patricia Konig Costa -> EMAIL_PATRICIA_KONIG_COSTA
```

Variaveis opcionais:

```env
SOFT4_BASE_URL=https://mainhardt.soft4.com.br
SOFT4_FILA_PATH=/chamado/fila-de-atendimento
SOFT4_CSV_PATH=/chamado/fila-de-atendimento/csv
SOFT4_TIMEOUT_SECONDS=60
SOFT4_RETRIES=3
SOFT4_API_PATH=/api/api.php
```

Compatibilidade legada:

- `config/email_bot.env` ainda pode fornecer valores SMTP antigos.
- `EMAIL_REMETENTE` pode ser usado como alternativa para `EMAIL_USUARIO`.
- `SENHA` pode ser usada como alternativa para `EMAIL_SENHA`.
- `SMTP_HOST` e `SMTP_PORT` podem ser usados como alternativas para
  `EMAIL_HOST` e `EMAIL_PORT`.

## Regra De Dias Uteis

O Soft4 e consultado com `SOFT4_DIAS_SEM_INTERACAO_ATENDENTE` como pre-filtro.
Depois do download, a automacao filtra o CSV localmente e so mantem chamados com
pelo menos esse limite em dias uteis sem interacao.

A contagem:

- comeca no dia seguinte a ultima interacao;
- inclui a data atual quando ela for dia util;
- ignora sabados, domingos e feriados nacionais do Brasil;
- ignora datas configuradas em `SOFT4_FERIADOS_ADICIONAIS`.

Configure `CSV_COLUNA_ULTIMA_INTERACAO` se o CSV exportado trouxer uma coluna
especifica de ultima interacao. Quando essa coluna nao existe, a automacao usa a
coluna `Dias sem interacao` como fallback para inferir a data aproximada.

`SOFT4_FERIADOS_ADICIONAIS` aceita datas separadas por virgula ou ponto e
virgula nos formatos `AAAA-MM-DD` ou `DD/MM/AAAA`.

O mesmo filtro por dias uteis e aplicado ao CSV do solicitante, usando
`SOFT4_DIAS_SEM_INTERACAO_SOLICITANTE` como limite e
`CSV_COLUNA_ULTIMA_INTERACAO_SOLICITANTE` como coluna de ultima interacao. O
download usa `SOFT4_TP_LISTAGEM_SOLICITANTE` como pre-filtro no Soft4.

## Execucao

A automacao roda como dois servicos independentes, como no sistema anterior.

Relatorio do atendente (envio para os atendentes e a gestora):

```powershell
python main.py
```

Relatorio do solicitante (envio individual para cada solicitante e relatorio
completo para `EMAIL_SOLICITANTE_TODOS_CHAMADOS`):

```powershell
python main.py --solicitante
```

Scheduler permanente, com os dois fluxos sequenciais:

```powershell
python service.py
```

Horarios diarios do scheduler, no formato `HH:MM`:

```env
FRANK_BOT_REQUESTER_TIME=08:00
FRANK_BOT_ATTENDANT_TIME=09:00
```

Esses sao tambem os horarios padrao quando as variaveis nao existem. No
Windows, `pythonw.exe service.py` pode ser usado para executar sem janela de
console. O processo deve ser iniciado a partir da raiz do projeto. Ele impede
uma segunda instancia por um mutex nomeado do Windows. O arquivo
`frank_bot_service.lock` contem apenas o PID para diagnostico; um arquivo
residual nao impede uma nova instancia depois que o processo anterior termina.

O scheduler executa eventos atrasados em no maximo cinco minutos. Eventos mais
antigos sao descartados e a proxima ocorrencia diaria e calculada, evitando uma
rajada de envios depois de suspensao prolongada. Retornos ou excecoes de uma
execucao sao registrados e nao encerram as proximas execucoes.

Na instalacao operacional atual, o atalho `Frank Bot Scheduler.lnk` na pasta
Inicializar do usuario executa o scheduler com o `pythonw.exe` da `.venv`. A
configuracao do atalho foi validada; ainda e necessario confirmar uma unica
instancia e o proximo evento no log depois do proximo login ou reinicio real.

Se o log registrar `Atendentes sem e-mail configurado`, esses atendentes nao
recebem relatorio individual quando a configuracao permite continuar. Complete
o mapeamento `EMAIL_NOME_DO_ATENDENTE` ou habilite a falha obrigatoria antes de
considerar a entrega completa.

### Como a aplicacao esta rodando

Atualmente, a aplicacao roda como um processo permanente `pythonw.exe`, sem
janela de terminal. O processo foi iniciado pelo atalho:

```text
Frank Bot Scheduler.lnk
```

O atalho fica na pasta Inicializar do usuario e aponta para:

```text
C:\Users\node.js\Desktop\PRD\frank\frank_bot\.venv\Scripts\pythonw.exe
```

com o argumento:

```text
C:\Users\node.js\Desktop\PRD\frank\frank_bot\service.py
```

e usa a raiz do projeto como diretorio de trabalho. Depois do login do usuario,
o Windows inicia esse atalho automaticamente. O scheduler mantem um unico
processo, aguarda os horarios diarios e executa os fluxos sequencialmente:

```text
08:00 - solicitantes
09:00 - atendentes
```

O acompanhamento deve ser feito em `logs/frank_bot.log`. O PID atual e gravado
em `frank_bot_service.lock`; nao documente nem reutilize um PID antigo, pois ele
muda sempre que o processo reinicia.

### Como iniciar manualmente

Abra o PowerShell na raiz do projeto. Para executar com terminal visivel:

```powershell
.\.venv\Scripts\python.exe service.py
```

Use `Ctrl+C` para encerrar essa forma de execucao.

Para executar em segundo plano, sem janela:

```powershell
.\.venv\Scripts\pythonw.exe service.py
```

Nao inicie manualmente se o atalho ja tiver criado uma instancia. A segunda
instancia sera rejeitada, mas deve-se evitar tentativas desnecessarias.

### Como verificar, parar e reiniciar

Para verificar o PID registrado e confirmar o processo:

```powershell
$schedulerPid = [int](Get-Content .\frank_bot_service.lock -Raw)
Get-Process -Id $schedulerPid
Get-Content .\logs\frank_bot.log -Tail 30
```

Para parar uma instancia sem janela, confirme primeiro que o PID pertence ao
`pythonw` do Frank Bot e entao execute:

```powershell
$schedulerPid = [int](Get-Content .\frank_bot_service.lock -Raw)
Get-Process -Id $schedulerPid
Stop-Process -Id $schedulerPid
```

Depois, para reiniciar sem janela:

```powershell
.\.venv\Scripts\pythonw.exe service.py
```

Uma finalizacao forcada pode deixar `frank_bot_service.lock` no disco, mas o
arquivo e apenas informativo. O mutex do Windows e liberado automaticamente e a
nova instancia pode sobrescrever o PID residual.

Dry-run:

```powershell
python main.py --dry-run
python main.py --solicitante --dry-run
```

O dry-run acessa o Soft4, baixa e filtra o CSV do respectivo relatorio e registra
nos logs quais envios seriam feitos, sem enviar e-mails. No relatorio do
atendente, apos uma simulacao bem-sucedida, envia apenas uma confirmacao para
`lucas.silva@mainhardt.com.br`; os itens da fila permanecem como `pending`. No
relatorio do solicitante, nenhum e-mail e enviado em dry-run.

Teste SMTP:

```powershell
python tools/send_test_email.py
```

Esse comando nao acessa o Soft4 e nao baixa CSV. Ele usa somente as
configuracoes SMTP de `.env` ou `config/email_bot.env`. Para enviar a outro
destinatario:

```powershell
python tools/send_test_email.py --to pessoa@empresa.com.br
```

Codigos de saida:

- `0`: sucesso.
- `1`: falha geral.
- `2`: falha de configuracao.

## Validacao

Validacao rapida de sintaxe:

```powershell
python -m compileall app tests tools
```

Testes unitarios:

```powershell
python tests/run_unittest_discovery.py
```

Testes isolados do scheduler (sem Soft4 ou SMTP):

```powershell
python -m unittest tests.test_service -v
```

Alternativa:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

## Estrutura

```text
.
|-- README.md
|-- CODEX_START_HERE.md
|-- main.py
|-- requirements.txt
|-- codex-context/
|   |-- README.md
|   |-- 01-overview.md
|   |-- 02-architecture.md
|   |-- 03-operations.md
|   |-- 04-decisions.md
|   |-- 05-backlog.md
|   `-- 06-inventory.md
|-- docs/
|   `-- superpowers/specs/
|-- app/
|   |-- main.py                 # CLI (argparse + --dry-run); reexporta run
|   |-- orchestrator/           # fluxo da automacao (run)
|   |-- services/               # facade (envio de e-mail + fila)
|   |-- config/                 # dataclasses + carregamento de env
|   |-- csv/                    # leitura de CSV + filtro de dias uteis
|   |-- queue/                  # dominio da fila de e-mail
|   |-- mailer/                 # transporte SMTP + templates + relatorio
|   |-- soft4/                  # integracao externa (Playwright/Soft4) + API Softdesk
|   |-- requester/              # entregas do relatorio por solicitante via API
|   `-- infra/                  # logging, cleanup e helpers de filesystem
|-- tests/
`-- tools/
```

## Saidas Geradas

CSVs baixados:

```text
downloads/fila_atendimento_YYYYMMDD_HHMMSS.csv
downloads/solicitante_YYYYMMDD_HHMMSS.csv
```

Fila de e-mail:

```text
email_queue/YYYYMMDD_HHMMSS/
|-- queue.json
|-- <atendente>.csv
`-- <atendente>.json
```

Logs:

```text
logs/frank_bot.log
```

O log tem rotacao automatica ao atingir 5 MB e mantem ate cinco arquivos
anteriores.

## Documentacao Tecnica

- `CODEX_START_HERE.md`: entrada segura para IA.
- `codex-context/README.md`: indice tecnico.
- `codex-context/01-overview.md`: objetivo, escopo, regras de negocio, entradas
  e saidas.
- `codex-context/02-architecture.md`: fluxo, modulos, configuracao e efeitos
  colaterais.
- `codex-context/03-operations.md`: runbook, validacao e troubleshooting.
- `codex-context/04-decisions.md`: decisoes arquiteturais e comportamentais.
- `codex-context/05-backlog.md`: riscos, debitos e melhorias.
- `codex-context/06-inventory.md`: inventario auditavel do estado atual.

## Cuidados Operacionais

- `.env` e `config/*.env` contem dados sensiveis.
- `perfil_soft4/` guarda sessao persistente do Chromium.
- `downloads/`, `email_queue/` e `logs/` podem conter dados operacionais.
- O navegador roda com `headless=True`.
- Nao alterar seletores de login sem testar contra a tela real.
- Nao remover `perfil_soft4/` sem necessidade; isso pode exigir novo login.
- Nao enviar testes para SMTP real sem confirmacao dos destinatarios.

