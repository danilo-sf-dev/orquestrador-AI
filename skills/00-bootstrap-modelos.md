---
name: bootstrap-modelos
role: orchestrator
preferred_model_role: ECONOMICAL
writes: [existing_STATE.md_if_resume]
context_loading: lazy
reads:
  - feature_state_metadata_only
  - runtime_model_bindings
  - user_request
forbidden_reads:
  - all_feature_artifacts
  - chat_transcript
forbidden_writes:
  - global_model_profile
---

# Skill — Bootstrap + Resume

## Objetivo
Ser o bootstrap mínimo do fluxo orquestrador: resolver feature, confirmar os bindings de modelo da **sessão**, definir `ROUTING_MODE` e decidir entre `RESUME` e `NEW` sem carregar a esteira inteira. Em roteamento manual, também estabelece o gate obrigatório de troca de papel antes de cada fase.

## Preset sugerido da sessão

- `HEAD_STRONG`: DeepSeek V4 Pro 0813
- `EXECUTOR`: GPT-5.6 Luna Pro
- `ECONOMICAL`: DeepSeek V4 Flash 0731
- `MULTIMODAL`: Gemini 3.7 Flash
- `JUDGE_PRIMARY`: DeepSeek V4 Pro 0813 em modo read-only/evidence-isolated
- `JUDGE_SECONDARY`: Gemini 3.7 Flash ou outro confirmado

Esses nomes são defaults do bootstrap, não configuração persistente do projeto.

## Política de contexto da sessão

O modo padrão do Orquestrador é **um chat/sessão por Jira/feature**, com troca de modelo dentro da mesma conversa quando o papel muda.

```text
MODEL_SWITCH     = trocar modelo/papel e continuar no mesmo chat
COMPACT_CONTEXT  = continuar na mesma sessão, resumindo o histórico quando suportado
FRESH_CONTEXT    = abrir nova conversa/contexto de forma explícita
```

Regras:

- `MODEL_SWITCH` é o padrão;
- mudança de papel/modelo **não** implica novo chat;
- `COMPACT_CONTEXT` é a opção intermediária quando o chat ficou longo/poluído mas ainda vale preservar decisões e continuidade; no VS Code usar `/compact` quando disponível;
- `/clear` no VS Code inicia uma nova sessão e, portanto, equivale conceitualmente a `FRESH_CONTEXT`, não a compactação;
- `FRESH_CONTEXT` é excepcional e só deve ser usado quando houver motivo explícito, como isolamento forte, loop grande, auditoria independente ou escolha do usuário;
- o Judge continua read-only e evidence-isolated mesmo no mesmo chat: histórico anterior não vale como evidência e conclusões do executor devem ser ignoradas;
- quando `FRESH_CONTEXT` for escolhido, usar `templates/handoff-packet.md` com o pacote mínimo permitido.

## Passo 1 — Resolver feature antes de pedir Jira

Pesquisar somente metadados mínimos dos `STATE.md` existentes.

Prioridade:

1. Jira informado explicitamente;
2. referência inequívoca na branch/repo atual;
3. features com `LIFECYCLE=ACTIVE|PAUSED`;
4. se houver uma única candidata, retomar;
5. se houver várias, pedir somente qual Jira deve ser retomado;
6. se não houver candidata, tratar como nova feature.

Não carregar artefatos completos apenas para descobrir qual feature está ativa.

## Passo 2 — Confirmar bindings da sessão

Mostrar o preset/runtime atual e perguntar se deve ser usado ou alterado.

Confirmar também:

- `ROUTING_MODE=automatic|manual`;
- contexto padrão da sessão: `MODEL_SWITCH` no mesmo chat;
- orçamento default: `US$40/mês`, alvo `US$8/feature`, warning `US$10`.

### Regra de sessão

`MODEL_ROLES_CONFIRMED_THIS_SESSION` nunca é herdado como verdade de uma sessão anterior.

Em `RESUME`, ao selecionar a feature:

```yaml
MODEL_ROLES_CONFIRMED_THIS_SESSION: false
```

Somente depois que os bindings atuais forem confirmados nesta nova sessão marcar:

```yaml
MODEL_ROLES_CONFIRMED_THIS_SESSION: true
```

### Regra de persistência

Não criar `.ai/config/model-profile.md` nem arquivo equivalente.

Em `RESUME`, o `STATE.md` existente pode registrar os papéis confirmados **nesta sessão** e o modo de roteamento.

Em `NEW`, **não criar `STATE.md` ainda**. Manter bindings, routing mode e orçamento como estado efêmero do bootstrap até o usuário informar o Jira. O `STATE.md` só nasce na skill `01-intake-jira.md`, dentro de `.ai/features/<JIRA-ID>/`. Se o runtime expuser o modelo efetivamente usado em uma fase, ele pode aparecer nas métricas históricas da fase; isso não vira configuração.

## Passo 3A — RESUME

Se a feature já existir:

1. ler apenas seu `STATE.md`;
2. resetar `MODEL_ROLES_CONFIRMED_THIS_SESSION=false` antes da confirmação desta sessão;
3. validar `LIFECYCLE`, `CURRENT_STATE` e `NEXT_ACTION`;
4. não refazer fases aprovadas;
5. carregar a skill do `CURRENT_STATE`;
6. aplicar o contrato `reads/forbidden_reads` da skill;
7. continuar de `NEXT_ACTION`.

## Passo 3B — NEW

Se não houver feature selecionada:

1. perguntar o `FLOW_MODE`: `QUICK` ou `COMUM`;
2. manter a escolha apenas em memória efêmera;
3. solicitar URL ou issue key do Jira;
4. rotear para `skills/15-jira-access.md`;
5. somente depois de `JIRA_CONTEXT_READY=true`, permitir que `01-intake-jira.md` crie a memória da feature.

Até o Jira ser resolvido:

- não criar `.ai/features/<JIRA-ID>/`;
- não persistir `STATE.md`;
- não gravar bindings de modelo no projeto;
- não iniciar Discovery/Quick Contract;
- manter bootstrap e `FLOW_MODE` apenas na sessão atual.

Não fazer entrevista de negócio no bootstrap.

## Saída mínima

```text
MODEL_ROLES_CONFIRMED_THIS_SESSION=true
ROUTING_MODE=automatic|manual
RESUME=true|false
SELECTED_JIRA=<id|none>
NEXT_ACTION=<ação>
```

## Regra obrigatória de troca manual de modelo

Se `ROUTING_MODE=manual`, nenhuma fase pode começar apenas porque `NEXT_ACTION` aponta para ela.

Antes de carregar a próxima skill:

```text
required_role = papel canônico da próxima fase
```

Se `required_role != CURRENT_MODEL_ROLE`:

```text
MODEL_HANDOFF_REQUIRED=true
NEXT_MODEL_ROLE=<required_role>
```

Exibir o `PHASE BANNER` definido no `orquestrador.md`, solicitar a troca manual e **parar**.

Por padrão, essa troca é um `MODEL_SWITCH`: o usuário seleciona o novo modelo **no mesmo chat**. Não pedir nova conversa apenas porque o papel mudou.

Somente após confirmação explícita do usuário:

```text
CURRENT_MODEL_ROLE=<required_role>
NEXT_MODEL_ROLE=
MODEL_HANDOFF_REQUIRED=false
```

Aí sim carregar a skill.

Nunca continuar em `ECONOMICAL` para uma fase `HEAD_STRONG` ou `EXECUTOR`; nunca continuar em `EXECUTOR` para `JUDGE_PRIMARY`.

Se o contexto estiver grande/poluído mas ainda útil, preferir `COMPACT_CONTEXT` (`/compact` quando suportado) antes de `FRESH_CONTEXT`.
Se houver necessidade explícita de isolamento, indicar `FRESH_CONTEXT` separadamente e gerar o handoff mínimo. `MODEL_HANDOFF_REQUIRED` sozinho nunca significa abrir novo chat.

## Contrato de nomes canônicos

Ao mostrar progresso, usar sempre `CURRENT_STATE`/estados canônicos. Não agrupar etapas sob nomes inventados como `RED + aprovação/lock` ou `Judge + QA + Commit`.
