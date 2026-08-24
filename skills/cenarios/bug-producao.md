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
Produção exige evidência antes de edição e julgamento reforçado.

## Pipeline
1. Confirmar modelos e usar JUDGE_SECONDARY quando disponível.
2. Intake: sintomas, horário, ambiente, impacto, logs, requests, correlação, versões.
3. Memory-first por endpoint/erro/feature relacionada.
4. HEAD_STRONG define hipóteses e evidências necessárias; não implementa.
5. ECONOMICAL faz investigação dirigida.
6. HEAD_STRONG consolida causa raiz provável/confirmada e solução mínima.
7. Aprovar solução + plano.
8. Criar regression RED e selar.
9. GO -> EXECUTOR implementa correção mínima.
10. GREEN + regressão proporcional ao risco.
11. Judge primário fresh-context read-only.
12. Judge secundário para impacto alto/cross-repo/contrato crítico.
13. QA/reprodução orientada.
14. Archive: causa raiz, sintomas, detecção, correção, prevenção, limitações.

## Proibições
- não tratar stacktrace como causa raiz automaticamente;
- não fazer alteração destrutiva em produção;
- não flexibilizar teste para aprovar fix;
- não permitir que juiz corrija código.


## Regra de testes unitários
Os testes RED devem incluir happy path e **edge cases aplicáveis** à história/bug. Edge cases relevantes não cobertos precisam de justificativa explícita; não criar cenários artificiais sem vínculo com critérios, regras, contratos ou riscos.
