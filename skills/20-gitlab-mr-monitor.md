---
name: gitlab-mr-monitor
description: >
  Consulta o status e os comentarios disponiveis de um Merge Request GitLab,
  usando somente endpoints REST GET e sem executar mutacoes remotas.
preferred_model_role: ECONOMICAL
context_loading: lazy

reads:
  - infrastructure/gitlab/gitlab-cache.py
  - infrastructure/gitlab/<repo-name>/<mr-title> - mr-<iid>.json
  - infrastructure/gitlab/gitlab-auth.local.json
  - .ai/features/<JIRA-ID>/delivery/pull-request-tracking.md_if_exists
  - .ai/features/<JIRA-ID>/delivery/pull-request.md_if_exists
  - skills/gitlab/gitlab-access-settings-local.md_if_primary_auth_unavailable

writes:
  - infrastructure/gitlab/<repo-name>/<mr-title> - mr-<iid>.json
  - gitlab_mr_status_ephemeral
  - pull_request_tracking_local_only_if_user_explicitly_requests_recording

forbidden_reads:
  - .env
  - documentacao-usuario/**

forbidden_writes:
  - remote_git_provider
  - source_code
  - tests
  - .env
  - credentials
  - tokens
---

# GitLab MR Monitor

## Objetivo

Verificar um Merge Request existente e informar somente o que estiver disponivel na API REST:

- status atual do MR;
- titulo, autor, branches e datas quando retornados;
- quem mergeou e o merge commit quando retornados;
- comentarios e eventos disponiveis em `notes`;
- respostas que a API apresentar como notas relacionadas ou sequenciais;
- data da ultima consulta;
- diferenca desde a ultima consulta quando houver historico local.

Esta skill nao cria, atualiza, comenta, aprova, resolve ou mergeia um MR. Tambem nao altera
codigo e nao inicia analise de implementacao automaticamente.

## Entrada

Aceitar uma destas formas:

```text
Verifique o MR https://gitportoprd.portoseguro.brasil/plataforma_devops/reem/resi/graal-reem-resi-motor-calculo/-/merge_requests/3
Verifique o MR do arquivo .ai/features/SGJA-160/delivery/pull-request-tracking.md
Verifique o MR 3 do projeto plataforma_devops/reem/resi/graal-reem-resi-motor-calculo
```

Tambem aceitar os atalhos usados no acompanhamento de historias Jira:

```text
Atualize o status do merge SGJA-160
Atualize o status de C:\\projetos\\graal-reem-resi-motor-calculo\\.ai\\features\\SGJA-160\\delivery
```

Nesses atalhos, `atualize` significa atualizar a consulta e o relatorio local com dados obtidos
por `GET`. Nao significa alterar o status, aprovar, comentar ou fazer merge no GitLab.

Se o usuario fornecer somente o nome local do repositorio, pedir a URL do projeto e o IID do MR.
Nao procurar o projeto por busca global.

## Arquivos de apoio

Depois de criar o MR manualmente, o usuario pode registrar a referencia em:

```text
.ai/features/<JIRA-ID>/delivery/pull-request-tracking.md
```

O arquivo deve conter, no minimo:

```text
PROJECT_URL: https://gitportoprd.portoseguro.brasil/plataforma_devops/reem/resi/graal-reem-resi-motor-calculo
PROJECT_PATH: plataforma_devops/reem/resi/graal-reem-resi-motor-calculo
MR_IID: 3
MR_URL: https://gitportoprd.portoseguro.brasil/.../merge_requests/3
LAST_CHECKED_AT:
LAST_NOTE_ID:
```

`delivery/pull-request.md` e contexto local da descricao; nao e prova de que o MR foi publicado.
A URL/IID do tracking ou a informacao explicita do usuario e a fonte para acessar o MR.

## Procedimento canonico

Usar obrigatoriamente `infrastructure/gitlab/gitlab-cache.py`.

1. Resolver `PROJECT_PATH` e `MR_IID` pela entrada do usuario ou pelo tracking local. Para um
  Jira ID, procurar somente a feature correspondente e ler
  `.ai/features/<JIRA-ID>/delivery/pull-request-tracking.md`.
2. Normalizar o recurso para:

```text
<PROJECT_PATH>::merge_requests/<MR_IID>
```

3. Atualizar somente o cache do MR:

```bash
python infrastructure/gitlab/gitlab-cache.py refresh \
  "<PROJECT_PATH>::merge_requests/<MR_IID>" --raw --pretty
```

4. Atualizar somente as notas do MR:

```bash
python infrastructure/gitlab/gitlab-cache.py refresh \
  "<PROJECT_PATH>::merge_requests/<MR_IID>/notes" \
  --param sort=desc --param order_by=updated_at --param per_page=100 --raw --pretty
```

5. Ler os dois caches com `read` se for necessario apresentar a resposta novamente.
6. Comparar `id` e `created_at` das notas com `LAST_NOTE_ID` quando o tracking existir.
7. Apresentar status e comentarios novos; se nao houver novidades, dizer isso claramente.

Todos os dados consultados do mesmo MR podem permanecer reunidos em um unico JSON legivel,
nomeado como `<titulo> - mr-<iid>.json` dentro da pasta curta `<repo-name>/`.

### Verificacao TLS em rede corporativa

Se o `refresh` falhar com `NETWORK_ERROR` contendo `CERTIFICATE_VERIFY_FAILED` (tipicamente
`Basic Constraints of CA cert not marked critical`, CA interna da empresa que nao valida na
maquina), reexecutar o mesmo comando uma unica vez prefixando `GITLAB_VERIFY_SSL=false`:

```bash
GITLAB_VERIFY_SSL=false python infrastructure/gitlab/gitlab-cache.py refresh \
  "<PROJECT_PATH>::merge_requests/<MR_IID>" --raw --pretty
```

O helper `gitlab-cache.py` ja suporta essa variavel (default `true`); nao alterar o script,
nao trocar de runtime e nao desativar verificacao como pratica padrao. Se a falha persistir,
reportar como erro de rede e parar.

## Endpoints permitidos

Somente estes endpoints de leitura fazem parte desta skill:

```text
GET /api/v4/projects/<project>/merge_requests/<iid>
GET /api/v4/projects/<project>/merge_requests/<iid>/notes
```

Nao chamar nesta skill:

```text
/discussions
/approvals
/approval_state
```

Esses endpoints nao fazem parte do contrato desta instalacao e ja retornaram `404`. A ausencia
deles nao deve ser tratada como erro operacional nem provocar tentativas alternativas.

## Interpretacao

Classificar a informacao sem inventar vinculos:

- `FACT`: campo retornado pela API, como `state`, `author`, `merged_by` ou `merge_commit_sha`;
- `FACT_NOTE`: nota retornada pela API, com autor, data, texto e `system`;
- `UNKNOWN`: informacao nao retornada, como aprovador formal quando nao houver campo/evento;
- `NOT_CHECKED`: algo fora do escopo desta skill, como analise do codigo ou pipeline.

`notes` e uma lista plana nesta instalacao. Nao afirmar que uma nota e resposta de outra nem
associar comentario a arquivo/classe/linha sem metadado explicito retornado pela API.

Eventos `system=true` devem ser separados de comentarios humanos. Exemplos:

- `merged` -> evento de merge;
- `mentioned in commit ...` -> referencia de commit;
- `added commits` -> atualizacao de commits;
- `changed the description` -> alteracao de descricao.

## Saida

Entregar uma resposta curta com:

```text
MR: !<iid> - <title>
STATUS: <state>
AUTOR: <nome/username ou UNKNOWN>
MERGEADO POR: <nome/username ou UNKNOWN>
MERGE COMMIT: <sha ou UNKNOWN>
ULTIMA ATUALIZACAO: <data ou UNKNOWN>

COMENTARIOS NOVOS:
- <data> - <autor>: <texto>

EVENTOS:
- <data> - <evento>: <autor>

LIMITES:
- aprovacao formal: FACT ou UNKNOWN;
- arquivo/classe/linha: NOT_CHECKED nesta skill;
- analise de codigo: NOT_CHECKED nesta skill.
```

Se o usuario pedir apenas verificacao, nao escrever em `pull-request-tracking.md`. Se pedir
explicitamente para registrar o resultado, atualizar somente o historico local autorizado e
preservar o conteudo anterior.

## Regra de autorizacao

Toda chamada remota desta skill e somente `GET`. Token com escopo `api` nao autoriza mutacao.
Nenhuma funcao de escrita remota pode ser adicionada por interpretacao do pedido de consulta.

As frases abaixo continuam sendo somente leitura:

```text
verifique o MR
veja se foi aprovado
veja se tem comentarios
consulte o status
```

Analise de codigo, resposta a comentario ou implementacao exigem pedido separado e explicito.
