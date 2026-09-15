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
  - <projeto>/.claude/settings.local.json

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
   └─ NÃO -> AUTH -> FETCH canônico -> WRITE single-line -> READ canônico
```

Cache válido sempre vence nova chamada ao Jira.

## Comandos oficiais

### Ler cache existente

```bash
python infrastructure/jira/jira-cache.py read SGJA-123
```

Esse comando:

- executa `JSON.parse` equivalente via parser nativo;
- normaliza automaticamente cache JSON válido que tenha sido salvo com pretty-print;
- mantém o arquivo físico como **MINIFIED SINGLE-LINE JSON**;
- extrai campos úteis;
- converte ADF (`description`/comentários) para texto;
- preserva custom fields não vazios na saída normalizada.

### Buscar somente quando houver cache miss

```bash
python infrastructure/jira/jira-cache.py fetch SGJA-123
```

`fetch` é cache-first. Se o cache existir e for válido, não autentica e não chama Jira.

Quando o projeto que possui a permissão Claude estiver fora do cwd atual, usar:

```bash
python infrastructure/jira/jira-cache.py fetch SGJA-123 --settings "<projeto>/.claude/settings.local.json"
```

### Atualização explícita

Somente quando o usuário pedir refresh/atualização:

```bash
python infrastructure/jira/jira-cache.py refresh SGJA-123 --settings "<projeto>/.claude/settings.local.json"
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

Nunca salvar como:

```json
{
  "key": "SGJA-123",
  "fields": {}
}
```

O helper usa serialização compacta para garantir esse formato.

## Contrato de leitura

Se `infrastructure/jira/<ISSUE-KEY>.json` existir:

1. não procurar credencial;
2. não chamar Jira;
3. não abrir o RAW gigante como estratégia principal;
4. não estudar outros JSONs antigos para descobrir o formato;
5. não tentar `jq`, PowerShell, parser improvisado ou nova linguagem;
6. executar o comando `read` oficial.

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

## Autenticação — somente em cache miss

Prioridade:

1. usar `infrastructure/jira/jira-auth.local.json` se ele possuir valores reais locais;
2. se o arquivo tiver placeholders, usar a permissão Jira já configurada em
   `<projeto>/.claude/settings.local.json`;
3. o caminho pode ser passado explicitamente com `--settings`.

A versão commitada de `jira-auth.local.json` é deliberadamente um template fake:

```json
{
  "jira": {
    "baseUrl": "https://SEU-DOMINIO.atlassian.net",
    "email": "SEU_EMAIL_AQUI",
    "apiToken": "SEU_TOKEN_AQUI"
  }
}
```

É permitido versionar o template enquanto contiver somente placeholders.

## Basic Auth obrigatório

Quando usar a API, o `Authorization` deve ser enviado **explicitamente na primeira requisição**:

```text
Authorization: Basic base64(email + ":" + token)
Accept: application/json
```

Endpoint canônico:

```text
GET <baseUrl>/rest/api/3/issue/<ISSUE-KEY>?expand=renderedFields,names
```

Não usar cliente que aguarde challenge HTTP antes de enviar Basic Auth. Esse comportamento já produziu
`404` falso para issues acessíveis.

## Segurança

Obrigatório:

- nunca imprimir `apiToken`;
- nunca imprimir o header `Authorization`;
- nunca persistir credencial em cache Jira;
- nunca copiar credencial para `.ai/`, `STATE.md`, `00-jira.md`, logs, QA, commit ou PR;
- nunca pedir que o usuário cole token no chat;
- se um token aparecer em chat/print/log, considerar exposto e recomendar revogação.

O helper lê credenciais somente em memória.

## Falhas

Classificar e parar; não trocar de runtime/estratégia por tentativa e erro.

- `401`: credencial inválida/expirada;
- `403`: usuário autenticado sem permissão;
- `404`: issue inexistente ou não visível **com o mecanismo canônico**;
- erro de rede: reportar conexão;
- cache inválido: o helper tenta novo fetch somente em `fetch`; `read` deve reportar o problema.

## Normalização da URL

Se receber:

```text
https://SEU-DOMINIO.atlassian.net/browse/SGJA-123
```

extrair:

```text
SGJA-123
```

Se já receber `SGJA-123`, usar diretamente.

## Anexos e imagens

Metadados de anexos podem existir no payload.

Não inventar conteúdo visual. Se imagem/diagrama for material ao entendimento, solicitar o arquivo ao
usuário, salvo quando o runtime possuir capacidade autorizada para obtê-lo.

## Saída esperada

Produzir:

```text
JIRA_CONTEXT_READY=true
```

mais o contexto normalizado **somente em memória da sessão**.

A persistência da feature continua pertencendo a `skills/01-intake-jira.md`, que protege `.ai/` no
`.gitignore` antes de criar `STATE.md` e `00-jira.md`.

O cache RAW em `infrastructure/jira/<ISSUE-KEY>.json` pertence exclusivamente a esta skill/helper.
