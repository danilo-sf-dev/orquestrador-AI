# 08 — Recuperação, bloqueios e erros

> HUMAN_ONLY. Este arquivo é para consulta do usuário e não deve ser carregado por agentes.

Este capítulo explica o que acontece quando o fluxo não segue o caminho feliz. O princípio é evitar
reiniciar a história inteira quando apenas um delta precisa ser corrigido.

## Judge = `FAIL`

Um `FAIL` do Judge não significa automaticamente “voltar para RED”. Primeiro o problema é classificado.

### `IMPLEMENTATION_DEFECT` — Defeito de implementação

O contrato, a solução e o RED continuam válidos; o código não atende ao esperado.

Fluxo:

```text
JUDGING
-> REWORK_IMPLEMENTATION
-> GREEN_VALIDATION
-> JUDGING fresh
```

Os testes RED selados não são alterados.

### `RED_CONTRACT_DEFECT` — Defeito no contrato RED

O Judge encontrou evidência de que o RED aprovado representa incorretamente o comportamento esperado.

Fluxo:

```text
JUDGING
-> JUDGE_RECOVERY [HEAD_STRONG]
```

O recovery analisa exatamente o delta. Ele não edita RED diretamente.

### `DISCOVERY_GAP` — Lacuna de investigação

Surgiu um fato relevante de código/contrato que não foi descoberto antes.

`JUDGE_RECOVERY` faz targeted rediscovery apenas em torno do finding, evitando repetir toda a
investigação.

### `REQUIREMENT_AMBIGUITY` — Ambiguidade de requisito

O Judge revelou uma decisão de produto/negócio que não pode ser inferida com segurança.

O recovery faz apenas a pergunta humana mínima necessária e permanece bloqueado até a resposta.

## Quando aparece `JUDGE_RECOVERY`

Esse estado existe para responder:

```text
O finding realmente revela algo novo?
O que muda?
A solução ainda é válida?
A SPEC/plano precisam de patch?
O RED continua válido?
É necessária decisão humana?
```

A saída fica em:

```text
recovery/judge-recovery-<N>.md
```

## `REOPEN RED`

Se o recovery concluir que o RED precisa mudar, ele apresenta motivo, delta e impacto.

Somente a frase exata:

```text
REOPEN RED
```

autoriza a reabertura.

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

Isso evita loops onde o executor altera testes apenas para obter GREEN.

## `GREEN_STATUS=FAIL`

Significa que algum check obrigatório aplicável falhou. O fluxo não deve avançar para Judge.

A correção normal é de implementação quando o contrato/RED continuam válidos. Se a falha revelar que o
RED ou contrato precisa mudar, deve haver recovery apropriado; o executor não muda sozinho.

## `GREEN_STATUS=INVALID_GREEN`

Acontece quando, por exemplo, um teste protegido pelo RED lock foi alterado sem reabertura formal.

O sistema não deve simplesmente recalcular o lock para aceitar a mudança. É necessário tratar a causa.

## `MISSING` e `PENDING_EXTERNAL`

Durante GREEN/Judge, uma evidência que não existe ainda não vira PASS por interpretação.

- `MISSING`: evidência esperada está ausente;
- `PENDING_EXTERNAL`: a SPEC já previa validação posterior, como QA/integration/external validation.

Requisito central sem a prova necessária ao escopo atual pode bloquear o PASS global.

## `JUDGING=BLOCKED`

Use quando faltam condições essenciais para julgar, como contrato válido, GREEN PASS ou evidência
fundamental. O Judge não deve completar a lacuna por adivinhação.

## QUICK abortado

Mensagens como:

```text
QUICK_AUTOGO_ABORTED
RECOMMENDED_FLOW=STANDARD_GATED
```

significam que a tarefa deixou de ser simples o suficiente para o fluxo curto.

Causas típicas:

- open question material;
- decisão estrutural;
- banco/migração;
- mensageria;
- segurança;
- concorrência;
- cross-repo inesperado;
- contrato material;
- necessidade de reinterpretar Jira ou RED.

Isso é um mecanismo de segurança, não uma falha do QUICK.

## `RED_EXECUTION_BLOCKED`

Pode acontecer quando a execução do RED descobre fato novo ou incompatibilidade de contrato antes de
conseguir produzir um RED válido.

O agente deve parar; não deve redesenhar o RED sozinho durante a execução.

## Judge secundário discorda

Quando `JUDGE_SECONDARY` é usado e há divergência material entre os juízes, não existe votação
automática. O fluxo deve ficar bloqueado para decisão humana.

## PR não foi “aberto”

No projeto atual, `PR_DESCRIPTION` gera texto para input manual. Se o agente disser que criou PR/MR
remoto usando essa skill, isso contradiz o contrato da skill.

## DOCX de QA não foi gerado

Se o ambiente não suportar geração de DOCX, o agente deve deixar `10-qa-guide.md` pronto e registrar o
bloqueio. Não deve fingir que o arquivo existe.

## Jira não acessível

A skill de Jira trata explicitamente:

- `401`: autenticação inválida/token expirado;
- `403`: usuário sem permissão;
- `404`: issue inexistente ou inacessível;
- erro de rede: falha de conexão.

Ela não deve inventar conteúdo da issue quando a consulta falha.

## Retomada após interrupção

Ao retomar uma feature, o `STATE.md` define `CURRENT_STATE` e `NEXT_ACTION`. O objetivo é continuar de
onde parou, não refazer fases aprovadas apenas porque a sessão/chat mudou.
