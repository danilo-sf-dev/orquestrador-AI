---
name: jira-access
description: >
  Acessa issues do Jira com política cache-first e procedimento determinístico
  de fetch, persistência single-line e leitura normalizada.
preferred_model_role: ECONOMICAL
context_loading: lazy

reads:
  - infrastructure/jira/jira-cache.py
  - infrastructure/jira/<ISSUE-KEY>.json
  - infrastructure/jira/jira-auth.local.json

forbidden_reads:
  - .env

writes:
  - infrastructure/jira/<ISSUE-KEY>.json
  - jira_context_ephemeral

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

## Fluxo canônico

```text
receber ISSUE_KEY
   ↓
cache infrastructure/jira/<ISSUE_KEY>.json existe e é válido?
   ├─ SIM -> READ canônico -> contexto normalizado
   └─ NÃO -> resolver env Jira -> FETCH canônico -> WRITE single-line -> READ canônico
```

Cache válido sempre vence nova chamada ao Jira.

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

O cache oficial é:

```text
infrastructure/jira/<ISSUE-KEY>.json
```

Formato obrigatório:

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

## Contrato de leitura

Se `infrastructure/jira/<ISSUE-KEY>.json` existir:

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
- não procurar credenciais em `.claude/settings.local.json`, outros projetos ou arquivos antigos.

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

## Segurança

Obrigatório:

- nunca imprimir `JIRA_API_TOKEN`;
- nunca imprimir o header `Authorization`;
- nunca persistir credencial em cache Jira;
- nunca copiar credencial para `.ai/`, `STATE.md`, `00-jira.md`, logs, QA, commit ou PR;
- nunca abrir `.env` no contexto da LLM;
- nunca pedir que o usuário cole token no chat;
- se token aparecer em chat/print/log, considerar exposto e recomendar revogação.

## Falhas

Classificar e parar; não trocar de runtime/estratégia por tentativa e erro.

- `AUTH_ENV_MISSING`: variável Jira ausente no ambiente/`.env`;
- `401`: credencial inválida/expirada;
- `403`: usuário autenticado sem permissão;
- `404`: issue inexistente ou não visível **com o mecanismo canônico**;
- erro de rede: reportar conexão;
- cache inválido: `fetch` pode refazer a consulta; `read` deve reportar o problema.

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
`infrastructure/jira/<ISSUE-KEY>.json` pertence exclusivamente a esta skill/helper e permanece local.
