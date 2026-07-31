# VALIDATION.md — Comandos e Checkpoints de Validacao

> Confirmado com o operador: a validacao de comportamento durante a
> refatoracao (cada etapa) usara apenas testes automatizados. O operador
> humano fica responsavel por rodar `python main.py --dry-run` ao final de
> cada etapa, se desejar validar contra Soft4/SMTP reais.

## Validacao OBRIGATORIA apos cada tarefa

A validacao abaixo deve ser executada integralmente apos a edicao de cada
tarefa do TODO. Qualquer falha interrompe a tarefa.

### 1. Compilacao

```powershell
python -m compileall app tests tools
```

**Criterio de sucesso**: saida sem erros de sintaxe ou importacao. Pode haver
avisos de cache; apenas erros sao bloqueantes.

### 2. Testes unitarios

```powershell
python tests/run_unittest_discovery.py
```

Alternativa equivalente:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

**Criterio de sucesso**:
- Resultado: `OK`.
- Quantidade de testes esperada (baseline 2026-07-31): **27 testes**.
  - Baseline original (refatoracao, 2026-07-30): 12 testes.
  - Etapa 9 da refatoracao reorganizou os 12 testes em arquivos menores.
  - As etapas 1-12 do feature do solicitante adicionaram testes de API,
    entrega e relatorio do solicitante (total atual: 27).

### 3. Checagem de imports quebrados

Apos a Etapa 8 (limpeza de shims), executar verificacao por `grep` para
confirmar que nenhum import legado permanece:

```powershell
# Deve retornar VAZIO apos Etapa 8:
rg "from app\.settings import|from app\.csv_utils import|from app\.business_days import|from app\.email_queue import|from app\.cleanup import|from app\.auth import|from app\.downloader import" app tests tools
```

Permitido apos Etapas 1-7 (permanece em uso em shims). Deve retornar vazio
apos a Etapa 8. Nota: `from app\.mailer import` NAO faz parte desta checagem
— `app/mailer/` e um pacote e esses imports sao legitimos.

### 4. Diff manual de HTML dos templates (Etapa 5)

Apos a quebra do `mailer.py` (Etapa 5),.e necessario validar que os 5 HTMLs
gerados pelo mailer sao **byte-a-byte identicos** aos do snapshot inicial.

Como capturar (sem credenciais):

- Os testes atuais ja validam substrings (`assertIn` em `test_manager_report_*`,
  `test_attendant_email_*`, `test_test_email_*`, `test_dry_run_success_*`,
  `test_requester_report_*`).
- Para comparacao completa, antes da Etapa 5 o operador deve salvar (em
  `docs/snapshots/baseline-templates/` — fora do controle de versao, em
  `.gitignore`) os 5 HTMLs via um script auxiliar de mock de `_send_message`
  com `MIMEMultipart` montado.
- Apos Etapa 5, repetir e fazer `diff` com baseline.

Se o baseline nao existir, aceite como referenciado que os `assertIn` dos
testes cobrem as celulas criticas.

## Validacao OPCIONAL (responsabilidade do operador)

### Dry-run real

```powershell
python main.py --dry-run
```

Requer credenciais `SOFT4_*` e `EMAIL_*` em `.env`/`config/*.env`. Nao deve
ser executado pelo agente sem aprovacao explicita.

Pontos a conferir apos dry-run:

- Saida: codigo `0` em caso de sucesso.
- Arquivo gerado em `email_queue/YYYYMMDD_HHMMSS/queue.json` com:
  - `criado_em`
  - `csv_origem`
  - `total_itens`
  - `itens` (lista)
  - `atendentes_sem_email`
- Arquivos `<atendente>.json` com `status: "pending"` (dry-run).
- Arquivos `<atendente>.csv` com conteudo filtrado.
- Log `logs/frank_bot.log` com linhas:
  - `Iniciando automacao`
  - `Modo dry-run ativo`
  - `Dry-run: email individual seria enviado para ...`
  - `Dry-run bem-sucedido`
  - `Automacao finalizada`

### Envio de email de teste

```powershell
python tools/send_test_email.py --to <destinatario>
```

Requer SMTP valido. Nao deve ser usado pelo agente sem aprovacao.

## Interrupcao em caso de falha

Se qualquer validacao obrigatoria falhar:

1. Interromper imediatamente.
2. Nao avancar para a proxima tarefa.
3. Nao executar commit.
4. Registrar o problema em `DECISIONS.md`.
5. Apresentar a causa e uma proposta de solucao para o operador.
