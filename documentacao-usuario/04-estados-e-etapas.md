# 04 — Estados e etapas

> HUMAN_ONLY. Este arquivo é para consulta do usuário e não deve ser carregado por agentes.

Use este arquivo quando aparecer um nome como `INTAKE`, `SPEC_PLAN_REVIEW` ou `GREEN_VALIDATION` e você
quiser saber o que ele representa. Os nomes em português são explicativos; o valor canônico continua
sendo o identificador em inglês.

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
| `JUDGE_RECOVERY` | Recovery dirigido | `17-judge-recovery.md` | `HEAD_STRONG` |
| `QA_REVIEW` | Revisão de QA | `11-qa-pack.md` | `EXECUTOR` |
| `COMMIT_REVIEW` | Revisão/execução de commits | `12-commit-workflow.md` | `EXECUTOR` |
| `PR_DESCRIPTION` | Descrição de PR/MR | `13-pull-request-workflow.md` | `EXECUTOR` |
| `READY_TO_ARCHIVE` | Pronto para arquivar | `14-arquivamento.md` | `ECONOMICAL` |
| `QUICK_AUTOGO` | Execução rápida AUTO-GO | `16-quick-autogo.md` | `EXECUTOR` |

## Regra V1.9.3 — transição determinística

Quando uma fase termina, ela deve deixar no `STATE.md`:

```text
CURRENT_STATE=<próximo estado canônico>
NEXT_ACTION=<ação suficiente para retomar>
```

Assim, `RESUME` não depende da memória do chat anterior.

---

## `MODEL_CONFIRMATION` — Confirmação de modelos

Resolve NEW/RESUME, confirma bindings papel → modelo e `ROUTING_MODE`.

`MODEL_ROLES_CONFIRMED_THIS_SESSION` é resetado no início de cada nova sessão e só volta a `true` após
a confirmação atual.

---

## `JIRA_ACCESS` — Acesso ao Jira

Consulta o Jira usando a configuração local e devolve `JIRA_CONTEXT_READY=true` em memória efêmera.
Não cria `.ai`, `STATE.md` ou `00-jira.md`.

---

## `INTAKE` — Triagem do Jira

Cria a memória da feature somente depois do Jira conhecido e da proteção de `.ai/` confirmada.

Saída típica:

```text
STANDARD_GATED -> MEMORY_LOOKUP
QUICK_AUTOGO    -> QUICK_AUTOGO
```

---

## `MEMORY_LOOKUP` — Consulta de memória

Procura features relacionadas sem carregar todo o histórico. Memória é pista; código atual continua
precisando de revalidação.

Próximo estado no COMUM: `DISCOVERY`.

---

## `DISCOVERY` — Investigação

Codebase Recon `entry-point-first`, search-first e evidência `FACT | INFERENCE | UNKNOWN`.

Objetivo: entender somente o fluxo necessário para requisitos/design.

Próximo estado: `REQUIREMENT_ANALYSIS`.

---

## `REQUIREMENT_ANALYSIS` — Análise de requisitos

Classifica itens como:

```text
EXPLICIT_REQUIREMENT
IMPLICIT_NECESSITY
ASSUMPTION
OPEN_QUESTION
TECHNICAL_RISK
OPTIONAL_IMPROVEMENT
```

Se houver pergunta bloqueante:

```text
INTERVIEW_OPTIONAL
```

Sem blocker:

```text
TECHNICAL_QUALITY_REVIEW  # somente se REQUIRED
ou
SOLUTION_DESIGN
```

Não cria novo gate humano.

---

## `INTERVIEW_OPTIONAL` — Entrevista opcional

Pergunta somente `Q-*` material que não pode ser resolvida por evidência. Depois volta para
`REQUIREMENT_ANALYSIS` fechar o delta.

---

## `TECHNICAL_QUALITY_REVIEW` — Revisão de qualidade técnica

Opcional. Só aparece quando existe gatilho real de arquitetura/qualidade. `NO_CHANGE` é resultado válido.

Depois: `SOLUTION_DESIGN`.

---

## `SOLUTION_DESIGN` — Desenho da solução

Executa Senior Approach Check e desenha a menor solução sólida. Não pede aprovação aqui.

Depois: `SOLUTION_REVIEW`.

---

## `SOLUTION_REVIEW` — Revisão da solução

Consolida requisitos/design e apresenta o gate:

```text
APROVAR SOLUÇÃO
```

Após aprovação: `SPEC_PLAN_REVIEW`.

---

## `SPEC_PLAN_REVIEW` — Revisão da SPEC e plano

Produz:

```text
03-spec.md
04-implementation-plan.md
```

Gate:

```text
APROVAR SPEC/PLANO
```

No fluxo normal segue para `RED_REVIEW`. Em recovery, se existir RED já lockado que precise mudar,
retorna para `JUDGE_RECOVERY` somente para solicitar `REOPEN RED`.

---

## `RED_REVIEW` — Revisão do contrato RED

Planeja testes/evidências sem editar ainda os testes do repositório.

Gate:

```text
APROVAR RED
```

Depois: `RED_EXECUTION`.

---

## `RED_EXECUTION` — Execução do RED

Materializa o RED aprovado, comprova `EXPECTED_FAIL` e gera `red-tests.lock`.

Se descobrir fato que invalida contrato/RED antes de conseguir concluir, não redesenha sozinho: passa
para `JUDGE_RECOVERY` como recovery pré-Judge.

Após RED válido: `WAITING_GO`.

---

## `WAITING_GO` — Aguardando GO

Agora é um estado formalmente suportado pela skill 08.

Nenhum código de produção é alterado enquanto aguarda:

```text
GO
```

Após GO:

```text
GO_APPROVED=true
CURRENT_STATE=IMPLEMENTING
```

---

## `IMPLEMENTING` — Implementação

Implementa o contrato aprovado sem alterar RED lockado. Se encontrar decisão material que invalide
contrato/RED, passa por recovery dirigido.

Após conclusão: `GREEN_VALIDATION`.

---

## `REWORK_IMPLEMENTATION` — Correção da implementação

Correção dirigida quando contrato e RED continuam válidos. Pode vir do Judge, GREEN ou recovery.

Após conclusão: `GREEN_VALIDATION`.

---

## `GREEN_VALIDATION` — Validação GREEN

Comprova lock, compile, testes, regressão e evidência do contrato.

Resultados:

```text
PASS          -> JUDGING
FAIL code-only -> REWORK_IMPLEMENTATION
FAIL contratual -> JUDGE_RECOVERY
INVALID_GREEN  -> JUDGE_RECOVERY
```

---

## `JUDGING` — Julgamento independente

Fresh context/read-only e `evidence-or-zero`.

```text
PASS/PASS_WITH_RISKS -> QA_REVIEW
IMPLEMENTATION_DEFECT -> REWORK_IMPLEMENTATION
outros FAIL -> JUDGE_RECOVERY
BLOCKED -> permanece JUDGING até resolver blocker
```

---

## `JUDGE_RECOVERY` — Recovery dirigido

Na V1.9.3 não é exclusivo do pós-Judge. Pode ser acionado por:

```text
RED_EXECUTION
IMPLEMENTATION
GREEN_VALIDATION
QUICK_AUTOGO
JUDGING
```

Ele não edita código/teste/contrato diretamente. Descobre **qual camada ficou inválida** e retorna ao
menor estado seguro:

```text
código       -> REWORK_IMPLEMENTATION
requisito    -> REQUIREMENT_ANALYSIS
solução      -> SOLUTION_DESIGN
SPEC/plano   -> SPEC_PLAN_REVIEW
RED          -> RED_REVIEW / REOPEN RED
```

Quando RED já está lockado, `REOPEN RED` continua sendo autorização humana exata obrigatória.

---

## `QA_REVIEW` — Revisão de QA

No COMUM, QA é obrigatório e termina em `APROVAR QA`.

No QUICK, pode haver:

```text
QA_STATUS=APPROVED
ou
QA_STATUS=NOT_REQUIRED_WITH_REASON
```

Em ambos os casos resolvidos: `COMMIT_REVIEW`.

---

## `COMMIT_REVIEW` — Revisão/execução de commits

Modos:

```text
AUTOMÁTICO
MANUAL
OUTROS
```

Quando commit fica `COMMITTED`, `EXTERNAL` ou `SKIPPED_BY_USER`:

```text
PR_DESCRIPTION      # se solicitado
ou
READY_TO_ARCHIVE    # se não solicitado
```

`DEFERRED` permanece em `COMMIT_REVIEW`.

---

## `PR_DESCRIPTION` — Descrição de PR/MR

Gera somente título/descrição para input manual. Não acessa provider remoto.

Depois de `PR_STATUS=DESCRIPTION_READY`, segue para `READY_TO_ARCHIVE`; não fica esperando estado
remoto do PR.

---

## `READY_TO_ARCHIVE` — Pronto para arquivar

Após autorização `ARQUIVAR`, cria `11-archive.md`, atualiza índice e finaliza:

```text
LIFECYCLE=DONE
NEXT_ACTION=NONE
```

---

## `QUICK_AUTOGO` — Execução rápida AUTO-GO

Antes do gate faz análise compacta e apresenta Quick Contract.

Se perder elegibilidade **antes** do AUTO-GO:

```text
FLOW_MODE=STANDARD_GATED
CURRENT_STATE=MEMORY_LOOKUP
```

Depois do AUTO-GO: RED -> lock -> implementação -> GREEN -> Judge.

Se surgir problema contratual durante execução, usa recovery dirigido em vez de reiniciar silenciosamente.

---

## Nota de legado — PRD → SPEC

Em features antigas você pode encontrar:

```text
03-prd.md
PRD_PLAN_REVIEW
PRD_PLAN_APPROVED
APROVAR PRD/PLANO
```

Correspondem historicamente a:

```text
03-spec.md
SPEC_PLAN_REVIEW
SPEC_PLAN_APPROVED
APROVAR SPEC/PLANO
```

Não reutilizar nomenclatura PRD em feature nova.
