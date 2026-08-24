---
name: pull-request-workflow
role: pull_request_delivery
description: >-
  Fluxo agnóstico e seguro para preparar e abrir Pull Request/Merge Request de
  uma feature Jira já commitada, criando primeiro o documento de PR dentro da
  memória da feature, respeitando o template nativo do repositório quando
  existir, validando gates, branches, commits, cross-repo e provider real.
  Use somente quando o usuário pedir explicitamente para abrir/criar PR/MR.
preferred_model_role: EXECUTOR
context_loading: lazy
reads:
  - STATE.md
  - 00-jira.md
  - 03-prd.md
  - 04-implementation-plan.md
  - 08-judgement.md
  - 09-qa-tests.md
  - 10-qa-guide.md
  - delivery/commit.md
  - git_diff_source_vs_target
  - project_pr_template_and_policy
writes:
  - delivery/pull-request.md
  - STATE.md
forbidden_reads:
  - chat_transcript
  - raw_discovery_logs
  - implementation_attempt_history
  - unrelated_feature_artifacts
forbidden_writes:
  - source_code
  - tests
  - approved_specs
remote_writes:
  - safe_push_if_needed
  - pull_request_create
source_edits: none
---

# Skill — Pull Request Workflow

## Princípio

PR é **publicação para revisão**, não implementação, julgamento ou merge.

Esta skill:

- não corrige código;
- não altera testes RED;
- não altera critérios/PRD para fazer a entrega parecer correta;
- não cria commit novo silenciosamente;
- não faz merge;
- não aprova o próprio PR;
- não executa force push;
- só abre PR/MR após solicitação explícita do usuário.

A solicitação do usuário para `abrir PR para <branch>` autoriza a criação do
PR e, quando necessário, um **push normal não destrutivo** da source branch para
seu remote configurado. Se o push exigir force, rebase destrutivo, resolução de
divergência ou outra mutação de risco, parar e solicitar decisão humana.

## Triggers

Exemplos válidos:

```text
abra o PR para develop
crie PR dessa história para main
abre um PR para release/2026.08
crie os PRs cross-repo para develop
```

Não disparar automaticamente apenas porque o commit terminou.

Se a target/base branch não foi informada e não existe regra inequívoca no
projeto, perguntar somente:

> Qual branch de destino/base devo usar para o PR?

Não assumir `main`, `master` ou `develop` por convenção genérica.

## Resultado esperado

Para cada repositório afetado:

1. validar que a feature está apta a ser publicada;
2. criar/atualizar `.ai/features/<JIRA-ID>/delivery/pull-request.md`;
3. garantir que a source branch está publicada de forma segura;
4. abrir o PR/MR para a target branch solicitada;
5. registrar provider, número, URL, branches e estado em `STATE.md`;
6. em cross-repo, registrar todos os PRs relacionados no documento canônico.

A criação do arquivo ocorre **antes** da chamada remota. Se a criação remota
falhar, o corpo do PR continua preservado para nova tentativa.

## Pré-flight obrigatório

Antes de qualquer push ou criação remota:

1. identificar o Jira/feature ativa e ler `STATE.md`;
2. carregar, quando existirem:
   - `00-jira.md`;
   - `03-prd.md`;
   - `04-implementation-plan.md`;
   - `05-red-tests.md` e `red-tests.lock`;
   - `06-implementation-summary.md`;
   - `07-green-evidence.md`;
   - `08-judgement.md`;
   - `09-qa-tests.md`;
   - `10-qa-guide.md`;
   - `delivery/commit.md`;
3. identificar todos os repositórios Git afetados;
4. detectar `remote`, provider e branch atual reais;
5. validar que a target branch solicitada existe no remote;
6. verificar commits da source em relação à target/base;
7. verificar working tree e mudanças locais não commitadas;
8. verificar que o escopo atualmente publicado continua compatível com o
   `JUDGEMENT_SCOPE_HASH` e que `JUDGEMENT_STALE=false`;
9. verificar `COMMIT_STATUS` e SHAs reais do fluxo;
10. detectar template/política de PR/MR do projeto;
11. detectar ferramenta autenticada suportada pelo provider;
12. não inventar URL, número de PR, reviewer, label ou comando.

## Gates mínimos

Para PR de implementação final:

- RED lock íntegro;
- GREEN válido;
- Judge = `PASS`, ou `PASS_WITH_RISKS` explicitamente aceito;
- QA aprovado quando o PR representa a entrega completa da história;
- commit(s) esperado(s) existentes;
- nenhuma mudança de código/teste pós-Judge sem revalidação;
- source branch diferente da target branch;
- target branch existente;
- nenhum secret evidente no diff;
- nenhum arquivo não relacionado incluído intencionalmente.

Se o usuário pedir PR intermediário antes de QA/final gate, tratar como fluxo
customizado e marcar claramente `PR_TYPE=INTERMEDIATE`; nunca declarar a
feature pronta por causa desse PR.

## Descoberta do provider e ferramenta

Derivar do remote Git e ferramentas realmente disponíveis.

Exemplos possíveis, **somente após detecção**:

- GitHub -> `gh` autenticado;
- GitLab -> `glab` autenticado;
- Azure DevOps -> `az repos`/integração configurada;
- Bitbucket -> ferramenta/API já configurada no ambiente;
- outro provider -> mecanismo disponível no projeto/ambiente.

Se não existir uma ferramenta autenticada capaz de criar o PR:

1. criar `delivery/pull-request.md` completo;
2. registrar `PR_STATUS=BLOCKED`;
3. informar exatamente o bloqueio;
4. fornecer o título/corpo prontos para uso;
5. **não fingir** que o PR foi aberto.

## Template — duas camadas

### 1. Documento canônico da feature — obrigatório

Sempre materializar o template `templates/pull-request.md` em:

```text
.ai/features/<JIRA-ID>/delivery/pull-request.md
```

Preencher somente com evidências reais da feature.

Ele é a memória do PR mesmo quando `.ai/features/` estiver com política
`local_only` e não entrar no Git.

### 2. Template nativo do repositório — prioridade na publicação remota

Antes de criar o corpo remoto, procurar template/política do projeto, por
exemplo:

- `.github/PULL_REQUEST_TEMPLATE.md`;
- `.github/PULL_REQUEST_TEMPLATE/`;
- `.gitlab/merge_request_templates/`;
- template/configuração equivalente do provider;
- `CONTRIBUTING.md`, README ou documentação de engenharia;
- regra explícita do time.

Se existir, respeitar sua estrutura e preencher os campos a partir do
`delivery/pull-request.md`. Não substituir silenciosamente o padrão corporativo.

Se não existir, usar o conteúdo do nosso template canônico como fallback do
corpo remoto, removendo apenas metadados estritamente internos que não façam
sentido no PR público do projeto.

## Como preencher o PR

### Resumo

Derivar de Jira/PRD + implementação final. Deve responder:

- qual problema/necessidade foi atendido;
- qual comportamento principal mudou;
- quais sistemas/repos foram afetados.

Não usar texto genérico como `ajustes da task`.

### Critérios de aceite

Usar o julgamento final e evidências para mapear cada AC.
Não marcar `PASS` se não houver evidência correspondente.

### O que foi alterado

Derivar de:

- `06-implementation-summary.md`;
- diff real source vs target;
- plano aprovado.

Se o diff divergir materialmente do summary/plano, registrar a divergência e
bloquear publicação se isso indicar escopo não julgado.

### Testes RED -> GREEN

Usar:

- `05-red-tests.md`;
- `red-tests.lock`;
- `07-green-evidence.md`.

O PR deve deixar explícito que happy path e edge cases aplicáveis foram
considerados. Não inventar cobertura percentual se o projeto não a mede.

### Judge

Registrar apenas o veredito/evidências necessárias. Não expor transcript ou
raciocínio interno do implementador/juiz.

### QA

Apontar collection/guia e limitações reais. Se `.ai/features/` for local-only,
usar caminho/descrição que faça sentido para o processo do time, sem colocar um
link quebrado no PR.

### Commits

Gerar a lista com `git log` real da source branch contra a target/base remota.
Nunca inventar SHA.

### Compatibilidade

Em mudanças cross-repo, incluir contrato, compatibilidade, ordem de deploy e
PRs relacionados quando aplicável.

## Título do PR

Detectar nesta ordem:

1. documentação/política do projeto;
2. padrão de PRs recentes, se a ferramenta do provider permitir consulta;
3. convenção explícita do time/Jira;
4. fallback:

```text
[JIRA-ID] <título curto e objetivo da história>
```

Não colocar prefixos como `feat:` no título do PR se o repositório não usa esse
padrão.

## Source branch e target branch

- `source`: branch Git atual do repositório, salvo se o usuário indicar outra;
- `target/base`: branch solicitada pelo usuário;
- validar a existência da target no remote;
- não abrir PR de uma branch para ela mesma;
- não trocar branch automaticamente para “corrigir” uma solicitação inconsistente.

## Push seguro

Quando a source ainda não estiver publicada ou estiver atrás apenas dos commits
locais esperados:

- push normal é permitido pela solicitação explícita de abertura do PR;
- configurar upstream se necessário;
- nunca usar `--force`/`--force-with-lease` automaticamente;
- se remote rejeitar o push, parar e relatar o motivo;
- não rebasear ou resolver conflitos automaticamente dentro desta skill.

## Working tree

Antes de abrir o PR:

- se houver mudança local não commitada relacionada à feature, bloquear e
  perguntar se o usuário quer voltar ao commit workflow;
- se houver mudança não relacionada, confirmar que ela não faz parte do diff
  remoto do PR e registrar aviso quando relevante;
- o PR é baseado nos commits remotos, não no conteúdo local não commitado.

## Cross-repo

Um PR não atravessa dois repositórios.

Para uma feature cross-repo:

1. criar um PR/MR por repositório;
2. usar a mesma memória canônica da história;
3. validar target branch de cada repo;
4. preencher `PRs relacionados` em todos os documentos/corpos quando possível;
5. registrar `DEPLOY_ORDER` e compatibilidade;
6. se os targets diferirem entre repos e o usuário não os informou, perguntar
   apenas o mapeamento faltante;
7. não marcar a feature como `PR_OPENED_COMPLETE` até todos os PRs obrigatórios
   estarem abertos ou explicitamente delegados.

Estrutura recomendada quando houver vários repos:

```text
.ai/features/<JIRA-ID>/
  delivery/
    pull-request.md       # índice/canônico
    pr/
      <repo-a>.md
      <repo-b>.md
```

## Criação remota

Depois de validar e gerar o documento:

1. preparar título;
2. preparar corpo conforme template do projeto ou fallback;
3. garantir source publicada com push seguro, se necessário;
4. criar PR/MR usando a ferramenta autenticada detectada;
5. capturar número/ID e URL retornados pela ferramenta;
6. atualizar `delivery/pull-request.md` e `STATE.md`;
7. registrar erro real se a criação falhar.

A solicitação explícita `abra o PR para <branch>` já é autorização para estes
passos não destrutivos. Não pedir uma segunda confirmação apenas por ritual.
Perguntar novamente somente diante de ambiguidade ou operação de risco.

## O que esta skill nunca faz

- merge;
- squash/merge;
- aprovação de review;
- adicionar reviewer/assignee/label por adivinhação;
- fechar PR existente;
- deletar branch;
- force push;
- alterar código/teste/documentação funcional para “melhorar o PR”;
- criar commit para incluir arquivo esquecido sem voltar ao commit workflow;
- esconder risco/finding para obter aprovação.

## Estado

Campos mínimos em `STATE.md`:

```text
PR_POLICY: explicit_request_only
PR_STATUS: NOT_REQUESTED | READY | CREATING | OPENED | BLOCKED | EXTERNAL | SKIPPED_BY_USER
PR_SOURCE_BRANCH:
PR_TARGET_BRANCH:
PR_PROVIDER:
PR_NUMBER:
PR_URL:
PR_TEMPLATE_SOURCE: project_native | feature_fallback
PR_OPENED_AT:
RELATED_PRS:
```

Transições:

```text
COMMITTED
  -> PR_READY
  -> PR_CREATING
  -> PR_OPENED
  -> READY_TO_ARCHIVE
```

ou, em bloqueio:

```text
PR_CREATING -> PR_BLOCKED
```

`PR_BLOCKED` não invalida código; apenas registra que a publicação remota não
foi concluída.

## Saída final ao usuário

Quando concluir, informar de forma objetiva:

- Jira;
- repo;
- source -> target;
- título;
- PR/MR número e URL reais;
- template usado;
- status dos gates relevantes;
- PRs relacionados, se cross-repo;
- caminho de `delivery/pull-request.md`;
- qualquer limitação/bloqueio.
