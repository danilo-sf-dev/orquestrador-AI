# 03 — Fluxos do Orquestrador

> HUMAN_ONLY. Este arquivo é para consulta do usuário e não deve ser carregado por agentes.

## Fluxo COMUM — `STANDARD_GATED`

Use quando a história/bug precisa de entendimento completo, decisões materiais ou controle maior.

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

Os principais gates são:

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

Use para mudança simples, localizada e de baixo risco.

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

O QUICK não cria apenas por formalidade os artefatos completos de Discovery, Requirements, Design,
SPEC e Plan. O contrato aprovado é o **Quick Contract**.

## Quando QUICK vira COMUM

O QUICK deve abortar para `STANDARD_GATED` se surgir algo que descaracterize uma tarefa simples, como:

- `OPEN_QUESTION` material;
- banco/migração;
- mensageria;
- segurança;
- concorrência;
- cross-repo inesperado;
- contrato material entre serviços;
- regra de negócio ambígua;
- decisão estrutural/arquitetural.

Isso não representa falha do fluxo; é proteção contra executar automaticamente uma mudança que passou
a exigir análise maior.

## Fluxo após Judge FAIL

O Judge classifica o problema antes de escolher o retorno.

```text
IMPLEMENTATION_DEFECT
    ↓
REWORK_IMPLEMENTATION
    ↓
GREEN_VALIDATION
    ↓
JUDGING fresh novamente
```

Para problemas que podem invalidar descoberta, requisito ou RED:

```text
RED_CONTRACT_DEFECT
DISCOVERY_GAP
REQUIREMENT_AMBIGUITY
    ↓
JUDGE_RECOVERY [HEAD_STRONG]
    ↓
analisa somente o finding/delta
```

O recovery pode concluir que basta corrigir implementação, que existe decisão humana pendente ou que o
RED realmente precisa ser reaberto.

Se o RED precisar mudar, o usuário deve autorizar exatamente:

```text
REOPEN RED
```

Depois disso há novo RED/lock, novo GREEN e novo Judge.

## Roteamento manual de modelos

Quando `ROUTING_MODE=manual`, uma mudança de papel pode interromper o fluxo antes da próxima etapa.
Exemplo típico:

```text
DISCOVERY [ECONOMICAL]
    ↓
handoff
    ↓
REQUIREMENT_ANALYSIS [HEAD_STRONG]
```

Outro ponto importante:

```text
GREEN_VALIDATION [EXECUTOR]
    ↓
handoff
    ↓
JUDGING [JUDGE_PRIMARY]
```

A troca existe para preservar custo e independência do Judge; não é uma nova fase funcional da história.

## Nota de legado

Em features antigas, `PRD_PLAN_REVIEW` e `APROVAR PRD/PLANO` correspondem historicamente ao que hoje é
`SPEC_PLAN_REVIEW` e `APROVAR SPEC/PLANO`.
