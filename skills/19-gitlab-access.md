---
name: gitlab-access
description: >
  Acessa recursos do GitLab (projetos, merge requests, issues, branches, arquivos,
  commits, tree) com política cache-first e procedimento determinístico de fetch,
  persistência single-line e leitura normalizada, usando o fallback local de settings
  somente quando a autenticação principal não estiver disponível.
preferred_model_role: ECONOMICAL
context_loading: lazy

reads:
  - infrastructure/gitlab/gitlab-cache.py
  - infrastructure/gitlab/<repo-name>/<mr-title> - mr-<iid>.json
  - infrastructure/gitlab/gitlab-auth.local.json
  - skills/gitlab/gitlab-access-settings-local.md_if_primary_auth_unavailable

forbidden_reads:
  - .env

writes:
  - infrastructure/gitlab/<repo-name>/<mr-title> - mr-<iid>.json
  - gitlab_context_ephemeral

forbidden_writes:
  - .ai/
  - STATE.md
  - gitlab_credentials
  - auth_config_contents
  - secrets
  - .env
---

# GitLab Access

## Transporte e fronteira de acesso

O acesso é feito diretamente pelo helper Python via **HTTP REST da API GitLab** (`/api/v4`).
Não há MCP, servidor MCP, ferramenta MCP ou descoberta de projetos por MCP neste fluxo.
O token é enviado na própria requisição HTTP e somente endpoints `GET` são usados.

Uma URL de clone como:

```text
https://gitportoprd.portoseguro.brasil/plataforma_devops/reem/resi/graal-reem-resi-motor-calculo.git
```

é normalizada para o projeto `plataforma_devops/reem/resi/graal-reem-resi-motor-calculo` e
consultada diretamente em:

```text
<GITLAB_BASE_URL>/api/v4/projects/plataforma_devops%2Freem%2Fresi%2Fgraal-reem-resi-motor-calculo
```

## Objetivo

Esta skill é a porta de entrada padrão para qualquer fluxo do orquestrador que precise de
contexto do GitLab (código, MR, issue, branch, arquivo, commit ou árvore do repositório).

Ela recebe um recurso como:

```text
https://gitportoprd.portoseguro.brasil/plataforma_devops/reem/resi/graal-reem-resi-motor-calculo.git
https://gitlab.SEU-DOMINIO.com/grupo/projeto
https://gitlab.SEU-DOMINIO.com/grupo/projeto/-/merge_requests/42
grupo/projeto
grupo/projeto::merge_requests/42
```

e deve entregar `GITLAB_CONTEXT_READY=true` com contexto normalizado **efêmero**.

## Regra principal — sem improvisação

Fetch, persistência e leitura do cache GitLab são procedimentos determinísticos.

O modelo **NÃO possui liberdade** para substituir o mecanismo oficial por `curl` ad-hoc, `jq`,
PowerShell, Node, Python improvisado, `HTTPPasswordMgrWithDefaultRealm`, leitura visual do JSON
bruto ou outra estratégia que considere equivalente.

Usar obrigatoriamente:

```text
infrastructure/gitlab/gitlab-cache.py
```

## Estratégia de acesso

`19-gitlab-access.md` é a única entrada canônica do estado `GITLAB_ACCESS`.
O helper `gitlab-cache.py` é o mecanismo padrão, cache-first e determinístico. Quando a
configuração principal não puder autenticar, usar sob demanda
`skills/gitlab/gitlab-access-settings-local.md` como fallback de **leitura**.

O fallback não cria uma nova fase, não repete o intake e deve devolver o mesmo contexto
normalizado efêmero. Ele pode gravar somente o cache RAW no pacote local do MR em
`infrastructure/gitlab/<repo-name>/<mr-title> - mr-<iid>.json`; não substitui a configuração principal nem
transforma posse de credencial em autorização para alterar o GitLab.

## Fluxo canônico

```text
receber RESOURCE (URL ou chave canônica)
   ↓
normalizar URL -> <grupo>/<projeto>[::<endpoint>]
   ↓
cache local do projeto/MR existe e é válido?
   ├─ SIM -> READ canônico -> contexto normalizado
   └─ NÃO -> resolver env GitLab -> FETCH canônico -> WRITE single-line -> READ canônico
```

Cache válido sempre vence nova chamada ao GitLab.

## Normalização da URL

Extrair o caminho do projeto e, quando houver, o sufixo de recurso. Remover `/-/` do caminho web.

| URL recebida | Chave canônica |
|---|---|
| `https://gitlab.x.com/grupo/projeto` | `grupo/projeto` |
| `https://gitlab.x.com/grupo/projeto/-/merge_requests/42` | `grupo/projeto::merge_requests/42` |
| `https://gitlab.x.com/grupo/sub/projeto/-/issues/7` | `grupo/sub/projeto::issues/7` |
| `https://gitlab.x.com/grupo/projeto/-/blob/main/README.md` | `grupo/projeto::repository/files/README.md` (com `--ref main`) |
| `https://gitlab.x.com/grupo/projeto/-/tree/main/src` | `grupo/projeto::repository/tree` (com `--ref main`) |
| `https://gitlab.x.com/grupo/projeto/-/commits/main` | `grupo/projeto::repository/commits` (com `--ref main`) |

Quando a URL for `/-/blob/`, `/-/tree/` ou `/-/commits/`, extrair a ref do segmento seguinte e
passar via `--ref`.

## Comandos oficiais

### Ler cache existente

```bash
python infrastructure/gitlab/gitlab-cache.py read grupo/projeto
python infrastructure/gitlab/gitlab-cache.py read grupo/projeto::merge_requests/42 --pretty
```

Esse comando:

- interpreta o JSON com parser nativo;
- normaliza automaticamente cache JSON válido salvo com pretty-print;
- mantém o arquivo físico como **MINIFIED SINGLE-LINE JSON**;
- projeta campos úteis por tipo de payload (projeto/MR/issue);
- preserva listas (tree, branches, commits) como estão.

### Buscar somente quando houver cache miss

```bash
python infrastructure/gitlab/gitlab-cache.py fetch grupo/projeto
python infrastructure/gitlab/gitlab-cache.py fetch grupo/projeto::repository/files/README.md --ref develop

# último MR merged, ordenado do mais recente para o mais antigo
python infrastructure/gitlab/gitlab-cache.py fetch \
  "plataforma_devops/reem/resi/graal-reem-resi-motor-calculo::merge_requests" \
  --param state=merged --param order_by=updated_at --param sort=desc --param per_page=1
```

`fetch` é cache-first. Se o cache existir e for válido, não lê `.env`, não autentica e não chama
o GitLab.

### Atualização explícita

Somente quando o usuário pedir refresh/atualização:

```bash
python infrastructure/gitlab/gitlab-cache.py refresh grupo/projeto::merge_requests/42
```

### Validar/normalizar cache

```bash
python infrastructure/gitlab/gitlab-cache.py validate grupo/projeto
```

### Endpoints suportados

Sufixos válidos na chave canônica (após `<grupo>/<projeto>::`):

```text
(vazio)                              -> projeto
repository/tree                      -> árvore do repositório (--ref)
repository/files/<caminho/arquivo>   -> metadados + conteúdo (--ref)
merge_requests[/<iid>]               -> lista ou MR única
issues[/<iid>]                       -> lista ou issue única
branches[/<nome>]                    -> lista ou branch única
repository/commits[/<sha>]           -> lista ou commit único
pipelines[/<id>]                     -> pipelines
```

Qualquer outro sufixo é repassado como caminho de endpoint (extensibilidade documentada).

Campos de query adicionais podem ser passados via flags (`--ref`). Não montar `curl` manual.

## Contrato de persistência

O cache oficial é:

```text
infrastructure/gitlab/<repo-name>/<mr-title> - mr-<iid>.json
```

Nome físico:

- `plataforma_devops/reem/resi/graal-reem-resi-motor-calculo` →
  `graal-reem-resi-motor-calculo/`;
- `...::merge_requests/3` → `SGJA-160 Modularização residencial - mr-3.json`.

Todos os recursos do mesmo MR (`merge_request`, `notes`, `changes` e `versions`) ficam no mesmo
JSON legível. O campo `project_path` preserva o path completo do GitLab; o nome curto é somente
uma convenção de organização local.

Formato obrigatório:

- resposta RAW da API GitLab;
- JSON válido;
- UTF-8;
- minificado;
- exatamente uma linha física;
- sem indentação/pretty-print;
- sem resumo;
- sem reconstrução manual pela LLM;
- sem mudança de schema.

O helper usa serialização compacta para garantir esse formato.

## Contrato de leitura

Se o pacote local do projeto/MR existir:

1. não procurar credencial;
2. não ler `.env`;
3. não chamar o GitLab;
4. não abrir o RAW gigante como estratégia principal;
5. não estudar outros JSONs antigos para descobrir o formato;
6. não tentar `jq`, PowerShell, parser improvisado ou nova linguagem;
7. executar o comando `read` oficial.

A saída normalizada contém, quando disponíveis:

- projeto: `id`, `name`, `path_with_namespace`, `default_branch`, `web_url`, `namespace`,
  `visibility`, `archived`, `topics`, `last_activity_at`;
- MR: `iid`, `title`, `state`, `source_branch`, `target_branch`, `author`, `web_url`, `labels`;
- issue: `iid`, `title`, `state`, `author`, `description`, `web_url`, `labels`;
- listas (tree/branches/commits/pipelines): payload como retornado.

## Configuração de autenticação

O arquivo versionado `infrastructure/gitlab/gitlab-auth.local.json` **não contém segredos**. Ele
apenas mapeia os campos para variáveis de ambiente:

```json
{
  "gitlab": {
    "baseUrl": "${GITLAB_BASE_URL}",
    "token": "${GITLAB_API_TOKEN}"
  }
}
```

Os valores reais ficam no `.env` local da raiz do orquestrador:

```text
GITLAB_BASE_URL=https://gitlab.SEU-DOMINIO.com
GITLAB_API_TOKEN=SEU_TOKEN_AQUI
# opcional: desativar a verificação TLS quando a CA interna não valida na máquina
GITLAB_VERIFY_SSL=false
```

Regras:

- `.env` real é local e deve permanecer ignorado pelo Git;
- `.env.example` é o template versionado sem segredos;
- o agente não deve abrir, imprimir, resumir ou copiar o conteúdo de `.env`;
- `gitlab-cache.py` carrega `.env` mecanicamente apenas em cache miss/refresh;
- variáveis já definidas no processo têm precedência sobre valores do `.env`;
- não procurar credenciais em arquivos antigos ou projetos arbitrários;
- usar `skills/gitlab/gitlab-access-settings-local.md` somente como fallback controlado desta
  skill, quando a autenticação principal não estiver disponível; a credencial permanece apenas
  em memória.

Se uma variável obrigatória estiver ausente, parar e informar somente o nome da variável/caminho
esperado; nunca pedir o token no chat.

### Verificação TLS em rede corporativa

O helper `gitlab-cache.py` honra a variável de ambiente **`GITLAB_VERIFY_SSL`** (default
`true`). Com `GITLAB_VERIFY_SSL=false` (`0`/`no` também aceitos), ele cria o contexto SSL com
`check_hostname=False` e `verify_mode=CERT_NONE`, permitindo conexão quando a CA interna da
empresa não valida na máquina.

Sintoma que indica essa necessidade:

```text
NETWORK_ERROR: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed:
  Basic Constraints of CA cert not marked critical
```

Nesse caso, reexecutar o mesmo comando com a variável definida no processo, sem alterar código
nem trocar de estratégia de autenticação:

```bash
GITLAB_VERIFY_SSL=false python infrastructure/gitlab/gitlab-cache.py fetch "<recurso>"
```

Uso restrito: é paliativo para CA interna, não autoriza desativar verificação em rede pública, e
não deve ser persistido em `.env` versionado nem em documento do projeto. Se a falha persistir,
classificar como erro de rede e parar (ver seção Falhas).

## Requisição canônica — formato validado em ambiente real

```text
METHOD: GET
URL: <baseUrl>/api/v4/projects/<url-encoded-path-with-namespace>[/<endpoint>][?ref=<ref>]
HEADERS:
  Accept: application/json
  PRIVATE-TOKEN: <PAT>
  # somente este header para PAT
```

Equivalente em curl, usando somente variáveis de ambiente:

```bash
curl --request GET \
  --url "${GITLAB_BASE_URL}/api/v4/projects/$(python -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=""))' "grupo/projeto")" \
  --header "Accept: application/json" \
  --header "PRIVATE-TOKEN: ${GITLAB_API_TOKEN}"
```

O helper `gitlab-cache.py` implementa a mesma semântica: resolve `${GITLAB_*}` e envia
`PRIVATE-TOKEN` já na **primeira requisição**. Não envia simultaneamente `Authorization: Bearer`
para evitar conflito entre esquemas de autenticação em proxies corporativos.

### Diferença deliberada em relação ao Jira

O Jira usa Basic Auth (`base64(email:apiToken)`). O GitLab usa **Personal/Project Access Token**
enviado em `PRIVATE-TOKEN` (aceita também `Bearer`). Por isso `gitlab-auth.local.json` **não**
possui campo `email` — apenas `baseUrl` e `token`.

### Regra anti-regressão de autenticação

É proibido substituir a requisição acima por mecanismo que aguarde challenge HTTP antes de enviar
o token.

Não usar:

```text
urllib.request.HTTPBasicAuthHandler
HTTPPasswordMgrWithDefaultRealm
cliente equivalente que espere 401/challenge antes de enviar o token
```

Se o mecanismo canônico falhar, classificar o status e parar. Não tentar outra estratégia de
autenticação.

Quando a falha for de configuração/autenticação principal e o fallback controlado estiver
disponível, executar o procedimento da skill de fallback uma única vez. Se ele também falhar,
reportar o status sem expor credenciais e sem tentar outras fontes.

## Segurança

Obrigatório:

- nunca imprimir `GITLAB_API_TOKEN`;
- nunca imprimir os headers `PRIVATE-TOKEN` / `Authorization`;
- nunca persistir credencial em cache GitLab;
- nunca copiar credencial para `.ai/`, `STATE.md`, logs, QA, commit ou PR;
- nunca abrir `.env` no contexto da LLM;
- nunca pedir que o usuário cole token no chat;
- se token aparecer em chat/print/log, considerar exposto e recomendar revogação.

## Regra de escrita

Esta skill, o helper canônico e o fallback executam somente leitura (`GET`) e cache local. Uma
credencial com permissão de escrita (`api`) não concede autorização ao agente. Criar MR, comentar
em MR/issue, criar branch, aprovar, mergear ou alterar qualquer recurso exige solicitação
explícita do usuário que identifique a ação, o recurso e o conteúdo/campos pretendidos; sem esses
três elementos, não fazer chamada de mutação.

`MR` nesta skill é **leitura de contexto**. Criar MR permanece fora de escopo e sujeito à regra
global de PR/MR somente por solicitação explícita.

## Falhas

Classificar e parar; não trocar de runtime/estratégia por tentativa e erro.

- `AUTH_ENV_MISSING`: variável GitLab ausente no ambiente/`.env`;
- `AUTH_NOT_CONFIGURED`: `gitlab-auth.local.json` ausente;
- `AUTH_CONFIG_INVALID`: campo sem referência `${VAR}`;
- `401`: token inválido/expirado;
- `403`: usuário autenticado sem permissão;
- `404`: projeto/recurso inexistente ou não visível;
- `INVALID_RESOURCE`: chave canônica malformada;
- erro de rede: reportar conexão;
  - se a mensagem contiver `CERTIFICATE_VERIFY_FAILED` / `Basic Constraints of CA cert not marked
    critical`, reexecutar uma única vez com `GITLAB_VERIFY_SSL=false` (ver “Verificação TLS em
    rede corporativa”); se persistir, reportar como erro de rede;
- cache inválido: `fetch` pode refazer a consulta; `read` deve reportar o problema.

## Uso pelo orquestrador

O GitLab Access **não** substitui o Jira como porta de entrada do fluxo. Ele é consultado:

- em `DISCOVERY` para leitura de código, árvore, arquivos e histórico;
- em `INTAKE` quando o card referencia um MR/projeto;
- em `SOLUTION_DESIGN` para validar arquitetura existente;
- em `COMMIT_REVIEW`/`PR_DESCRIPTION` para conferir estado remoto antes de propor ação.

Sempre `GET` + cache local. Nunca mutação automática.

## Anexos e imagens

Metadados de anexos podem existir no payload. Não inventar conteúdo visual. Se imagem/diagrama
for material ao entendimento, solicitar o arquivo ao usuário, salvo quando o runtime possuir
capacidade autorizada para obtê-lo.