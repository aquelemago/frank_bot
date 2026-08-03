# Operations

## Setup

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Do not print, summarize, or commit `.env`, `config/*.env`, cookies, tokens, or
browser profile data.

## Run

The automation runs as two independent services. Attendant report (attendants +
manager):

```powershell
python main.py
```

Requester report (individual per requester + full report to
`EMAIL_SOLICITANTE_TODOS_CHAMADOS`):

```powershell
python main.py --solicitante
```

Safe functional simulation:

```powershell
python main.py --dry-run
python main.py --solicitante --dry-run
```

Attendant dry-run still accesses Soft4, downloads and filters the CSV, creates
the queue, and sends a confirmation e-mail only to
`lucas.silva@mainhardt.com.br`. It does not send individual attendant e-mails
or the manager report, and queue items stay as `pending`. Requester dry-run
downloads and filters the requester CSV and logs the planned sends; it sends
no e-mails.

SMTP test only:

```powershell
python tools/send_test_email.py
```

This does not access Soft4 and does not download CSV. By default, the test is
addressed to `lucas.silva@mainhardt.com.br`; pass `--to` to override the
recipient when appropriate.

## Exit Codes

- `0`: automation finished successfully.
- `1`: general automation failure.
- `2`: configuration failure.

## Safe Validation

Syntax:

```powershell
python -m compileall app tests tools
```

Tests:

```powershell
python tests/run_unittest_discovery.py
```

Alternative:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

## Expected Logs

Logs go to the terminal and to `logs/frank_bot.log`. The file rotates at 5 MB
and keeps up to five previous files.

Representative messages:

```text
[INFO] Iniciando automacao
[INFO] Acessando fila de atendimento
[INFO] Sessao reutilizada
[INFO] CSV baixado
[INFO] Fila de email criada
[INFO] Email enviado
[INFO] Automacao finalizada
```

## Common Failures

- `Variavel obrigatoria ausente`: required configuration is missing.
- `Falha ao autenticar`: Soft4 credentials, selectors, or persistent profile may
  need review.
- `Resposta HTML recebida no lugar do CSV`: likely expired session, changed
  endpoint, invalid token, or login response.
- `CSV retornado pelo Soft4 nao contem cabecalho nem dados`: the queue search may
  have no records or the CSV endpoint may have changed.
- `CSV sem coluna de ultima interacao ou dias sem interacao`: adjust
  `CSV_COLUNA_ULTIMA_INTERACAO` or confirm the CSV export header.
- `Coluna de atendente nao encontrada`: adjust `CSV_COLUNA_ATENDENTE`.
- `Atendentes sem e-mail configurado`: add `EMAIL_NOME_DO_ATENDENTE` entries or
  adjust `EMAIL_FALHAR_SE_ATENDENTE_SEM_EMAIL`.
- `Nenhum numero de chamado encontrado no CSV do solicitante` or
  `Coluna nao encontrada no CSV do solicitante`: adjust `CSV_COLUNA_ID_CHAMADO`.
- `Chamado <n> nao encontrado na API Softdesk`: the chamado number has no
  resolvable record; the chamado is ignored and logged.
- `Rate limit da API Softdesk`: HTTP 429; the client retries after
  `Retry-After` up to `SOFT4_RETRIES`.
- `Falha ao consultar o chamado <n> na API Softdesk`: confirm
  `SOFTDESK_API_KEY` and network access to the Softdesk endpoint.
- SMTP errors: confirm host, port, username, password, MFA/app password, and
  authenticated SMTP permissions.

## Operational Safety

- Do not run the real automation against Soft4/SMTP without explicit approval of
  environment, credentials, and recipients.
- Test mailer changes with mocks or monkeypatching before any real SMTP test.
- Test Playwright/authentication changes carefully against the real screen only
  after approval.
- Do not remove `perfil_soft4/` unless requested; it may force a fresh login.
- Do not clear `downloads/` or `email_queue/` manually unless requested.

