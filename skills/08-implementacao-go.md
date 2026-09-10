---
name: implementacao-go
role: implementation
preferred_model_role: EXECUTOR
writes: [source_code, 06-implementation-summary.md, STATE.md]
context_loading: lazy
reads:
  - STATE.md
  - 03-prd.md
  - 04-implementation-plan.md
  - 05-red-tests.md
  - red-tests.lock
  - source_code_relevant_only
forbidden_reads:
  - chat_transcript
  - raw_discovery_logs
  - rejected_hypotheses_history
  - all_feature_artifacts
forbidden_writes:
  - locked_red_tests
  - approved_prd
  - approved_plan
  - acceptance_criteria
---

# Skill — Implementação GO / Rework

## Estados suportados

```text
IMPLEMENTING
REWORK_IMPLEMENTATION
```

### Pré-condições de `IMPLEMENTING`
- solução aprovada;
- PRD/plano aprovados;
- RED aprovado e selado;
- usuário disse `GO` ou equivalente.

### Pré-condições de `REWORK_IMPLEMENTATION`
- `JUDGE_STATUS=FAIL`;
- `JUDGE_FAIL_CLASS=IMPLEMENTATION_DEFECT`, ou recovery concluiu `DECISION=IMPLEMENTATION_ONLY`;
- RED/lock continuam válidos;
- handoff contém findings objetivos do Judge/recovery.

## Objetivo
Implementar o mínimo necessário para satisfazer o plano e levar os testes selados a GREEN.

## Regras
1. Ler `red-tests.lock` antes de editar.
2. Não modificar testes RED selados.
3. Seguir padrões válidos do projeto e arquitetura existente; preservar o estilo de build, testes,
   logging, formatação e tratamento de erro já adotados.
4. Evitar refactor fora de escopo salvo necessidade comprovada.
5. Em cross-repo, preservar contrato e ordem de deploy definida.
6. Registrar decisões emergentes em `STATE.md`.
7. Se surgir decisão arquitetural nova que muda o plano, parar e escalar ao `HEAD_STRONG`.
8. Se suspeitar que um teste RED está incorreto, **não pedir nem executar `REOPEN RED` diretamente**. Parar e rotear para `JUDGE_RECOVERY [HEAD_STRONG]`; somente esse recovery pode justificar a reabertura e pedir a autorização humana explícita `REOPEN RED`.
9. Em `REWORK_IMPLEMENTATION`, ler apenas o finding/delta necessário; não reinvestigar a história inteira nem reabrir artefatos aprovados sem necessidade.
10. Executar as unidades `PLAN-*` respeitando `DEPENDS_ON`, `AC_LINKS` e `DESIGN_DECISIONS`.
11. Preferir padrões confirmados e promovidos para `02-solution.md`/`04-implementation-plan.md`;
    divergência intencional deve ter motivo e risco registrados, nunca apenas preferência do executor.
12. Não criar arquivo, abstração ou refactor que não possa ser ligado a AC, decisão aprovada, risco ou
    necessidade técnica demonstrável.
13. Aplicar a qualidade aprovada sem transformar heurísticas de tamanho, grep ou estilo em regras
    rígidas. Preferir a menor implementação coesa, tipos/contratos claros e testes de comportamento;
    não introduzir pattern por preferência do executor.

## `06-implementation-summary.md`
Guardar somente:
- arquivos alterados;
- comportamento implementado;
- unidades `PLAN-*` concluídas e seus `AC_LINKS`;
- decisões `DD-*` aplicadas;
- decisões novas aprovadas;
- desvios do plano;
- pendências;
- riscos.

Não guardar transcript detalhado de tentativas, greps ou erros já resolvidos.


## Saída de rework

Após corrigir `REWORK_IMPLEMENTATION`:

```text
CURRENT_STATE=GREEN_VALIDATION
NEXT_ACTION=REVALIDATE_GREEN
```

Nunca retornar automaticamente a `RED_REVIEW` ou `RED_EXECUTION`.
