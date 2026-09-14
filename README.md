# Workflow agêntico — V1.9.3

Este pacote define uma esteira agnóstica de modelos para histórias Jira, bugs, mudanças cross-repo,
testes, QA, commit e descrição de Pull Request. O objetivo continua sendo **qualidade alta com contexto
controlado e custo previsível**.

## Foco da V1.9

A V1.9 mantém os controles de execução da V1.8 e fortalece o que acontece **antes do RED**:

1. Discovery econômico com **Codebase Recon / entry-point-first**;
2. `Requirement Analysis` para gap scan, assumptions e open questions;
3. `Solution Design` com **Senior Approach Check** proporcional;
4. revisão arquitetural opcional, sem transformar todo Jira em refactor;
5. `03-spec.md` como **SPEC canônica** da feature;
6. rastreabilidade `R/Jira -> AC -> DD -> PLAN -> código/teste/evidência`;
7. RED/GREEN com gates mecânicos;
8. Judge com regra **evidence-or-zero**;
9. QUICK preservado, sem artefatos/gates completos desnecessários;
10. skills principais abaixo de 400 linhas e referências lazy-loaded quando necessário.

Evolução desta linha:

- **V1.9.1:** manual humano em `documentacao-usuario/` + guardrail `HUMAN_ONLY`;
- **V1.9.2:** `SPEC` passa a ser a nomenclatura canônica ativa no lugar de PRD;
- **V1.9.3:** fecha state machine/RESUME, generaliza recovery pré/pós-Judge e reduz duplicação dos cenários.

Não foram adicionados novos agentes, novos juízes nem novos gates humanos obrigatórios.

## Filosofia

```text
ENTENDER MELHOR
Discovery + evidência
        ↓
ANALISAR MELHOR
Requirements + gaps + assumptions/open questions
        ↓
PROJETAR MELHOR
Solution Design + arquitetura proporcional
        ↓
CONTRATO
SPEC canônica
        ↓
EXECUTAR COM PROVA
RED -> Code -> GREEN -> Judge
```

A SPEC manda sobre implementação e testes. O executor não pode redefinir silenciosamente requisitos,
RED ou decisões aprovadas para fazer a solução passar.

## Entrada única do agente

```text
Leia e siga:
"<caminho>/orquestrador.md"
```

O orquestrador resolve `RESUME` ou `NEW`, seleciona fluxo, papel, skill, contexto permitido e gate.
Cada fase concluída deixa `CURRENT_STATE` + `NEXT_ACTION` suficientes para retomada determinística.

### Documentação exclusiva do usuário

O manual humano está em:

```text
documentacao-usuario/README.md
```

Essa pasta é **HUMAN_ONLY**: agentes não devem lê-la, buscá-la, indexá-la, incluí-la em handoff ou usá-la
como fonte técnica. A fonte operacional continua sendo `orquestrador.md`, a skill atual e os artefatos
permitidos da feature.

### Fluxos

```text
QUICK / AUTO-GO
- mudança simples, localizada, inequívoca e de baixo risco
- uma aprovação inicial
- RED -> implementação -> GREEN automáticos até Judge

COMUM / COMPLETA
- discovery + análise de requisitos + design + SPEC/plano
- gates completos existentes
```

`FAST | STANDARD | CRITICAL` alteram somente profundidade/rigor; não removem gates.

## Papéis de modelo

- `ECONOMICAL`: Jira, busca, recon, memória, evidência, archive;
- `HEAD_STRONG`: requisitos materiais, design, arquitetura, solução, planejamento e recovery;
- `EXECUTOR`: RED, implementação, GREEN, QA e commit;
- `JUDGE_PRIMARY`: julgamento independente em fresh context/read-only;
- `JUDGE_SECONDARY`: reforço independente em risco alto;
- `MULTIMODAL`: quando visual é essencial.

Preset atual:

```text
HEAD_STRONG     -> DeepSeek V4 Pro 0813
EXECUTOR        -> GPT-5.6 Luna Pro
ECONOMICAL      -> DeepSeek V4 Flash 0731
MULTIMODAL      -> Gemini 3.7 Flash
JUDGE_PRIMARY   -> DeepSeek V4 Pro fresh/read-only
```

O binding papel → modelo pertence à sessão/runtime. Não usar `.ai/config/model-profile.md`.

## Lazy loading

Por fase carregar apenas:

```text
orquestrador mínimo
+ STATE.md
+ skill atual
+ referência condicional explicitamente necessária
+ reads permitidos
+ código/testes relevantes
```

Não carregar automaticamente README, `documentacao-usuario/**`, todas as skills/referências,
transcript, logs brutos ou features antigas completas.

## Memória por feature

```text
.ai/features/JIRA-1234/
  STATE.md
  00-jira.md
  01-discovery.md
  01-requirements.md
  01-quality-review.md  # opcional
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

No QUICK, criar somente artefatos realmente usados. `.ai/` é sempre local e deve estar efetivamente
ignorada pelo Git ao iniciar/reusar a memória e novamente antes de qualquer commit.

> **Nota de legado:** features antigas podem conter `03-prd.md` e nomes `PRD_PLAN_*`. Para leitura
> histórica, interpretar como predecessor da SPEC atual; não propagar PRD para novas features.

## Fluxo COMUM

```text
JIRA_ACCESS [ECONOMICAL]
-> INTAKE [ECONOMICAL]
-> MEMORY_LOOKUP [ECONOMICAL]
-> DISCOVERY [ECONOMICAL]
-> REQUIREMENT_ANALYSIS [HEAD_STRONG]
   -> INTERVIEW_OPTIONAL somente se OPEN_QUESTION bloqueante
-> TECHNICAL_QUALITY_REVIEW [HEAD_STRONG] somente quando requerida
-> SOLUTION_DESIGN [HEAD_STRONG]
-> SOLUTION_REVIEW [HEAD_STRONG] [APROVAR SOLUÇÃO]
-> SPEC_PLAN_REVIEW [HEAD_STRONG] [APROVAR SPEC/PLANO]
-> RED_REVIEW [EXECUTOR] [APROVAR RED]
-> RED_EXECUTION [EXECUTOR] cria/executa RED + lock
-> WAITING_GO [EXECUTOR] [GO]
-> IMPLEMENTING [EXECUTOR]
-> GREEN_VALIDATION [EXECUTOR]
-> JUDGING [JUDGE_PRIMARY]
-> QA_REVIEW [EXECUTOR]
-> COMMIT_REVIEW [EXECUTOR] [AUTOMÁTICO | MANUAL | OUTROS]
-> PR_DESCRIPTION quando solicitado
-> READY_TO_ARCHIVE [ECONOMICAL]
```

`Requirement Analysis`, `Solution Design` e `Technical Quality Review` não adicionam gates humanos.

## Requirement Analysis e Solution Design

`skills/04a-analise-requisitos.md` separa requisito explícito, necessidade implícita, assumption,
open question, risco técnico e melhoria opcional. Só uma pergunta material bloqueia o fluxo.

`skills/04b-design-solucao.md` executa o Senior Approach Check e prefere a menor solução suficiente,
reutilizando padrões válidos do projeto sem introduzir abstração por preferência.

## SPEC + Plano

`skills/06-spec-plano.md` cria `03-spec.md`, a SPEC canônica. A matriz principal é:

```text
R-* -> AC-* -> DD-* -> PLAN-* -> arquivo/diff -> teste/evidência
```

Delta material posterior retorna à fase responsável; executor não redefine a SPEC.

## RED / GREEN

RED mantém `RED_REVIEW` e `RED_EXECUTION`. GREEN usa gate mecânico com lock, compile, testes, regressão,
failures/skips inesperados, evidência do contrato e diff limpo dos testes lockados.

## Judge e recovery dirigido

Judge executa fresh/read-only e aplica **evidence-or-zero**.

Todo `FAIL` é classificado como:

```text
IMPLEMENTATION_DEFECT
RED_CONTRACT_DEFECT
DISCOVERY_GAP
REQUIREMENT_AMBIGUITY
```

Somente `IMPLEMENTATION_DEFECT` volta direto para rework.

`skills/17-judge-recovery.md` agora é o recovery dirigido único para findings contratuais, podendo ser
acionado por RED, implementação, GREEN, QUICK ou Judge. Ele retorna ao menor estado seguro:

```text
Requirement delta -> REQUIREMENT_ANALYSIS
Solution delta    -> SOLUTION_DESIGN
SPEC/Plan delta   -> SPEC_PLAN_REVIEW
RED delta         -> RED_REVIEW / REOPEN RED quando lockado
Code only         -> REWORK_IMPLEMENTATION
```

Se o RED estiver lockado, contratos superiores são revalidados/reaprovados primeiro quando necessário;
só depois o recovery pode solicitar exatamente `REOPEN RED`.

## QUICK / AUTO-GO

QUICK não materializa Requirements/Design/SPEC/Plan completos. Antes do Quick Contract executa versões
compactas de Codebase Recon, Requirement Gap, Assumptions/Open Questions e Senior Solution Check.

Antes do AUTO-GO, perda de elegibilidade migra formalmente para `STANDARD_GATED -> MEMORY_LOOKUP`.
Depois que a execução começou, uma descoberta material usa recovery dirigido para preservar o trabalho válido.

QA no QUICK pode ser aprovado normalmente ou `NOT_REQUIRED_WITH_REASON`.

## Cenários

`skills/cenarios/` contém somente overlays de risco/profundidade. Cenários não duplicam nem substituem o
pipeline canônico do `orquestrador.md`, reduzindo drift e contexto.

## Commit e PR

- `12-commit-workflow.md`: commits faseados por intenção; `AUTOMÁTICO`, `MANUAL` ou `OUTROS`.
- `13-pull-request-workflow.md`: gera somente título/descrição para preenchimento manual; não cria PR/MR remoto.
- depois do commit/descrição de PR, o estado aponta explicitamente para archive quando aplicável.

## Orçamento

```text
MONTHLY_BUDGET_USD=40
FEATURE_TARGET_USD=8
FEATURE_WARNING_USD=10
```

Economia vem de search-first, lazy loading, contexto compacto, model routing e gates mecânicos — nunca
de omitir validação material.
