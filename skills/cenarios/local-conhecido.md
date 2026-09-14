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

## Regra principal
Este cenário **não define pipeline próprio**. Estados, gates, papéis e transições vêm exclusivamente do
`orquestrador.md` e da skill atual.

## Delta deste cenário
1. Fazer Memory Lookup normalmente quando o fluxo exigir.
2. Discovery curto e dirigido para validar dependências, comportamento atual e testes relacionados.
3. Pular entrevista quando não houver `OPEN_QUESTION` bloqueante.
4. Manter Requirement Analysis e Senior Solution Check curtos quando o contrato já estiver claro.
5. Não remover `APROVAR SOLUÇÃO`, `APROVAR SPEC/PLANO`, `APROVAR RED` ou `GO` do fluxo COMUM.

## Objetivo
Economizar input por conhecimento do ponto de alteração, sem pular controles de qualidade.

## Regra de testes unitários
Os testes RED devem incluir happy path e **edge cases aplicáveis**. Edge cases relevantes não cobertos
precisam de justificativa explícita; não criar cenários artificiais sem vínculo com critérios, regras,
contratos ou riscos.
