---
name: scenario-bug-producao
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

# Cenário — Bug de produção

## Regra de rigor
Produção exige evidência antes de edição e profundidade `CRITICAL` salvo justificativa explícita em contrário.

## Regra principal
Este cenário **não define pipeline próprio**. Estados, gates, papéis e transições vêm exclusivamente do
`orquestrador.md` e da skill atual.

## Delta deste cenário
- Intake deve registrar sintomas, ambiente, impacto, logs/requests disponíveis, versões e correlação quando existirem.
- Discovery deve trabalhar por hipóteses e evidências; stacktrace não vira causa raiz automaticamente.
- `EXECUTION_LEVEL=CRITICAL` amplia verificação de contratos, persistência/transação, integração e regressão.
- Solução deve preferir correção mínima e rollback/mitigação quando relevante.
- RED exige teste de regressão quando tecnicamente viável.
- GREEN deve executar regressão proporcional ao impacto.
- `JUDGE_SECONDARY` é recomendado para impacto alto, cross-repo, contrato crítico ou divergência material.
- Archive deve registrar causa raiz, sintomas, detecção, correção, prevenção e limitações úteis.

## Proibições
- não fazer alteração destrutiva em produção;
- não flexibilizar teste para aprovar fix;
- não permitir que Judge corrija código;
- não pular gates canônicos por urgência.

## Regra de testes unitários
Os testes RED devem incluir happy path e **edge cases aplicáveis**. Edge cases relevantes não cobertos
precisam de justificativa explícita; não criar cenários artificiais sem vínculo com critérios, regras,
contratos ou riscos.
