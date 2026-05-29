# Projeto

## Objetivo

Automacao Python para acompanhar a fila de atendimento do Soft4/Mainhardt,
baixar um CSV filtrado de chamados sem interacao do atendente, separar os
registros por atendente, enviar e-mails individuais com anexos e enviar um
relatorio consolidado para a gestora.

## Estado Atual

- Codigo principal em `app/`.
- Entrada publica: `python main.py`.
- Auditoria segura em 2026-05-26 encontrou 13 arquivos Python e 9 arquivos Markdown versionaveis/tecnicos, ignorando artefatos runtime e arquivos sensiveis.
- Playwright Chromium roda em `headless=True`.
- Sessao persistente em `perfil_soft4/`.
- CSV completo salvo em `downloads/fila_atendimento_YYYYMMDD_HHMMSS.csv`.
- Fila por execucao em `email_queue/YYYYMMDD_HHMMSS/`.
- Cada atendente recebe um CSV filtrado.
- A gestora recebe relatorio consolidado com CSV completo em anexo.
- O e-mail individual pede revisao prioritaria de chamados sem interacao.
- O fluxo antigo `src/extrair_chamados.py` -> `data/chamados.json` foi removido.
- Dependencias declaradas: `playwright`, `python-dotenv` e `requests`.
- Testes atuais cobrem fila por atendente, e-mail individual, relatorio gerencial, normalizacao e regra de dias uteis.

## Escopo

O projeto faz:

1. Carrega configuracoes de `.env`.
2. Carrega compatibilidade com `config/email_bot.env` e `config/email_atendente.env`.
3. Cria diretorios de runtime quando necessario.
4. Abre Chromium persistente via Playwright.
5. Reutiliza cookies e sessao em `perfil_soft4/`.
6. Detecta tela de login por campo de senha.
7. Faz login quando necessario.
8. Captura CSRF/cookies/headers a partir da pagina autenticada.
9. Executa a pesquisa filtrada via `fetch` dentro da pagina.
10. Baixa o CSV com o mesmo payload filtrado.
11. Remove CSVs antigos de `downloads/`.
12. Salva o CSV completo timestampado.
13. Filtra o CSV por chamados com 3 ou mais dias uteis sem interacao.
14. Le o CSV com deteccao de delimitador.
15. Resolve a coluna de atendente por nome configurado ou fallback contendo `ATENDENTE`.
16. Agrupa registros por atendente.
17. Resolve destinatarios por `EMAIL_NOME_DO_ATENDENTE`.
18. Remove filas antigas de `email_queue/`.
19. Cria uma fila nova por execucao.
20. Gera CSV individual e JSON de metadados por atendente.
21. Envia e-mail individual para cada atendente.
22. Envia relatorio gerencial consolidado para a gestora.
23. Marca itens como `pending`, `sent` ou `failed`.
24. Retorna codigo de saida conforme sucesso, erro geral ou erro de configuracao.
25. Remove caches Python locais no inicio e no fim.

Fora de escopo atual:

- Nao altera chamados no Soft4.
- Nao usa Selenium, PyAutoGUI ou automacao visual.
- Nao mantem historico de filas antigas.
- Nao possui modo `dry-run`.
- Nao possui reenvio isolado de itens `failed`.
- Nao executa agendamento nativo.

## Regras De Negocio

- O filtro padrao e `SEM_INTERACAO_ATENDENTE`.
- O prazo padrao e 3 dias uteis sem interacao do atendente.
- A data da ultima interacao nao conta; a contagem comeca no dia seguinte.
- A data atual conta se for dia util.
- Dias uteis excluem sabados, domingos, feriados nacionais do Brasil e feriados adicionais configurados.
- `SOFT4_FERIADOS_ADICIONAIS` aceita datas extras configuraveis.
- Se a coluna configurada em `CSV_COLUNA_ULTIMA_INTERACAO` existir e a data estiver vazia/invalida, o registro e ignorado e a ocorrencia e logada.
- Se o CSV nao trouxer coluna de ultima interacao, a automacao usa `Dias sem interacao` como fallback para inferir a data aproximada a partir da data da exportacao.
- Atendentes sem e-mail podem bloquear a fila se `EMAIL_FALHAR_SE_ATENDENTE_SEM_EMAIL=true`.
- Quando `EMAIL_FALHAR_SE_ATENDENTE_SEM_EMAIL=false`, atendentes sem e-mail entram em `atendentes_sem_email` no resumo e sao ignorados no envio individual.
- O relatorio gerencial usa o CSV completo filtrado localmente, nao apenas os itens com e-mail resolvido.

## Sistema Externo

- URL base padrao: `https://mainhardt.soft4.com.br`
- Fila de atendimento: `/chamado/fila-de-atendimento`
- Endpoint JSON da pesquisa: `/chamado/fila-de-atendimento/json`
- Endpoint CSV: `/chamado/fila-de-atendimento/csv`

## Entradas E Saidas

Entradas:

- `.env` na raiz, sem versionar.
- `config/email_bot.env` para compatibilidade SMTP legada.
- `config/email_atendente.env` para mapa de atendentes.
- Sessao/cookies persistidos em `perfil_soft4/`.
- CSV retornado pelo Soft4 via POST autenticado.

Saidas:

- `downloads/fila_atendimento_YYYYMMDD_HHMMSS.csv`.
- `email_queue/YYYYMMDD_HHMMSS/queue.json`.
- `email_queue/YYYYMMDD_HHMMSS/<atendente>.csv`.
- `email_queue/YYYYMMDD_HHMMSS/<atendente>.json`.
- E-mails SMTP para atendentes e gestora quando a automacao real e executada.
