# Guia de Execução

Este documento descreve como executar a automação Frank Bot para enviar relatórios para atendentes e solicitantes.

## Pré-requisitos

1. **Configurações**: Certifique-se de que os seguintes arquivos estão configurados:
   - `.env` na raiz do projeto
   - `config/email_bot.env` com credenciais SMTP
   - `config/email_atendente.env` com mapeamento de emails de atendentes
   - `assinatura.png` na raiz do projeto (para assinatura nos emails)

2. **Dependências**: Instale as dependências do projeto:
   ```bash
   pip install -r requirements.txt
   ```

3. **Arquivo de assinatura**: O arquivo `assinatura.png` deve estar presente na raiz do projeto para que a assinatura apareça nos emails.

## Modos de Execução

### 1. Envio para Atendentes

Envia relatórios para atendentes com chamados sem interação.

**Comando:**
```bash
python main.py
```

**O que faz:**
- Baixa o CSV de chamados sem interação de atendentes
- Filtra chamados com 3 dias úteis sem interação (configurável)
- Envia email individual para cada atendente com seus chamados
- Envia relatório consolidado para a gestora
- Salva os arquivos na pasta `email_queue/`

**Configurações relevantes:**
- `SOFT4_DIAS_SEM_INTERACAO_ATENDENTE`: Dias sem interação (padrão: 3)
- `EMAIL_GESTORA_RELATORIO`: Email da gestora
- `EMAIL_FALHAR_SE_ATENDENTE_SEM_EMAIL`: Falhar se atendente não tiver email

### 2. Envio para Solicitantes

Envia relatórios para solicitantes com chamados sem interação.

**Comando:**
```bash
python main.py --solicitante
```

**O que faz:**
- Baixa o CSV de chamados sem interação de solicitantes
- Filtra chamados com 5 dias úteis sem interação (configurável)
- Consulta a API do Softdesk para obter emails dos solicitantes
- Envia email individual para cada solicitante com seus chamados
- Inclui a assinatura da Mainhardt no email
- Salva os arquivos na pasta `downloads/` com prefixo `solicitante_`

**Configurações relevantes:**
- `SOFT4_DIAS_SEM_INTERACAO_SOLICITANTE`: Dias sem interação (padrão: 5)
- `SOFTDESK_API_KEY`: Chave para consultar emails dos solicitantes
- `EMAIL_SOLICITANTE_RELATORIO`: Email padrão para relatório de solicitantes
- `EMAIL_SOLICITANTE_TODOS_CHAMADOS`: Email para cópia do relatório completo

### 3. Modo Dry-Run (Teste)

Executa o fluxo sem enviar emails reais (exceto confirmação de dry-run).

**Para atendentes:**
```bash
python main.py --dry-run
```

**Para solicitantes:**
```bash
python main.py --solicitante --dry-run
```

**O que faz:**
- Executa todas as etapas de download e processamento
- Cria a fila de emails na pasta `email_queue/`
- Não envia emails para atendentes ou solicitantes
- Envia apenas um email de confirmação para `lucas.silva@mainhardt.com.br`

### 4. Teste de Email

Envia um email de teste para verificar as configurações SMTP.

**Comando:**
```bash
python tools/send_test_email.py --to SEU_EMAIL@DOMINIO.COM
```

**O que faz:**
- Envia um email de teste com a assinatura da Mainhardt
- Verifica se as configurações SMTP estão funcionando
- Não acessa o Soft4 nem processa CSV

## Verificação de Resultados

Após a execução, verifique:

1. **Logs**: `logs/frank_bot.log` para detalhes da execução
2. **Downloads**: `downloads/` para os arquivos CSV baixados
3. **Fila de emails**: `email_queue/` para os arquivos gerados (em modo dry-run)
4. **Caixa de entrada**: Verifique se os emails foram recebidos

## Solução de Problemas

**Problema: Assinatura não aparece no email**
- Verifique se `assinatura.png` existe na raiz do projeto
- Verifique as permissões do arquivo
- Teste com `python tools/send_test_email.py`

**Problema: Emails não são enviados**
- Verifique as configurações SMTP em `.env` e `config/email_bot.env`
- Verifique os logs em `logs/frank_bot.log`
- Teste a conexão SMTP com `python tools/send_test_email.py`

**Problema: CSV não é baixado**
- Verifique as credenciais do Soft4 em `.env`
- Verifique se o navegador está autenticado (pasta `perfil_soft4/`)
- Verifique a conexão com a internet

## Agendamento

Para agendar execuções automáticas, você pode usar o cron (Linux) ou Task Scheduler (Windows).

Exemplo de cron para executar diariamente às 8h:
```bash
0 8 * * * /caminho/para/o/projeto/venv/bin/python /caminho/para/o/projeto/main.py --solicitante
```

Exemplo para atendentes:
```bash
0 9 * * * /caminho/para/o/projeto/venv/bin/python /caminho/para/o/projeto/main.py
```

## Notas Importantes

1. A assinatura é adicionada automaticamente a todos os emails de solicitantes e testes
2. Os emails de atendentes não incluem assinatura (apenas solicitantes)
3. Em modo dry-run, nenhum email é enviado para atendentes ou solicitantes (exceto confirmação)
4. Os arquivos CSV são salvos em `downloads/` com timestamp
5. A fila de emails é salva em `email_queue/` com timestamp
