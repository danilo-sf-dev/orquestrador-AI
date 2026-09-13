# ORQUESTRADOR — Engenharia de Software Java/Spring Boot

**Versão:** 1.9.0  
**Objetivo:** ser a porta única de entrada. O orquestrador decide **estado, fluxo, skill, papel, gate e próxima ação**; cada skill define como executar sua fase.

## 1. Princípio central

```text
ORQUESTRADOR = estado + roteamento + gates + próxima ação
SKILL        = execução detalhada da etapa
```

Não duplicar aqui regras detalhadas das skills.

## 2. Invariantes globais

1. Papéis: `HEAD_STRONG`, `EXECUTOR`, `ECONOMICAL`, `MULTIMODAL`, `JUDGE_PRIMARY`, `JUDGE_SECONDARY`.
2. Binding papel → modelo pertence à sessão/runtime; não persistir `model-profile.md`.
3. `STATE.md` é checkpoint curto; detalhes ficam nos artefatos da feature.
4. Lazy loading: carregar somente core + STATE + skill atual + reads/referências explicitamente necessárias.
5. Transcript, logs brutos e features antigas completas não entram automaticamente no contexto.
6. Fluxo comum é contract-driven: `Jira -> Discovery -> Requirements -> Design -> Solution -> SPEC -> RED -> Code -> GREEN -> Judge`.
7. `03-prd.md` mantém o nome físico por compatibilidade, mas semanticamente é a **SPEC canônica** aprovada.
8. Requirement Analysis separa `EXPLICIT_REQUIREMENT`, `IMPLICIT_NECESSITY`, `ASSUMPTION`, `OPEN_QUESTION`, `TECHNICAL_RISK`, `OPTIONAL_IMPROVEMENT`.
9. `OPEN_QUESTION` bloqueia somente quando a resposta muda materialmente comportamento, contrato, negócio, segurança, persistência, integração, efeito destrutivo ou desenho do RED.
10. Solution Design segue arquitetura válida existente por padrão, prefere a menor mudança suficiente e só propõe mudança estrutural com ganho material demonstrável.
11. Revisão arquitetural (`18`) continua opcional e especializada; não é checklist obrigatório.
12. `OPTIONAL_IMPROVEMENT` nunca vira escopo, RED ou obrigação do Judge sem aprovação explícita.
13. Planejamento e julgamento usam `R/Jira -> AC -> DD -> PLAN -> arquivo/diff -> teste/evidência`.
14. RED aprovado fica protegido por `red-tests.lock`; implementação/GREEN não podem alterá-lo.
15. GREEN usa evidência mecânica; código presente ou teste verde sem rastreabilidade não prova AC.
16. Judge é fresh-context/read-only e usa `evidence-or-zero`: sem evidência suficiente não há `PASS`.
17. Mudança no escopo julgado invalida o julgamento e exige novo GREEN + Judge.
18. Judge FAIL deve ser classificado como `IMPLEMENTATION_DEFECT`, `RED_CONTRACT_DEFECT`, `DISCOVERY_GAP` ou `REQUIREMENT_AMBIGUITY`.
19. `IMPLEMENTATION_DEFECT` volta apenas para rework; demais classes passam por `JUDGE_RECOVERY`.
20. `REOPEN RED` exige recovery + autorização humana exata `REOPEN RED`.
21. `RED_REVIEW` e `RED_EXECUTION` são estados distintos.
22. Conclusões materiais distinguem `FACT`, `INFERENCE`, `UNKNOWN` e apontam evidência quando possível.
23. Cada arquivo principal de skill deve ficar abaixo de 400 linhas físicas; detalhe condicional vai para referência lazy.
24. `.ai/` é estritamente local: `NEVER_STAGE`, `NEVER_COMMIT`, `NEVER_PUSH`.
25. Ao criar/reusar `.ai/`, confirmar regra efetiva no `.gitignore`; repetir verificação antes de qualquer commit.
26. Commit oferece `AUTOMÁTICO | MANUAL | OUTROS`; automático mantém commits faseados e mensagens EN.
27. PR só ocorre por solicitação explícita; `ABRIR PR` gera título/descrição para input manual e não cria PR/MR remoto.
28. Merge, rebase, force push e operações Git destrutivas não são automáticos.
29. Credenciais Jira nunca entram em memória, logs, commit ou PR.
30. Em `ROUTING_MODE=manual`, toda mudança de papel é gate; sem confirmação técnica de troca automática, tratar como manual.
31. Antes de cada fase mostrar `PHASE BANNER` com estado canônico, skill, papel/modelo e ação do usuário.

## 3. NEW e RESUME

Antes de NEW, procurar feature ativa inequívoca. Se existir, ler `STATE.md` e executar somente `NEXT_ACTION`; não repetir fase aprovada sem fato novo/recovery.

Para NEW, escolher:

```text
QUICK / AUTO-GO
- tarefa simples, localizada, baixo risco e comportamento claro
- uma aprovação inicial; depois RED -> implementação -> GREEN até Judge

COMUM / COMPLETA
- história/bug/integração que precisa discovery, requisitos, design, SPEC/plano e gates completos
```

Depois:

```text
receber URL/ID Jira
-> skills/15-jira-access.md
-> JIRA_CONTEXT_READY=true
-> criar/persistir feature
-> rotear para fluxo escolhido
```

## 4. PHASE BANNER / troca de modelo

Antes de cada fase:

```text
PHASE
STATE: <CANONICAL_STATE>
STATUS: PENDING | IN_PROGRESS | BLOCKED | COMPLETE
SKILL: <arquivo.md>
ROLE: <ROLE>
MODEL_SUGGESTED: <binding da sessão>
NEXT_ACTION: <ação canônica>
USER_ACTION: <ação necessária ou AUTO_CONTINUE>
```

Se `ROUTING_MODE=manual` e o próximo papel diferir do atual, salvar estado, marcar
`MODEL_HANDOFF_REQUIRED=true` e parar até confirmação específica da troca.

## 5. Skills e papéis

| Estado | Skill | Papel |
|---|---|---|
| `MODEL_CONFIRMATION` | `00-bootstrap-modelos.md` | ORCHESTRATOR |
| `JIRA_ACCESS` | `15-jira-access.md` | `ECONOMICAL` |
| `INTAKE` | `01-intake-jira.md` | `ECONOMICAL` |
| `MEMORY_LOOKUP` | `02-memoria-feature.md` | `ECONOMICAL` |
| `DISCOVERY` | `03-investigacao.md` | `ECONOMICAL` |
| `REQUIREMENT_ANALYSIS` | `04a-analise-requisitos.md` | `HEAD_STRONG` |
| `INTERVIEW_OPTIONAL` | `04-entrevista-opcional.md` | `HEAD_STRONG` |
| `TECHNICAL_QUALITY_REVIEW` | `18-qualidade-arquitetural.md` | `HEAD_STRONG` |
| `SOLUTION_DESIGN` | `04b-design-solucao.md` | `HEAD_STRONG` |
| `SOLUTION_REVIEW` | `05-solucao-proposta.md` | `HEAD_STRONG` |
| `PRD_PLAN_REVIEW` | `06-prd-plano.md` | `HEAD_STRONG` |
| `RED_REVIEW` | `07-testes-red.md` | `EXECUTOR` |
| `RED_EXECUTION` | `07-testes-red.md` | `EXECUTOR` |
| `IMPLEMENTING` | `08-implementacao-go.md` | `EXECUTOR` |
| `REWORK_IMPLEMENTATION` | `08-implementacao-go.md` | `EXECUTOR` |
| `GREEN_VALIDATION` | `09-validacao-green.md` | `EXECUTOR` |
| `JUDGING` | `10-juiz.md` | `JUDGE_PRIMARY` |
| `JUDGE_RECOVERY` | `17-judge-recovery.md` | `HEAD_STRONG` |
| `QA_REVIEW` | `11-qa-pack.md` | `EXECUTOR` |
| `COMMIT_REVIEW` | `12-commit-workflow.md` | `EXECUTOR` |
| `PR_DESCRIPTION` | `13-pull-request-workflow.md` | `EXECUTOR` |
| `READY_TO_ARCHIVE` | `14-arquivamento.md` | `ECONOMICAL` |
| `QUICK_AUTOGO` | `16-quick-autogo.md` | `EXECUTOR` |

## 6. Binding sugerido

| Papel | Modelo sugerido |
|---|---|
| `HEAD_STRONG` | DeepSeek V4 Pro 0813 |
| `EXECUTOR` | GPT-5.6 Luna Pro |
| `ECONOMICAL` | DeepSeek V4 Flash 0731 |
| `MULTIMODAL` | Gemini 3.7 Flash |
| `JUDGE_PRIMARY` | DeepSeek V4 Pro 0813 fresh/read-only |
| `JUDGE_SECONDARY` | Gemini 3.7 Flash ou outro independente |

Economizar pelo custo total esperado: `ECONOMICAL` coleta/compacta; `HEAD_STRONG` decide/desambigua;
`EXECUTOR` aplica contrato aprovado; `JUDGE_*` preserva independência.

## 7. Fluxo `STANDARD_GATED`

```text
JIRA_ACCESS [ECONOMICAL]
-> INTAKE [ECONOMICAL]
-> MEMORY_LOOKUP [ECONOMICAL]
-> DISCOVERY [ECONOMICAL]
-> handoff HEAD_STRONG quando manual
-> REQUIREMENT_ANALYSIS [HEAD_STRONG]
   -> se Q bloqueante: INTERVIEW_OPTIONAL -> REQUIREMENT_ANALYSIS (delta)
-> TECHNICAL_QUALITY_REVIEW [HEAD_STRONG] somente se requerido
-> SOLUTION_DESIGN [HEAD_STRONG]
-> SOLUTION_REVIEW [HEAD_STRONG] [APROVAR SOLUÇÃO]
-> PRD_PLAN_REVIEW [HEAD_STRONG] [APROVAR PRD/PLANO]
-> handoff EXECUTOR
-> RED_REVIEW [EXECUTOR] [APROVAR RED]
-> RED_EXECUTION [EXECUTOR] cria/executa RED + lock
-> WAITING_GO [EXECUTOR] [GO]
-> IMPLEMENTING [EXECUTOR]
-> GREEN_VALIDATION [EXECUTOR]
-> handoff JUDGE_PRIMARY
-> JUDGING [JUDGE_PRIMARY]
   -> PASS/PASS_WITH_RISKS: QA
   -> IMPLEMENTATION_DEFECT: REWORK_IMPLEMENTATION -> GREEN -> Judge fresh
   -> demais FAIL classes: JUDGE_RECOVERY [HEAD_STRONG]
-> QA_REVIEW [EXECUTOR] [APROVAR QA]
-> COMMIT_REVIEW [EXECUTOR] [AUTOMÁTICO | MANUAL | OUTROS]
-> PR_DESCRIPTION somente se solicitado
-> READY_TO_ARCHIVE [ECONOMICAL]
```

`REQUIREMENT_ANALYSIS`, `SOLUTION_DESIGN` e `TECHNICAL_QUALITY_REVIEW` não adicionam gates humanos.
`FAST | STANDARD | CRITICAL` alteram profundidade, nunca quantidade de gates.

## 8. Fluxo `QUICK_AUTOGO`

A lógica está em `skills/16-quick-autogo.md`. QUICK não cria artefatos completos de Requirements/Design/SPEC.
Antes do Quick Contract executa versões compactas de Codebase Recon, Requirement Gap,
Assumptions/Open Questions e Senior Solution Check. Blocker material ou decisão estrutural aborta QUICK
para `STANDARD_GATED`.

Após `AUTO-GO`: RED -> lock -> implementação -> GREEN sem novas aprovações até Judge.

## 9. Lazy loading e handoff

Carregar por chamada:

```text
ORCHESTRATOR_CORE
+ STATE.md
+ skill atual
+ referência condicional roteada
+ reads permitidos
+ código necessário
```

Handoff usa `templates/handoff-packet.md`; apontar artefatos em vez de copiar transcript.

## 10. Memória por Jira

```text
.ai/features/<JIRA-ID>/
  STATE.md
  00-jira.md
  01-discovery.md
  01-requirements.md
  01-quality-review.md     # opcional
  02-design.md
  02-solution.md
  03-prd.md                # SPEC canônica; nome legado
  04-implementation-plan.md
  05-red-tests.md
  red-tests.lock
  06-implementation-summary.md
  07-green-evidence.md
  08-judgement.md
  09-qa-tests.md
  10-qa-guide.md
  11-archive.md
  recovery/
  qa/
  delivery/
```

No QUICK, criar somente artefatos realmente usados. `11-archive.md` é canônico; `13-archive.md` é legado.

## 11. STATE mínimo

```yaml
JIRA:
FLOW_MODE:
LIFECYCLE:
CURRENT_STATE:
NEXT_ACTION:
EXECUTION_LEVEL:
CANONICAL_HOME:
REPOSITORIES:
CURRENT_MODEL_ROLE:
NEXT_MODEL_ROLE:
JIRA_CONTEXT_READY:
REQUIREMENT_ANALYSIS_STATUS:
BLOCKING_OPEN_QUESTIONS:
TECHNICAL_QUALITY_REVIEW_STATUS:
SOLUTION_DESIGN_STATUS:
SOLUTION_APPROVED:
SPEC_STATUS:
PRD_PLAN_APPROVED:
RED_APPROVED:
RED_LOCKED:
RED_REOPEN_COUNT:
GREEN_STATUS:
JUDGE_STATUS:
JUDGE_FAIL_CLASS:
RECOVERY_STATUS:
QA_STATUS:
COMMIT_MODE:
COMMIT_PLAN_STATUS:
COMMIT_STATUS:
PR_STATUS:
PENDING:
```

## 12. Orçamento

```text
MONTHLY_BUDGET_USD=40
FEATURE_TARGET_USD=8
FEATURE_WARNING_USD=10
```

Economia vem de search-first, lazy loading, contexto compacto, model routing e gates mecânicos — nunca
de omitir validação material.

## 13. Cenários on-demand

`skills/cenarios/` ajusta profundidade sem alterar invariantes/gates.

## 14. Loop operacional

```text
referenciar orquestrador.md
-> RESUME ou NEW
-> FLOW_SELECTION se NEW
-> JIRA_ACCESS
-> LOAD CURRENT SKILL ONLY
-> LOAD ALLOWED CONTEXT ONLY
-> EXECUTE
-> CHECK GATE
-> SAVE STATE + NEXT_ACTION
-> HANDOFF quando necessário
-> NEXT
```
