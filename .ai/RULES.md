# RULES.md — Regras Obrigatorias

## Fontes de verdade (em prioridade)

1. Codigo-fonte.
2. Testes.
3. Documentacao do projeto.

Em caso de divergencia entre documentacao e codigo, **registrar a divergencia
em `DECISIONS.md` antes de prosseguir**. Nao tomar decisoes automaticas.

## Proibicoes (nunca)

- Nunca alterar comportamento da aplicacao.
- Nunca alterar regras de negocio.
- Nunca alterar integracoes externas (Soft4, SMTP).
- Nunca alterar formato de entrada (env, CSV, endpoints).
- Nunca alterar formato de saida (logs, CSVs por atendente, queue.json,
  metadados JSON, HTML dos 5 e-mails, codigos de saida 0/1/2).
- Nunca adicionar funcionalidades.
- Nunca remover funcionalidades.
- Nunca alterar configuracao funcional (variaveis, defaults, lista de
  excecoes `CsvReadError`/`EmailQueueError` etc.).
- Nunca executar mais de uma tarefa do `TODO.md` por vez.
- Nunca continuar automaticamente para a proxima tarefa — encerrar a
  execucao apos atualizar PROGRESS.md.
- Nunca ler, imprimir ou resumir `.env` ou `config/*.env` (credenciais).
- Nunca executar automacao real contra Soft4/SMTP sem aprovacao explicita do
  operador.
- Nunca remover shims de compatibilidade em etapa intermediaria — aguardar a
  etapa de limpeza.

## Obrigatorios (sempre)

- Sempre justificar a alteracao (objetivo + arquivos + impacto + risco).
- Sempre manter alteracoes pequenas e incrementais.
- Sempre manter o projeto compilando (`python -m compileall app tests tools`).
- Sempre manter todos os testes verdes
  (`python tests/run_unittest_discovery.py`).
- Sempre preservar compatibilidade de imports via shims durante as etapas
  intermediarias.
- Sempre atualizar a documentacao impactada (README.md, codex-context/,
  docs/).
- Sempre atualizar `PROGRESS.md` ao final de cada tarefa.
- Sempre atualizar `DECISIONS.md` quando houver decisao tomada ou divergencia
  registrada.
- Sempre commitar UMA tarefa por commit
  ( mensagem: `refactor: etapa N - <resumo>` para refatoracao ou
  `feat: etapa N - <resumo>` para funcionalidade ).

## Tratamento de problemas

Ao encontrar codigo inesperado, documentacao desatualizada, testes
inconsistentes, conflitos de arquitetura ou riscos nao previstos:

1. Nao tomar decisoes automaticamente.
2. Registrar o problema em `DECISIONS.md` com impacto.
3. Aguardar confirmacao do operador antes de prosseguir.

## Padroes de qualidade

Priorizar, em ordem:

1. Simplicidade.
2. Baixo acoplamento.
3. Alta coesao.
4. Separacao de responsabilidades.
5. Reutilizacao de codigo existente.
6. Clareza.
7. Facilidade de manutencao.

Evitar:

- Abstracoes desnecessarias.
- Arquiteturas complexas (Clean Architecture, DDD, Hexagonal, CQRS, design
  patterns complexos).
- Over-engineering — a solucao deve ser proporcional ao tamanho do projeto.

## Critérios de conclusao de tarefa

Uma tarefa so e considerada concluida quando:

- `python -m compileall app tests tools` sem erros.
- `python tests/run_unittest_discovery.py` 100% verde (27 testes).
- Documentacao impactada foi atualizada.
- `PROGRESS.md` foi atualizado.
- Nenhum shim novo ficou pendente de uso (nao usar shims como desculpa para
  perpetuar duplicacao).
