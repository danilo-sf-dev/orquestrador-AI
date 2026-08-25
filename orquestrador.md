# ORQUESTRADOR — Engenharia de Software Java/Spring Boot

**Versão:** 1.6.2  
**Objetivo:** ser a porta única de entrada. O orquestrador decide **estado, fluxo, skill, papel, gate e próxima ação**. Cada skill define **como executar** a sua fase.

---

## 1. Princípio central

```text
ORQUESTRADOR
= estado + roteamento + gates + próxima ação

SKILL
= execução detalhada da etapa
```

Não duplicar no orquestrador regras detalhadas de Jira, Discovery, RED, implementação, GREEN, Judge, QA, Commit ou PR.

---

## 2. Invariantes globais

1. Skills trabalham com papéis: `HEAD_STRONG`, `EXECUTOR`, `ECONOMICAL`, `MULTIMODAL`, `JUDGE_PRIMARY`, `JUDGE_SECONDARY`.
2. Binding papel → modelo é resolvido pela sessão/runtime; não persistir `model-profile.md`.
3. `STATE.md` é checkpoint operacional curto, não documentação completa.
4. Lazy loading: carregar apenas core + `STATE.md` + skill atual + `reads` permitidos + código necessário.
5. Transcript completo não entra automaticamente em implementação, GREEN ou Judge.
6. RED aprovado fica protegido por `red-tests.lock`.
7. Judge deve ser fresh-context/read-only e não pode editar implementação.
8. Mudança em escopo já julgado invalida o julgamento e exige GREEN + novo Judge.
9. Commit exige confirmação explícita.
10. PR só ocorre por solicitação explícita.
11. Operações Git destrutivas, merge, rebase ou force push não são automáticos.
12. Credenciais Jira nunca entram em memória, logs, commit ou PR.
13. `.ai/` é memória estritamente local e **nunca pode ser versionada**. Ao criar ou reutilizar `.ai/`, verificar imediatamente se o `.gitignore` do repositório contém uma regra efetiva que ignore `.ai/`; se não contiver, adicionar `.ai/` antes de continuar.
14. Antes de qualquer commit, verificar novamente com Git que `.ai/` está ignorada e que nenhum arquivo sob `.ai/` está staged/tracked. Se a proteção falhar, o commit fica bloqueado até corrigir.

---

## 3. Entrada única: `/orquestrador`

### 3.1 RESUME antes de NEW

Ao iniciar:

```text
1. Resolver feature ativa/candidata.
2. Se existir feature inequívoca -> ler STATE.md e executar NEXT_ACTION.
3. Se não existir -> iniciar NEW.
```

No `RESUME`, não repetir Jira, Discovery, solução, PRD ou RED já concluídos sem motivo explícito.

### 3.2 NEW: selecionar fluxo antes do Jira

Perguntar:

```text
Qual tipo de execução deseja iniciar?

1. QUICK / AUTO-GO
   Tarefa simples, localizada, de baixo risco e comportamento claro.
   Após sua aprovação inicial, RED -> implementação -> GREEN seguem sem
   novas aprovações até o handoff para Judge.

2. COMUM / COMPLETA
   História, bug, integração ou alteração que precisa de discovery,
   solução, plano e gates completos.

Responda: QUICK ou COMUM.
```

Persistir depois que o Jira for conhecido:

```yaml
FLOW_MODE: QUICK_AUTOGO | STANDARD_GATED
```

### 3.3 Jira é porta comum

```text
receber URL/ID Jira
-> skills/15-jira-access.md
-> JIRA_CONTEXT_READY
-> criar/persistir feature
-> rotear para o fluxo selecionado
```

Nenhuma feature nova avança sem `JIRA_CONTEXT_READY=true`.

### 3.4 Proteção obrigatória da memória local `.ai/`

Quando a feature precisar criar ou reutilizar `.ai/`:

```text
1. localizar o root Git canônico da feature;
2. verificar se `.ai/` existe;
3. verificar se `.ai/` está efetivamente ignorada pelo Git;
4. se não estiver, adicionar a regra `.ai/` ao `.gitignore` do repositório;
5. confirmar novamente que Git ignora `.ai/`;
6. somente então criar/usar `.ai/features/<JIRA-ID>/`.
```

Regra absoluta:

```text
.ai/ = LOCAL_ONLY
.ai/ NEVER_COMMIT
.ai/ NEVER_STAGE
.ai/ NEVER_PUSH
```

Não existe modo `include` ou `ask` para a memória `.ai/`. Ela nunca deve subir para o repositório remoto.

Se `.ai/` já existir ao iniciar/resumir uma feature, a mesma verificação é obrigatória antes de continuar.

---

## 4. Skills e papéis

| Estado | Skill | Papel |
|---|---|---|
| `MODEL_CONFIRMATION` | `00-bootstrap-modelos.md` | ORCHESTRATOR |
| `JIRA_ACCESS` | `15-jira-access.md` | `ECONOMICAL` |
| `INTAKE` | `01-intake-jira.md` | `ECONOMICAL` |
| `MEMORY_LOOKUP` | `02-memoria-feature.md` | `ECONOMICAL` |
| `DISCOVERY` | `03-investigacao.md` | `ECONOMICAL` |
| `INTERVIEW_OPTIONAL` | `04-entrevista-opcional.md` | `HEAD_STRONG` |
| `SOLUTION_REVIEW` | `05-solucao-proposta.md` | `HEAD_STRONG` |
| `PRD_PLAN_REVIEW` | `06-prd-plano.md` | `HEAD_STRONG` |
| `RED_REVIEW` | `07-testes-red.md` | `EXECUTOR` |
| `IMPLEMENTING` | `08-implementacao-go.md` | `EXECUTOR` |
| `GREEN_VALIDATION` | `09-validacao-green.md` | `EXECUTOR` |
| `JUDGING` | `10-juiz.md` | `JUDGE_PRIMARY` |
| `QA_REVIEW` | `11-qa-pack.md` | `EXECUTOR` |
| `COMMIT_REVIEW` | `12-commit-workflow.md` | `EXECUTOR` |
| `PR_READY` | `13-pull-request-workflow.md` | `EXECUTOR` |
| `READY_TO_ARCHIVE` | `14-arquivamento.md` | `ECONOMICAL` |
| `QUICK_AUTOGO` | `16-quick-autogo.md` | `EXECUTOR` |

---

## 5. Binding de modelos — sugestão atual

| Papel | Modelo sugerido |
|---|---|
| `HEAD_STRONG` | DeepSeek V4 Pro 0813 |
| `EXECUTOR` | GPT-5.6 Luna Pro |
| `ECONOMICAL` | DeepSeek V4 Flash 0731 |
| `MULTIMODAL` | Gemini 3.7 Flash |
| `JUDGE_PRIMARY` | DeepSeek V4 Pro 0813 fresh/read-only |
| `JUDGE_SECONDARY` | Gemini 3.7 Flash ou outro independente |

Se o runtime não trocar modelos automaticamente, a troca é manual no handoff.

---

## 6. Fluxo `STANDARD_GATED`

```text
JIRA_ACCESS
-> INTAKE
-> MEMORY_LOOKUP
-> DISCOVERY
-> INTERVIEW_OPTIONAL se necessário
-> SOLUTION_REVIEW       [APROVAR SOLUÇÃO]
-> PRD_PLAN_REVIEW       [APROVAR PRD/PLANO]
-> RED_REVIEW            [APROVAR RED]
-> WAITING_GO            [GO]
-> IMPLEMENTING
-> GREEN_VALIDATION
-> JUDGE_HANDOFF
-> JUDGING
-> QA_REVIEW             [APROVAR QA]
-> COMMIT_REVIEW         [CONFIRMAR COMMIT]
-> PR_READY somente se solicitado
-> READY_TO_ARCHIVE
```

Regras detalhadas pertencem às skills correspondentes.

`FAST | STANDARD | CRITICAL` controlam apenas profundidade/rigor neste fluxo; não removem gates.

---

## 7. Fluxo `QUICK_AUTOGO`

A lógica detalhada fica exclusivamente em:

```text
skills/16-quick-autogo.md
```

Entrada:

```text
JIRA_CONTEXT_READY=true
FLOW_MODE=QUICK_AUTOGO
```

Saídas esperadas:

```text
QUICK_READY_FOR_JUDGE
QUICK_AUTOGO_ABORTED
QA_DECISION
COMMIT_REVIEW
```

No `QUICK_READY_FOR_JUDGE`, parar para troca manual para `JUDGE_PRIMARY` quando o runtime não puder trocar automaticamente.

---

## 8. Lazy loading e handoff

Por chamada carregar apenas:

```text
ORCHESTRATOR_CORE
+ STATE.md
+ skill atual
+ reads permitidos
+ código necessário
```

Não carregar automaticamente:

```text
README
todas as skills
todos os templates
transcript completo
raw discovery logs
hipóteses descartadas
outras features inteiras
```

Para troca de papel/modelo usar `templates/handoff-packet.md` com:

```text
JIRA
CURRENT_STATE
NEXT_STATE
EXECUTION_LEVEL
ROLE
OBJECTIVE
READ
DO_NOT_READ
CONSTRAINTS
APPROVED_DECISIONS
PENDING
WRITE
EXPECTED_OUTPUT
```

---

## 9. Memória por Jira

Pasta:

```text
.ai/features/<JIRA-ID>/
```

Estrutura estável:

```text
STATE.md
00-jira.md
01-discovery.md
02-solution.md
03-prd.md
04-implementation-plan.md
05-red-tests.md
red-tests.lock
06-implementation-summary.md
07-green-evidence.md
08-judgement.md
09-qa-tests.md
10-qa-guide.md
11-archive.md
qa/
delivery/
  commit.md
  pull-request.md
  pr/
```

No QUICK, criar apenas os artefatos realmente usados.

Compatibilidade:
- `11-archive.md` é o canônico;
- `13-archive.md` é apenas legado;
- novas gravações usam `11-archive.md` + `delivery/`.

---

## 10. STATE mínimo

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
RED_LOCKED:
GREEN_STATUS:
JUDGE_STATUS:
QA_STATUS:
COMMIT_STATUS:
PR_STATUS:
PENDING:
```

Detalhes de Jira, critérios, classes, riscos, métricas e delivery ficam nos artefatos próprios.

---

## 11. Orçamento

```text
MONTHLY_BUDGET_USD=40
FEATURE_TARGET_USD=8
FEATURE_WARNING_USD=10
```

Custo nunca autoriza reduzir qualidade.

---

## 12. Cenários on-demand

```text
skills/cenarios/historia-padrao.md
skills/cenarios/local-conhecido.md
skills/cenarios/bug-desenvolvimento.md
skills/cenarios/bug-producao.md
skills/cenarios/cross-repo.md
```

Cenários ajustam profundidade, não regras centrais de segurança.

---

## 13. Loop operacional

```text
/orquestrador
-> RESUME ou NEW
-> se NEW: FLOW_SELECTION
-> JIRA_ACCESS
-> LOAD CURRENT SKILL ONLY
-> LOAD ALLOWED CONTEXT ONLY
-> EXECUTE
-> CHECK GATE
-> SAVE STATE + NEXT_ACTION
-> HANDOFF quando necessário
-> NEXT
```
