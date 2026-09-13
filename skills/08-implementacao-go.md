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

```text
IMPLEMENTING
REWORK_IMPLEMENTATION
```

## Contrato de entrada

No `STANDARD_GATED`, implementar contra SPEC + plano aprovados. No `QUICK_AUTOGO`, implementar contra o
Quick Contract aprovado + RED selado. Nunca exigir artefato STANDARD que o QUICK deliberadamente não cria.

### Pré-condições `IMPLEMENTING`

STANDARD:
- solução aprovada;
- SPEC/plano aprovados;
- RED aprovado/selado;
- usuário disse `GO`.

QUICK:
- Quick Contract aprovado por `AUTO-GO`;
- RED comprovado/selado;
- execução ainda elegível ao QUICK.

### Pré-condições `REWORK_IMPLEMENTATION`
- `JUDGE_STATUS=FAIL`;
- `JUDGE_FAIL_CLASS=IMPLEMENTATION_DEFECT`, ou recovery concluiu `DECISION=IMPLEMENTATION_ONLY`;
- contrato aprovado da modalidade continua válido;
- RED/lock continuam válidos;
- handoff contém finding objetivo.

## Objetivo
Implementar o mínimo necessário para satisfazer o contrato aprovado e levar os testes selados a GREEN.

## Regras
1. Ler `red-tests.lock` antes de editar.
2. Não modificar testes RED selados.
3. Seguir padrões válidos do projeto e arquitetura existente.
4. Evitar refactor fora de escopo salvo necessidade comprovada.
5. Em cross-repo, preservar contrato e ordem de deploy definida.
6. Se surgir decisão material nova, parar e escalar ao `HEAD_STRONG`; executor não redesenha contrato.
7. Se suspeitar que RED está incorreto, não alterar nem pedir reabertura diretamente: rotear para `JUDGE_RECOVERY`.
8. Em rework, ler somente finding/delta necessário; não reinvestigar a história inteira.
9. STANDARD: executar `PLAN-*` e rastrear `R/AC/DD`. QUICK: rastrear comportamento do Quick Contract + RED.
10. Não criar arquivo, abstração ou refactor sem ligação a requisito/contrato, decisão aprovada, risco ou necessidade técnica demonstrável.
11. Preferir a menor implementação coesa; pattern não entra por preferência do executor.

## `06-implementation-summary.md`
Guardar somente:
- arquivos alterados;
- comportamento implementado;
- origem (`PLAN/AC/DD` no STANDARD ou item do Quick Contract no QUICK);
- decisões novas já aprovadas;
- desvios do contrato/plano;
- pendências/riscos.

Não guardar transcript de tentativas, greps ou erros resolvidos.

## Saída de rework

```text
CURRENT_STATE=GREEN_VALIDATION
NEXT_ACTION=REVALIDATE_GREEN
```

Nunca retornar automaticamente a RED.
