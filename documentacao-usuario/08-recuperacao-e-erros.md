# 08 — Recuperação, bloqueios e erros

> HUMAN_ONLY. Este arquivo é para consulta do usuário e não deve ser carregado por agentes.

O princípio do recovery é corrigir **somente o delta inválido**, evitando reiniciar a história inteira.

## `JUDGE_RECOVERY` — recovery dirigido

Apesar do nome canônico ter nascido no fluxo pós-Judge, a V1.9.3 usa a mesma skill de recovery para
findings materiais descobertos em:

```text
RED_EXECUTION
IMPLEMENTATION
GREEN_VALIDATION
QUICK_AUTOGO
JUDGING
```

Ela analisa apenas o trigger/finding atual e responde:

```text
O requisito mudou?
A solução continua válida?
A SPEC/plano continuam válidos?
O RED continua válido?
Existe decisão humana pendente?
Qual é o menor estado seguro para retomar?
```

A saída fica em:

```text
recovery/judge-recovery-<N>.md
```

## Retornos possíveis

### Somente implementação

```text
JUDGE_RECOVERY
-> REWORK_IMPLEMENTATION
-> GREEN_VALIDATION
-> JUDGING fresh
```

Nenhum contrato ou teste selado é alterado.

### Requisito afetado

```text
JUDGE_RECOVERY
-> REQUIREMENT_ANALYSIS
-> fluxo normal de design/solução/SPEC novamente
```

Aprovações downstream afetadas ficam stale e precisam ser refeitas pelos gates já existentes.

### Solução afetada

```text
JUDGE_RECOVERY
-> SOLUTION_DESIGN
-> SOLUTION_REVIEW
-> APROVAR SOLUÇÃO
-> SPEC_PLAN_REVIEW
```

### Somente SPEC/plano afetado

```text
JUDGE_RECOVERY
-> SPEC_PLAN_REVIEW
-> APROVAR SPEC/PLANO
```

### RED precisa mudar

Se ainda não existe lock válido, volta ao `RED_REVIEW` e usa `APROVAR RED` normalmente.

Se já existe `red-tests.lock`, o recovery não altera testes sozinho. Depois de revalidar/reaprovar os
contratos superiores afetados, ele solicita exatamente:

```text
REOPEN RED
```

## `REOPEN RED`

Somente essa frase exata autoriza alterar RED previamente lockado.

Depois:

```text
lock antigo inválido
-> RED_REVIEW aplica somente delta aprovado
-> RED_EXECUTION
-> novo red-tests.lock
-> implementação/rework
-> GREEN_VALIDATION
-> JUDGING fresh
```

`sim`, `ok` ou `aprovado` não substituem esse gate.

## Judge = `FAIL`

### `IMPLEMENTATION_DEFECT`

Contrato e RED continuam válidos:

```text
JUDGING
-> REWORK_IMPLEMENTATION
-> GREEN_VALIDATION
-> JUDGING fresh
```

### `RED_CONTRACT_DEFECT`

RED representa incorretamente o comportamento esperado:

```text
JUDGING
-> JUDGE_RECOVERY
```

### `DISCOVERY_GAP`

Fato relevante de código/contrato não foi descoberto antes. O recovery faz targeted rediscovery apenas
ao redor do finding.

### `REQUIREMENT_AMBIGUITY`

Existe decisão de produto/negócio que não pode ser inferida. O recovery pergunta somente o mínimo
necessário e depois retorna para `REQUIREMENT_ANALYSIS` quando houver mudança material.

## Finding antes do Judge

Se RED, implementação ou GREEN detectar que o contrato pode estar errado, o executor **não** altera
SPEC ou teste selado. Ele registra:

```text
RECOVERY_SOURCE
RECOVERY_CLASS
```

e passa para `JUDGE_RECOVERY [HEAD_STRONG]`.

Isso elimina o antigo buraco em que uma fase pré-Judge tentava usar um recovery que exigia
`JUDGE_STATUS=FAIL`.

## `GREEN_STATUS=FAIL`

Se contrato/RED continuam válidos e a falha é apenas da implementação:

```text
GREEN_VALIDATION
-> REWORK_IMPLEMENTATION
```

Se houver dúvida material sobre contrato/RED, passa por recovery dirigido.

## `GREEN_STATUS=INVALID_GREEN`

Exemplo: teste protegido pelo RED lock foi alterado sem autorização. O sistema não recalcula o lock para
aceitar a mudança; passa por recovery.

## `MISSING` e `PENDING_EXTERNAL`

- `MISSING`: evidência necessária está ausente;
- `PENDING_EXTERNAL`: contrato já previa validação posterior, como QA/integration/external validation.

Evidência futura não vira PASS antecipado.

## `JUDGING=BLOCKED`

Falta condição/evidência essencial para julgar. O Judge permanece bloqueado; não completa a lacuna por
adivinhação.

## QUICK abortado

### Antes do AUTO-GO

Perdeu elegibilidade:

```text
FLOW_MODE=STANDARD_GATED
CURRENT_STATE=MEMORY_LOOKUP
```

### Depois que execução começou

Descoberta material usa recovery dirigido para preservar o trabalho ainda válido.

## Judge secundário discorda

Não existe votação automática. Divergência material fica bloqueada para decisão humana.

## PR não foi “aberto”

`PR_DESCRIPTION` gera texto para input manual. Se o agente disser que criou PR/MR remoto usando essa
skill, contradiz o contrato.

## DOCX de QA não foi gerado

Se o ambiente não suportar DOCX, deixar `10-qa-guide.md` pronto e registrar o bloqueio; não fingir que o
arquivo existe.

## Jira não acessível

- `401`: autenticação inválida/token expirado;
- `403`: usuário sem permissão;
- `404`: issue inexistente ou inacessível;
- erro de rede: falha de conexão.

A skill não inventa conteúdo da issue quando a consulta falha.

## Retomada após interrupção

`STATE.md` define `CURRENT_STATE` e `NEXT_ACTION`. A V1.9.3 exige que toda transição de fase deixe esses
dois campos suficientes para `RESUME` sem depender do histórico do chat.
