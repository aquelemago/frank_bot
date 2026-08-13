# Regras permanentes para agentes

- Leia `CODEX_START_HERE.md` antes de trabalhar e depois localize o plano da tarefa.
- Trate os planos em `codex-context/plans/` como fonte de verdade da implementação.
- Entenda o código real antes de modificá-lo e respeite estritamente o escopo do plano.
- Não faça refatorações não solicitadas nem instale dependências sem necessidade explícita; prefira a biblioteca padrão do Python.
- Mantenha mudanças pequenas e use Git/diff para conferir exatamente o que mudou.
- Valide cada milestone programaticamente. Nunca conclua uma milestone apenas por inspeção visual.
- Uma milestone só está concluída quando seu critério de aceitação puder ser demonstrado por uma validação programática reproduzível.
- Falha de teste é um problema a ser diagnosticado e corrigido, não um motivo para avançar no plano.
- Ao falhar: classifique a causa, corrija implementação ou teste conforme a causa comprovada e repita teste -> diagnóstico -> correção -> teste até passar. Não avance enquanto a milestone atual ou a regressão acumulada falhar.
- Não mascare testes, não remova assertions para obter sucesso e não altere testes para aceitar comportamento incorreto.
- Após cada milestone, rode novamente seu teste, os testes das milestones anteriores e os testes relevantes preexistentes.
- Atualize o progresso somente depois da validação passar e registre descobertas e decisões relevantes no próprio plano.
- Não execute Soft4, Playwright/Chromium contra produção, SMTP, e-mails ou qualquer automação externa real sem autorização explícita.

Fluxo obrigatório:

```text
IMPLEMENTAR -> EXECUTAR TESTE -> PASSOU?
SIM: executar regressão, atualizar o plano e seguir.
NÃO: identificar causa -> corrigir -> repetir o mesmo teste até passar.
```
