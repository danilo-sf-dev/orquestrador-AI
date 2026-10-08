---
name: gitlab-access-settings-local
description: Acessa a API do GitLab usando a permissão curl/token registrada no settings.local.json do projeto.
preferred_model_role: ECONOMICAL
context_loading: lazy

reads:
  - <projeto>/.claude/settings.local.json
  - ~/.config/glab-cli/config.yml_if_present

writes:
  - <orquestrador>/infrastructure/gitlab/<RESOURCE-KEY>.json

forbidden_writes:
  - credentials
  - tokens
  - logs_with_auth_headers
---

# GitLab Access via settings.local.json

## Quando usar

Usar quando `infrastructure/gitlab/gitlab-auth.local.json` estiver com placeholders não
resolvidos (variável de ambiente ausente), mas outro projeto Claude possuir uma permissão
`Bash(curl ...)` funcional que acesse o GitLab, ou existir um token local já autorizado.

## Procedimento

1. Abrir o `settings.local.json` do projeto que acessa o GitLab.
2. Localizar uma entrada que comece com uma das formas:

```text
Bash(curl -s --header "PRIVATE-TOKEN: <token>" https://gitlab.<dominio>
Bash(curl -s -H "PRIVATE-TOKEN: <token>" https://gitlab.<dominio>
Bash(curl -s --header "Authorization: Bearer <token>" https://gitlab.<dominio>
Bash(curl -s -u <usuario>:<token> https://gitlab.<dominio>
```

3. Extrair o token somente em memória. Nunca imprimir esse valor.
4. Montar o header explicitamente:

```text
PRIVATE-TOKEN: <token>
```

ou, quando a entrada usar Basic Auth:

```text
Authorization: Basic base64(usuario + ":" + token)
```

5. Consultar cada recurso pela API REST:

```text
GET https://gitlab.<dominio>/api/v4/projects/<url-encoded-path-with-namespace>
Accept: application/json
PRIVATE-TOKEN: <token>
```

Para sub-recursos, anexar o endpoint ao path do projeto:

```text
/merge_requests/<iid>
/issues/<iid>
/repository/tree?ref=<ref>
/repository/files/<url-encoded-filepath>?ref=<ref>
/repository/branches/<nome>
/repository/commits?ref=<ref>
/pipelines
```

6. Para cada resposta HTTP `200`, salvar o corpo JSON em:

```text
infrastructure/gitlab/<RESOURCE-KEY>.json
```

Seguindo o contrato de persistência da skill principal: RAW, UTF-8, minificado, uma linha física.

7. Validar `id`/`path_with_namespace` quando for projeto; `iid`/`state` quando for MR ou issue;
   `ref`/`name` quando for branch; `id` quando for commit.

## Regra importante

Usar o header `PRIVATE-TOKEN` explicitamente na primeira requisição. Não depender apenas de um
cliente que aguarde um desafio HTTP para enviar o token, pois isso não reproduziu o acesso que
funcionou no Postman/curl.

NUNCA ESCREVER NO GITLAB SEM A PERMISSAO DO USUARIO

## Exemplo seguro

```python
import base64
import json
import pathlib
import re
import urllib.parse
import urllib.request

settings = json.loads(pathlib.Path(settings_path).read_text(encoding="utf-8"))
entry = next(
    item for item in settings["permissions"]["allow"]
    if "gitlab." in item and "curl" in item
)

# token extraído apenas em memória; nunca logar
match = re.search(r"PRIVATE-TOKEN:\s*([A-Za-z0-9_\-]+)", entry)
if match:
    header_name, header_value = "PRIVATE-TOKEN", match.group(1)
else:
    basic = re.search(r"curl -s -u (.*?) https://gitlab", entry).group(1)
    user, token = basic.split(":", 1)
    header_name = "Authorization"
    header_value = "Basic " + base64.b64encode(
        f"{user}:{token}".encode()
    ).decode()

project_ref = urllib.parse.quote("grupo/projeto", safe="")
request = urllib.request.Request(
    f"https://gitlab.SEU-DOMINIO.com/api/v4/projects/{project_ref}",
    headers={
        "Accept": "application/json",
        header_name: header_value,
    },
)
```

## Diagnóstico

- `200`: recurso acessível; salvar o JSON.
- `401`: token inválido ou expirado.
- `403`: usuário autenticado sem permissão (verificar escopo `read_api`/`api`).
- `404`: projeto/recurso inexistente ou ocultado por falta de permissão.
- `200` em lista vazia (`[]`): nenhum item visível para o filtro aplicado.
- erro de TLS: em rede corporativa, a CA interna pode não validar na máquina e a requisição
  falha com `CERTIFICATE_VERIFY_FAILED ... Basic Constraints of CA cert not marked critical`.
  Quando o helper `gitlab-cache.py` estiver sendo usado, reexecutar uma única vez com
  `GITLAB_VERIFY_SSL=false` (opção suportada pelo helper); não alterar o script nem trocar de
  estratégia de autenticação. Se persistir, reportar como erro de rede.

## Segurança

- Nunca copiar token para documentação, memória persistente, logs ou resposta.
- Nunca imprimir os headers `PRIVATE-TOKEN` / `Authorization`.
- Não usar token exposto em chat, anexo ou arquivo versionado.
- Se um token for exposto, revogá-lo no GitLab e gerar outro imediatamente.
- `settings.local.json` deve permanecer local e fora do commit.
- NUNCA ESCREVER NO GITLAB SEM A PERMISSAO DO USUARIO