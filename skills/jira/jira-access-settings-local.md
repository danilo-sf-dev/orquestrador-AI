---
name: jira-access-settings-local
description: Acessa a API do Jira usando a permissão curl registrada no settings.local.json do projeto.
preferred_model_role: ECONOMICAL
context_loading: lazy

reads:
  - <projeto>/.claude/settings.local.json

writes:
  - <orquestrador>/infrastructure/jira/<EPIC>/<SPRINT>/<ITEM>/<ISSUE-KEY>[TAG].json

forbidden_writes:
  - credentials
  - tokens
  - logs_with_auth_headers
---

# Jira Access via settings.local.json

## Quando usar

Usar quando `infrastructure/jira/jira-auth.local.json` estiver com placeholders,
mas outro projeto Claude possuir uma permissão `Bash(curl -s -u ...)` funcional.

## Procedimento

1. Abrir o `settings.local.json` do projeto que acessa o Jira.
2. Localizar uma entrada que comece com:

```text
Bash(curl -s -u <email>:<token> https://portoseguro.atlassian.net
```

3. Extrair o e-mail e o token somente em memória. Nunca imprimir esses valores.
4. Montar o Basic Auth explicitamente:

```text
Authorization: Basic base64(email + ":" + token)
```

5. Consultar cada issue pela API REST:

```text
GET https://portoseguro.atlassian.net/rest/api/3/issue/<ISSUE-KEY>?expand=renderedFields
Accept: application/json
Authorization: Basic <base64>
```

6. Para cada resposta HTTP `200`, salvar o corpo JSON em:

```text
infrastructure/jira/<EPIC>/<SPRINT>/<ITEM>/<ISSUE-KEY>[TAG].json
```

seguindo os labels do contrato de persistência de `skills/15-jira-access.md`.

7. Validar `key`, `fields.summary`, `fields.status.name`,
`fields.issuetype.name` e `fields.parent.key`.

## Regra importante

Usar o header `Authorization` explicitamente na primeira requisição. Não depender
apenas de um cliente que aguarde um desafio HTTP para enviar o Basic Auth, pois
isso não reproduziu o acesso que funcionou no Postman/curl.
- NUNCA ESCREVER NO JIRA SEM A PERMISSAO DO USUARIO

## Escrita — somente sob pedido explícito

Por padrão o fallback é leitura (`GET`) e cache local. Escrever no Jira exige
**solicitação explícita do usuário** com **ação + issue + conteúdo/campos**. Sem os
três, não executar mutação.

Confirmados os três, o procedimento é o mesmo da skill principal
(`skills/15-jira-access.md`, seção “Regra de escrita / Procedimento canônico de
mutação”), reutilizando a credencial resolvida aqui:

```text
METHOD: PUT
URL: https://portoseguro.atlassian.net/rest/api/3/issue/<ISSUE-KEY>
HEADERS:
  Accept: application/json
  Content-Type: application/json
  Authorization: Basic <base64(email + ":" + token)>
BODY: {"fields": { "<campo>": <valor> }}   # conteúdo rico usa ADF
```

Códigos esperados: `204` (atualização), `201` (comentário via
`POST .../issue/<ISSUE-KEY>/comment`), `400` (payload inválido), `401`/`403`
(sem permissão), `404` (issue não visível). Depois de gravar, revalidar com
`python infrastructure/jira/jira-cache.py refresh <ISSUE-KEY>`. Nunca persistir
credencial/header em logs, docs, QA, commit ou PR.

## Exemplo seguro

```python
import base64
import json
import pathlib
import re
import urllib.request

settings = json.loads(pathlib.Path(settings_path).read_text(encoding="utf-8"))
entry = next(
    item for item in settings["permissions"]["allow"]
    if item.startswith("Bash(curl -s -u ")
)
credentials = re.search(
    r"Bash\\(curl -s -u (.*?) https://portoseguro\\.atlassian\\.net",
    entry,
).group(1)
email, token = credentials.split(":", 1)
auth_value = base64.b64encode(f"{email}:{token}".encode()).decode()

request = urllib.request.Request(
    f"https://portoseguro.atlassian.net/rest/api/3/issue/{issue_key}"
    "?expand=renderedFields",
    headers={
        "Accept": "application/json",
        "Authorization": f"Basic {auth_value}",
    },
)
```

## Diagnóstico

- `200`: issue acessível; salvar o JSON.
- `401`: credencial inválida ou expirada.
- `403`: usuário autenticado sem permissão.
- `404`: issue inexistente ou ocultada por falta de permissão.
- `200` na busca JQL com `issues: []`: nenhuma issue pesquisada está visível.

## Segurança

- Nunca copiar token para documentação, memória persistente, logs ou resposta.
- Nunca imprimir o header `Authorization`.
- Não usar token exposto em chat, anexo ou arquivo versionado.
- Se um token for exposto, revogá-lo no Jira e gerar outro imediatamente.
- `settings.local.json` deve permanecer local e fora do commit.
- NUNCA ESCREVER NO JIRA SEM A PERMISSAO DO USUARIO
