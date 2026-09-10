# ORQUESTRADOR — Engenharia de Software Java/Spring Boot

**Versão:** 1.8.0
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
9. Commit exige escolha explícita de modo: `AUTOMÁTICO`, `MANUAL` ou `OUTROS`. `AUTOMÁTICO` autoriza a execução faseada conforme a skill 12; `MANUAL` exige `POSSO COMITAR` após o plano; `OUTROS` nunca implica autorização de commit.
10. PR só ocorre por solicitação explícita.
11. Operações Git destrutivas, merge, rebase ou force push não são automáticos.
12. Credenciais Jira nunca entram em memória, logs, commit ou PR.
13. `ABRIR PR` significa gerar título/descrição para input manual; acesso/criação remota de PR/MR é proibido pela skill 13.
13. `.ai/` é memória estritamente local e **nunca pode ser versionada**. Ao criar ou reutilizar `.ai/`, verificar imediatamente se o `.gitignore` do repositório contém uma regra efetiva que ignore `.ai/`; se não contiver, adicionar `.ai/` antes de continuar.
14. Antes de qualquer commit, verificar novamente com Git que `.ai/` está ignorada e que nenhum arquivo sob `.ai/` está staged/tracked. Se a proteção falhar, o commit fica bloqueado até corrigir.
15. Os nomes de estado exibidos ao usuário são **canônicos** e devem ser exatamente os definidos na tabela `Skills e papéis`. Não renomear, resumir, traduzir ou agrupar estados em checklists/status.
16. Em `ROUTING_MODE=manual`, **toda mudança de papel de modelo é um gate obrigatório**. A próxima skill não pode ser executada com o papel/modelo anterior.
17. Antes de cada fase, exibir um `PHASE BANNER` com `STATE`, `SKILL`, `ROLE`, `MODEL_SUGGESTED` e `USER_ACTION`. O banner é a fonte visual de verdade para o usuário.
18. Se o papel requerido pela próxima fase for diferente do papel atual e o runtime não trocar modelo automaticamente, parar em `MODEL_HANDOFF_REQUIRED` e aguardar confirmação do usuário após a troca manual.
19. `Judge FAIL` nunca retorna genericamente para RED. O Judge deve classificar o `FAIL` como `IMPLEMENTATION_DEFECT`, `RED_CONTRACT_DEFECT`, `DISCOVERY_GAP` ou `REQUIREMENT_AMBIGUITY`.
20. `IMPLEMENTATION_DEFECT` retorna somente para `REWORK_IMPLEMENTATION`; as outras classes passam por `JUDGE_RECOVERY [HEAD_STRONG]` antes de qualquer mudança em solução/PRD/RED.
21. `REOPEN RED` é uma exceção explícita: somente após recovery justificar impacto e o usuário responder exatamente `REOPEN RED`.
22. `RED_REVIEW` e `RED_EXECUTION` são estados diferentes: revisão/aprovação não pode ser apresentada como se os testes já tivessem sido criados/executados/locked.
23. Conclusões que mudam solução, plano ou julgamento devem apontar evidência e distinguir `FACT`, `INFERENCE` e `UNKNOWN`.
24. Cada arquivo principal de skill deve permanecer abaixo de 400 linhas físicas. Detalhe condicional vai para referência focada e só é carregado quando o modo correspondente exigir.
25. Planejamento e julgamento usam a cadeia `Jira/AC -> DD -> PLAN -> arquivo/diff -> teste/evidência`; itens sem origem ou validação explícita não entram silenciosamente no escopo.
26. Revisão de qualidade arquitetural é opcional e só ocorre por solicitação explícita ou evidência de
    problema estrutural consistente; patterns e mudanças arquiteturais não são objetivos por si só.

---

## 3. Entrada única: referência a `orquestrador.md`

No VS Code/Cursor, iniciar informando o caminho deste arquivo e pedindo para lê-lo e segui-lo. Não
depender de comando registrado na interface.

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

## 3.5 Contrato visual de fase e troca de modelo

Antes de cada fase, mostrar a fonte visual de verdade:

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

Usar somente estados canônicos da tabela `Skills e papéis` mais estados de controle (`MODEL_HANDOFF_REQUIRED`, `JUDGE_HANDOFF`, `WAITING_GO`). Nunca substituir por agrupamentos como `RED + lock`, `Implementação + GREEN` ou `Judge + QA + Commit`.

Se `ROUTING_MODE=manual` e `NEXT_MODEL_ROLE != CURRENT_MODEL_ROLE`, salvar o estado, marcar `MODEL_HANDOFF_REQUIRED=true`, mostrar o banner e **parar**. Só executar a próxima skill após confirmação específica da troca (`CONTINUAR RED`, `CONTINUAR JUDGE`, etc.). Em routing automático sem confirmação técnica da troca, tratar como manual.

Ao usuário perguntar onde está, mostrar primeiro apenas `STATE`, `ROLE/MODEL` e `NEXT_ACTION`; listar o fluxo completo somente se solicitado.

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
| `TECHNICAL_QUALITY_REVIEW` | `18-qualidade-arquitetural.md` | `HEAD_STRONG` |
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

### Roteamento por responsabilidade

Roteamento otimiza o custo total esperado, incluindo releitura, tentativas, rework e nova validação —
não apenas o preço de uma chamada.

- `ECONOMICAL` coleta e compacta evidências; não encerra decisão arquitetural ambígua.
- `HEAD_STRONG` resolve arquitetura, hipóteses concorrentes, segurança, concorrência/transação,
  contrato de alto impacto e premissa técnica contestada.
- `EXECUTOR` aplica plano aprovado; ambiguidade material ou falha repetida não autoriza improviso.
- `JUDGE_*` preserva independência; força de modelo não substitui fresh context/read-only.

Quando uma fase encontrar responsabilidade de outro papel, registrar a incerteza e a evidência,
salvar o estado e rotear para a fase forte já responsável por aquela decisão (`TECHNICAL_QUALITY_REVIEW`,
`SOLUTION_REVIEW`, `PRD_PLAN_REVIEW` ou `JUDGE_RECOVERY`). Depois da decisão, voltar ao papel econômico/executor; não
manter `HEAD_STRONG` por precaução.

---

## 6. Fluxo `STANDARD_GATED`

```text
JIRA_ACCESS            [ECONOMICAL]
-> INTAKE              [ECONOMICAL]
-> MEMORY_LOOKUP       [ECONOMICAL]
-> DISCOVERY           [ECONOMICAL]
-> MODEL_HANDOFF_REQUIRED se próxima fase exigir HEAD_STRONG
-> INTERVIEW_OPTIONAL  [HEAD_STRONG] se necessário
-> TECHNICAL_QUALITY_REVIEW [HEAD_STRONG] somente se requerido por evidência ou solicitação explícita
-> SOLUTION_REVIEW     [HEAD_STRONG] [APROVAR SOLUÇÃO]
-> PRD_PLAN_REVIEW     [HEAD_STRONG] [APROVAR PRD/PLANO]
-> MODEL_HANDOFF_REQUIRED para EXECUTOR
-> RED_REVIEW          [EXECUTOR] [APROVAR RED]
-> RED_EXECUTION       [EXECUTOR] cria/executa RED + lock
-> WAITING_GO          [EXECUTOR] [GO]
-> IMPLEMENTING        [EXECUTOR]
-> GREEN_VALIDATION    [EXECUTOR]
-> JUDGE_HANDOFF
-> MODEL_HANDOFF_REQUIRED para JUDGE_PRIMARY
-> JUDGING             [JUDGE_PRIMARY]
   -> PASS/PASS_WITH_RISKS: seguir para QA
   -> FAIL + IMPLEMENTATION_DEFECT: handoff para EXECUTOR -> REWORK_IMPLEMENTATION -> GREEN_VALIDATION -> novo JUDGING fresh
   -> FAIL + DISCOVERY_GAP|RED_CONTRACT_DEFECT|REQUIREMENT_AMBIGUITY: handoff para HEAD_STRONG -> JUDGE_RECOVERY
-> MODEL_HANDOFF_REQUIRED para EXECUTOR quando QA for a próxima fase
-> QA_REVIEW           [EXECUTOR] [APROVAR QA]
-> COMMIT_REVIEW       [EXECUTOR] [ESCOLHER: AUTOMÁTICO | MANUAL | OUTROS]
-> PR_DESCRIPTION      [EXECUTOR] somente se solicitado; gera conteúdo para input manual, sem acesso remoto
-> MODEL_HANDOFF_REQUIRED para ECONOMICAL quando archive for executado
-> READY_TO_ARCHIVE    [ECONOMICAL]
```

Regras detalhadas pertencem às skills correspondentes.

`FAST | STANDARD | CRITICAL` controlam apenas profundidade/rigor neste fluxo; não removem gates.

`TECHNICAL_QUALITY_REVIEW` não cria gate adicional. Sua saída é insumo opcional da solução e pode
concluir `NO_CHANGE`. O fluxo `QUICK_AUTOGO` não executa essa revisão; pedido de melhoria estrutural
ou evidência que a exija deve migrar para `STANDARD_GATED`.

---

## 6.1 Recovery após Judge FAIL

Roteamento determinístico; detalhes em `skills/17-judge-recovery.md`:

| `JUDGE_FAIL_CLASS` | Próximo estado | Papel | Regra |
|---|---|---|---|
| `IMPLEMENTATION_DEFECT` | `REWORK_IMPLEMENTATION` | `EXECUTOR` | RED/lock intocáveis; depois GREEN + Judge fresh |
| `DISCOVERY_GAP` | `JUDGE_RECOVERY` | `HEAD_STRONG` | micro-investigação somente do finding |
| `RED_CONTRACT_DEFECT` | `JUDGE_RECOVERY` | `HEAD_STRONG` | não editar RED até recovery + autorização |
| `REQUIREMENT_AMBIGUITY` | `JUDGE_RECOVERY` | `HEAD_STRONG` | perguntar somente a decisão mínima necessária |

`JUDGE_RECOVERY` nunca reinicia Discovery completo. `REOPEN RED` só existe quando a skill 17 justificar impacto e o usuário responder exatamente `REOPEN RED`; depois ocorre handoff para `EXECUTOR`, `RED_REVIEW` aplica somente o delta aprovado e então executa nova `RED_EXECUTION`.

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

No `QUICK_AUTOGO`, após `JIRA_ACCESS [ECONOMICAL]`, aplicar `MODEL_HANDOFF_REQUIRED` para `EXECUTOR` antes do Quick Contract quando o roteamento for manual. No `QUICK_READY_FOR_JUDGE`, aplicar novamente o gate para `JUDGE_PRIMARY`. `IMPLEMENTATION_DEFECT` pode voltar a rework do QUICK; qualquer `DISCOVERY_GAP`, `RED_CONTRACT_DEFECT` ou `REQUIREMENT_AMBIGUITY` aborta o QUICK e migra para `JUDGE_RECOVERY` no fluxo comum. Após Judge PASS, se houver QA/Commit com `EXECUTOR`, aplicar novo handoff antes de continuar.

---

## 8. Lazy loading e handoff

Por chamada carregar apenas:

```text
ORCHESTRATOR_CORE
+ STATE.md
+ skill atual
+ referência condicional explicitamente roteada pela skill atual
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
todas as referências de uma skill de uma vez
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
01-quality-review.md  # somente quando TECHNICAL_QUALITY_REVIEW ocorrer
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
recovery/
  judge-recovery-<N>.md
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
RED_APPROVED:
RED_LOCKED:
RED_REOPEN_COUNT:
GREEN_STATUS:
JUDGE_STATUS:
JUDGE_FAIL_CLASS:
RECOVERY_STATUS:
QA_STATUS:
COMMIT_MODE: # AUTO | MANUAL | OTHER
COMMIT_PLAN_STATUS:
COMMIT_STATUS:
PR_STATUS: # NOT_REQUESTED | DESCRIPTION_READY | SKIPPED_BY_USER
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
referenciar orquestrador.md
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
