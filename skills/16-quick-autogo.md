---
name: quick-autogo
description: >
  Fluxo curto para tarefas pequenas, localizadas e de baixo risco. Após uma
  única aprovação AUTO-GO, executa RED, lock, implementação e GREEN sem novas
  interrupções até o handoff para Judge.
model_role: EXECUTOR
context_loading: lazy
reads:
  - STATE.md
  - 00-jira.md
  - source_code_relevant
  - related_tests
writes:
  - STATE.md
  - 05-red-tests.md
  - red-tests.lock
  - source_code
  - 06-implementation-summary.md
  - 07-green-evidence.md
forbidden_reads:
  - full_chat_transcript
  - unrelated_features
  - unrelated_repository_files
forbidden_writes:
  - jira_credentials
  - approved_requirements
  - locked_red_tests_after_lock
---

# QUICK / AUTO-GO

## Objetivo
Executar tarefas simples com poucas interações sem remover entendimento correto, análise mínima de
requisitos, escolha técnica consciente, TDD, RED lock, GREEN e Judge independente.

QUICK reduz cerimônia, não qualidade. Não criar Discovery/Requirements/Design/SPEC/Plan completos apenas
para preencher estrutura.

## Pré-condições

```yaml
FLOW_MODE: QUICK_AUTOGO
JIRA_CONTEXT_READY: true
```

O Quick Contract e `AUTO-GO -> RED -> implementação -> GREEN` exigem `EXECUTOR`. Em routing manual,
fazer handoff antes do Quick Contract.

## Elegibilidade
QUICK é adequado quando a mudança é localizada, de baixo risco, comportamento inequívoco, normalmente
single-repo, objetivamente testável e sem decisão arquitetural relevante.

Abortar para `STANDARD_GATED` se houver banco/migração, mensageria, segurança, concorrência, contrato
material entre serviços, cross-repo inesperado, regra de negócio ambígua ou decisão estrutural.

## Compact Requirement Analysis
Antes do Quick Contract, verificar somente dimensões aplicáveis:

```text
validation/null/invalid
error behavior
contract compatibility
external dependency failure
data/state branches
idempotency/concurrency quando houver sinal
```

Classificar pontos materiais como:

```text
EXPLICIT | IMPLICIT_NECESSITY | ASSUMPTION | OPEN_QUESTION | RISK | OPTIONAL
```

Se existir `OPEN_QUESTION` capaz de mudar comportamento, contrato, regra de negócio, segurança,
persistência, integração ou desenho do RED:

```text
QUICK_AUTOGO_ABORTED
RECOMMENDED_FLOW=STANDARD_GATED
REASON=BLOCKING_OPEN_QUESTION
```

Não usar QUICK para inferir e corrigir depois.

## Compact Senior Solution Check
Antes do Quick Contract, verificar:

1. existe abordagem significativamente mais simples?
2. existe padrão equivalente já usado no projeto?
3. a mudança cria acoplamento/camada/abstração desnecessária?
4. cruza boundary/contrato que torne a tarefa não simples?
5. há efeito colateral previsível em outro fluxo?

Se houver trade-off material ou necessidade de revisão estrutural, migrar para `STANDARD_GATED`.
Melhoria estética/sintática não bloqueia e não amplia escopo.

## Quick Contract — única aprovação inicial
Apresentar:

```text
QUICK CONTRACT — <JIRA>

Entendimento:
- ...

Requisitos/assumptions relevantes:
- ...

Escopo provável:
- ...

Abordagem escolhida:
- ...

RED planejado:
1. ...
2. ...
3. edge cases aplicáveis ...

Riscos/gatilhos de escalonamento:
- ...

AUTO-GO autoriza:
RED -> comprovação RED -> lock -> implementação -> GREEN -> rework técnico
sem novas perguntas até o handoff para Judge.
```

Aguardar exatamente:

```text
AUTO-GO
```

Sem `AUTO-GO`, não modificar código/testes do repositório.

## Execução automática
Após aprovação:

```text
criar RED
-> executar e comprovar falha pelo motivo esperado
-> registrar 05-red-tests.md
-> gerar red-tests.lock
-> implementar somente o contrato aprovado
-> executar GREEN
-> corrigir somente implementação quando necessário
-> repetir GREEN até PASS ou bloqueio real
```

Cada teste precisa estar ligado a comportamento/requisito explícito do Quick Contract. Cobrir happy
path e edge cases aplicáveis; não criar caso artificial.

`UNEXPECTED_PASS` ou falha por motivo incorreto não contam como RED comprovado. Após lock, testes
protegidos não podem ser alterados silenciosamente.

## GREEN mecânico
GREEN exige:

```text
RED_LOCK=VALID
COMPILE=PASS|N/A_WITH_REASON
RED_TESTS=PASS
RELATED_REGRESSION=PASS|N/A_WITH_REASON
UNEXPECTED_FAILURES=0
UNEXPECTED_SKIPPED=0
LOCKED_TEST_DIFF=CLEAN
```

Persistir evidência real em `07-green-evidence.md`. Não inventar contagens não reportadas.

## Escalonamento durante execução
Abortar QUICK se surgir segundo repositório, mudança de contrato material, banco/migração, mensageria,
segurança, concorrência, arquitetura, requisito conflitante, necessidade de reinterpretar Jira ou RED
impossível de definir sem decisão humana.

```text
QUICK_AUTOGO_ABORTED
RECOMMENDED_FLOW=STANDARD_GATED
REASON=<motivo>
```

Nunca converter silenciosamente QUICK em implementação complexa.

## Handoff para Judge
Quando GREEN estiver válido:

```text
QUICK_READY_FOR_JUDGE
GREEN: PASS
RED_LOCK: VALID
NEXT_MODEL_ROLE: JUDGE_PRIMARY
```

O Judge recebe somente Jira, Quick Contract aprovado, RED spec/lock, diff relevante e GREEN evidence.
Não fornecer transcript nem histórico de tentativas. No QUICK, o Quick Contract é o contrato aprovado;
não exigir artefatos exclusivos do fluxo STANDARD.

## Judge FAIL
Usar a classificação da skill 10:

- `IMPLEMENTATION_DEFECT`: `REWORK_IMPLEMENTATION -> GREEN_VALIDATION -> JUDGING fresh`, sem tocar RED.
- `RED_CONTRACT_DEFECT`, `DISCOVERY_GAP` ou `REQUIREMENT_AMBIGUITY`: abortar QUICK e migrar para
  `JUDGE_RECOVERY [HEAD_STRONG]`.

Não reabrir RED dentro do QUICK sem recovery formal.

## QA e delivery
Após Judge PASS, perguntar se QA/documentação é necessário. Se sim, executar skill 11; se não,
registrar justificativa.

Depois seguir `COMMIT_REVIEW`. Commit mantém modos `AUTOMÁTICO | MANUAL | OUTROS`; PR continua on-demand
e apenas gera descrição para input manual; archive segue skill 14.

## Artefatos QUICK
Criar somente:

```text
STATE.md
00-jira.md
05-red-tests.md
red-tests.lock
06-implementation-summary.md
07-green-evidence.md
08-judgement.md
09-qa-tests.md       # se QA existir
10-qa-guide.md       # se QA existir
11-archive.md
delivery/
```
