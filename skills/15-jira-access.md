---
name: jira-access
description: >
  Acessa uma issue do Jira a partir de uma URL ou issue key, usando
  credenciais configuradas em infrastructure/jira/jira-auth.local.json.
preferred_model_role: ECONOMICAL
context_loading: lazy

reads:
  - infrastructure/jira/jira-auth.local.json

writes:
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

Esta skill é a porta de entrada padrão para qualquer fluxo do orquestrador que comece por um card do Jira.

Ela recebe uma URL como:

```text
https://SEU-DOMINIO.atlassian.net/browse/SGJA-123
```

ou diretamente:

```text
SGJA-123
```

e deve:

1. extrair a issue key;
2. carregar as credenciais/configuração local;
3. consultar a API REST do Jira;
4. interpretar o JSON retornado;
5. gerar o contexto normalizado da issue;
6. devolver contexto normalizado **efêmero** ao orquestrador;
7. nunca criar `.ai/`, `STATE.md` ou `00-jira.md` nesta skill;
8. nunca exibir, registrar ou persistir credencial real fora da chamada.

## Arquivo de autenticação

Caminho esperado:

```text
infrastructure/jira/jira-auth.local.json
```

A versão commitada no repositório é deliberadamente um **template fake**, por exemplo:

```json
{
  "jira": {
    "baseUrl": "https://SEU-DOMINIO.atlassian.net",
    "email": "SEU_EMAIL_AQUI",
    "apiToken": "SEU_TOKEN_AQUI"
  }
}
```

É permitido versionar esse template enquanto ele contiver somente placeholders/fake values.

Se o usuário preencher valores reais localmente para execução, essa modificação passa a ser sensível:

- nunca stagear ou commitar os valores reais;
- nunca copiar valores reais para memória, logs, QA, commit ou PR;
- antes de commit, tratar qualquer diff real desse arquivo como segredo e excluí-lo do stage.

## Consulta da issue

Depois de ler `baseUrl`, `email` e `apiToken`, montar a chamada equivalente a:

```bash
curl -sS \
  -u "${JIRA_EMAIL}:${JIRA_API_TOKEN}" \
  "${JIRA_BASE_URL}/rest/api/3/issue/${JIRA_ID}" \
  -H "Accept: application/json"
```

Os valores devem ser obtidos do arquivo. Nunca imprimir a linha final contendo credenciais reais.

## Normalização da URL

Se o usuário fornecer:

```text
https://SEU-DOMINIO.atlassian.net/browse/SGJA-123
```

extrair:

```text
SGJA-123
```

Se o usuário já fornecer `SGJA-123`, usar diretamente.

## Dados que devem ser extraídos

Quando disponíveis no payload do Jira:

- issue key;
- summary/título;
- status;
- issue type;
- description;
- acceptance criteria presentes na descrição/campos retornados;
- subtasks;
- issue links e dependências;
- labels;
- components;
- assignee somente se for relevante para o fluxo;
- metadados de anexos.

Não transformar subtasks ou instruções técnicas automaticamente em Acceptance Criteria. Manter cada categoria separada.

## Anexos e imagens

O endpoint `/rest/api/3/issue/{id}` pode retornar metadados de anexos, mas esta skill não deve assumir que consegue interpretar o conteúdo visual.

Se houver imagem ou diagrama relevante:

1. registrar que existe anexo visual;
2. não inventar o conteúdo;
3. solicitar que o usuário forneça a imagem no chat, salvo se o runtime possuir capacidade específica e autorizada para baixar/ler o anexo.

## Segurança

Obrigatório:

- nunca mostrar `apiToken` real;
- nunca mostrar o valor completo de `email` junto com token real;
- nunca copiar credenciais para `STATE.md`;
- nunca copiar credenciais para `00-jira.md`;
- nunca salvar credenciais reais em logs, artefatos, commits ou PRs;
- nunca pedir que o usuário cole o token no chat se o arquivo configurável estiver ausente/incompleto.

Se o arquivo não existir ou ainda contiver placeholders ao executar contra o Jira, parar o intake e informar apenas o caminho esperado:

```text
infrastructure/jira/jira-auth.local.json
```

## Falhas

- `401`: autenticação inválida ou token expirado;
- `403`: usuário autenticado sem permissão para a issue;
- `404`: issue inexistente ou inacessível;
- erro de rede: reportar falha de conexão e não inventar dados.

## Saída esperada

Produzir `JIRA_CONTEXT_READY=true` + contexto normalizado **somente em memória da sessão**.

A persistência pertence a `skills/01-intake-jira.md`, que primeiro protege `.ai/` no `.gitignore` e só então cria `.ai/features/<JIRA-ID>/STATE.md` e `00-jira.md`.

A saída nunca deve conter credenciais reais.
