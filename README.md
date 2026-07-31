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

Observacao: `requests` esta declarado, mas o codigo atual nao possui import
direto dele. Confirme impacto operacional antes de remover.

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
EMAIL_SOLICITANTE_RELATORIO=lcabra570@gmail.com
NOME_SOLICITANTE_RELATORIO=Teste
```

Quando `SOFTDESK_API_KEY` estiver preenchida, o relatorio do solicitante e
enviado individualmente para cada solicitante. A automacao consulta a API do
Softdesk (`GET /api/api.php/chamado?codigo=<numero do chamado>`, cabecalho
`hash-api`) para obter o e-mail do solicitante de cada chamado do CSV, agrupa os
chamados por e-mail e envia um relatorio por destinatario. `CSV_COLUNA_ID_CHAMADO`
indica a coluna com o numero do chamado. Sem a chave, mantem o comportamento
legado de enviar um unico relatorio para `EMAIL_SOLICITANTE_RELATORIO`.

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

Execucao real:

```powershell
python main.py
```

Dry-run:

```powershell
python main.py --dry-run
```

O dry-run acessa o Soft4, baixa e filtra os CSVs do atendente e do solicitante,
cria a fila e registra nos logs quais envios seriam feitos. Ele nao envia
e-mails individuais nem os relatorios gerencial e do solicitante; apos uma
simulacao bem-sucedida, envia apenas uma confirmacao para
`lucas.silva@mainhardt.com.br`. Os itens da fila permanecem como `pending`.

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

