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
WAITING_GO
IMPLEMENTING
REWORK_IMPLEMENTATION
```

## `WAITING_GO`

Este estado existe somente no `STANDARD_GATED`, depois de RED válido e lockado.

Pré-condições:

```yaml
CURRENT_STATE: WAITING_GO
RED_APPROVED: true
RED_LOCKED: true
```

Neste estado:

- não editar código de produção;
- não editar testes;
- mostrar que RED está válido/selado;
- solicitar exatamente `GO`.

Após `GO`:

```yaml
GO_APPROVED: true
CURRENT_STATE: IMPLEMENTING
NEXT_ACTION: IMPLEMENT_APPROVED_CONTRACT
NEXT_MODEL_ROLE: EXECUTOR
```

Sem `GO`, permanecer em `WAITING_GO`.

## Contrato de entrada

No `STANDARD_GATED`, implementar contra SPEC + plano aprovados. No `QUICK_AUTOGO`, implementar contra o
Quick Contract aprovado + RED selado. Nunca exigir artefato STANDARD que o QUICK deliberadamente não cria.

### Pré-condições `IMPLEMENTING`

STANDARD:
- solução aprovada;
- SPEC/plano aprovados;
- RED aprovado/selado;
- `GO_APPROVED=true`.

QUICK:
- Quick Contract aprovado por `AUTO-GO`;
- RED comprovado/selado;
- execução ainda elegível ao QUICK.

### Pré-condições `REWORK_IMPLEMENTATION`
- quando originado do Judge: `JUDGE_STATUS=FAIL` + `JUDGE_FAIL_CLASS=IMPLEMENTATION_DEFECT`;
- ou recovery concluiu `DECISION=IMPLEMENTATION_ONLY`;
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
6. Se surgir decisão material nova, parar; executor não redesenha contrato.
7. Se houver indício de que requisito, SPEC/plano ou RED estão incorretos, não alterar contrato/teste nem pedir reabertura diretamente. Registrar o finding mínimo e rotear para recovery dirigido.
8. Em rework, ler somente finding/delta necessário; não reinvestigar a história inteira.
9. STANDARD: executar `PLAN-*` e rastrear `R/AC/DD`. QUICK: rastrear comportamento do Quick Contract + RED.
10. Não criar arquivo, abstração ou refactor sem ligação a requisito/contrato, decisão aprovada, risco ou necessidade técnica demonstrável.
11. Preferir a menor implementação coesa; pattern não entra por preferência do executor.

## Recovery pré-Judge

Se durante implementação surgir fato que possa invalidar contrato aprovado ou RED:

```yaml
RECOVERY_STATUS: REQUIRED
RECOVERY_SOURCE: IMPLEMENTATION
RECOVERY_CLASS: CONTRACT_MISMATCH
CURRENT_STATE: JUDGE_RECOVERY
NEXT_ACTION: ANALYZE_TARGETED_RECOVERY
NEXT_MODEL_ROLE: HEAD_STRONG
```

`JUDGE_RECOVERY` é reutilizado como recovery dirigido também antes do Judge; a skill 17 decide o menor retorno válido.

## `06-implementation-summary.md`
Guardar somente:
- arquivos alterados;
- comportamento implementado;
- origem (`PLAN/AC/DD` no STANDARD ou item do Quick Contract no QUICK);
- decisões novas já aprovadas;
- desvios do contrato/plano;
- pendências/riscos.

Não guardar transcript de tentativas, greps ou erros resolvidos.

## Transição após implementação/rework

Quando a implementação terminar sem blocker de contrato:

```yaml
CURRENT_STATE: GREEN_VALIDATION
NEXT_ACTION: VALIDATE_GREEN
NEXT_MODEL_ROLE: EXECUTOR
```

Nunca retornar automaticamente a RED.
