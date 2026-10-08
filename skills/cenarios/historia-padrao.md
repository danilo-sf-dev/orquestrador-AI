---
name: scenario-historia-padrao
load_mode: on_demand
context_loading: lazy
reads:
  - STATE.md
  - scenario_signal_only
forbidden_reads:
  - chat_transcript
  - unrelated_feature_artifacts
writes:
  - STATE.md
---

# Cenário — História padrão

## Quando usar
Nova história Jira com critérios de aceite e, frequentemente, endpoint/arquitetura indicada.

## Regra principal
Este cenário **não define pipeline próprio**. Estados, gates, papéis e transições vêm exclusivamente do
`orquestrador.md` e da skill atual.

## Delta deste cenário
- usar `STANDARD` como profundidade inicial quando não houver sinal de risco maior ou menor;
- começar Discovery pelas âncoras do Jira, especialmente endpoint/controller/componente citado;
- manter Requirement Analysis + Solution Design proporcionais ao escopo;
- preservar todos os gates canônicos do fluxo `STANDARD_GATED`;
- usar `JUDGE_SECONDARY` somente se surgir risco que justifique reforço.

## Otimização
Se endpoint já estiver no Jira, Discovery começa por ele. Não indexar workspace inteiro sem necessidade.

## Regra de testes unitários
Os testes RED devem incluir happy path e **edge cases aplicáveis** à história/bug. Edge cases relevantes
não cobertos precisam de justificativa explícita; não criar cenários artificiais sem vínculo com
critérios, regras, contratos ou riscos.
