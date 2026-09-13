# 04 — Estados e etapas

> HUMAN_ONLY. Este arquivo é para consulta do usuário e não deve ser carregado por agentes.

Use este arquivo quando aparecer um nome como `INTAKE`, `SPEC_PLAN_REVIEW` ou `GREEN_VALIDATION`.
Os nomes em português são traduções humanas; o valor canônico continua sendo o identificador em inglês.

## Referência rápida

| Estado canônico | Tradução humana | Skill principal | Papel |
|---|---|---|---|
| `MODEL_CONFIRMATION` | Confirmação de modelos | `00-bootstrap-modelos.md` | ORCHESTRATOR |
| `JIRA_ACCESS` | Acesso ao Jira | `15-jira-access.md` | `ECONOMICAL` |
| `INTAKE` | Triagem do Jira | `01-intake-jira.md` | `ECONOMICAL` |
| `MEMORY_LOOKUP` | Consulta de memória | `02-memoria-feature.md` | `ECONOMICAL` |
| `DISCOVERY` | Investigação | `03-investigacao.md` | `ECONOMICAL` |
| `REQUIREMENT_ANALYSIS` | Análise de requisitos | `04a-analise-requisitos.md` | `HEAD_STRONG` |
| `INTERVIEW_OPTIONAL` | Entrevista opcional | `04-entrevista-opcional.md` | `HEAD_STRONG` |
| `TECHNICAL_QUALITY_REVIEW` | Revisão de qualidade técnica | `18-qualidade-arquitetural.md` | `HEAD_STRONG` |
| `SOLUTION_DESIGN` | Desenho da solução | `04b-design-solucao.md` | `HEAD_STRONG` |
| `SOLUTION_REVIEW` | Revisão da solução | `05-solucao-proposta.md` | `HEAD_STRONG` |
| `SPEC_PLAN_REVIEW` | Revisão da SPEC e plano | `06-spec-plano.md` | `HEAD_STRONG` |
| `RED_REVIEW` | Revisão do contrato RED | `07-testes-red.md` | `EXECUTOR` |
| `RED_EXECUTION` | Execução do RED | `07-testes-red.md` | `EXECUTOR` |
| `WAITING_GO` | Aguardando GO | `08-implementacao-go.md` | `EXECUTOR` |
| `IMPLEMENTING` | Implementação | `08-implementacao-go.md` | `EXECUTOR` |
| `REWORK_IMPLEMENTATION` | Correção da implementação | `08-implementacao-go.md` | `EXECUTOR` |
| `GREEN_VALIDATION` | Validação GREEN | `09-validacao-green.md` | `EXECUTOR` |
| `JUDGING` | Julgamento independente | `10-juiz.md` | `JUDGE_PRIMARY` |
| `JUDGE_RECOVERY` | Recuperação pós-Judge | `17-judge-recovery.md` | `HEAD_STRONG` |
| `QA_REVIEW` | Revisão de QA | `11-qa-pack.md` | `EXECUTOR` |
| `COMMIT_REVIEW` | Revisão/execução de commits | `12-commit-workflow.md` | `EXECUTOR` |
| `PR_DESCRIPTION` | Descrição de PR/MR | `13-pull-request-workflow.md` | `EXECUTOR` |
| `READY_TO_ARCHIVE` | Pronto para arquivar | `14-arquivamento.md` | `ECONOMICAL` |
| `QUICK_AUTOGO` | Execução rápida AUTO-GO | `16-quick-autogo.md` | `EXECUTOR` |

## `MODEL_CONFIRMATION` — Confirmação de modelos
Bootstrap da sessão: resolve retomada, bindings de papel/modelo e roteamento.

## `JIRA_ACCESS` — Acesso ao Jira
Consulta o Jira usando credenciais locais e produz contexto efêmero; não cria memória persistente.

## `INTAKE` — Triagem do Jira
Cria a feature após Jira conhecido, protege `.ai/`, persiste `STATE.md` e `00-jira.md` e classifica cenário/risco.

## `MEMORY_LOOKUP` — Consulta de memória
Procura features anteriores relacionadas; memória ajuda, mas código atual precisa ser revalidado.

## `DISCOVERY` — Investigação
Investiga código/testes com entry-point-first e search-first, classificando `FACT`, `INFERENCE` e `UNKNOWN`.

## `REQUIREMENT_ANALYSIS` — Análise de requisitos
Separa requisitos explícitos, necessidades implícitas, assumptions, open questions, riscos e melhorias opcionais.
Pode bloquear somente por `OPEN_QUESTION` material.

## `INTERVIEW_OPTIONAL` — Entrevista opcional
Pergunta apenas o mínimo necessário para resolver bloqueio real e retorna à análise de requisitos.

## `TECHNICAL_QUALITY_REVIEW` — Revisão de qualidade técnica
Revisão arquitetural opcional, ativada somente por gatilho real. `NO_CHANGE` é resultado válido.

## `SOLUTION_DESIGN` — Desenho da solução
Executa Senior Approach Check e desenha a menor solução sólida, respeitando arquitetura válida existente.

## `SOLUTION_REVIEW` — Revisão da solução
Consolida solução e apresenta o gate `APROVAR SOLUÇÃO`.

## `SPEC_PLAN_REVIEW` — Revisão da SPEC e plano
Cria `03-spec.md` e `04-implementation-plan.md`, estabelece rastreabilidade e apresenta `APROVAR SPEC/PLANO`.
Depois da aprovação, a SPEC fica congelada para RED, implementação, GREEN e Judge.

## `RED_REVIEW` — Revisão do contrato RED
Planeja testes/evidências. Gate: `APROVAR RED`.

## `RED_EXECUTION` — Execução do RED
Materializa testes, comprova falha pelo motivo esperado e gera `red-tests.lock`.

## `WAITING_GO` — Aguardando GO
Pausa explícita entre RED selado e implementação. Gate: `GO`.

## `IMPLEMENTING` — Implementação
Implementa o mínimo necessário contra SPEC/plano/RED no COMUM ou Quick Contract/RED no QUICK.

## `REWORK_IMPLEMENTATION` — Correção da implementação
Corrige implementação após `IMPLEMENTATION_DEFECT` sem alterar RED válido.

## `GREEN_VALIDATION` — Validação GREEN
Prova mecanicamente que implementação atende contrato e preserva RED lock.

## `JUDGING` — Julgamento independente
Judge fresh/read-only aplica evidence-or-zero e emite `PASS`, `PASS_WITH_RISKS`, `FAIL` ou `BLOCKED`.

## `JUDGE_RECOVERY` — Recuperação pós-Judge
Micro-fluxo para `DISCOVERY_GAP`, `RED_CONTRACT_DEFECT` ou `REQUIREMENT_AMBIGUITY`; `REOPEN RED` só após análise.

## `QA_REVIEW` — Revisão de QA
Produz/revisa cenários e entregáveis de QA. Gate: `APROVAR QA`.

## `COMMIT_REVIEW` — Revisão/execução de commits
Oferece `AUTOMÁTICO`, `MANUAL` ou `OUTROS` e protege `.ai/` contra versionamento.

## `PR_DESCRIPTION` — Descrição de PR/MR
Gera somente título/descrição para input manual; não abre PR/MR remoto.

## `READY_TO_ARCHIVE` — Pronto para arquivar
Consolida memória final após Judge/QA/commit/PR resolvidos e autorização `ARQUIVAR`.

## `QUICK_AUTOGO` — Execução rápida AUTO-GO
Analisa de forma compacta e, após `AUTO-GO`, executa RED -> lock -> implementação -> GREEN até Judge/bloqueio.

## Nota de legado
Features antigas podem mostrar `PRD_PLAN_REVIEW`, `PRD_PLAN_APPROVED` ou `03-prd.md`. Eles são nomes
históricos do conceito que hoje aparece como `SPEC_PLAN_REVIEW`, `SPEC_PLAN_APPROVED` e `03-spec.md`.
