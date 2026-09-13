# 03 — Fluxos do Orquestrador

> HUMAN_ONLY. Este arquivo é para consulta do usuário e não deve ser carregado por agentes.

## Fluxo COMUM — `STANDARD_GATED`

```text
JIRA_ACCESS              Acesso ao Jira
    ↓
INTAKE                   Triagem do Jira
    ↓
MEMORY_LOOKUP            Consulta de memória relacionada
    ↓
DISCOVERY                Investigação dirigida do código
    ↓
REQUIREMENT_ANALYSIS     Análise de requisitos e lacunas
    ↓
INTERVIEW_OPTIONAL       Somente se houver pergunta realmente bloqueante
    ↓
TECHNICAL_QUALITY_REVIEW Somente quando houver gatilho arquitetural real
    ↓
SOLUTION_DESIGN          Desenho técnico da menor solução sólida
    ↓
SOLUTION_REVIEW          Revisão da solução → APROVAR SOLUÇÃO
    ↓
SPEC_PLAN_REVIEW         SPEC + plano → APROVAR SPEC/PLANO
    ↓
RED_REVIEW               Desenho do RED → APROVAR RED
    ↓
RED_EXECUTION            Criação/execução dos testes RED + lock
    ↓
WAITING_GO               Aguarda GO
    ↓
IMPLEMENTING             Implementação
    ↓
GREEN_VALIDATION         Validação mecânica do GREEN
    ↓
JUDGING                  Judge independente, fresh/read-only
    ↓
QA_REVIEW                QA → APROVAR QA
    ↓
COMMIT_REVIEW            AUTOMÁTICO | MANUAL | OUTROS
    ↓
PR_DESCRIPTION           Somente se solicitado; gera texto, não abre PR remoto
    ↓
READY_TO_ARCHIVE         Pronto para arquivamento/memória final
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
triagem/contexto mínimo
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
handoff para JUDGE_PRIMARY
 ↓
JUDGING
 ↓
QA se necessário
 ↓
COMMIT_REVIEW
 ↓
PR_DESCRIPTION se solicitado
 ↓
archive
```

O QUICK não cria por formalidade artefatos completos de Discovery, Requirements, Design, SPEC e Plan.
O contrato aprovado é o **Quick Contract**.

## Quando QUICK vira COMUM

O QUICK aborta para `STANDARD_GATED` se surgir `OPEN_QUESTION` material, banco/migração, mensageria,
segurança, concorrência, cross-repo inesperado, contrato material, regra de negócio ambígua ou decisão arquitetural.

## Fluxo após Judge FAIL

```text
IMPLEMENTATION_DEFECT
    ↓
REWORK_IMPLEMENTATION
    ↓
GREEN_VALIDATION
    ↓
JUDGING fresh novamente
```

Para `RED_CONTRACT_DEFECT`, `DISCOVERY_GAP` ou `REQUIREMENT_AMBIGUITY`:

```text
JUDGE_RECOVERY [HEAD_STRONG]
```

Se o RED precisar mudar, o usuário autoriza exatamente `REOPEN RED`; depois há novo RED/lock, GREEN e Judge.

## Roteamento manual de modelos

Mudança de papel pode interromper o fluxo para troca manual de modelo, por exemplo:

```text
DISCOVERY [ECONOMICAL]
-> REQUIREMENT_ANALYSIS [HEAD_STRONG]

GREEN_VALIDATION [EXECUTOR]
-> JUDGING [JUDGE_PRIMARY]
```

A troca preserva custo e independência; não é fase funcional adicional.
