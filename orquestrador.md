# ORQUESTRADOR — Engenharia de Software Java/Spring Boot

**Versão:** 1.5  
**Objetivo:** ser a porta única de entrada da esteira. O orquestrador decide **estado, roteamento, contexto, gate e próxima ação**; cada skill define **como executar** sua fase.

---

## 1. Regra de ouro

```text
ORQUESTRADOR
= onde estamos
+ qual feature está ativa
+ qual skill carregar
+ qual papel/modelo executa
+ qual contexto pode entrar
+ qual gate precisa ser respeitado
+ qual é a próxima ação

SKILL
= como executar aquela etapa
```

O orquestrador não replica instruções detalhadas de Discovery, RED, GREEN, Judge, QA, Commit ou PR.

---

## 2. Invariantes globais

1. **Papéis antes de modelos.** Skills usam `HEAD_STRONG`, `EXECUTOR`, `ECONOMICAL`, `MULTIMODAL`, `JUDGE_PRIMARY` e `JUDGE_SECONDARY`.
2. **Sem `model-profile.md`.** O binding papel → modelo é resolvido na sessão/runtime.
3. **Memória primeiro.** Antes de investigação ampla, consultar `.ai/features/` e `.ai/FEATURE_INDEX.md`.
4. **Entrevista é exceção.** Perguntar somente quando Jira + memória + código + testes/docs não resolverem ambiguidade material.
5. **Aprovações permanecem fixas.** Solução, PRD/Plano, RED, GO, QA, Commit e Archive mantêm seus gates; `FAST|STANDARD|CRITICAL` nunca agrupam, removem ou pulam aprovações.
6. **RED protegido.** Após `APROVAR RED`, testes selados por `red-tests.lock` não podem ser alterados durante implementação/GREEN sem `REOPEN RED` + nova aprovação.
7. **Judge independente.** Judge usa contexto novo/read-only, não implementa e não recebe transcript/tentativas do executor.
8. **FAIL volta para implementação.** Nunca adaptar requisito, RED ou julgamento para acomodar código incorreto.
9. **Gates humanos não são implícitos.** Silêncio não vale aprovação.
10. **Contexto é contrato.** Cada skill declara `reads`, `writes`, `forbidden_reads` e `forbidden_writes`.
11. **Lazy loading obrigatório.** Carregar apenas core mínimo + `STATE.md` + skill atual + artefatos permitidos + código necessário.
12. **Memória não é verdade eterna.** Feature anterior deve ser validada contra código atual.
13. **Commit/PR não reabrem implementação.** Se o escopo julgado mudar, voltar para GREEN/Judge.
14. **Sem merge, force push ou operação destrutiva sem solicitação explícita.**

---

## 3. Entrada única: `/orquestrador`

Ao receber `/orquestrador`:

```text
1. Resolver feature ativa/candidata sem carregar todas as features.
2. Resolver/confirmar bindings de modelo da sessão.
3. Se houver feature a retomar -> RESUME.
4. Se não houver -> solicitar Jira + breve descrição.
5. Carregar somente a skill correspondente ao CURRENT_STATE.
```

### 3.1 Persistência no fluxo NEW

No fluxo `NEW`, o bootstrap **não cria `STATE.md` antes de conhecer o Jira**. Bindings de modelo e decisões de bootstrap permanecem efêmeros até o usuário informar `JIRA-ID + breve descrição`. Somente então `01-intake-jira.md` cria `.ai/features/<JIRA-ID>/STATE.md` e `00-jira.md`.

No fluxo `RESUME`, o `STATE.md` existente pode ser atualizado normalmente.

### 3.2 RESUME com múltiplas features

Prioridade para resolver a feature:

1. Jira informado pelo usuário;
2. referência inequívoca da branch/repo atual;
3. `STATE.md` com `LIFECYCLE=ACTIVE|PAUSED` localizado por metadados;
4. 1 candidata -> retomar;
5. mais de 1 -> perguntar qual Jira;
6. nenhuma -> iniciar nova feature.

Ao retomar:

```text
STATE.md
-> CURRENT_STATE
-> NEXT_ACTION
-> skill atual
-> reads permitidos
```

Não repetir Jira, discovery, solução, PRD ou RED já aprovados sem motivo explícito.

---

## 4. Lazy loading — contrato obrigatório

### Contexto permitido por chamada

```text
ORCHESTRATOR_CORE
+ STATE.md da feature selecionada
+ skill atual
+ arquivos declarados em reads
+ código/testes estritamente necessários
```

### Não carregar automaticamente

```text
README.md
+ todas as skills
+ cenários não selecionados
+ todos os templates
+ transcript completo
+ raw discovery logs
+ hipóteses descartadas
+ todos os artefatos da feature
+ outras features inteiras
```

- Templates entram somente quando a skill atual precisa deles.
- `skills/cenarios/` são overlays on-demand e **não alteram os gates globais**.
- Em runtime com dispatcher, `reads`/`forbidden_*` devem ser aplicados tecnicamente.
- Sem dispatcher, gerar `handoff packet` e exigir que o próximo agente respeite `READ`/`DO_NOT_READ`.

---

## 5. Nível de execução — profundidade, nunca gates

Cada feature registra em `STATE.md`:

```text
EXECUTION_LEVEL: FAST | STANDARD | CRITICAL
```

O nível controla **profundidade e rigor operacional**, sem alterar a máquina de aprovações:

| Nível | Profundidade | Gates |
|---|---|---|
| `FAST` | mudança localizada/baixo risco: discovery curto e leitura mínima necessária | **iguais ao fluxo padrão** |
| `STANDARD` | profundidade normal para histórias e bugs comuns | **iguais ao fluxo padrão** |
| `CRITICAL` | discovery mais profundo, evidência mais ampla, regressão reforçada e maior rigor de Judge | **iguais ao fluxo padrão** |

Regras:

- default: `STANDARD`;
- `FAST` não elimina PRD, RED, Judge, QA ou qualquer aprovação humana;
- `CRITICAL` pode recomendar `JUDGE_SECONDARY` dentro da mesma fase de julgamento, sem criar um novo gate humano;
- sinais como produção, cross-repo, contrato público, persistência sensível, mensageria, concorrência ou segurança devem impedir redução automática para `FAST`;
- o usuário pode elevar o nível a qualquer momento;
- overlays de `skills/cenarios/` podem aprofundar investigação/testes, mas nunca modificar gates.

---

## 6. Binding de modelos — sessão, não projeto

| Papel | Modelo sugerido hoje |
|---|---|
| `HEAD_STRONG` | DeepSeek V4 Pro |
| `EXECUTOR` | GPT-5.6 Luna Pro |
| `ECONOMICAL` | DeepSeek V4 Flash 0731 |
| `MULTIMODAL` | Gemini 3.7 Flash |
| `JUDGE_PRIMARY` | DeepSeek V4 Pro em fresh context/read-only |
| `JUDGE_SECONDARY` | Gemini 3.7 Flash ou outro confirmado |

A skill `skills/00-bootstrap-modelos.md` contém o bootstrap detalhado. O repositório persiste papéis/estado, não configuração global modelo → papel.

---

## 7. Máquina de estados e roteamento

| Estado | Skill | Papel | Gate | Próximo estado padrão |
|---|---|---|---|---|
| `MODEL_CONFIRMATION` | `00-bootstrap-modelos.md` | ORCHESTRATOR | confirmar perfil | `INTAKE` ou `RESUME` |
| `INTAKE` | `01-intake-jira.md` | `ECONOMICAL` | — | `MEMORY_LOOKUP` |
| `MEMORY_LOOKUP` | `02-memoria-feature.md` | `ECONOMICAL` | — | `DISCOVERY` |
| `DISCOVERY` | `03-investigacao.md` | `ECONOMICAL` | — | `INTERVIEW_OPTIONAL` ou `SOLUTION_REVIEW` |
| `INTERVIEW_OPTIONAL` | `04-entrevista-opcional.md` | `HEAD_STRONG` | resposta humana se necessária | `SOLUTION_REVIEW` |
| `SOLUTION_REVIEW` | `05-solucao-proposta.md` | `HEAD_STRONG` | `APROVAR SOLUÇÃO` | `PRD_PLAN_REVIEW` |
| `PRD_PLAN_REVIEW` | `06-prd-plano.md` | `HEAD_STRONG` | `APROVAR PRD/PLANO` | `RED_REVIEW` |
| `RED_REVIEW` | `07-testes-red.md` | `EXECUTOR` | `APROVAR RED` | `WAITING_GO` |
| `WAITING_GO` | `08-implementacao-go.md` | `EXECUTOR` | `GO` | `IMPLEMENTING` |
| `IMPLEMENTING` | `08-implementacao-go.md` | `EXECUTOR` | — | `GREEN_VALIDATION` |
| `GREEN_VALIDATION` | `09-validacao-green.md` | `EXECUTOR` | — | `JUDGING` ou `REWORK` |
| `JUDGING` | `10-juiz.md` | `JUDGE_PRIMARY` | automático/read-only | `QA_REVIEW` ou `REWORK` |
| `REWORK` | `08-implementacao-go.md` | `EXECUTOR` | — | `GREEN_VALIDATION` |
| `QA_REVIEW` | `11-qa-pack.md` | `EXECUTOR` | `APROVAR QA` | `COMMIT_REVIEW` |
| `COMMIT_REVIEW` | `12-commit-workflow.md` | `EXECUTOR` | confirmação de commit | `COMMITTED` |
| `COMMITTED` | — | ORCHESTRATOR | — | `PR_READY` ou `READY_TO_ARCHIVE` |
| `PR_READY` | `13-pull-request-workflow.md` | `EXECUTOR` | `ABRIR PR PARA <branch>` | `PR_OPENED|PR_BLOCKED` |
| `READY_TO_ARCHIVE` | `14-arquivamento.md` | `ECONOMICAL` | `ARQUIVAR` | `ARCHIVED` |

`PR` é on-demand. Se não solicitado, registrar `PR_STATUS=NOT_REQUESTED` e seguir para archive quando os demais gates estiverem resolvidos.

---

## 8. QA — preservado como na esteira anterior

Após Judge válido, a fase QA continua obrigatória no fluxo padrão:

```text
09-qa-tests.md
+ collection Postman/Insomnia
+ 10-qa-guide.md
+ DOCX em qa/ quando o ambiente suportar
-> APROVAR QA
```

Não existem `QA_FULL`, `QA_LIGHT` ou `QA_NOT_REQUIRED` nesta versão. A lógica detalhada pertence exclusivamente a `skills/11-qa-pack.md`.

---

## 9. Handoff entre papéis/modelos

Quando houver troca de papel/modelo, gerar handoff curto a partir de `templates/handoff-packet.md`.

O handoff aponta para artefatos e contém apenas:

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

Se handoff + artefatos permitidos forem suficientes, transcript anterior é proibido.

---

## 10. Memória por feature — compatibilidade estável

Pasta:

```text
.ai/features/<JIRA-ID>/
```

Estrutura canônica:

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
11-archive.md                  # nome estável da memória final
qa/
delivery/
  commit.md
  pull-request.md
  pr/                         # opcional em cross-repo
```

**`11-archive.md` é um identificador estável de compatibilidade, não o número da fase cronológica.** Commit e PR ficam em `delivery/` para que novas etapas de entrega não renumerem a memória histórica.

Compatibilidade de leitura:

- preferir `11-archive.md` como canônico;
- se `11-archive.md` não existir, aceitar `13-archive.md` apenas como legado transitório das versões anteriores;
- aceitar `11-commit.md` / `12-pull-request.md` como legado transitório;
- novas gravações usam somente `11-archive.md` e `delivery/`.

---

## 11. Orçamento e observabilidade

```text
MONTHLY_BUDGET_USD=40
FEATURE_TARGET_USD=8
FEATURE_WARNING_USD=10
```

Quando disponíveis, registrar por fase/papel:

```text
COST_USD
INPUT_TOKENS
CACHE_READ_TOKENS
OUTPUT_TOKENS
CACHE_HIT_RATIO
MODEL_ESCALATIONS
DURATION
```

Ao atingir `FEATURE_WARNING_USD`, informar custo conhecido, fase e pendências sem comprometer qualidade.

---

## 12. Cenários on-demand

Carregar somente quando aplicável:

- `skills/cenarios/historia-padrao.md`
- `skills/cenarios/local-conhecido.md`
- `skills/cenarios/bug-desenvolvimento.md`
- `skills/cenarios/bug-producao.md`
- `skills/cenarios/cross-repo.md`

Cenários podem ajustar profundidade de investigação ou recomendar segundo Judge, mas **não podem remover/agrupar os gates globais**.

---

## 13. Critério de pronto

`READY_FOR_QA` exige:

- critérios de aceite mapeados;
- solução e PRD/plano aprovados;
- RED aprovado e lock íntegro;
- implementação compilável;
- unitários GREEN, incluindo happy path + edge cases aplicáveis;
- Judge `PASS` ou risco explicitamente aceito;
- limitações registradas.

`READY_TO_ARCHIVE` exige:

- QA aprovado;
- collection e guia produzidos;
- commit policy resolvida;
- PR policy resolvida;
- memória compactada e pesquisável.

---

## 14. Regra operacional curta

```text
/orquestrador
-> RESOLVE FEATURE
-> RESUME ou NEW
-> LOAD ONLY CURRENT SKILL
-> LOAD ONLY ALLOWED CONTEXT
-> EXECUTE
-> CHECK FIXED GATE
-> SAVE STATE + NEXT_ACTION
-> HANDOFF
-> UNLOAD OLD PHASE
-> NEXT
```
