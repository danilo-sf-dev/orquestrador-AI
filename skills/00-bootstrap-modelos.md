---
name: bootstrap-modelos
role: orchestrator
preferred_model_role: HEAD_STRONG
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
Ser o bootstrap mínimo de `/orquestrador`: resolver feature, confirmar os bindings de modelo da **sessão** e decidir entre `RESUME` e `NEW` sem carregar a esteira inteira.

## Preset sugerido da sessão

- `HEAD_STRONG`: DeepSeek V4 Pro
- `EXECUTOR`: GPT-5.6 Luna Pro
- `ECONOMICAL`: DeepSeek V4 Flash 0731
- `MULTIMODAL`: Gemini 3.7 Flash
- `JUDGE_PRIMARY`: DeepSeek V4 Pro em contexto novo/read-only
- `JUDGE_SECONDARY`: Gemini 3.7 Flash ou outro confirmado

Esses nomes são defaults do bootstrap, não configuração persistente do projeto.

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
- orçamento default: `US$40/mês`, alvo `US$8/feature`, warning `US$10`.

### Regra de persistência

Não criar `.ai/config/model-profile.md` nem arquivo equivalente.

Em `RESUME`, o `STATE.md` existente pode registrar que os papéis foram confirmados **nesta sessão** e o modo de roteamento.

Em `NEW`, **não criar `STATE.md` ainda**. Manter bindings, routing mode e orçamento como estado efêmero do bootstrap até o usuário informar o Jira. O `STATE.md` só nasce na skill `01-intake-jira.md`, dentro de `.ai/features/<JIRA-ID>/`. Se o runtime expuser o modelo efetivamente usado em uma fase, ele pode aparecer nas métricas históricas da fase; isso não vira configuração.

## Passo 3A — RESUME

Se a feature já existir:

1. ler apenas seu `STATE.md`;
2. validar `LIFECYCLE`, `CURRENT_STATE` e `NEXT_ACTION`;
3. não refazer fases aprovadas;
4. carregar a skill do `CURRENT_STATE`;
5. aplicar o contrato `reads/forbidden_reads` da skill;
6. continuar de `NEXT_ACTION`.

## Passo 3B — NEW

Se não houver feature selecionada, na mesma mensagem solicitar:

```text
JIRA-ID:
Breve descrição:
```

Até receber o Jira:

- não criar `.ai/features/<JIRA-ID>/`;
- não persistir `STATE.md`;
- não gravar bindings de modelo no projeto;
- manter o resultado do bootstrap apenas na sessão atual.

Não fazer entrevista de negócio no bootstrap.

## Saída mínima

```text
MODEL_ROLES_CONFIRMED_THIS_SESSION=true
ROUTING_MODE=automatic|manual
RESUME=true|false
SELECTED_JIRA=<id|none>
NEXT_ACTION=<ação>
```
