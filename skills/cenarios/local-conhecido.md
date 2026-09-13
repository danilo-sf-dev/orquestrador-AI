---
name: scenario-local-conhecido
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

# Cenário — Local de alteração conhecido

## Quando usar
O Jira já informa endpoint/controller/componente e o código confirma claramente o ponto de atuação.

## Otimização
1. Memory lookup.
2. Discovery curto e dirigido apenas para validar dependências e testes.
3. Pular entrevista se não houver ambiguidade.
4. Se a solução for trivial e não houver decisão arquitetural, HEAD ainda revisa a proposta de solução de forma curta antes do gate.
5. Continuar SPEC/plano -> RED -> GO -> GREEN -> Judge -> QA -> Commit -> Archive.

## Objetivo
Economizar input sem pular gates de qualidade.

## Regra de testes unitários
Os testes RED devem incluir happy path e **edge cases aplicáveis** à história/bug. Edge cases relevantes não cobertos precisam de justificativa explícita; não criar cenários artificiais sem vínculo com critérios, regras, contratos ou riscos.
