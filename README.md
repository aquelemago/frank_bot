# Automacao Soft4 - Exportacao CSV Por Atendente

Automacao Python para acessar a fila de atendimento do Soft4/Mainhardt, baixar o CSV filtrado de chamados sem interacao do atendente, separar a fila por atendente e enviar e-mails via Office365 com os anexos correspondentes. Ao final, tambem envia um relatorio consolidado para a gestora.

## Leitura Para IA

Agentes de IA devem comecar por `CODEX_START_HERE.md`.
Este `README.md` e apenas o guia humano e operacional.

Nao leia, imprima ou resuma valores de `.env` ou `config/*.env`.

## Objetivo

O fluxo operacional atual:

1. Carrega configuracoes locais.
2. Abre Chromium via Playwright em modo headless.
3. Reutiliza a sessao persistente do Soft4 quando possivel.
4. Faz login automaticamente quando a sessao expira.
5. Acessa a fila de atendimento.
6. Executa a pesquisa filtrada por chamados sem interacao do atendente.
7. Baixa o CSV por POST autenticado.
8. Mantem apenas o CSV completo mais recente em `downloads/`.
9. Cria uma fila nova em `email_queue/YYYYMMDD_HHMMSS/`.
10. Gera um CSV por atendente.
11. Envia e-mail individual para cada atendente.
12. Envia relatorio consolidado para a gestora.
13. Registra status `pending`, `sent` ou `failed` em JSON.
14. Remove caches Python locais ao iniciar e finalizar.

## Requisitos

- Windows com PowerShell.
- Python 3.11+ funcional.
- Playwright.
- Chromium instalado pelo Playwright.
- Acesso ao Soft4/Mainhardt.
- Conta SMTP Office365 com permissao de envio.

## Instalacao

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Dependencias declaradas em `requirements.txt`:

- `playwright`
- `python-dotenv`
- `requests`

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
```

Mapeie atendentes em `config/email_atendente.env`:

```env
EMAIL_NOME_DO_ATENDENTE=atendente@empresa.com.br
```

Exemplo de normalizacao:

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
```

Compatibilidade legada:

- `config/email_bot.env` ainda pode fornecer valores SMTP antigos.
- `EMAIL_REMETENTE` pode ser usado como alternativa para `EMAIL_USUARIO`.
- `SENHA` pode ser usada como alternativa para `EMAIL_SENHA`.
- `SMTP_HOST` e `SMTP_PORT` podem ser usados como alternativas para `EMAIL_HOST` e `EMAIL_PORT`.

## Regra De Dias Uteis

O Soft4 continua sendo consultado com `SOFT4_DIAS_SEM_INTERACAO_ATENDENTE` como
pre-filtro. Depois do download, a automacao filtra o CSV localmente e so mantem
chamados com pelo menos esse limite em dias uteis sem interacao.

A contagem:

- comeca no dia seguinte a ultima interacao;
- inclui a data atual quando ela for dia util;
- ignora sabados, domingos e feriados nacionais do Brasil;
- ignora tambem datas configuradas em `SOFT4_FERIADOS_ADICIONAIS`.

Configure `CSV_COLUNA_ULTIMA_INTERACAO` se o CSV exportado trouxer uma coluna
especifica de ultima interacao. Quando essa coluna nao existe, a automacao usa a
coluna `Dias sem interacao` como fallback para inferir a data aproximada.

`SOFT4_FERIADOS_ADICIONAIS` aceita datas separadas por virgula ou ponto e
virgula nos formatos `AAAA-MM-DD` ou `DD/MM/AAAA`.

## Execucao

```powershell
python main.py
```

Para baixar e processar o CSV, criar a fila e validar a rotina sem enviar
nenhum e-mail:

```powershell
python main.py --dry-run
```

Codigos de saida:

- `0`: automacao finalizada com sucesso.
- `1`: falha geral de automacao.
- `2`: falha de configuracao.

## Testes E Validacao

Validacao rapida de sintaxe:

```powershell
python -m compileall app tests
```

Testes unitarios:

```powershell
python tests/run_unittest_discovery.py
```

Alternativa:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

Auditoria leve do projeto:

```powershell
python C:\Users\lucas.silva\.codex\skills\softdesk-python-qa\scripts\audit_project.py .
```

Nao rode a automacao real contra Soft4/SMTP sem confirmar que as credenciais e destinatarios estao corretos.

## Estrutura

```text
.
|-- README.md
|-- CODEX_START_HERE.md
|-- main.py
|-- requirements.txt
|-- codex-context/
|   |-- README.md
|   |-- 01-projeto.md
|   |-- 02-arquitetura.md
|   |-- 03-runbook.md
|   |-- 04-backlog.md
|   |-- 05-historico.md
|   `-- 06-inventario.md
|-- app/
|   |-- __init__.py
|   |-- auth.py
|   |-- business_days.py
|   |-- cleanup.py
|   |-- csv_utils.py
|   |-- downloader.py
|   |-- email_queue.py
|   |-- mailer.py
|   |-- main.py
|   `-- settings.py
|-- config/
|   |-- email_bot.env
|   `-- email_atendente.env
|-- downloads/
|-- email_queue/
|-- perfil_soft4/
`-- tests/
```

## Modulos Principais

- `main.py`: ponto de entrada publico; chama `app.main.main()`.
- `app/main.py`: interpreta `--dry-run` e orquestra setup, login, download,
  fila, envio e limpeza.
- `app/settings.py`: carrega `.env`, arquivos legados, dataclasses e diretorios.
- `app/auth.py`: gerencia Playwright, sessao persistente, login e headers.
- `app/downloader.py`: executa POST autenticado e salva o CSV completo.
- `app/csv_utils.py`: normaliza chaves, le CSV e resolve colunas.
- `app/email_queue.py`: separa CSV por atendente e grava metadados.
- `app/mailer.py`: monta e envia e-mails SMTP; o e-mail individual ao atendente
  informa chamados sem interacao ha 3 dias ou mais e pede revisao prioritaria.
- `app/cleanup.py`: remove `__pycache__` fora de `.venv` e `perfil_soft4`.

## Saidas Geradas

CSV completo:

```text
downloads/fila_atendimento_YYYYMMDD_HHMMSS.csv
```

Fila de e-mail:

```text
email_queue/YYYYMMDD_HHMMSS/
|-- queue.json
|-- <atendente>.csv
`-- <atendente>.json
```

`queue.json` resume a execucao. Cada `<atendente>.json` registra destinatario, CSV, quantidade de registros, status e erro quando houver.

## Logs

Os logs sao exibidos no terminal e gravados em:

```text
logs/frank_bot.log
```

O arquivo possui rotacao automatica ao atingir 5 MB, mantendo ate cinco
arquivos anteriores.

Exemplos esperados:

```text
[INFO] Iniciando automacao
[INFO] Acessando fila de atendimento
[INFO] Sessao reutilizada
[INFO] CSV baixado
[INFO] Fila de email criada
[INFO] Email enviado
[INFO] Automacao finalizada
```

## Cuidados Operacionais

- `.env` e `config/*.env` contem dados sensiveis.
- `perfil_soft4/` guarda sessao persistente do Chromium.
- `downloads/` e `email_queue/` sao recriados parcialmente a cada execucao.
- O navegador roda com `headless=True`.
- Nao alterar seletores de login sem testar contra a tela real.
- Nao remover `perfil_soft4/` sem necessidade; isso pode exigir novo login.
- Nao enviar testes para SMTP real sem monkeypatch/mock.

## Documentacao De Contexto

Agentes de IA devem iniciar por `CODEX_START_HERE.md`.
O indice tecnico oficial fica em `codex-context/README.md`.
