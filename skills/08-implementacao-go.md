---
name: implementacao-go
role: implementation
preferred_model_role: EXECUTOR
writes: [source_code, 06-implementation-summary.md, STATE.md]
context_loading: lazy
reads:
  - STATE.md
  - 01-requirements.md_if_exists
  - 02-design.md_if_exists
  - 02-solution.md_if_exists
  - 03-spec.md_if_exists
  - 04-implementation-plan.md_if_exists
  - quick_contract_if_flow_mode_quick
  - 05-red-tests.md
  - red-tests.lock
  - judge_or_recovery_finding_if_rework
  - source_code_relevant_only
forbidden_reads:
  - chat_transcript
  - raw_discovery_logs
  - rejected_hypotheses_history
  - all_feature_artifacts
forbidden_writes:
  - locked_red_tests
  - approved_spec
  - approved_plan
  - acceptance_criteria
---

# Skill — Implementação GO / Rework

## Estados suportados
`IMPLEMENTING` e `REWORK_IMPLEMENTATION`.

## Contrato de entrada
No `STANDARD_GATED`, implementar contra SPEC + plano aprovados. No `QUICK_AUTOGO`, contra Quick Contract + RED selado.

### Pré-condições `IMPLEMENTING`
STANDARD: solução aprovada; SPEC/plano aprovados; RED selado; usuário disse `GO`.
QUICK: Quick Contract aprovado por `AUTO-GO`; RED selado; execução elegível ao QUICK.

### Pré-condições `REWORK_IMPLEMENTATION`
- `JUDGE_STATUS=FAIL`;
- `JUDGE_FAIL_CLASS=IMPLEMENTATION_DEFECT`, ou recovery concluiu `IMPLEMENTATION_ONLY`;
- contrato aprovado continua válido;
- RED/lock continuam válidos.

## Objetivo
Implementar o mínimo necessário para satisfazer contrato aprovado e levar testes selados a GREEN.

## Regras
1. Ler `red-tests.lock` antes de editar.
2. Não modificar testes RED selados.
3. Seguir padrões válidos do projeto.
4. Evitar refactor fora de escopo.
5. Preservar contratos/ordem de deploy cross-repo.
6. Decisão material nova escala ao `HEAD_STRONG`.
7. Suspeita de RED incorreto vai para `JUDGE_RECOVERY`.
8. Em rework, ler somente finding/delta necessário.
9. STANDARD rastreia `PLAN/AC/DD`; QUICK rastreia Quick Contract + RED.
10. Não criar abstração/refactor sem origem técnica demonstrável.
11. Preferir menor implementação coesa.

## `06-implementation-summary.md`
Guardar arquivos alterados, comportamento implementado, origem, decisões novas aprovadas, desvios e riscos.
Não guardar transcript de tentativas.

## Saída de rework

```text
CURRENT_STATE=GREEN_VALIDATION
NEXT_ACTION=REVALIDATE_GREEN
```

Nunca retornar automaticamente a RED.
