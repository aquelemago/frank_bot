# Runbook

## Setup

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Nao imprima nem resuma `.env` ou `config/*.env`.

## Execucao

```powershell
python main.py
```

Execucao segura sem envio de e-mails:

```powershell
python main.py --dry-run
```

O modo `--dry-run` ainda acessa o Soft4, baixa e filtra o CSV e cria a fila
com itens `pending`, mas nao chama o SMTP individual nem o relatorio gerencial.

Codigos de saida:

- `0`: automacao finalizada com sucesso.
- `1`: falha geral de automacao.
- `2`: falha de configuracao.

Nao rode a automacao real contra Soft4/SMTP sem confirmar ambiente, credenciais e destinatarios.

## Validacao Segura

Sintaxe:

```powershell
python -m compileall app tests
```

Testes:

```powershell
python tests/run_unittest_discovery.py
```

Alternativa:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

Auditoria de contexto:

```powershell
python C:\Users\lucas.silva\.codex\skills\project-context-auditor\scripts\audit_project_context.py .
```

Auditoria leve sem expor env:

```powershell
python C:\Users\lucas.silva\.codex\skills\softdesk-python-qa\scripts\audit_project.py .
```

## Logs Esperados

Os logs sao enviados ao terminal e ao arquivo rotativo
`logs/frank_bot.log`. Cada arquivo pode atingir 5 MB e ate cinco arquivos
anteriores sao mantidos.

```text
[INFO] Iniciando automacao
[INFO] Acessando fila de atendimento
[INFO] Sessao reutilizada
[INFO] CSV baixado
[INFO] Fila de email criada
[INFO] Email enviado
[INFO] Automacao finalizada
```

## Falhas Comuns

- `Variavel obrigatoria ausente`: conferir se `.env` existe e se variaveis obrigatorias foram preenchidas.
- `Falha ao autenticar`: conferir credenciais Soft4, seletores da tela de login e perfil persistente.
- `Resposta HTML recebida no lugar do CSV`: pode indicar sessao expirada, endpoint alterado, token invalido ou retorno de login.
- `CSV retornado pelo Soft4 nao contem cabecalho nem dados`: pode indicar filtro sem registros ou mudanca no endpoint.
- `Coluna de atendente nao encontrada`: conferir cabecalho real do CSV e ajustar `CSV_COLUNA_ATENDENTE`.
- `Atendentes sem e-mail configurado`: adicionar `EMAIL_NOME_DO_ATENDENTE` em `config/email_atendente.env` ou ajustar `EMAIL_FALHAR_SE_ATENDENTE_SEM_EMAIL`.
- Erro SMTP: conferir host, porta, usuario, senha, MFA/app password e permissao SMTP autenticado no Office365.

## Cuidados

- Ao mexer em e-mail, testar com monkeypatch/mock de SMTP.
- Ao mexer em Playwright, evitar execucao real sem aprovacao.
- Nao remover `perfil_soft4/` sem necessidade; isso pode exigir novo login.
- Nao limpar `downloads/` ou `email_queue/` sem pedido explicito.
- Nao tratar `.codex-audit/` como substituto do codigo; use apenas como indice para revisao.

## Skills Locais Relevantes

- `softdesk-python-qa`: QA e refatoracao conservadora deste projeto.
- `softdesk-docs-orientation`: manutencao da documentacao de contexto do Softdesk.
- `project-context-auditor`: auditoria segura do projeto e suporte a atualizacao de `codex-context/`.
