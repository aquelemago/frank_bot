# Agente: Relatório de Solicitante

## Regras

1. Código é a fonte da verdade. Leia antes de editar.
2. Uma tarefa por vez. Compile → testes → commit → pare.
3. Compilação: `python -m compileall app tests tools`
4. Testes: `python tests/run_unittest_discovery.py` (27 existentes devem continuar verdes)
5. Não alterar comportamento do relatório de atendente existente.
6. Não executar contra Soft4/SMTP real sem aprovação.
7. Mensagem de commit: `feat: etapa N - <resumo>`

## Estrutura

- `TODO.md`: lista de tarefas (única fonte de ordem)