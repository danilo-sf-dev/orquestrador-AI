# ORQUESTRADOR — Engenharia de Software Java/Spring Boot

**Versão:** 1.9.4  
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
4. Toda fase concluída deve persistir `CURRENT_STATE` + `NEXT_ACTION` suficientes para `RESUME` determinístico.
5. Lazy loading: carregar somente core + STATE + skill atual + reads/referências explicitamente necessárias.
6. `documentacao-usuario/**` é **HUMAN_ONLY** e possui exclusão global absoluta: nenhuma skill/agente pode ler, buscar, indexar, resumir, citar, incluir em handoff ou usar seu conteúdo como evidência, memória ou fonte de decisão. Se uma busca global retornar resultado desse path, ignorar sem abrir o arquivo.
7. Transcript, logs brutos e features antigas completas não entram automaticamente no contexto.
8. Fluxo comum é contract-driven: `Jira -> Discovery -> Requirements -> Design -> Solution -> SPEC -> RED -> Code -> GREEN -> Judge`.
9. `03-spec.md` é o artefato canônico da SPEC aprovada para novas features.
10. Requirement Analysis separa `EXPLICIT_REQUIREMENT`, `IMPLICIT_NECESSITY`, `ASSUMPTION`, `OPEN_QUESTION`, `TECHNICAL_RISK`, `OPTIONAL_IMPROVEMENT`.
11. `OPEN_QUESTION` bloqueia somente quando a resposta muda materialmente comportamento, contrato, negócio, segurança, persistência, integração, efeito destrutivo ou desenho do RED.
12. Solution Design segue arquitetura válida existente por padrão, prefere a menor mudança suficiente e só propõe mudança estrutural com ganho material demonstrável.
13. Revisão arquitetural (`18`) continua opcional e especializada; não é checklist obrigatório.
14. `OPTIONAL_IMPROVEMENT` nunca vira escopo, RED ou obrigação do Judge sem aprovação explícita.
15. Planejamento e julgamento usam rastreabilidade do contrato até código/teste/evidência.
16. RED aprovado fica protegido por `red-tests.lock`; implementação/GREEN não podem alterá-lo.
17. GREEN usa evidência mecânica; código presente ou teste verde sem rastreabilidade não prova contrato.
18. Judge é read-only/evidence-isolated e usa `evidence-or-zero`: sem evidência suficiente não há `PASS`. Mesmo no mesmo chat, histórico anterior não vale como evidência de julgamento.
19. Mudança no escopo julgado invalida o julgamento e exige novo GREEN + Judge.
20. Judge FAIL é classificado como `IMPLEMENTATION_DEFECT`, `RED_CONTRACT_DEFECT`, `DISCOVERY_GAP` ou `REQUIREMENT_AMBIGUITY`.
21. `IMPLEMENTATION_DEFECT` volta apenas para rework; demais classes passam por `JUDGE_RECOVERY`.
22. `JUDGE_RECOVERY` é recovery dirigido por finding e também pode ser acionado **antes do Judge** por RED/implementação/GREEN/QUICK quando surgir fato capaz de invalidar contrato ou RED.
23. Recovery sempre retorna ao menor estado seguro; contrato afetado fica stale e usa novamente seu gate normal.
24. `REOPEN RED` exige recovery + autorização humana exata `REOPEN RED`; nenhuma outra fase altera lock/teste selado diretamente.
25. `RED_REVIEW` e `RED_EXECUTION` são estados distintos.
26. Conclusões materiais distinguem `FACT`, `INFERENCE`, `UNKNOWN` e apontam evidência quando possível.
27. Cada arquivo principal de skill deve ficar abaixo de 400 linhas físicas; detalhe condicional vai para referência lazy.
28. `.ai/` é estritamente local: `NEVER_STAGE`, `NEVER_COMMIT`, `NEVER_PUSH`.
29. Ao criar/reusar `.ai/`, confirmar regra efetiva no `.gitignore`; repetir verificação antes de qualquer commit.
30. Commit oferece `AUTOMÁTICO | MANUAL | OUTROS`; automático mantém commits faseados e mensagens EN.
31. PR só ocorre por solicitação explícita; `ABRIR PR` gera título/descrição para input manual e não cria PR/MR remoto.
32. Merge, rebase, force push e operações Git destrutivas não são automáticos.
33. Credenciais Jira reais nunca entram em memória, logs, commit ou PR. O arquivo versionado do projeto contém somente placeholders/fake credentials.
34. Em `ROUTING_MODE=manual`, toda mudança de papel é gate; sem confirmação técnica de troca automática, tratar como manual.
35. Troca de papel/modelo usa `MODEL_SWITCH` no mesmo chat por padrão. Ela nunca implica automaticamente nova conversa.
36. Quando a sessão ficar longa/poluída mas ainda útil, preferir `COMPACT_CONTEXT`; no VS Code usar `/compact` quando disponível. `/clear` inicia nova sessão e equivale conceitualmente a `FRESH_CONTEXT`.
37. `FRESH_CONTEXT` é excepcional e explícito: usar apenas quando isolamento real for necessário ou solicitado.
38. Antes de cada fase mostrar `PHASE BANNER` com estado canônico, skill, papel/modelo e ação do usuário.
39. `MODEL_ROLES_CONFIRMED_THIS_SESSION` deve ser resetado no início de cada nova sessão antes do bootstrap confirmar bindings atuais.
40. **Legado PRD:** features antigas podem conter `03-prd.md`, `PRD_PLAN_REVIEW` e `PRD_PLAN_APPROVED`. Interpretar como predecessores históricos da SPEC/plan atuais; não usar PRD em novas features.

## 3. NEW e RESUME

Antes de NEW, procurar feature ativa inequívoca. Se existir, ler `STATE.md`, resetar a confirmação de modelos da sessão e executar somente `NEXT_ACTION`; não repetir fase aprovada sem fato novo/recovery.

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

## 4. PHASE BANNER / troca de modelo e contexto

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

Por padrão, a confirmação significa apenas selecionar o novo modelo **no mesmo chat** (`MODEL_SWITCH`).

Política de contexto:

```text
SAME_CHAT / MODEL_SWITCH
- default para todo o fluxo
- mantém a mesma conversa ao trocar modelo/papel

COMPACT_CONTEXT
- mantém a mesma sessão
- resume/poda histórico antigo quando o runtime suportar
- no VS Code: /compact
- preferir quando contexto ficou grande/poluído, mas decisões anteriores ainda importam

FRESH_CONTEXT
- nova sessão/contexto
- excepcional e explícito
- usar para isolamento forte, auditoria realmente independente, loops muito grandes ou escolha do usuário
- no VS Code, /clear inicia nova sessão e portanto entra nesta categoria
```

`MODEL_HANDOFF_REQUIRED=true` nunca significa, sozinho, abrir novo chat.

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
| `SPEC_PLAN_REVIEW` | `06-spec-plano.md` | `HEAD_STRONG` |
| `RED_REVIEW` | `07-testes-red.md` | `EXECUTOR` |
| `RED_EXECUTION` | `07-testes-red.md` | `EXECUTOR` |
| `WAITING_GO` | `08-implementacao-go.md` | `EXECUTOR` |
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
| `JUDGE_PRIMARY` | DeepSeek V4 Pro 0813 read-only/evidence-isolated |
| `JUDGE_SECONDARY` | Gemini 3.7 Flash ou outro independente |

Economizar pelo custo total esperado: `ECONOMICAL` coleta/compacta; `HEAD_STRONG` decide/desambigua;
`EXECUTOR` aplica contrato aprovado; `JUDGE_*` preserva independência de responsabilidade e evidência.

## 7. Fluxo `STANDARD_GATED`

```text
JIRA_ACCESS [ECONOMICAL]
-> INTAKE [ECONOMICAL]
-> MEMORY_LOOKUP [ECONOMICAL]
-> DISCOVERY [ECONOMICAL]
-> REQUIREMENT_ANALYSIS [HEAD_STRONG]
   -> Q bloqueante: INTERVIEW_OPTIONAL -> REQUIREMENT_ANALYSIS (delta)
-> TECHNICAL_QUALITY_REVIEW [HEAD_STRONG] somente se requerido
-> SOLUTION_DESIGN [HEAD_STRONG]
-> SOLUTION_REVIEW [HEAD_STRONG] [APROVAR SOLUÇÃO]
-> SPEC_PLAN_REVIEW [HEAD_STRONG] [APROVAR SPEC/PLANO]
-> RED_REVIEW [EXECUTOR] [APROVAR RED]
-> RED_EXECUTION [EXECUTOR] cria/executa RED + lock
-> WAITING_GO [EXECUTOR] [GO]
-> IMPLEMENTING [EXECUTOR]
-> GREEN_VALIDATION [EXECUTOR]
-> JUDGING [JUDGE_PRIMARY]
   -> PASS/PASS_WITH_RISKS: QA_REVIEW
   -> IMPLEMENTATION_DEFECT: REWORK_IMPLEMENTATION -> GREEN -> Judge
   -> demais FAIL classes: JUDGE_RECOVERY [HEAD_STRONG]
-> QA_REVIEW [EXECUTOR] [APROVAR QA]
-> COMMIT_REVIEW [EXECUTOR] [AUTOMÁTICO | MANUAL | OUTROS]
-> PR_DESCRIPTION somente se solicitado
-> READY_TO_ARCHIVE [ECONOMICAL] [ARQUIVAR]
```

`REQUIREMENT_ANALYSIS`, `SOLUTION_DESIGN` e `TECHNICAL_QUALITY_REVIEW` não adicionam gates humanos.
`FAST | STANDARD | CRITICAL` alteram profundidade, nunca quantidade de gates.

## 8. Fluxo `QUICK_AUTOGO`

A lógica está em `skills/16-quick-autogo.md`. QUICK não cria artefatos completos de Requirements/Design/SPEC.
Antes do Quick Contract executa versões compactas de Codebase Recon, Requirement Gap,
Assumptions/Open Questions e Senior Solution Check.

Antes de `AUTO-GO`, perda de elegibilidade migra formalmente para:

```text
FLOW_MODE=STANDARD_GATED
CURRENT_STATE=MEMORY_LOOKUP
```

Depois que a execução QUICK já começou, descoberta material usa `JUDGE_RECOVERY` dirigido para preservar
o que ainda for válido. Após `AUTO-GO`: RED -> lock -> implementação -> GREEN -> Judge.

No QUICK, QA pode ser `APPROVED` ou `NOT_REQUIRED_WITH_REASON` antes do commit.

## 9. Recovery dirigido

`JUDGE_RECOVERY` é o único micro-fluxo de recovery contratual. Ele pode receber finding de:

```text
RED_EXECUTION
IMPLEMENTATION
GREEN_VALIDATION
QUICK_AUTOGO
JUDGE
```

Ele classifica impacto em requisito, solução, SPEC/plano e RED e retorna ao **menor estado seguro**.

Regras:

- implementation-only -> `REWORK_IMPLEMENTATION`;
- requirement delta -> `REQUIREMENT_ANALYSIS`;
- solution delta -> `SOLUTION_DESIGN`;
- SPEC/plan delta -> `SPEC_PLAN_REVIEW`;
- RED sem lock -> `RED_REVIEW` com gate normal;
- RED lockado -> reaprovar contratos superiores primeiro, quando necessário, e então solicitar `REOPEN RED`.

Recovery não edita diretamente código, teste selado ou contrato aprovado.

## 10. Lazy loading, exclusões e handoff

Carregar por chamada:

```text
ORCHESTRATOR_CORE
+ STATE.md
+ skill atual
+ referência condicional roteada
+ reads permitidos
+ código necessário
```

Exclusão absoluta antes de qualquer leitura/busca:

```text
documentacao-usuario/**  # HUMAN_ONLY
```

Handoff usa `templates/handoff-packet.md`; apontar artefatos em vez de copiar transcript. O template também
carrega `documentacao-usuario/**` em `DO_NOT_READ` como defesa adicional.

No `MODEL_SWITCH` normal, handoff não exige nova sessão. Em `COMPACT_CONTEXT`, preservar no resumo pelo menos
Jira/objetivo, decisões aprovadas, contrato vigente, `CURRENT_STATE`, `NEXT_ACTION`, RED lock e blockers atuais.
Em `FRESH_CONTEXT`, passar somente o pacote mínimo permitido pela skill destino.

## 11. Memória por Jira

```text
.ai/features/<JIRA-ID>/
  STATE.md
  00-jira.md
  01-discovery.md
  01-requirements.md
  01-quality-review.md     # opcional
  02-design.md
  02-solution.md
  03-spec.md
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

Ao consultar features antigas, `03-prd.md` significa o predecessor histórico da atual `03-spec.md`.

## 12. STATE mínimo

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
SPEC_PLAN_APPROVED:
RED_APPROVED:
RED_LOCKED:
RED_REOPEN_COUNT:
GO_APPROVED:
GREEN_STATUS:
JUDGE_STATUS:
JUDGE_FAIL_CLASS:
RECOVERY_STATUS:
RECOVERY_SOURCE:
RECOVERY_CLASS:
RECOVERY_RED_REOPEN_REQUIRED:
QA_STATUS:
COMMIT_MODE:
COMMIT_PLAN_STATUS:
COMMIT_STATUS:
PR_STATUS:
PENDING:
```

## 13. Orçamento

```text
MONTHLY_BUDGET_USD=40
FEATURE_TARGET_USD=8
FEATURE_WARNING_USD=10
```

Economia vem de search-first, lazy loading, contexto compacto, model routing e gates mecânicos — nunca
de omitir validação material.

## 14. Cenários on-demand

`skills/cenarios/` contém apenas **overlays/deltas** de profundidade e risco. Cenário não define pipeline
próprio e não pode substituir estados/gates do `orquestrador.md`.

## 15. Loop operacional

```text
referenciar orquestrador.md
-> RESUME ou NEW
-> FLOW_SELECTION se NEW
-> JIRA_ACCESS
-> FILTRAR HUMAN_ONLY PATHS
-> LOAD CURRENT SKILL ONLY
-> LOAD ALLOWED CONTEXT ONLY
-> EXECUTE
-> CHECK GATE
-> SAVE CURRENT_STATE + NEXT_ACTION
-> MODEL_SWITCH no mesmo chat quando o papel mudar
-> COMPACT_CONTEXT somente quando útil
-> FRESH_CONTEXT somente quando explicitamente necessário
-> NEXT
```
