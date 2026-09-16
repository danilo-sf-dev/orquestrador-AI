---
name: scenario-bug-desenvolvimento
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

# Cenário — Bug em desenvolvimento

## Objetivo
Corrigir comportamento ainda não produtivo com causa/evidência suficiente e teste de regressão explícito.

## Regra principal
Este cenário **não define pipeline próprio**. Estados, gates, papéis e transições vêm exclusivamente do
`orquestrador.md` e da skill atual.

## Delta deste cenário
- Intake deve separar claramente comportamento esperado x observado.
- Discovery deve tentar reproduzir/localizar a causa antes de concluir.
- Requirement Analysis só pergunta quando o comportamento esperado continuar ambíguo.
- RED deve incluir teste de regressão ligado à causa/comportamento aprovado.
- Implementação deve corrigir a causa com o menor delta suficiente.
- Archive deve preservar causa raiz, padrão de falha e prevenção quando reutilizáveis.

## Memória importante
Arquivar a causa raiz e o padrão de falha para que bugs semelhantes sejam encontrados por busca futura.

## Regra de testes unitários
Os testes RED devem incluir happy path e **edge cases aplicáveis** ao bug. Edge cases relevantes não
cobertos precisam de justificativa explícita; não criar cenários artificiais sem vínculo com critérios,
regras, contratos ou riscos.
