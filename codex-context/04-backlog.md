# Backlog E Riscos

## Pendencias Tecnicas

- Confirmar o nome exato da coluna de atendente no CSV exportado pelo Soft4 em producao.
- Confirmar o nome exato da coluna de ultima interacao no CSV exportado pelo Soft4 em producao.
- Confirmar se `requests` ainda e dependencia necessaria, pois a auditoria atual nao encontrou import direto nos arquivos Python do projeto.
- Inicializar ou conectar esta pasta a um repositorio Git se houver necessidade de rastrear diffs e historico tecnico com seguranca.
- Confirmar se o POST do CSV precisa de campos adicionais quando o Soft4 mudar a tela.
- Testar login headless com credenciais reais apos qualquer mudanca em `app/auth.py`.
- Testar envio SMTP com conta Office365 controlada antes de liberar rotina operacional.
- Adicionar testes para validacao de settings e erros de configuracao.
- Adicionar testes para leitura de CSV com delimitadores variados.
- Adicionar teste para parsing de multiplos destinatarios.

## Melhorias Recomendadas

- Criar comando de reenvio de itens `failed` sem baixar novo CSV.
- Mascarar e-mails nos logs quando logs forem compartilhados fora do time.
- Parametrizar grupos de solucao e status hoje fixos no payload.
- Documentar exemplo sanitizado de `queue.json`.
- Adicionar CI simples com `compileall` e `unittest`.
- Criar fixture CSV sanitizada para ampliar testes.
- Criar checklist operacional para atualizar `06-inventario.md` apos auditorias relevantes.

## Regras Para Mudancas Seguras

- Ler `README.md` e `codex-context/README.md` antes de alterar comportamento.
- Rodar `project-context-auditor` quando a tarefa exigir atualizar ou reorganizar contexto tecnico.
- Ler o codigo afetado antes de editar documentacao ou implementar mudancas.
- Preservar `python main.py` e `app.main.run()`.
- Nao expor segredos nem abrir arquivos sensiveis.
- Nao rodar Soft4/SMTP real sem aprovacao.
- Atualizar `05-historico.md` quando houver mudanca relevante.
