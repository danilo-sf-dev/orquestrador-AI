# 06 — Gates e comandos do usuário

> HUMAN_ONLY. Este arquivo é para consulta do usuário e não deve ser carregado por agentes.

Um **gate** é uma parada explícita que exige autorização/decisão antes de o fluxo avançar.

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
| `AUTOMÁTICO` | `COMMIT_REVIEW` | executar o plano de commits congelado |
| `MANUAL` | `COMMIT_REVIEW` | revisar plano antes de autorizar commit |
| `OUTROS` | `COMMIT_REVIEW` | seguir instrução específica sem inferir commit |
| `ARQUIVAR` | `READY_TO_ARCHIVE` | produzir memória final da feature |

## `APROVAR SOLUÇÃO`
Aceita a solução técnica apresentada. Ainda haverá SPEC/plano, RED e implementação.

## `APROVAR SPEC/PLANO`
Aprova a SPEC canônica + plano de implementação. Depois disso, a SPEC vira contrato para RED,
implementação, GREEN e Judge. O executor não pode mudá-la silenciosamente.

## `APROVAR RED`
Autoriza sair de `RED_REVIEW` e entrar em `RED_EXECUTION`. A aprovação não significa que RED já foi
comprovado; a prova ocorre na execução.

## `GO`
No COMUM, autoriza implementação depois de RED aprovado, executado, falhando pelo motivo esperado e selado.

## `AUTO-GO`
Autoriza o QUICK a executar RED -> lock -> implementação -> GREEN -> rework técnico até Judge/bloqueio real.

## `REOPEN RED`
Gate especial: só após `JUDGE_RECOVERY` demonstrar necessidade real. A resposta deve ser exatamente
`REOPEN RED`; isso invalida o lock e exige novo RED, GREEN e Judge.

## `APROVAR QA`
Aceita o pacote de QA e permite seguir para commit.

## Commit — `AUTOMÁTICO | MANUAL | OUTROS`
`AUTOMÁTICO` executa plano congelado; `MANUAL` exige revisão e `POSSO COMITAR`; `OUTROS` não autoriza
commit por inferência. Mensagens enviadas ao repositório permanecem em inglês.

## Pedido de PR/MR
“abre o PR” significa gerar título + descrição para input manual. A skill não acessa provider remoto,
não faz push nem cria PR/MR.

## `ARQUIVAR`
Autoriza consolidar `11-archive.md` e atualizar o índice de features, após demais fases resolvidas.

## Nota de legado
Em features antigas, o gate pode aparecer como `APROVAR PRD/PLANO` no estado `PRD_PLAN_REVIEW`.
Interprete-o como predecessor histórico do atual `APROVAR SPEC/PLANO` / `SPEC_PLAN_REVIEW`.
