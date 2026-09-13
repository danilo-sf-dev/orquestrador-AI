# Workflow agêntico para Java/Spring Boot — V1.9.0

Este pacote define uma esteira agnóstica de modelos para histórias Jira, bugs, mudanças cross-repo,
testes, QA, commit e descrição de Pull Request. O objetivo continua sendo **qualidade alta com contexto
controlado e custo previsível**.

## Foco da V1.9.0

A V1.9 mantém os controles de execução da V1.8 e fortalece o que acontece **antes do RED**:

1. Discovery econômico com **Codebase Recon / entry-point-first**;
2. nova `Requirement Analysis` para gap scan, assumptions e open questions;
3. nova `Solution Design` com **Senior Approach Check** proporcional;
4. revisão arquitetural opcional preservada, sem transformar todo Jira em refactor;
5. `03-prd.md` tratado semanticamente como **SPEC canônica**;
6. rastreabilidade `R/Jira -> AC -> DD -> PLAN -> código/teste/evidência`;
7. RED/GREEN com gates mais mecânicos;
8. Judge com regra **evidence-or-zero** por critério;
9. QUICK preservado: executa versões compactas de Requirement Analysis + Solution Check sem novos artefatos/gates;
10. skills principais abaixo de 400 linhas e referências lazy-loaded quando necessário.

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

## Entrada única

```text
Leia e siga:
"<caminho>/orquestrador.md"
```

O orquestrador resolve `RESUME` ou `NEW`, seleciona fluxo, papel, skill, contexto permitido e gate.

### Fluxos

```text
QUICK / AUTO-GO
- mudança simples, localizada, inequívoca e de baixo risco
- uma aprovação inicial
- RED -> implementação -> GREEN automáticos até handoff para Judge

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

Não carregar automaticamente README, todas as skills/referências, transcript, logs brutos ou features antigas completas.

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
  03-prd.md             # nome legado; conteúdo = SPEC canônica
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

## Fluxo COMUM

```text
JIRA_ACCESS [ECONOMICAL]
-> INTAKE [ECONOMICAL]
-> MEMORY_LOOKUP [ECONOMICAL]
-> DISCOVERY [ECONOMICAL]
-> HANDOFF HEAD_STRONG
-> REQUIREMENT_ANALYSIS [HEAD_STRONG]
   -> INTERVIEW_OPTIONAL somente se OPEN_QUESTION bloqueante
-> TECHNICAL_QUALITY_REVIEW [HEAD_STRONG] somente quando requerida
-> SOLUTION_DESIGN [HEAD_STRONG]
-> SOLUTION_REVIEW [HEAD_STRONG] [APROVAR SOLUÇÃO]
-> PRD_PLAN_REVIEW [HEAD_STRONG] [APROVAR PRD/PLANO]
-> HANDOFF EXECUTOR
-> RED_REVIEW [EXECUTOR] [APROVAR RED]
-> RED_EXECUTION [EXECUTOR] cria/executa RED + lock
-> WAITING_GO [EXECUTOR] [GO]
-> IMPLEMENTING [EXECUTOR]
-> GREEN_VALIDATION [EXECUTOR]
-> HANDOFF JUDGE_PRIMARY
-> JUDGING [JUDGE_PRIMARY]
-> QA_REVIEW [EXECUTOR] [APROVAR QA]
-> COMMIT_REVIEW [EXECUTOR] [AUTOMÁTICO | MANUAL | OUTROS]
-> PR_DESCRIPTION quando solicitado
-> READY_TO_ARCHIVE [ECONOMICAL]
```

`Requirement Analysis`, `Solution Design` e `Technical Quality Review` não adicionam gates humanos.
A única parada adicional possível é uma pergunta material que tornaria inseguro prosseguir por inferência.

## Requirement Analysis

`skills/04a-analise-requisitos.md` separa:

```text
EXPLICIT_REQUIREMENT
IMPLICIT_NECESSITY
ASSUMPTION
OPEN_QUESTION
TECHNICAL_RISK
OPTIONAL_IMPROVEMENT
```

`OPEN_QUESTION` só bloqueia quando a resposta puder mudar materialmente comportamento, contrato, regra
de negócio, segurança, persistência, integração, efeito destrutivo ou desenho do RED.

## Solution Design

`skills/04b-design-solucao.md` executa o Senior Approach Check: solução mais simples, padrão equivalente,
acoplamento/abstração desnecessária, boundaries/contratos e efeitos colaterais. A regra é **seguir
arquitetura válida existente e escolher a menor mudança suficiente**.

`skills/18-qualidade-arquitetural.md` continua opcional e especializada.

## SPEC + Plano

`skills/06-prd-plano.md` mantém `03-prd.md` por compatibilidade, mas o conteúdo passa a ser a SPEC
canônica. A matriz principal é:

```text
R-* -> AC-* -> DD-* -> PLAN-* -> arquivo/diff -> teste/evidência
```

Delta material posterior retorna à fase responsável; executor não redefine a SPEC.

## RED / GREEN

RED mantém `RED_REVIEW` e `RED_EXECUTION`. Todos os ACs precisam de evidência planejada; evidência pode
ser unitária, integrada, estática, QA ou externa quando apropriado.

GREEN usa gate mecânico com lock, compile, testes, regressão, failures/skips inesperados, evidência por
AC e diff limpo dos testes lockados.

## Judge e recovery

Judge executa fresh/read-only e avalia cada AC com **evidence-or-zero**. Sem evidência suficiente, não
marca `PASS` por plausibilidade.

Todo `FAIL` é classificado como:

```text
IMPLEMENTATION_DEFECT
RED_CONTRACT_DEFECT
DISCOVERY_GAP
REQUIREMENT_AMBIGUITY
```

Somente `IMPLEMENTATION_DEFECT` volta direto para rework; os demais passam por `17-judge-recovery.md`.

## QUICK / AUTO-GO

QUICK não materializa Requirements/Design/SPEC/Plan completos. Antes do Quick Contract executa versões
compactas de Codebase Recon, Requirement Gap, Assumptions/Open Questions e Senior Solution Check. Se
surgir blocker material ou decisão estrutural, migra para COMUM.

## Commit e PR

- `12-commit-workflow.md`: commits faseados por intenção; `AUTOMÁTICO`, `MANUAL` ou `OUTROS`.
- `13-pull-request-workflow.md`: gera somente título/descrição para preenchimento manual; não cria PR/MR remoto.

## Orçamento

```text
MONTHLY_BUDGET_USD=40
FEATURE_TARGET_USD=8
FEATURE_WARNING_USD=10
```

Economia deve vir de search-first, lazy loading, compactação, model routing e gates determinísticos —
nunca de omitir requisito, teste ou validação material.
