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

Permanent Python scheduler (requester and attendant flows run sequentially):

```powershell
python service.py
```

Daily schedule configuration uses local machine time and `HH:MM` values:

```env
FRANK_BOT_REQUESTER_TIME=08:00
FRANK_BOT_ATTENDANT_TIME=09:00
```

Those values are the defaults. On Windows, `pythonw.exe service.py` runs
without a console window. Logs continue in `logs/frank_bot.log`. Only one
instance may hold the named Windows mutex associated with
`frank_bot_service.lock`. The operating system releases the mutex when the
process ends, including after an abrupt termination. The lock file contains the
PID for diagnostics, but a residual file does not block a new instance.

An occurrence delayed by at most five minutes is executed once. Older
occurrences are discarded and the next daily occurrence is calculated. A
non-zero application return or an exception is logged without permanently
stopping the scheduler. Stop an interactive execution with `Ctrl+C`.

## Current Scheduler Deployment

- `Frank Bot Scheduler.lnk` is installed in the current user's Startup folder.
- The shortcut uses the virtual environment's `pythonw.exe`, the absolute path
  to `service.py`, and the project root as its working directory.
- Target, arguments, working directory, startup through the shortcut, named
  mutex protection, and duplicate-instance rejection were validated on
  2026-08-13.
- The requester and attendant production flows both completed with exit code
  `0` during authorized validation.
- The remaining production-readiness check is to confirm, after the next real
  login or reboot, that exactly one instance starts and the next event in
  `logs/frank_bot.log` is correct.
- Rafaela Zen currently has no attendant e-mail mapping. Her attendant rows are
  skipped while `EMAIL_FALHAR_SE_ATENDENTE_SEM_EMAIL` allows continuation.

After a login or reboot, verify the scheduler with the PID stored in
`frank_bot_service.lock` and inspect the latest log entries. Do not start a
second permanent instance manually.

## Running State And Operator Commands

The deployed application runs as one permanent `pythonw.exe` process without a
console. It is launched by `Frank Bot Scheduler.lnk` from the current user's
Startup folder. The shortcut targets:

```text
C:\Users\node.js\Desktop\PRD\frank\frank_bot\.venv\Scripts\pythonw.exe
```

Its argument is the absolute path to `service.py`, and its working directory is
the project root. The default daily schedule is requester at `08:00` and
attendant at `09:00`, using local machine time. These values come from the
scheduler process environment and are not loaded automatically from `.env`.

Start interactively from the project root:

```powershell
.\.venv\Scripts\python.exe service.py
```

Stop an interactive instance with `Ctrl+C`. Start without a console:

```powershell
.\.venv\Scripts\pythonw.exe service.py
```

Inspect the deployed process and recent activity:

```powershell
$schedulerPid = [int](Get-Content .\frank_bot_service.lock -Raw)
Get-Process -Id $schedulerPid
Get-Content .\logs\frank_bot.log -Tail 30
```

Before stopping a background instance, verify that this PID belongs to the Frank
Bot `pythonw` process. Then stop only that exact PID:

```powershell
$schedulerPid = [int](Get-Content .\frank_bot_service.lock -Raw)
Get-Process -Id $schedulerPid
Stop-Process -Id $schedulerPid
```

Restart it with `pythonw.exe service.py` or invoke the Startup shortcut. A stale
PID file after forced termination is diagnostic only; the named Windows mutex is
released by the operating system and remains the source of truth for exclusivity.

To run one flow directly instead of the permanent scheduler:

```powershell
.\.venv\Scripts\python.exe main.py --solicitante
.\.venv\Scripts\python.exe main.py
```

These direct commands access Soft4 and may send real e-mails. Confirm the
environment and recipients before running them.

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

Scheduler tests only (all external execution is mocked):

```powershell
python -m unittest tests.test_service -v
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

