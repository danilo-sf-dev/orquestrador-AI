# 06 — Gates e comandos do usuário

> HUMAN_ONLY. Este arquivo é para consulta do usuário e não deve ser carregado por agentes.

Um **gate** é uma parada explícita que exige autorização/decisão antes de o fluxo avançar. Nem toda
etapa possui gate.

## Referência rápida

| Comando/gate | Onde aparece | O que autoriza |
|---|---|---|
| `APROVAR SOLUÇÃO` | `SOLUTION_REVIEW` | aceitar a solução técnica consolidada |
| `APROVAR SPEC/PLANO` | `SPEC_PLAN_REVIEW` | congelar SPEC + plano para RED |
| `APROVAR RED` | `RED_REVIEW` | permitir materializar/executar o RED planejado |
| `GO` | `WAITING_GO` | iniciar implementação no fluxo COMUM |
| `AUTO-GO` | `QUICK_AUTOGO` | executar RED → lock → implementação → GREEN automaticamente até Judge/bloqueio |
| `REOPEN RED` | `JUDGE_RECOVERY` | invalidar lock atual e alterar RED pelo delta aprovado |
| `APROVAR QA` | `QA_REVIEW` | aceitar o pacote de QA |
| `AUTOMÁTICO` | `COMMIT_REVIEW` | executar o plano de commits congelado sem nova confirmação por grupo |
| `MANUAL` | `COMMIT_REVIEW` | revisar plano antes de autorizar commit |
| `OUTROS` | `COMMIT_REVIEW` | seguir instrução específica do usuário sem inferir commit |
| `ARQUIVAR` | `READY_TO_ARCHIVE` | produzir memória final da feature |

## `APROVAR SOLUÇÃO`

Aparece depois que requisitos e design foram analisados.

Ao aprovar, você aceita a solução técnica apresentada para a feature. A aprovação não significa que o
código foi escrito; ainda haverá SPEC/plano, RED e implementação.

Antes do gate, a solução deve ter zero pergunta bloqueante e não deve incluir melhoria opcional como
escopo sem aprovação.

## `APROVAR SPEC/PLANO`

Aprova:

```text
SPEC canônica + plano de implementação
```

Depois disso a SPEC vira contrato para RED, implementação, GREEN e Judge. O executor não pode mudá-la
silenciosamente para acomodar código.

## `APROVAR RED`

Autoriza sair do planejamento do RED (`RED_REVIEW`) e entrar na materialização/execução
(`RED_EXECUTION`).

Antes da aprovação, os testes planejados devem estar ligados aos requisitos/ACs/riscos e cada AC deve
ter forma de verificação prevista.

A aprovação não significa que RED já foi comprovado; a prova só ocorre em `RED_EXECUTION`.

## `GO`

É usado no fluxo COMUM depois que:

- RED foi aprovado;
- os testes foram materializados;
- falharam pelo motivo esperado;
- `red-tests.lock` foi criado.

`GO` autoriza iniciar a implementação. Não autoriza alterar os testes protegidos.

## `AUTO-GO`

É a autorização única inicial do fluxo QUICK.

Antes dela, o agente deve apresentar o Quick Contract com entendimento, requisitos/assumptions
relevantes, escopo provável, abordagem, RED planejado e riscos/gatilhos de escalonamento.

Depois de `AUTO-GO`, o fluxo pode executar:

```text
RED -> comprovação RED -> lock -> implementação -> GREEN -> rework técnico de implementação
```

sem novas perguntas até o handoff para Judge, salvo bloqueio real ou perda de elegibilidade do QUICK.

## `REOPEN RED`

Este é um gate especial e propositalmente rigoroso.

O Judge **não** solicita reabertura diretamente. Primeiro `JUDGE_RECOVERY` precisa demonstrar que o
contrato RED realmente está incorreto e explicar o impacto.

Para autorizar, a resposta deve ser exatamente:

```text
REOPEN RED
```

`sim`, `ok` ou `aprovado` não são autorização válida.

Ao reabrir:

- o lock atual é invalidado;
- somente o delta documentado pelo recovery pode ser aplicado;
- há nova execução RED;
- novo lock;
- novo GREEN;
- novo Judge fresh.

## `APROVAR QA`

Aparece quando o pacote de QA foi produzido. O material pode incluir cenários, collection
Postman/Insomnia, guia Markdown e DOCX quando o ambiente suportar.

A aprovação permite seguir para commit.

## Commit — `AUTOMÁTICO | MANUAL | OUTROS`

### `AUTOMÁTICO`

Autoriza executar o plano de commits já congelado grupo por grupo. Os commits continuam faseados por
intenção e a mensagem enviada ao repositório é em inglês.

Se arquivos, agrupamento, mensagem, ordem, quantidade de commits ou escopo mudarem materialmente, a
autorização deixa de valer e o fluxo deve parar.

### `MANUAL`

O agente apresenta o plano PT-BR + EN antes de mutar Git. Depois aguarda uma das respostas previstas:

```text
POSSO COMITAR
PRECISA AJUSTAR
OUTROS
```

### `OUTROS`

Serve quando você quer instruir algo diferente, inclusive não commitar naquele momento. Não autoriza
commit por inferência.

## Pedido de PR/MR

No contrato atual, frases como:

```text
abre o PR
pode abrir o PR
cria o PR
faz o merge request
```

significam somente:

```text
GERAR TÍTULO + DESCRIÇÃO FINAL PARA INPUT MANUAL
```

A skill de PR não acessa GitLab/GitHub/Azure/Bitbucket, não faz push e não cria PR/MR remoto.

## `ARQUIVAR`

É a autorização para consolidar a memória final em `11-archive.md` e atualizar o índice de features.

O archive só deve ocorrer quando Judge, QA, commit e PR estiverem resolvidos conforme as políticas do
fluxo.

## Troca de modelo não é aprovação funcional

Em `ROUTING_MODE=manual`, o sistema também pode parar para você trocar de modelo. Essa parada existe
para garantir que a próxima etapa use o papel correto; ela não substitui gates como `APROVAR RED` ou
`GO`.

## Nota de legado

Em features antigas, o gate pode aparecer como `APROVAR PRD/PLANO` no estado `PRD_PLAN_REVIEW`.
Interprete-o como predecessor histórico do atual `APROVAR SPEC/PLANO` em `SPEC_PLAN_REVIEW`.
