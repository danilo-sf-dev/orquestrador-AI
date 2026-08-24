---
name: scenario-cross-repo
load_mode: on_demand
context_loading: lazy
reads:
  - STATE.md
  - scenario_signal_only
forbidden_reads:
  - chat_transcript
  - unrelated_feature_artifacts
writes:
  - STATE.md
---

# Cenário — Mudança cross-repo

## Quando usar
Uma história/bug altera ou depende de dois ou mais repositórios que se chamam ou compartilham contrato.

## Canonical feature memory
Criar uma única pasta canônica `.ai/features/<JIRA-ID>/`. Nos demais repos, criar `FEATURE-LINK.md` apontando para ela.

## Contrato obrigatório
No `STATE.md` e PRD:

```text
SOURCE_REPO:
TARGET_REPO:
INTERACTION: REST|EVENT|DB|OTHER
ENDPOINT/TOPIC:
REQUEST_SCHEMA:
RESPONSE_SCHEMA:
ERRORS:
AUTH/HEADERS:
COMPATIBILITY:
DEPLOY_ORDER:
ROLLBACK:
```

## Discovery
ECONOMICAL rastreia ambos os lados antes do HEAD decidir.

## RED
Criar testes de cada lado do contrato quando possível. Selar todos os arquivos RED envolvidos.

## Implementação
EXECUTOR pode alternar repos, mas deve atualizar um único `STATE.md` canônico.

## Judge
Julgar o fluxo end-to-end conceitual e a compatibilidade, não apenas “repo A passa testes”. Para risco alto, usar dois juízes independentes.

## Commit
Aplicar `skills/12-commit-workflow.md`. Validar todos os repos antes do primeiro commit no fluxo seguro, criar um commit por repo, respeitar contrato/compatibilidade/ordem e registrar todos os SHAs na memória canônica.

## Archive
Indexar a feature em cada repo por ponteiro e na memória canônica por endpoints/contratos/classes de ambos.


## Regra de testes unitários
Os testes RED devem incluir happy path e **edge cases aplicáveis** à história/bug. Edge cases relevantes não cobertos precisam de justificativa explícita; não criar cenários artificiais sem vínculo com critérios, regras, contratos ou riscos.
