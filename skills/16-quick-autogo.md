---
name: quick-autogo
description: >
  Fluxo curto para tarefas pequenas, localizadas e de baixo risco. Após uma
  única aprovação AUTO-GO, executa RED, lock, implementação e GREEN sem novas
  interrupções até o handoff para Judge.
preferred_model_role: EXECUTOR
context_loading: lazy
reads:
  - STATE.md
  - 00-jira.md
  - source_code_relevant
  - related_tests
writes:
  - STATE.md
  - 05-red-tests.md
  - test_files_required_by_quick_red
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
CURRENT_STATE: QUICK_AUTOGO
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
persistência, integração ou desenho do RED, migrar formalmente:

```yaml
FLOW_MODE: STANDARD_GATED
CURRENT_STATE: MEMORY_LOOKUP
NEXT_ACTION: LOOKUP_RELATED_MEMORY
NEXT_MODEL_ROLE: ECONOMICAL
```

Registrar também:

```text
QUICK_AUTOGO_ABORTED
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

Se houver trade-off material ou necessidade de revisão estrutural, usar a mesma transição formal para
`STANDARD_GATED -> MEMORY_LOOKUP`. Melhoria estética/sintática não bloqueia e não amplia escopo.

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
Se surgir segundo repositório, mudança de contrato material, banco/migração, mensageria, segurança,
concorrência, arquitetura, requisito conflitante ou necessidade de reinterpretar Jira/RED **depois que
a execução já começou**, não reiniciar silenciosamente como STANDARD.

Registrar:

```yaml
FLOW_MODE: STANDARD_GATED
RECOVERY_STATUS: REQUIRED
RECOVERY_SOURCE: QUICK_AUTOGO
RECOVERY_CLASS: CONTRACT_MISMATCH
CURRENT_STATE: JUDGE_RECOVERY
NEXT_ACTION: ANALYZE_TARGETED_RECOVERY
NEXT_MODEL_ROLE: HEAD_STRONG
```

O recovery decide o menor ponto seguro de retorno e preserva o que continuar válido.

## Handoff para Judge
Quando GREEN estiver válido:

```yaml
GREEN_STATUS: PASS
CURRENT_STATE: JUDGING
NEXT_ACTION: JUDGE_DELIVERY
NEXT_MODEL_ROLE: JUDGE_PRIMARY
```

Em routing manual, marcar `MODEL_HANDOFF_REQUIRED=true` e parar para troca.

O Judge recebe somente Jira, Quick Contract aprovado, RED spec/lock, diff relevante e GREEN evidence.
Não fornecer transcript nem histórico de tentativas. No QUICK, o Quick Contract é o contrato aprovado;
não exigir artefatos exclusivos do fluxo STANDARD.

## Judge FAIL
Usar a classificação da skill 10:

- `IMPLEMENTATION_DEFECT`: `REWORK_IMPLEMENTATION -> GREEN_VALIDATION -> JUDGING fresh`, sem tocar RED.
- `RED_CONTRACT_DEFECT`, `DISCOVERY_GAP` ou `REQUIREMENT_AMBIGUITY`: marcar `FLOW_MODE=STANDARD_GATED` e rotear para `JUDGE_RECOVERY [HEAD_STRONG]` com o finding mínimo.

Não reabrir RED dentro do QUICK sem recovery formal.

## QA e delivery
Após Judge `PASS` ou `PASS_WITH_RISKS`, decidir se QA/documentação é necessário.

Se sim:

```yaml
CURRENT_STATE: QA_REVIEW
NEXT_ACTION: PREPARE_QA_PACK
NEXT_MODEL_ROLE: EXECUTOR
```

Se não:

```yaml
QA_STATUS: NOT_REQUIRED_WITH_REASON
CURRENT_STATE: COMMIT_REVIEW
NEXT_ACTION: PREPARE_COMMIT_PLAN
NEXT_MODEL_ROLE: EXECUTOR
```

Commit mantém modos `AUTOMÁTICO | MANUAL | OUTROS`; PR continua on-demand e apenas gera descrição para input manual; archive segue skill 14.

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
