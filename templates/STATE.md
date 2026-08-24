# STATE — <JIRA-ID>

> Criar este arquivo somente depois que o `JIRA-ID` for conhecido no fluxo NEW. Em RESUME, atualizar o STATE existente.

## Identidade
- JIRA:
- TITLE:
- SHORT_DESCRIPTION:
- LIFECYCLE: ACTIVE # ACTIVE | PAUSED | DONE
- CURRENT_STATE: MODEL_CONFIRMATION
- NEXT_ACTION: BOOTSTRAP
- SCENARIO:
- EXECUTION_LEVEL: STANDARD # FAST | STANDARD | CRITICAL; controla profundidade, nunca gates

## Sessão / roteamento
- MODEL_ROLES_CONFIRMED_THIS_SESSION: false
- ROUTING_MODE: automatic # automatic | manual

> Não persistir `model-profile` global. O binding papel -> modelo é resolvido pela sessão/runtime.

## Orçamento
- MONTHLY_BUDGET_USD: 40
- FEATURE_TARGET_USD: 8
- FEATURE_WARNING_USD: 10
- COST_OBSERVED_USD:

## Métricas acumuladas
- INPUT_TOKENS:
- CACHE_READ_TOKENS:
- OUTPUT_TOKENS:
- CACHE_HIT_RATIO:
- MODEL_ESCALATIONS:
- DURATION:
- COST_BY_ROLE:
- COST_BY_PHASE:

## Critérios de aceite
- [ ] AC1
- [ ] AC2

## Âncoras
- ENDPOINTS:
- CONTROLLERS_CLASSES:
- ARCHITECTURE_DOCS:
- LOGS_ERRORS:

## Repositórios
- PRIMARY:
- RELATED:

## Fluxo atual compactado

## Contratos

## Decisões aprovadas

## Related features / memória reutilizada

## Aprovações
- SOLUTION_APPROVED: false
- PRD_PLAN_APPROVED: false
- RED_APPROVED: false
- RED_LOCKED: false
- RED_LOCK_FILE: red-tests.lock
- GO_APPROVED: false
- QA_APPROVED: false
- ARCHIVE_APPROVED: false

## Status de validação
- BUILD:
- UNIT_TESTS:
- GREEN_STATUS:
- JUDGE_STATUS:
- JUDGEMENT_STALE: false
- QA_STATUS:

## Commit
- COMMIT_POLICY: ask
- FEATURE_MEMORY_COMMIT_POLICY: ask
- COMMIT_STATUS: PENDING
- COMMITS_BY_REPO:
- COMMIT_RECORD: delivery/commit.md

## Pull Request
- PR_POLICY: explicit_request_only
- PR_STATUS: NOT_REQUESTED
- PR_SOURCE_BRANCH:
- PR_TARGET_BRANCH:
- PR_PROVIDER:
- PR_NUMBER:
- PR_URL:
- RELATED_PRS:
- PR_RECORD: delivery/pull-request.md

## Pendências

## Riscos / limitações

## Resume
- LAST_COMPLETED_PHASE:
- RESUME_HINT:
