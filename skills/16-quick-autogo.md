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

## 1. Objetivo

Executar tarefas simples com poucas interações humanas sem remover:
- entendimento correto do Jira;
- TDD com RED;
- proteção por lock;
- GREEN;
- Judge independente.

QUICK reduz cerimônia, não qualidade.

---

## 2. Pré-condições

```yaml
FLOW_MODE: QUICK_AUTOGO
JIRA_CONTEXT_READY: true
```

Antes de modificar código, validar elegibilidade.

---

## 3. Elegibilidade

QUICK é adequado quando a alteração é:
- localizada;
- de baixo risco;
- comportamento inequívoco;
- normalmente single-repo;
- testável objetivamente;
- sem decisão arquitetural relevante;
- sem banco/migração;
- sem mensageria;
- sem segurança;
- sem concorrência;
- sem mudança material de contrato entre serviços.

Número de arquivos é apenas sinal, não regra rígida.

---

## 4. Quick Contract — primeira interação

Após Jira + leitura mínima do código, apresentar:

```text
QUICK CONTRACT — <JIRA>

Entendimento:
- ...

Escopo provável:
- ...

Comportamento/origem esperada:
- ...

RED planejado:
1. ...
2. ...
3. edge cases aplicáveis ...

Sinais de elegibilidade:
- ...

Riscos/gatilhos de escalonamento:
- ...

AUTO-GO autoriza:
RED -> comprovação RED -> lock -> implementação -> GREEN -> rework técnico
sem novas perguntas até o handoff para Judge.
```

Aguardar:

```text
AUTO-GO
```

Sem `AUTO-GO`, não modificar código de produção.

---

## 5. Execução automática após AUTO-GO

```text
criar RED
-> executar e comprovar RED
-> registrar 05-red-tests.md
-> gerar red-tests.lock
-> implementar somente o escopo aprovado
-> executar GREEN
-> corrigir implementação quando necessário
-> repetir GREEN até PASS ou bloqueio real
```

Não pedir autorização intermediária para teste, implementação, build ou correção dentro do escopo aprovado.

---

## 6. RED

Cobrir quando aplicável:
- happy path;
- null/ausência/optional;
- vazio;
- boundary;
- mapping/serialization;
- erro de dependência;
- branch relevante;
- regressão adjacente.

Estados:

```text
COVERED
NOT_APPLICABLE
DEFERRED_WITH_REASON
```

Após lock, testes protegidos não podem ser alterados silenciosamente.

Se o RED estiver conceitualmente errado:

```text
QUICK_AUTOGO_ABORTED
REASON=REOPEN_RED_REQUIRED
```

---

## 7. Escalonamento obrigatório

Abortar QUICK quando surgir:
- segundo repositório inesperado;
- contrato entre serviços;
- banco/migração;
- mensageria;
- segurança;
- concorrência;
- arquitetura;
- regra de negócio ambígua;
- requisito conflitante;
- necessidade de reinterpretar o Jira;
- RED impossível de definir sem decisão humana.

Saída:

```text
QUICK_AUTOGO_ABORTED
RECOMMENDED_FLOW=STANDARD_GATED
REASON=<motivo>
```

Nunca converter silenciosamente uma tarefa QUICK em implementação complexa.

---

## 8. GREEN

GREEN exige:
- RED agora verde;
- testes relevantes existentes verdes;
- build/compile aplicável;
- lock íntegro;
- nenhuma alteração fora do escopo sem justificativa.

Persistir em:

```text
07-green-evidence.md
```

---

## 9. Handoff para Judge — segunda interação

Quando GREEN estiver válido:

```text
QUICK_READY_FOR_JUDGE

GREEN: PASS
RED_LOCK: VALID

PRÓXIMA ETAPA: JUDGE
PAPEL RECOMENDADO: JUDGE_PRIMARY

Se o runtime não troca modelo automaticamente:
troque manualmente o modelo no chat e responda:

CONTINUAR JUDGE
```

Gerar handoff via `templates/handoff-packet.md`.

O Judge recebe apenas:
- `00-jira.md`;
- Quick Contract/decisões aprovadas;
- `05-red-tests.md`;
- `red-tests.lock`;
- diff/código final relevante;
- `07-green-evidence.md`.

Não fornecer transcript completo nem histórico de tentativas do executor.

Executar `skills/10-juiz.md`.

---

## 10. Judge FAIL

Se `FAIL`:
- voltar ao executor;
- corrigir implementação;
- executar GREEN novamente;
- gerar novo handoff;
- rodar novo Judge fresh.

Se a correção exigir mudar requisito, Quick Contract ou RED:

```text
QUICK_AUTOGO_ABORTED
```

---

## 11. QA — terceira interação

Após Judge `PASS`:

```text
Esta tarefa precisa de QA/documentação?

1. SIM — executar QA
2. NÃO — registrar justificativa e seguir
```

Estados:

```text
QA_REQUIRED
QA_NOT_REQUIRED_WITH_REASON
```

Se SIM, recomendar papel/modelo e executar `skills/11-qa-pack.md`.
Se NÃO, registrar justificativa curta.

---

## 12. Delivery

Depois do QA:

```text
-> COMMIT_REVIEW
```

Commit exige confirmação explícita.

PR continua on-demand; `PR_STATUS=NOT_REQUESTED` é válido.

Archive segue `skills/14-arquivamento.md`.

---

## 13. Artefatos QUICK

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

Não criar Discovery/Solution/PRD/Plan apenas para preencher estrutura.
