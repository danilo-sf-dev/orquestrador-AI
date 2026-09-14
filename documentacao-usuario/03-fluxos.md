# 03 — Fluxos do Orquestrador

> HUMAN_ONLY. Este arquivo é para consulta do usuário e não deve ser carregado por agentes.

## Fluxo COMUM — `STANDARD_GATED`

```text
JIRA_ACCESS
    ↓
INTAKE
    ↓
MEMORY_LOOKUP
    ↓
DISCOVERY
    ↓
REQUIREMENT_ANALYSIS
    ↓
INTERVIEW_OPTIONAL            # somente se pergunta bloqueante
    ↓
TECHNICAL_QUALITY_REVIEW      # somente se houver gatilho real
    ↓
SOLUTION_DESIGN
    ↓
SOLUTION_REVIEW               # APROVAR SOLUÇÃO
    ↓
SPEC_PLAN_REVIEW              # APROVAR SPEC/PLANO
    ↓
RED_REVIEW                    # APROVAR RED
    ↓
RED_EXECUTION                 # comprova RED + lock
    ↓
WAITING_GO                    # GO
    ↓
IMPLEMENTING
    ↓
GREEN_VALIDATION
    ↓
JUDGING
    ↓
QA_REVIEW
    ↓
COMMIT_REVIEW
    ↓
PR_DESCRIPTION                # somente se solicitado
    ↓
READY_TO_ARCHIVE              # ARQUIVAR
```

`INTERVIEW_OPTIONAL` e `TECHNICAL_QUALITY_REVIEW` não aparecem obrigatoriamente em toda história.
`REQUIREMENT_ANALYSIS`, `SOLUTION_DESIGN` e a revisão técnica opcional não criam novos gates humanos.

## Onde o usuário normalmente para no COMUM

```text
APROVAR SOLUÇÃO
APROVAR SPEC/PLANO
APROVAR RED
GO
APROVAR QA
modo de commit
ARQUIVAR
```

Também pode existir troca manual de modelo entre fases quando `ROUTING_MODE=manual`.

## Fluxo QUICK — `QUICK_AUTOGO`

```text
Jira
 ↓
INTAKE
 ↓
QUICK_AUTOGO
  ├─ Codebase Recon compacto
  ├─ Requirement Analysis compacta
  ├─ Senior Solution Check compacto
  └─ Quick Contract
 ↓
AUTO-GO
 ↓
RED -> comprovação RED -> lock
 ↓
implementação
 ↓
GREEN
 ↓
JUDGING
 ↓
QA se necessário
 ↓
COMMIT_REVIEW
 ↓
PR_DESCRIPTION se solicitado
 ↓
READY_TO_ARCHIVE
```

O QUICK não cria artefatos completos de Discovery, Requirements, Design, SPEC e Plan só por cerimônia.
O contrato aprovado é o **Quick Contract**.

### QUICK perde elegibilidade antes do AUTO-GO

Migra formalmente para:

```text
FLOW_MODE=STANDARD_GATED
CURRENT_STATE=MEMORY_LOOKUP
```

Isso permite que o fluxo COMUM faça memória + discovery completo antes de continuar.

### QUICK encontra problema depois que começou

Não reinicia silenciosamente como COMUM. Usa `JUDGE_RECOVERY` como recovery dirigido para descobrir o
menor ponto seguro de retorno, preservando tudo que ainda for válido.

## Recovery dirigido — antes ou depois do Judge

Apesar do nome canônico `JUDGE_RECOVERY`, essa skill pode ser acionada por:

```text
RED_EXECUTION
IMPLEMENTATION
GREEN_VALIDATION
QUICK_AUTOGO
JUDGING
```

Ela responde:

```text
O que realmente ficou inválido?
Requisito?
Solução?
SPEC/plano?
RED?
Somente implementação?
```

E retorna ao menor estado necessário:

```text
somente código       -> REWORK_IMPLEMENTATION
requisito             -> REQUIREMENT_ANALYSIS
solução               -> SOLUTION_DESIGN
SPEC/plano            -> SPEC_PLAN_REVIEW
RED sem lock          -> RED_REVIEW
RED lockado           -> REOPEN RED após reaprovar contratos superiores quando necessário
```

Se o RED precisar ser alterado depois de lockado, a autorização continua sendo exatamente:

```text
REOPEN RED
```

Depois há novo RED/lock, novo GREEN e novo Judge.

## Judge = FAIL

```text
IMPLEMENTATION_DEFECT
    ↓
REWORK_IMPLEMENTATION
    ↓
GREEN_VALIDATION
    ↓
JUDGING
```

Outras classes:

```text
RED_CONTRACT_DEFECT
DISCOVERY_GAP
REQUIREMENT_AMBIGUITY
    ↓
JUDGE_RECOVERY [HEAD_STRONG]
```

## Roteamento manual de modelos

Quando `ROUTING_MODE=manual`, mudança de papel pode interromper o fluxo antes da próxima etapa.
Exemplos:

```text
DISCOVERY [ECONOMICAL]
    ↓ MODEL_SWITCH no mesmo chat
REQUIREMENT_ANALYSIS [HEAD_STRONG]

GREEN_VALIDATION [EXECUTOR]
    ↓ MODEL_SWITCH no mesmo chat
JUDGING [JUDGE_PRIMARY]
```

A troca de modelo não é novo gate funcional e não cria nova conversa por padrão.

Se o chat estiver longo/poluído, mas o histórico ainda tiver decisões úteis, pode-se usar `COMPACT_CONTEXT`
(`/compact` no VS Code quando disponível). `FRESH_CONTEXT` fica para isolamento explícito; `/clear` no VS Code
inicia uma nova sessão e entra nessa categoria.

## RESUME

Toda fase concluída deve deixar `CURRENT_STATE` + `NEXT_ACTION` suficientes para a próxima sessão saber
qual skill carregar e qual ação executar, sem depender da memória do chat.

## Nota de legado

Em features antigas, `PRD_PLAN_REVIEW` e `APROVAR PRD/PLANO` correspondem historicamente ao que hoje é
`SPEC_PLAN_REVIEW` e `APROVAR SPEC/PLANO`.
