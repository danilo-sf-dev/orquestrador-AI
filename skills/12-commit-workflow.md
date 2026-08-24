---
name: commit-workflow
role: commit_delivery
description: >-
  Fluxo seguro e agnóstico de commit para histórias/bugs da esteira Jira,
  preservando RED lock, GREEN, julgamento independente, escopo por repositório,
  memória da feature e Conventional Commits quando não houver convenção superior.
  Use quando o usuário pedir commit/git commit ou quando uma feature aprovada
  chegar ao checkpoint de commit antes do arquivamento.
preferred_model_role: EXECUTOR
context_loading: lazy
reads:
  - STATE.md
  - 04-implementation-plan.md
  - red-tests.lock
  - 07-green-evidence.md
  - 08-judgement.md
  - 09-qa-tests.md
  - 10-qa-guide.md
  - git_status_diff_stage
  - project_commit_conventions
  - project_build_test_config
writes:
  - delivery/commit.md
  - STATE.md
forbidden_reads:
  - chat_transcript
  - raw_discovery_logs
  - implementation_attempt_history
  - unrelated_feature_artifacts
forbidden_writes:
  - source_code
  - locked_red_tests
  - approved_specs
source_edits: none_by_default
---

# Skill — Commit Workflow da Feature

## Princípio

Commit é **empacotamento e rastreabilidade**, não substituto de qualidade.
Esta skill não corrige implementação, não altera critérios de aceite e não
“faz o commit passar” enfraquecendo testes ou gates.

Ela funciona em Java/Spring Boot, mas não assume Maven, Gradle, Spotless,
Checkstyle ou qualquer comando sem detectar que o projeto realmente os usa.
Em workspace multi-repo, cada repositório Git é tratado separadamente.

## Trigger

Use quando:

- o usuário pedir `commit`, `git commit` ou preparação de commit;
- a esteira chegar ao checkpoint de commit após QA/Judge conforme a política da feature;
- o usuário pedir para preparar stage, mensagem ou validar o que será commitado;
- uma mudança cross-repo precisar de commits coordenados.

Não executar `git commit` silenciosamente. Sempre existe confirmação final.

## Pré-flight obrigatório

Antes de formatar, testar, stagear ou commitar:

1. identificar todos os repositórios Git afetados pela feature;
2. ler `.ai/features/<JIRA-ID>/STATE.md` e, quando existirem:
   - `04-implementation-plan.md`;
   - `red-tests.lock`;
   - `07-green-evidence.md`;
   - `08-judgement.md`;
   - `09-qa-tests.md` / `10-qa-guide.md`;
3. detectar branch atual, `git status`, staged/unstaged e arquivos não rastreados;
4. detectar convenções do repositório antes de inventar comandos ou mensagem;
5. detectar build/test/formatter pelos arquivos reais do projeto;
6. verificar o escopo julgado e a integridade dos testes RED;
7. identificar arquivos sensíveis/proibidos e mudanças não relacionadas;
8. em cross-repo, ler contrato e `DEPLOY_ORDER`/compatibilidade antes de propor ordem dos commits.

### Prioridade para descobrir comandos

Usar, nesta ordem:

1. comandos aprovados em `04-implementation-plan.md` ou documentação canônica do projeto;
2. wrappers/scripts versionados (`mvnw`, `gradlew`, `Makefile`, scripts próprios etc.);
3. `pom.xml`, `build.gradle`, `build.gradle.kts` e configurações existentes;
4. CI (`.github/workflows`, Jenkinsfile, pipeline corporativo) apenas como evidência de comandos realmente usados;
5. convenções detectadas no repositório;
6. perguntar ao usuário quando não houver escolha segura.

Exemplos como `mvn test`, `./mvnw test`, `gradle test` ou `spotlessApply` **não autorizam execução** por si só.

## Passo 1 — Escolha do fluxo

Se o usuário ainda não especificou o tipo de commit, perguntar com estas quatro opções:

| Opção | Comportamento |
|---|---|
| **Commit seguro da feature** | Verifica gates, RED lock, escopo julgado, validações necessárias, stage intencional e commit. Não executa formatter que altere código depois do Judge. |
| **Revalidar e commit** | Permite formatter/auto-fix detectado; se qualquer arquivo julgado mudar, invalida GREEN/Judge e exige revalidação antes do commit. |
| **Commit parcial** | Commit de escopo explícito, por exemplo código+testes, QA/docs/memória ou apenas um repo. Mantém os gates aplicáveis ao escopo. |
| **Outros** | Usuário descreve fluxo personalizado; listar passos/pulos e pedir confirmação antes de executar. |

Pergunta sugerida:

> Qual fluxo de commit deseja executar: Commit seguro da feature, Revalidar e commit, Commit parcial ou Outros?

### Commit seguro da feature

1. não alterar código nem testes;
2. verificar `red-tests.lock` quando `RED_LOCKED=true`;
3. verificar GREEN válido;
4. verificar Judge = `PASS`, ou `PASS_WITH_RISKS` explicitamente aceito;
5. verificar se o escopo atual é o mesmo que foi julgado;
6. verificar QA quando se tratar de commit final completo da feature;
7. rodar apenas validações não mutantes que sejam exigidas e estejam detectadas;
8. revisar `git status`, `git diff`, staged e arquivos não relacionados;
9. stagear somente arquivos pretendidos;
10. preparar mensagem de commit conforme convenção detectada;
11. mostrar plano final e pedir confirmação;
12. executar o commit somente após confirmação.

### Revalidar e commit

1. detectar formatter/auto-fix configurado;
2. informar previamente quais comandos podem modificar arquivos;
3. pedir confirmação antes de qualquer mutação automática;
4. executar somente ferramentas realmente configuradas;
5. se formatter/auto-fix alterar produção, configuração ou testes do escopo julgado:
   - marcar `GREEN_STALE=true`;
   - marcar `JUDGEMENT_STALE=true`;
   - voltar para GREEN e novo Judge;
   - **não commitar antes da nova aprovação técnica**;
6. depois da revalidação, seguir o fluxo seguro.

### Commit parcial

O usuário define explicitamente o escopo. Exemplos:

- `código + testes unitários`;
- `QA collection + guia`;
- `memória da feature`;
- `somente repo A` em uma história cross-repo;
- arquivos específicos.

Regras:

- não misturar mudança não relacionada apenas porque está no working tree;
- código/testes exigem GREEN + Judge aplicáveis;
- QA/docs exigem QA aprovado quando forem o artefato final aprovado;
- memória da feature segue a política de versionamento abaixo;
- se o commit parcial deixar a feature incompleta, registrar isso em `STATE.md`.

### Outros

Antes de executar:

1. converter pedido em passos concretos;
2. listar comandos que serão executados;
3. listar gates/validações que serão pulados;
4. explicar qualquer risco relevante;
5. pedir confirmação;
6. bloquear pedido destrutivo ou ambíguo até esclarecimento.

Nunca executar sem confirmação explícita: `reset --hard`, `clean -f`, remoções em massa, rebase destrutivo, force push ou equivalentes.

## Integridade RED/GREEN

Se `RED_LOCKED=true`:

1. carregar `red-tests.lock`;
2. recalcular os hashes dos testes selados sem alterá-los;
3. se houver divergência não autorizada, retornar `RED_LOCK_VIOLATION`;
4. bloquear commit de implementação até `REOPEN RED` + nova aprovação + novo lock.

A skill de commit **não corrige teste RED**.

## Integridade do julgamento

O Judge deve registrar em `08-judgement.md`:

```text
JUDGEMENT_SCOPE:
- arquivos de produção/configuração julgados
- testes unitários julgados

JUDGEMENT_SCOPE_HASH_METHOD:
JUDGEMENT_SCOPE_HASH:
```

Antes do commit de implementação:

1. recomputar o hash usando o mesmo método;
2. se divergir, marcar `JUDGEMENT_STALE=true`;
3. bloquear commit final da implementação;
4. executar novamente GREEN e Judge em contexto novo.

Mudanças posteriores apenas em QA/docs/memória não invalidam o Judge de código,
desde que não alterem arquivos do `JUDGEMENT_SCOPE`.

## Estado mínimo para cada tipo de commit

| Tipo | Requisito mínimo |
|---|---|
| Implementação/código | RED lock íntegro + GREEN válido + Judge PASS/risco aceito |
| Testes unitários | RED lock íntegro; mudanças pós-lock só via `REOPEN RED` |
| QA final | QA aprovado |
| Docs/memória | conteúdo aprovado/aplicável + política de versionamento |
| Commit final completo | Judge aprovado + QA aprovado + escopo julgado íntegro |

Se o usuário pedir explicitamente um commit intermediário/WIP fora desses gates,
tratar como `Outros`, mostrar o que está incompleto e exigir confirmação explícita.
Nunca declarar a feature pronta por causa desse commit.

## Convenção de commit

### Descoberta

Priorizar:

1. `CONTRIBUTING.md`, README/documentação de engenharia;
2. commitlint/config/hook existente;
3. padrão observável em commits recentes do próprio repositório;
4. regra explícita da feature/time;
5. somente na ausência de convenção, usar o fallback abaixo.

### Fallback — Conventional Commits

```text
<type>(<scope>): <descrição>
```

Tipos permitidos por fallback:

`feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `chore`, `ci`

A descrição é em português por padrão e deve explicar a intenção.
Não usar mensagens vagas como `update`, `fix`, `changes` ou `WIP`.

Jira ID:

- seguir a convenção do repositório se existir;
- se não existir, preferir corpo/footer `Refs: <JIRA-ID>` em vez de inventar formato no subject.

Exemplos de fallback:

```text
feat(orcamento): adicionar validação da API única

Refs: JIRA-1234
```

```text
fix(calculo): evitar duplicidade no processamento da proposta

Refs: JIRA-5678
```

```text
test(orcamento): adicionar casos de borda do cálculo

Refs: JIRA-1234
```

## Atomicidade e escopo

Princípios:

- um commit deve ter uma intenção técnica coerente;
- código e seus testes unitários normalmente pertencem ao mesmo commit quando formam uma mudança atômica;
- não separar somente para produzir “mais commits”;
- não misturar refactor não relacionado com a história;
- QA/docs podem ser commit separado quando isso corresponde ao processo do time;
- não fazer `git add .` cegamente em workspace sujo;
- revisar sempre `git diff --staged` antes da confirmação final.

## Multi-repo / cross-repo

Cada repo recebe commit independente.

Antes de qualquer commit:

1. validar todos os repositórios afetados no fluxo **Commit seguro da feature**;
2. confirmar contrato entre repos;
3. confirmar compatibilidade e ordem indicada em `DEPLOY_ORDER`, quando houver;
4. mostrar a ordem proposta de commits;
5. mostrar arquivos e mensagem de cada repo;
6. pedir confirmação.

Não tentar criar “um commit Git” atravessando repositórios.
Usar o mesmo Jira ID para rastreabilidade, respeitando o padrão de cada repo.

Se um repo não puder ser validado, não fingir atomicidade cross-repo: registrar `CROSS_REPO_COMMIT_BLOCKED` e explicar o impacto.

## Memória da feature no Git

Configuração:

```text
FEATURE_MEMORY_COMMIT_POLICY = ask | include | local_only
```

Default: `ask`.

Descobrir primeiro se `.ai/` já é versionado ou ignorado pelo projeto.
Nunca contrariar `.gitignore`/política do repositório sem autorização.

Se `include`:

- commitar apenas memória técnica útil e estável;
- não commitar transcript de chat;
- não commitar secrets/tokens;
- não commitar logs gigantes;
- remover caminhos locais e metadados irrelevantes de provider/custo quando não agregarem valor futuro;
- em cross-repo, versionar a memória canônica no repo escolhido e apenas `FEATURE-LINK.md` nos demais quando essa for a estratégia aprovada.

Se `local_only`, registrar no `STATE.md` que a memória não viajará com o Git.

## Segurança

Antes da confirmação final, mostrar/verificar:

- repo e branch;
- Jira da feature;
- staged files;
- diff staged;
- untracked relevantes;
- arquivos deliberadamente excluídos;
- ausência de secrets/credenciais evidentes;
- RED lock;
- GREEN/Judge/QA aplicáveis;
- mensagem final;
- política da memória `.ai/`;
- em multi-repo, ordem e commits de todos os repos.

Nunca stagear automaticamente, salvo se a política do projeto disser o contrário:

- `.env*` com credenciais;
- tokens/chaves/certificados privados;
- dumps/logs;
- diretórios de build (`target/`, `build/`) quando não versionados;
- metadata de IDE (`.idea/`, `.vscode/`) quando não versionada pelo projeto;
- arquivos não relacionados à feature.

## Graphify — integração opcional

Somente aplicar se o projeto já possuir Graphify e regras locais para ele.
Esta skill:

- não instala Graphify;
- não executa `extract`/`update` automaticamente;
- não usa `graphify-out/` como memória canônica da feature;
- nunca stageia `graphify-out/` como parte da implementação;
- respeita hooks/guards existentes do projeto.

Se não houver Graphify no projeto, ignorar esta seção sem perguntar.

## Registro `delivery/commit.md`

Registrar apenas fatos:

```text
JIRA:
FLOW:
MEMORY_POLICY:

REPO:
BRANCH:
BASE_SHA:
GATES:
VALIDATIONS:
RED_LOCK_STATUS:
JUDGEMENT_SCOPE_HASH_STATUS:
STAGED_FILES:
EXCLUDED_FILES:
COMMIT_MESSAGE:
COMMIT_SHA:
SKIPPED_VALIDATIONS:
RISKS/NOTES:
```

Para cross-repo, repetir o bloco `REPO` por repositório.
Nunca inventar `COMMIT_SHA`: escrever somente após o commit existir.

## Atualização de estado

Após sucesso:

```text
COMMIT_STATUS=COMMITTED
COMMIT_SHA=<sha>
```

Em multi-repo, registrar um SHA por repo.

Se o commit for delegado externamente:

```text
COMMIT_STATUS=EXTERNAL
```

Se usuário dispensar explicitamente:

```text
COMMIT_STATUS=SKIPPED_BY_USER
```

## Resultado ao usuário

Informar de forma compacta:

- fluxo escolhido;
- repos/branches;
- ferramentas e convenções detectadas;
- gates e validações executados;
- status do RED lock e do julgamento;
- arquivos incluídos/excluídos;
- mensagem(ns) de commit;
- SHA(s), se criados;
- política aplicada à memória `.ai/`;
- validações puladas e motivo;
- pendência que impeça arquivamento.
