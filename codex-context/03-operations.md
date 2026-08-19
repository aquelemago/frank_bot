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

## Recommended Windows Deployment

Production scheduling uses two independent Windows Task Scheduler tasks rather
than a permanently sleeping Python process:

```text
08:00 - \FrankBot\Frank Bot - Solicitantes -> main.py --solicitante
09:00 - \FrankBot\Frank Bot - Atendentes   -> main.py
```

The host must remain powered on and connected to the required corporate
network. Use a dedicated, least-privileged technical account. Do not use
`SYSTEM`; the Playwright profile and network access must belong to the
operational identity.

Deployment status on 2026-08-19: both tasks were registered and validated by
the elevated installer, the legacy Startup shortcut was removed, and no report
was executed during installation. The remaining acceptance step is to inspect
Task Scheduler history and the application log after the next natural 08:00
and 09:00 windows.

Validate locally without registering or executing tasks:

```powershell
.\tools\install_windows_scheduled_tasks.ps1 -ValidateOnly
```

Install from an elevated PowerShell. Windows prompts securely for the technical
account credential:

```powershell
.\tools\install_windows_scheduled_tasks.ps1 -RemoveLegacyStartupShortcut
```

Optional schedule parameters are `-RequesterTime HH:mm` and
`-AttendantTime HH:mm`. The installer is idempotent and validates the registered
actions. It sets the project root as working directory, uses the virtual
environment Python, limits each run to one hour, and configures
`MultipleInstances=IgnoreNew`. It deliberately disables delayed starts and
automatic retries to prevent late or duplicate e-mails.

The legacy Startup shortcut is removed only after both tasks validate and only
when its target is confirmed as this project's `pythonw.exe service.py`.
`service.py` remains a fallback in the repository, but must not run concurrently
with the Windows tasks.

Inspect definitions and last results without triggering a real send:

```powershell
Get-ScheduledTask -TaskPath "\FrankBot\"
Get-ScheduledTaskInfo -TaskPath "\FrankBot\" -TaskName "Frank Bot - Solicitantes"
Get-ScheduledTaskInfo -TaskPath "\FrankBot\" -TaskName "Frank Bot - Atendentes"
Get-Content .\logs\frank_bot.log -Tail 30
```

Validate and execute rollback:

```powershell
.\tools\uninstall_windows_scheduled_tasks.ps1 -ValidateOnly
.\tools\uninstall_windows_scheduled_tasks.ps1
```

The uninstaller only addresses the two managed task names and requires
confirmation. It does not restart the legacy scheduler.

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
- Requester report contains unexpected chamados: confirm the effective request
  uses groups `[118, 257]`, status `[8]`, listing type
  `SEM_INTERACAO_SOLICITANTE`, and 3 days. The Softdesk API only resolves
  requester e-mails and does not select report rows.
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

