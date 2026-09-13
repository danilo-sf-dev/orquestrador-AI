# 07 — Memória e artefatos

> HUMAN_ONLY. Este arquivo é para consulta do usuário e não deve ser carregado por agentes.

## `.ai/` — memória operacional local

A pasta `.ai/` pertence à execução das features Jira e **não deve subir para o Git**.

```text
NEVER_STAGE
NEVER_COMMIT
NEVER_PUSH
```

A proteção é verificada ao criar/reusar `.ai/` e novamente antes de commit.
`documentacao-usuario/` é diferente: fica versionada, mas proibida no contexto dos agentes.

## Estrutura do fluxo COMUM

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
  09-qa-tests.md            # quando QA existir
  10-qa-guide.md            # quando QA existir
  11-archive.md
  recovery/
  qa/
  delivery/
```

## Estrutura do QUICK

O QUICK evita artefatos completos por cerimônia. Normalmente usa `STATE.md`, Jira, RED/lock,
implementation summary, GREEN evidence, judgement, QA quando necessário, archive e delivery.

## `STATE.md` — checkpoint operacional
Guarda onde a feature está e o próximo passo. Não deve virar documentação completa.

Campos centrais incluem `CURRENT_STATE`, `NEXT_ACTION`, papéis/modelos, `SOLUTION_APPROVED`,
`SPEC_STATUS`, `SPEC_PLAN_APPROVED`, RED/GREEN/Judge/QA/commit/PR.

## `00-jira.md`
Snapshot normalizado do Jira, sem credenciais.

## `01-discovery.md`
Evidência compacta da investigação, sem dumps brutos.

## `01-requirements.md`
Contrato de requisitos com `R-*`, assumptions, open questions, riscos e melhorias opcionais.

## `01-quality-review.md`
Revisão arquitetural opcional; findings `TQ-*` não viram obrigação automaticamente.

## `02-design.md`
Desenho técnico, Senior Approach Check, decisões `SD-*`, boundaries, contratos e riscos.

## `02-solution.md`
Solução aprovada; decisões materiais promovidas usam `DD-*`.

## `03-spec.md` — SPEC canônica
Define comportamento observável, ACs, constraints, assumptions aceitas, contratos, requisitos não
funcionais, decisões e riscos/validação.

Depois de `APROVAR SPEC/PLANO`, fica congelada. Mudança material posterior volta à fase responsável.

## `04-implementation-plan.md`
Organiza `PLAN-*`, dependências, requisitos/ACs, arquivos, testes e verificação.

## `05-red-tests.md`
Contrato RED e evidência real da execução. `UNEXPECTED_PASS`/`WRONG_FAILURE` não são RED válido.

## `red-tests.lock`
Protege testes RED por hash; só `REOPEN RED` formal autoriza invalidar e produzir novo lock.

## `06-implementation-summary.md`
Resumo do que foi implementado e de onde veio no contrato/plano.

## `07-green-evidence.md`
Evidência mecânica de lock, compile, testes, regressão e limitações.

## `08-judgement.md`
Veredito, avaliação por AC, findings e selo/hash do escopo julgado.

## QA
`09-qa-tests.md`, `10-qa-guide.md` e `qa/` guardam cenários e entregáveis de QA.

## `delivery/`
Guarda registros de commit e descrição de PR por repo quando necessário.

## `11-archive.md`
Memória pesquisável final com conhecimento reutilizável. `13-archive.md` pode existir como legado.

## `.ai/FEATURE_INDEX.md`
Índice pequeno para localizar features anteriores sem carregar histórico inteiro.

## Nota de legado PRD -> SPEC

Features arquivadas em versões anteriores podem conter:

```text
03-prd.md
PRD_PLAN_REVIEW
PRD_PLAN_APPROVED
APROVAR PRD/PLANO
```

Esses nomes pertencem ao modelo anterior. Conceitualmente, `03-prd.md` cumpria papel equivalente/próximo
à SPEC atual. Ao consultar uma feature antiga, use o conteúdo como memória histórica após revalidação.
Novas features usam exclusivamente:

```text
03-spec.md
SPEC_PLAN_REVIEW
SPEC_PLAN_APPROVED
APROVAR SPEC/PLANO
```
