---
name: jira-access
description: >
  Acessa issues do Jira com política cache-first e procedimento determinístico
  de fetch, persistência single-line e leitura normalizada, usando o fallback
  local de settings somente quando a autenticação principal não estiver disponível.
preferred_model_role: ECONOMICAL
context_loading: lazy

reads:
  - infrastructure/jira/jira-cache.py
  - infrastructure/jira/<EPIC>/<SPRINT>/<ITEM>/<ISSUE-KEY>[TAG].json
  - infrastructure/jira/jira-auth.local.json
  - skills/jira/jira-access-settings-local.md_if_primary_auth_unavailable

forbidden_reads:
  - .env

writes:
  - infrastructure/jira/<EPIC>/<SPRINT>/<ITEM>/<ISSUE-KEY>[TAG].json
  - jira_context_ephemeral
  - jira_issue_fields_only_on_explicit_user_request

forbidden_writes:
  - .ai/
  - STATE.md
  - 00-jira.md
  - jira_credentials
  - auth_config_contents
  - secrets
  - .env
---

# Jira Access

## Transporte e fronteira de acesso

O acesso é feito diretamente pelo helper Python via **HTTP REST da API Jira** (`/rest/api/3`).
Não há MCP, servidor MCP, ferramenta MCP ou outro transporte intermediário neste fluxo.
O helper envia `Authorization: Basic ...` na própria requisição HTTP e usa `GET` para leitura de
issues e cache local. Mutação (`PUT`/`POST`) só é permitida sob **solicitação explícita do usuário**
(ver “Regra de escrita”), nunca de forma autônoma.

## Objetivo

Esta skill é a porta de entrada padrão para qualquer fluxo do orquestrador que comece por Jira.

Ela recebe uma URL como:

```text
https://SEU-DOMINIO.atlassian.net/browse/SGJA-123
```

ou diretamente:

```text
SGJA-123
```

e deve entregar `JIRA_CONTEXT_READY=true` com contexto normalizado **efêmero**.

## Regra principal — sem improvisação

Fetch, persistência e leitura do cache Jira são procedimentos determinísticos.

O modelo **NÃO possui liberdade** para substituir o mecanismo oficial por `jq`, PowerShell, Node,
Python ad-hoc, `HTTPBasicAuthHandler`, leitura visual do JSON bruto ou outra estratégia que considere
equivalente.

Usar obrigatoriamente:

```text
infrastructure/jira/jira-cache.py
```

## Estratégia de acesso

`15-jira-access.md` é a única entrada canônica do estado `JIRA_ACCESS`.
O helper `jira-cache.py` continua sendo o mecanismo padrão, cache-first e
determinístico. Quando a configuração principal não puder autenticar, usar sob
demanda `skills/jira/jira-access-settings-local.md` como fallback de **leitura**.

O fallback não cria uma nova fase, não repete o intake e deve devolver o mesmo
contexto normalizado efêmero. Ele pode gravar somente o cache RAW na árvore
`infrastructure/jira/<EPIC>/<SPRINT>/<ITEM>/<ISSUE-KEY>[TAG].json`; não substitui a configuração
principal nem transforma posse de credencial em autorização para alterar o Jira.

## Fluxo canônico

Quando o usuário aponta a **tarefa em que está atuando** (sub-tarefa ou história):

```text
receber ISSUE_KEY (tarefa/história do usuário)
   ↓
CHAIN canônico: garante item + história + épico
   ↓
READ canônico -> contexto normalizado
```

Quando o usuário informa apenas uma key isolada para consulta:

```text
cache do ISSUE_KEY existe na árvore e é válido?
   ├─ SIM -> READ canônico -> contexto normalizado
   └─ NÃO -> resolver env Jira -> FETCH canônico -> WRITE single-line -> READ canônico
```

Cache válido sempre vence nova chamada ao Jira.

A resolução do caminho é feita pelo helper (`find_cache_path`), que localiza o arquivo do
`ISSUE_KEY` **por busca**, independente de épico/sprint. O modelo nunca monta o caminho à mão.

## Comandos oficiais

### Ler cache existente

```bash
python infrastructure/jira/jira-cache.py read SGJA-123
```

Esse comando:

- interpreta o JSON com parser nativo;
- normaliza automaticamente cache JSON válido salvo com pretty-print;
- mantém o arquivo físico como **MINIFIED SINGLE-LINE JSON**;
- extrai campos úteis;
- converte ADF (`description`/comentários) para texto;
- preserva custom fields não vazios na saída normalizada.

### Trazer a tarefa com a cadeia (uso principal)

```bash
python infrastructure/jira/jira-cache.py chain SGJA-211
```

Garante no cache o item informado mais a história e o épico ancestrais. Ancestral já cacheado não é
reconsultado. É o comando padrão quando o usuário diz qual tarefa/história vai atuar.

### Buscar somente quando houver cache miss

```bash
python infrastructure/jira/jira-cache.py fetch SGJA-123
```

`fetch` é cache-first. Se o cache existir e for válido, não lê `.env`, não autentica e não chama Jira.

### Atualização explícita

Somente quando o usuário pedir refresh/atualização:

```bash
python infrastructure/jira/jira-cache.py refresh SGJA-123
```

### Validar/normalizar cache

```bash
python infrastructure/jira/jira-cache.py validate SGJA-123
```

## Contrato de persistência

O cache oficial é gravado numa **árvore** derivada da hierarquia do Jira:

```text
infrastructure/jira/
  jira-cache.py
  jira-auth.local.json
  <EPIC> [Épico]/
    <EPIC>[EPICO].json
    <SPRINT>/
      <ITEM> [História|Delivery]/
        <ITEM>[HISTORIA|DELIVERY].json
        <SUB> [Sub-tarefa].json
```

Convenção de labels (obrigatória):

| Elemento | Label | Exemplo |
|---|---|---|
| Pasta do épico | `<KEY> [Épico]` | `SGJA-3 [Épico]` |
| Épico sem payload no cache | `<KEY> [Épico] (não cacheado)` | `SGJA-147 [Épico] (não cacheado)` |
| Pasta da sprint | `<nome> (<id>)` | `Squad Sprint 4 (58959)` |
| Item sem sprint | `(SEM SPRINT)` | `(SEM SPRINT)` |
| Pasta do item nível 0 | `<KEY> [História\|Delivery]` | `SGJA-210 [História]` |
| Arquivo do item | `<KEY>[TAG].json` | `SGJA-210[HISTORIA].json` |
| Arquivo de sub-tarefa | `<KEY>[SUB-TAREFA].json` | `SGJA-211[SUB-TAREFA].json` |

`TAG` é o tipo do item em maiúsculas sem acento: `EPICO`, `HISTORIA`, `DELIVERY`, `SUB-TAREFA`.

Regras de derivação:

- épico do item = `customfield_10008` / `customfield_10432`; se ausente, sobe a cadeia de `parent`;
- sprint = **última entrada** de `customfield_10010` (as anteriores são carry-over histórico);
- `História` e `Delivery` são **irmãos** (ambos filhos diretos do épico);
- sub-tarefa fica na pasta do pai, sem sprint própria;
- caminho não resolvido (pai fora do cache) cai para o flat `infrastructure/jira/<KEY>.json`.

### Fluxo de entrada do usuário — trazer a cadeia

Histórias e épicos podem ser criados por qualquer pessoa, e uma história **pode ser compartilhada**
com colegas (dev par, QA). Isso é normal: o `assignee` da história pode não ser o usuário.

O fluxo de trabalho é: o usuário informa **a tarefa em que está atuando** (sub-tarefa ou história) e o
modelo deve trazer **a tarefa + a história + o épico** e seguir a árvore normal.

Use o comando de cadeia:

```bash
python infrastructure/jira/jira-cache.py chain SGJA-211
```

`chain`:

- garante o item informado no cache;
- sobe a cadeia de `parent` e faz `fetch` de cada ancestral ausente (história → épico);
- respeita cache-first: ancestral já cacheado **não** é reconsultado;
- não inventa elo: se o ancestral não existir, para ali;
- reposiciona o item na árvore após os ancestrais existirem.

### Escopo do cache

O cache **não é espelho do board** e também **não é filtrado** por titularidade. Ele guarda:

- a cadeia da tarefa/história que o usuário está atuando (via `chain`);
- itens sem `assignee`, que permanecem para evitar `fetch` futuro (o usuário só pede `refresh`
  quando começar por eles).

`creator` é **informação**, nunca regra. `assignee` serve para o usuário identificar o dono, não para
excluir do cache.

Não remover itens do cache por questões de titularidade. Se houver referência órfã (pai ou filho sem
cache), usar `chain`/`fetch` para fechar a árvore — nunca deixar `(não cacheado)` pendurado quando o
item fizer parte da tarefa em andamento.

Formato do conteúdo permanece obrigatório:

- resposta RAW do Jira;
- JSON válido;
- UTF-8;
- minificado;
- exatamente uma linha física;
- sem indentação/pretty-print;
- sem resumo;
- sem reconstrução manual pela LLM;
- sem mudança de schema.

Exemplo conceitual:

```json
{"expand":"...","id":"...","key":"SGJA-123","fields":{...}}
```

O helper usa serialização compacta para garantir esse formato.

### Migração do layout flat

Caches no layout antigo (`infrastructure/jira/<KEY>.json`) permanecem legíveis: o helper localiza
por busca e, na primeira leitura/normalização, move o arquivo para a árvore automaticamente. Nenhuma
migração manual é necessária.

## Contrato de leitura

Se o cache do `ISSUE-KEY` existir na árvore:

1. não procurar credencial;
2. não ler `.env`;
3. não chamar Jira;
4. não abrir o RAW gigante como estratégia principal;
5. não estudar outros JSONs antigos para descobrir o formato;
6. não tentar `jq`, PowerShell, parser improvisado ou nova linguagem;
7. executar o comando `read` oficial.

A saída normalizada contém, quando disponíveis:

- key;
- summary;
- status;
- issue type;
- parent;
- epic;
- sprint (última entrada da carga de sprint, ou `null`);
- backlog (`true` quando não houver sprint atual);
- description em texto;
- comments em texto;
- subtasks;
- labels;
- custom fields não vazios, com nome quando o Jira fornecer `names`.

## Configuração de autenticação

O arquivo versionado `infrastructure/jira/jira-auth.local.json` **não contém segredos**. Ele apenas mapeia os campos para variáveis de ambiente:

```json
{
  "jira": {
    "baseUrl": "${JIRA_BASE_URL}",
    "email": "${JIRA_EMAIL}",
    "apiToken": "${JIRA_API_TOKEN}"
  }
}
```

Os valores reais ficam no `.env` local da raiz do orquestrador:

```text
JIRA_BASE_URL=https://SEU-DOMINIO.atlassian.net
JIRA_EMAIL=SEU_EMAIL_AQUI
JIRA_API_TOKEN=SEU_TOKEN_AQUI
```

Regras:

- `.env` real é local e deve permanecer ignorado pelo Git;
- `.env.example` é o template versionado sem segredos;
- o agente não deve abrir, imprimir, resumir ou copiar o conteúdo de `.env`;
- `jira-cache.py` carrega `.env` mecanicamente apenas em cache miss/refresh;
- variáveis já definidas no processo têm precedência sobre valores do `.env`;
- não procurar credenciais em arquivos antigos ou projetos arbitrários;
- usar `skills/jira/jira-access-settings-local.md` somente como fallback controlado desta skill,
  quando a autenticação principal não estiver disponível; a credencial permanece apenas em memória.

Se uma variável obrigatória estiver ausente, parar e informar somente o nome da variável/caminho esperado; nunca pedir o token no chat.

## Requisição canônica — formato validado em ambiente real

A chamada deve reproduzir o request que retornou `HTTP 200` no ambiente real.

```text
METHOD: GET
URL: <baseUrl>/rest/api/3/issue/<ISSUE-KEY>?expand=renderedFields,names
HEADERS:
  Accept: application/json
  Authorization: Basic <base64(email + ":" + apiToken)>
```

Equivalente em curl, usando somente variáveis de ambiente:

```bash
AUTH_B64="$(printf '%s' "${JIRA_EMAIL}:${JIRA_API_TOKEN}" | base64 | tr -d '\r\n')"

curl --request GET \
  --url "${JIRA_BASE_URL}/rest/api/3/issue/${ISSUE_KEY}?expand=renderedFields,names" \
  --header "Accept: application/json" \
  --header "Authorization: Basic ${AUTH_B64}"
```

O helper `jira-cache.py` implementa a mesma semântica: resolve `${JIRA_*}`, monta
`base64(email:apiToken)` e envia `Authorization` já na **primeira requisição**.

### Regra anti-regressão de autenticação

É proibido substituir a requisição acima por mecanismo que aguarde challenge HTTP antes de enviar Basic Auth.

Não usar:

```text
urllib.request.HTTPBasicAuthHandler
HTTPPasswordMgrWithDefaultRealm
cliente equivalente que espere 401/challenge antes de enviar Basic Auth
```

Esse padrão já gerou `404` falso para issues que retornaram `200` com o header explícito.

Se o mecanismo canônico falhar, classificar o status e parar. Não tentar outra estratégia de autenticação.

Quando a falha for de configuração/autenticação principal e o fallback controlado estiver disponível,
executar o procedimento da skill de fallback uma única vez. Se ele também falhar, reportar o status sem
expor credenciais e sem tentar outras fontes.

## Segurança

Obrigatório:

- nunca imprimir `JIRA_API_TOKEN`;
- nunca imprimir o header `Authorization`;
- nunca persistir credencial em cache Jira;
- nunca copiar credencial para `.ai/`, `STATE.md`, `00-jira.md`, logs, QA, commit ou PR;
- nunca abrir `.env` no contexto da LLM;
- nunca pedir que o usuário cole token no chat;
- se token aparecer em chat/print/log, considerar exposto e recomendar revogação.

## Regra de escrita

Esta skill executa leitura (`GET`) e cache local por padrão. Uma credencial com permissão de escrita
**não** concede autorização ao agente.

Criar, atualizar, comentar ou transicionar uma issue exige **solicitação explícita do usuário** que
identifique **três elementos**: a **ação** (ex.: atualizar descrição), a **issue** (key ou URL) e o
**conteúdo/campos pretendidos**. Sem os três, **não** fazer chamada de mutação — nem propor, nem
assumir. Escrita é sempre opt-in e nunca inferida de contexto, cache, status da tarefa ou pedido de
leitura.

### Procedimento canônico de mutação (somente sob pedido explícito)

Confirmados os três elementos:

1. **Resolver credencial pelo mecanismo oficial**: usar `resolve_auth()` do
   `infrastructure/jira/jira-cache.py` (ou o fallback de `skills/jira/jira-access-settings-local.md`
   quando a autenticação principal não estiver disponível). Nunca ler `.env` diretamente, nunca
   imprimir e-mail/token, nunca imprimir o header `Authorization`.
2. **Montar a URL**: `<baseUrl>/rest/api/3/issue/<ISSUE-KEY>`.
3. **Montar o corpo**: JSON `{"fields": { ... }}` apenas com os campos pedidos. Conteúdo rico usa
   ADF (`{"type":"doc","version":1,"content":[...]}`). Não alterar outros campos nem remover
   dados existentes sem pedido.
4. **Enviar a mutação**: `PUT` para atualizar campos (ex.: `description`, `summary`) ou
   `POST /rest/api/3/issue/<ISSUE-KEY>/comment` para comentar. Header
   `Content-Type: application/json` e `Accept: application/json`.
5. **Confirmar o resultado**: `HTTP 204` (atualização) ou `HTTP 201` (comentário) indicam sucesso.
   Falhas seguem a mesma classificação de status da seção `Falhas`. Em caso de `400`, apresentar o
   erro do Jira **sem** exibir credenciais.
6. **Revalidar pelo caminho de leitura**: executar `python infrastructure/jira/jira-cache.py refresh
   <ISSUE-KEY>` para recarregar o cache e confirmar o valor gravado.
7. **Emitir apenas o necessário**: informar a key, o campo alterado e o status HTTP. **Nunca**
   persistir credencial, header de auth ou corpo de requisição em `.ai/`, `STATE.md`, `00-jira.md`,
   logs, QA, commit ou PR.

Escopo permitido: campos de issue e comentários. **Fora de escopo**: criar issues, alterar
workflow/transições sem pedido, executar JQL de escrita, alterar permissões ou qualquer operação em
lote.

## Falhas

Classificar e parar; não trocar de runtime/estratégia por tentativa e erro.

Leitura:

- `AUTH_ENV_MISSING`: variável Jira ausente no ambiente/`.env`;
- `401`: credencial inválida/expirada;
- `403`: usuário autenticado sem permissão;
- `404`: issue inexistente ou não visível **com o mecanismo canônico**;
- erro de rede: reportar conexão;
- cache inválido: `fetch` pode refazer a consulta; `read` deve reportar o problema.

Escrita (somente sob pedido explícito):

- `204`: mutação aplicada com sucesso (sem corpo);
- `201`: comentário criado;
- `400`: payload inválido — apresentar a mensagem do Jira sem expor credenciais;
- `401`/`403`: credencial sem permissão de escrita — parar e informar;
- `404`: issue inexistente ou não visível — parar;
- `USER_PERMISSION_MISSING`: sem alvo (ação/issue/conteúdo) identificados pelo usuário — **não**
  executar mutação.

## Normalização da URL

Se receber URL `/browse/SGJA-123`, extrair `SGJA-123`. Se já receber a key, usar diretamente.

## Anexos e imagens

Metadados de anexos podem existir no payload. Não inventar conteúdo visual. Se imagem/diagrama for material ao entendimento, solicitar o arquivo ao usuário, salvo quando o runtime possuir capacidade autorizada para obtê-lo.

## Saída esperada

Produzir:

```text
JIRA_CONTEXT_READY=true
```

mais o contexto normalizado **somente em memória da sessão**.

A persistência da feature continua pertencendo a `skills/01-intake-jira.md`. O cache RAW em
`infrastructure/jira/<EPIC>/<SPRINT>/<ITEM>/<ISSUE-KEY>[TAG].json` pertence exclusivamente a esta
skill/helper e permanece local.
