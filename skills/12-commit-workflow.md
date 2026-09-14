---
name: commit-workflow
role: commit_delivery
description: >-
  Fluxo seguro e agnóstico de commit para histórias/bugs da esteira Jira,
  preservando RED lock, GREEN, julgamento independente, escopo por repositório,
  memória local e convenções do projeto. Use quando o usuário pedir commit ou
  quando uma feature aprovada chegar ao checkpoint de commit.
preferred_model_role: EXECUTOR
context_loading: lazy
reads:
  - STATE.md
  - 04-implementation-plan.md_if_exists
  - red-tests.lock
  - 07-green-evidence.md
  - 08-judgement.md
  - 09-qa-tests.md_if_exists
  - 10-qa-guide.md_if_exists
  - git_status_diff_stage
  - project_commit_conventions
  - project_build_test_config
writes:
  - delivery/commit.md
  - STATE.md
forbidden_reads:
  - chat_transcript
  - raw_discovery_logs
  - implementation_attempt_history
  - unrelated_feature_artifacts
forbidden_writes:
  - source_code
  - locked_red_tests
  - approved_specs
source_edits: none_by_default
---

# Skill — Commit Workflow da Feature

## Princípio

Commit é empacotamento e rastreabilidade, não correção de qualidade. Esta skill não altera
implementação, testes selados ou critérios para fazer um gate passar. Cada repositório Git é tratado
separadamente e nenhum comando de build, formatação ou commit é presumido sem evidência local.

## Quando usar

- pedido explícito de commit, stage, mensagem ou preparação de commit;
- checkpoint `COMMIT_REVIEW` após os gates aplicáveis;
- commits coordenados de uma mudança cross-repo.

Nunca executar `git commit` silenciosamente. O usuário escolhe `AUTOMÁTICO`, `MANUAL` ou `OUTROS`.

## Carregamento progressivo obrigatório

Carregar somente a referência necessária à etapa atual:

1. Para escolher modo, analisar o diff e criar o plano, ler
   [`references/commit-workflow/planning-and-modes.md`](references/commit-workflow/planning-and-modes.md).
2. Antes de stagear ou executar qualquer commit, ler
   [`references/commit-workflow/integrity-and-conventions.md`](references/commit-workflow/integrity-and-conventions.md).
3. Ao persistir decisão ou apresentar o resultado, ler
   [`references/commit-workflow/record-and-state.md`](references/commit-workflow/record-and-state.md).

Não carregar as três referências apenas para explicar a skill ou exibir status.

## Pré-flight

Antes de qualquer mutação Git:

1. identificar todos os repositórios e branches afetados;
2. ler `STATE.md` e apenas os artefatos de gate existentes;
3. inspecionar status, diff, staged/unstaged e untracked;
4. confirmar que `.ai/` está efetivamente ignorada, não tracked e não staged;
5. detectar convenção de commit e comandos reais do projeto;
6. verificar RED lock, GREEN, julgamento e QA aplicáveis;
7. separar arquivos relacionados, não relacionados e sensíveis;
8. em cross-repo, confirmar contrato, compatibilidade e ordem.

Se qualquer precondição necessária estiver ausente, bloquear a execução e dizer exatamente qual
evidência falta. Não usar o commit para contornar fase incompleta.

## Contrato de execução

Todo modo produz um `COMMIT PLAN` por intenção, nunca por extensão ou pasta. Código, teste,
configuração e documentação podem pertencer ao mesmo commit quando formam uma unidade revisável e
reversível. Mudanças independentes devem ser separadas.

- `AUTOMÁTICO`: a escolha explícita autoriza executar o plano congelado grupo por grupo, sem nova
  confirmação, usando somente a mensagem em inglês. Mudança material encerra a autorização.
- `MANUAL`: apresentar plano PT-BR + EN antes de mutar Git e aguardar exatamente `POSSO COMITAR`,
  `PRECISA AJUSTAR` ou `OUTROS`.
- `OUTROS`: seguir literalmente a instrução; nunca inferir autorização de commit.

Antes de cada commit:

1. stagear somente o grupo atual;
2. revisar o diff staged;
3. repetir proteção de `.ai/` e secrets;
4. confirmar correspondência exata ao plano;
5. executar com a mensagem EN;
6. registrar SHA real e validar o stage restante.

## Paradas obrigatórias

Parar e invalidar a autorização anterior se mudar arquivo, agrupamento, mensagem, ordem, quantidade
de commits ou escopo do plano. Também parar se RED lock, GREEN, julgamento, QA ou proteção de `.ai/`
deixarem de ser válidos.

Operações destrutivas, merge, rebase e force push continuam fora deste fluxo e exigem instrução
explícita própria. Nunca usar `git add .` cegamente em workspace com mudanças não relacionadas.

## Saída

Persistir fatos em `delivery/commit.md` e atualizar `STATE.md` conforme a referência de registro. Ao
final, informar por repositório: branch, grupos, intenção, arquivos, mensagens PT-BR/EN, validações,
exclusões, SHAs reais e qualquer pendência para arquivamento.

## Transição após o commit

Quando `COMMIT_STATUS=COMMITTED | EXTERNAL | SKIPPED_BY_USER`, o commit está resolvido para fins de fluxo.

Se o usuário pediu descrição de PR/MR:

```yaml
CURRENT_STATE: PR_DESCRIPTION
NEXT_ACTION: GENERATE_PR_DESCRIPTION
NEXT_MODEL_ROLE: EXECUTOR
```

Caso contrário:

```yaml
CURRENT_STATE: READY_TO_ARCHIVE
NEXT_ACTION: REQUEST_ARCHIVE
NEXT_MODEL_ROLE: ECONOMICAL
```

`COMMIT_STATUS=DEFERRED` mantém `CURRENT_STATE=COMMIT_REVIEW` e não satisfaz a pré-condição de arquivamento.
