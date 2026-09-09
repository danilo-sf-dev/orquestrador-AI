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

Não executar `git commit` silenciosamente. Ao solicitar commit, o usuário deve escolher
explicitamente um modo de execução: **AUTOMÁTICO**, **MANUAL** ou **OUTROS**.

- `AUTOMÁTICO`: a própria escolha autoriza a skill a analisar, fasear, stagear, validar e
  executar todos os commits do plano sem nova confirmação humana entre os grupos. O
  faseamento semântico continua obrigatório e somente a mensagem em inglês pode ser
  gravada no repositório. Ao final, apresentar resumo completo do que foi commitado.
- `MANUAL`: a skill analisa e apresenta o plano faseado completo antes de qualquer
  mutação Git. Depois do plano, deve sempre oferecer `POSSO COMITAR`, `PRECISA AJUSTAR`
  e `OUTROS`. Somente `POSSO COMITAR` autoriza executar exatamente o plano apresentado.
- `OUTROS`: o usuário descreve como deseja prosseguir. Nunca interpretar `OUTROS` como
  autorização implícita para commitar.

Qualquer mudança material no agrupamento, arquivos, mensagens, ordem ou escopo após um
plano congelado/autorizado invalida a autorização anterior e exige novo plano/decisão do usuário.

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
4. executar a proteção obrigatória de `.ai/`: confirmar ignore efetivo e ausência de `.ai/**` tracked/staged;
5. detectar convenções do repositório antes de inventar comandos ou mensagem;
6. detectar build/test/formatter pelos arquivos reais do projeto;
7. verificar o escopo julgado e a integridade dos testes RED;
8. identificar arquivos sensíveis/proibidos e mudanças não relacionadas;
9. em cross-repo, ler contrato e `DEPLOY_ORDER`/compatibilidade antes de propor ordem dos commits.

### Prioridade para descobrir comandos

Usar, nesta ordem:

1. comandos aprovados em `04-implementation-plan.md` ou documentação canônica do projeto;
2. wrappers/scripts versionados (`mvnw`, `gradlew`, `Makefile`, scripts próprios etc.);
3. `pom.xml`, `build.gradle`, `build.gradle.kts` e configurações existentes;
4. CI (`.github/workflows`, Jenkinsfile, pipeline corporativo) apenas como evidência de comandos realmente usados;
5. convenções detectadas no repositório;
6. perguntar ao usuário quando não houver escolha segura.

Exemplos como `mvn test`, `./mvnw test`, `gradle test` ou `spotlessApply` **não autorizam execução** por si só.

## Passo 0 — Planejamento semântico de commits

Antes de `git add` ou de propor mensagem, analisar o diff completo de cada repositório
afetado e decidir **quantas unidades lógicas de commit realmente existem**.

O objetivo não é produzir vários commits por obrigação. O objetivo é evitar um único
commit grande quando o diff contém mudanças independentes. Se todo o diff representar
uma única intenção coerente, **um único commit é a saída correta**.

### Regra de agrupamento

Agrupar arquivos pela **razão da mudança**, não por pasta, extensão ou categoria técnica.

Pergunta principal:

> Estes arquivos estão mudando pelo mesmo motivo e formam uma unidade que faz sentido
> revisar e reverter em conjunto?

Critérios para colocar arquivos no mesmo commit:

1. mesma intenção funcional/técnica;
2. mesma responsabilidade dentro da alteração;
3. mesma causa/motivo de mudança;
4. fazem sentido como unidade de revisão;
5. podem ser revertidos juntos sem misturar outra intenção independente.

Portanto, **não aplicar regras artificiais** como:

```text
src/    -> feat
tests/  -> test
config/ -> chore
```

Código, testes, configuração e documentação podem pertencer ao mesmo commit quando
são partes inseparáveis da mesma mudança. Da mesma forma, testes só devem virar um
commit `test:` separado quando representarem uma intenção independente, e não apenas
por estarem em uma pasta de testes.

### Quando separar

Separar em commits distintos quando houver intenções independentes, por exemplo:

- feature principal + refactor oportunista não necessário para a feature;
- correção funcional + limpeza técnica independente;
- alteração de build/tooling sem relação direta com o comportamento entregue;
- documentação autônoma;
- dois comportamentos diferentes que possam ser revisados/revertidos separadamente;
- mudanças independentes em um mesmo repositório presentes no working tree.

### Commit Plan obrigatório

Todo modo usa o mesmo motor de análise e deve construir um `COMMIT PLAN` faseado antes
de qualquer `git commit`. No modo `MANUAL`, o plano deve ser apresentado ao usuário
antes de qualquer mutação Git. No modo `AUTOMÁTICO`, o plano pode ser congelado
internamente e executado sem uma segunda aprovação, mas deve aparecer integralmente no
resumo final junto com o resultado real.

Formato mínimo:

```text
COMMIT PLAN — <JIRA>

────────────────────────────────
COMMIT 1
────────────────────────────────
Tipo: feat
Intenção: <por que este grupo existe>

Arquivos:
- A
- B
- C

PT-BR:
feat(...): <descrição em português>

EN — COPY:
feat(...): <description in English>

────────────────────────────────
COMMIT 2
────────────────────────────────
Tipo: chore
Intenção: <outra mudança independente>

Arquivos:
- X
- Y

PT-BR:
chore(...): <descrição em português>

EN — COPY:
chore(...): <description in English>

Ordem: 1 -> 2
Arquivos excluídos/não relacionados:
- ...
```

`MESSAGE_PTBR` existe para entendimento/revisão do usuário. `MESSAGE_EN` é a versão
executável e é a **única** mensagem permitida em `git commit` realizado pela skill.

Para cada grupo, validar:

```text
SAME_INTENT=true
REVIEWABLE_UNIT=true
REVERTABLE_UNIT=true
UNRELATED_CHANGES=false
```

Se algum critério não puder ser sustentado, reorganizar o grupo antes de congelar/apresentar o plano.

### Autorização e execução do plano

#### Modo `AUTOMÁTICO`

A escolha explícita de `AUTOMÁTICO` autoriza a execução do plano faseado após as
validações obrigatórias. Não pedir uma segunda aprovação do plano nem confirmação entre
commits, desde que o plano não mude.

Para cada grupo:

1. stagear somente os arquivos do grupo atual;
2. revisar `git diff --staged`;
3. repetir a proteção obrigatória de `.ai/`;
4. validar secrets/arquivos proibidos;
5. confirmar que o staged corresponde exatamente ao grupo planejado;
6. executar `git commit` usando **somente `MESSAGE_EN`**;
7. registrar o SHA real;
8. limpar/validar o stage;
9. avançar para o próximo grupo.

Ao final, apresentar `COMMIT RESULT` com cada grupo, intenção, arquivos,
`MESSAGE_PTBR`, `MESSAGE_EN — COMMITTED` e SHA.

#### Modo `MANUAL`

Depois de apresentar o plano final, **parar** e sempre oferecer:

```text
1. POSSO COMITAR
   Executa exatamente o plano apresentado.

2. PRECISA AJUSTAR
   Mantém a execução bloqueada e recebe as alterações solicitadas pelo usuário.

3. OUTROS
   O usuário informa como deseja prosseguir, inclusive não commitar agora.
```

Regras:

- `POSSO COMITAR`: congelar o plano como `APPROVED` e executar os grupos exatamente
  como apresentados, usando somente `MESSAGE_EN` no Git;
- `PRECISA AJUSTAR`: não executar nenhuma mutação Git; aplicar a solicitação, gerar
  novo plano e reapresentar as três opções;
- `OUTROS`: interpretar literalmente a instrução. Exemplos válidos: adiar o commit,
  usuário executar externamente, commitar apenas parte do plano ou encerrar a etapa.
  Se houver qualquer mutação Git pedida de forma ambígua, pedir confirmação específica;
- `não vou commitar agora`/equivalente: registrar `COMMIT_STATUS=DEFERRED` e não alterar
  stage/repositório;
- `vou commitar manualmente`/equivalente: registrar `COMMIT_STATUS=EXTERNAL` e não
  alterar stage/repositório.

#### Mudança material durante execução

Em qualquer modo, **parar** se:

- um arquivo mudar de grupo;
- surgir arquivo novo relevante;
- a mensagem precisar mudar materialmente;
- a ordem dos commits mudar;
- um commit precisar ser dividido ou fundido;
- o diff atual divergir do plano congelado;
- qualquer gate/integridade deixar de ser válido.

No `AUTOMÁTICO`, a autorização automática termina nesse ponto e o usuário deve decidir
como prosseguir. No `MANUAL`, gerar novo plano e voltar para `POSSO COMITAR`,
`PRECISA AJUSTAR` ou `OUTROS`.

## Passo 1 — Escolha do modo de execução

Ao usuário solicitar commit e ainda não existir `COMMIT_MODE` definido para a etapa,
apresentar **sempre**:

| Opção | Comportamento |
|---|---|
| **AUTOMÁTICO** | Analisa o diff, cria o plano semântico faseado, stageia/valida grupo por grupo, executa todos os commits automaticamente em inglês e entrega o resumo final com SHAs. |
| **MANUAL** | Analisa o diff e apresenta o plano faseado PT-BR + EN. Depois pergunta `POSSO COMITAR`, `PRECISA AJUSTAR` ou `OUTROS`. |
| **OUTROS** | O usuário descreve o comportamento desejado. Pode inclusive não commitar agora. Nunca implica autorização automática. |

Pergunta sugerida:

> Como deseja trabalhar com os commits: **AUTOMÁTICO**, **MANUAL** ou **OUTROS**?

Persistir a escolha:

```text
COMMIT_MODE=AUTO | MANUAL | OTHER
```

A escolha de modo controla **quem autoriza a execução**, mas não muda a regra de
faseamento: em `AUTO` e `MANUAL`, o agrupamento continua sendo semântico e obrigatório.

## Passo 2 — Política técnica do commit

A política técnica é ortogonal ao modo de execução. Se o usuário não pedir uma variação
específica e o contexto indicar entrega final normal da feature, usar **Commit seguro da
feature**. Só perguntar por política técnica quando houver ambiguidade real ou quando o
usuário pedir revalidação, commit parcial/WIP ou comportamento personalizado.

| Política | Comportamento |
|---|---|
| **Commit seguro da feature** | Verifica gates, RED lock, escopo julgado e validações não mutantes antes de stage/commit. |
| **Revalidar e commit** | Permite formatter/auto-fix detectado; qualquer mudança em escopo julgado invalida GREEN/Judge e exige revalidação. |
| **Commit parcial** | Trabalha apenas no escopo explícito (arquivos, artefatos ou repo), preservando os gates aplicáveis. |
| **Outros** | Usuário define política técnica personalizada; listar passos/pulos e riscos antes de executar. |

### Commit seguro da feature

1. não alterar código nem testes;
2. verificar `red-tests.lock` quando `RED_LOCKED=true`;
3. verificar GREEN válido;
4. verificar Judge = `PASS`, ou `PASS_WITH_RISKS` explicitamente aceito;
5. verificar se o escopo atual é o mesmo que foi julgado;
6. verificar QA quando se tratar de commit final completo da feature;
7. rodar apenas validações não mutantes que sejam exigidas e estejam detectadas;
8. revisar `git status`, `git diff`, staged e arquivos não relacionados;
9. preparar o `COMMIT PLAN` faseado com `MESSAGE_PTBR` + `MESSAGE_EN`;
10. seguir o modo escolhido: `AUTO` executa após as validações; `MANUAL` apresenta o
    plano e aguarda `POSSO COMITAR`, `PRECISA AJUSTAR` ou `OUTROS`; `OTHER` segue a
    instrução explícita do usuário sem presumir autorização.

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

Para cada grupo, gerar obrigatoriamente duas mensagens semanticamente equivalentes:

```text
MESSAGE_PTBR=<mensagem para entendimento/revisão do usuário>
MESSAGE_EN=<mensagem final executável>
```

Regras:

- `MESSAGE_PTBR` deve explicar a intenção em português;
- `MESSAGE_EN` deve explicar a mesma intenção em inglês natural e técnico;
- o `type` e o `scope` seguem a convenção do projeto e não precisam ser traduzidos;
- **todo `git commit` executado pela skill usa exclusivamente `MESSAGE_EN`**;
- nunca commitar a versão PT-BR por engano;
- não usar mensagens vagas como `update`, `fix`, `changes` ou `WIP`.

Jira ID:

- seguir a convenção do repositório se existir;
- se não existir, preferir corpo/footer `Refs: <JIRA-ID>` em vez de inventar formato no subject.

Exemplos de fallback:

```text
PT-BR:
feat(orcamento): adicionar validação da API única

EN — COPY/COMMIT:
feat(orcamento): add API única validation

Refs: JIRA-1234
```

```text
PT-BR:
fix(calculo): evitar duplicidade no processamento da proposta

EN — COPY/COMMIT:
fix(calculo): prevent duplicate proposal processing

Refs: JIRA-5678
```

```text
PT-BR:
test(orcamento): adicionar casos de borda do cálculo

EN — COPY/COMMIT:
test(orcamento): add calculation edge cases

Refs: JIRA-1234
```

## Atomicidade e escopo

A atomicidade é **semântica**, não baseada em tipo de arquivo.

Princípios:

- um commit representa uma intenção coerente;
- agrupar por motivo da mudança, não por `src/`, `test/`, extensão ou linguagem;
- código + teste + configuração podem ficar juntos quando são uma única unidade funcional;
- teste separado só quando tiver intenção própria;
- não separar apenas para produzir “mais commits”;
- não juntar tudo apenas porque pertence ao mesmo Jira;
- refactor/cleanup incidental e independente tende a ter commit próprio;
- cada commit deve ser revisável e reversível como unidade razoável;
- quando todas as mudanças possuem uma única intenção, um único commit é válido e preferível;
- não fazer `git add .` cegamente em workspace sujo;
- revisar `git diff --staged` antes **de cada commit** da sequência congelada/autorizada;
- repetir a proteção de `.ai/` imediatamente antes **de cada `git commit`**.

A ordem deve respeitar dependências entre unidades lógicas e, sempre que razoável,
manter o repositório em estado consistente a cada commit. Não criar separações que
produzam commits intermediários artificialmente quebrados apenas para satisfazer uma
classificação `feat/test/chore`.

## Multi-repo / cross-repo

Cada repo recebe commit independente.

Antes de qualquer commit:

1. validar todos os repositórios afetados no fluxo **Commit seguro da feature**;
2. confirmar contrato entre repos;
3. confirmar compatibilidade e ordem indicada em `DEPLOY_ORDER`, quando houver;
4. incorporar a ordem proposta, arquivos e mensagens de cada repo no `COMMIT PLAN`;
5. no `MANUAL`, apresentar o plano cross-repo antes de qualquer mutação;
6. no `AUTO`, executar a ordem congelada após as validações sem confirmação adicional;
7. em `OTHER`, seguir apenas a instrução explícita do usuário.

Não tentar criar “um commit Git” atravessando repositórios.
Usar o mesmo Jira ID para rastreabilidade, respeitando o padrão de cada repo.

Se um repo não puder ser validado, não fingir atomicidade cross-repo: registrar `CROSS_REPO_COMMIT_BLOCKED` e explicar o impacto.

## Memória `.ai/` — proteção absoluta

A pasta `.ai/` é memória local do orquestrador e **nunca pode entrar em commit, push ou PR**.

Não existe configuração `ask`, `include` ou exceção por feature. A política é fixa:

```text
AI_MEMORY_POLICY = LOCAL_ONLY
.ai/ NEVER_COMMIT
.ai/ NEVER_STAGE
.ai/ NEVER_PUSH
```

Antes de preparar qualquer commit, em **cada repositório afetado**:

1. verificar que o `.gitignore` possui regra efetiva para `.ai/`;
2. validar com Git que um caminho sob `.ai/` está realmente ignorado;
3. verificar se existe qualquer arquivo `.ai/**` tracked ou staged;
4. se houver `.ai/**` staged, removê-lo do stage sem apagar o arquivo local;
5. se houver `.ai/**` tracked, bloquear o commit e informar que a proteção precisa ser corrigida antes de continuar;
6. repetir a validação imediatamente antes do `git commit`.

Se `.ai/` não estiver ignorada, adicionar `.ai/` ao `.gitignore` antes de continuar.

Essa proteção é obrigatória mesmo que a feature já exista ou tenha sido retomada por `RESUME`.

## Segurança

Antes de qualquer execução Git mutante, mostrar/verificar no `MANUAL` e verificar
internamente no `AUTO`:

- repo e branch;
- Jira da feature;
- staged files;
- diff staged;
- untracked relevantes;
- arquivos deliberadamente excluídos;
- ausência de secrets/credenciais evidentes;
- `.ai/` efetivamente ignorada e sem qualquer arquivo tracked/staged;
- RED lock;
- GREEN/Judge/QA aplicáveis;
- mensagem final;
- política da memória `.ai/`;
- em multi-repo, ordem e commits de todos os repos.

Nunca incluir automaticamente no stage os itens abaixo. Convenção explícita do projeto
pode justificar exceção apenas para itens não sensíveis; `.ai/`, credenciais e secrets
continuam proibidos:

- `.env*` com credenciais;
- tokens/chaves/certificados privados;
- dumps/logs;
- diretórios de build (`target/`, `build/`) quando não versionados;
- `.ai/` e qualquer arquivo sob `.ai/**` — proibição absoluta;
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
COMMIT_MODE: AUTO | MANUAL | OTHER
MEMORY_POLICY:

REPO:
BRANCH:
BASE_SHA:
GATES:
VALIDATIONS:
RED_LOCK_STATUS:
JUDGEMENT_SCOPE_HASH_STATUS:
COMMIT_PLAN_STATUS: PROPOSED | APPROVED | EXECUTED | DEFERRED | EXTERNAL | SKIPPED
COMMIT_GROUPS:
  - ORDER:
    TYPE:
    INTENT:
    FILES:
    MESSAGE_PTBR:
    MESSAGE_EN:
    EXECUTION_STATUS: PLANNED | COMMITTED | NOT_EXECUTED
    SHA:
EXCLUDED_FILES:
SKIPPED_VALIDATIONS:
RISKS/NOTES:
```

Registrar cada commit lógico separadamente. Para cross-repo, repetir o bloco `REPO`
por repositório. Nunca inventar `SHA`: escrever somente após o commit existir.

## Atualização de estado

Ao entrar na etapa:

```text
COMMIT_MODE=AUTO | MANUAL | OTHER
COMMIT_PLAN_STATUS=PENDING | PROPOSED | APPROVED | EXECUTED | DEFERRED | EXTERNAL | SKIPPED
```

Após execução bem-sucedida pela skill:

```text
COMMIT_PLAN_STATUS=EXECUTED
COMMIT_STATUS=COMMITTED
COMMIT_COUNT=<n>
COMMIT_SHAS=<sha1,sha2,...>
```

Se houver um único commit, `COMMIT_COUNT=1`. Em multi-repo, registrar a sequência de
SHAs por repositório.

Se o usuário decidir não commitar agora:

```text
COMMIT_PLAN_STATUS=DEFERRED
COMMIT_STATUS=DEFERRED
```

`DEFERRED` preserva o plano, mas **não satisfaz** a pré-condição de arquivamento.

Se o commit for delegado ao usuário/fluxo externo:

```text
COMMIT_PLAN_STATUS=EXTERNAL
COMMIT_STATUS=EXTERNAL
```

Se usuário dispensar explicitamente o commit:

```text
COMMIT_PLAN_STATUS=SKIPPED
COMMIT_STATUS=SKIPPED_BY_USER
```

## Resultado ao usuário

### Quando ainda não houve execução (`MANUAL`)

Mostrar o `COMMIT PLAN` completo e terminar sempre com:

```text
Como deseja continuar?
1. POSSO COMITAR
2. PRECISA AJUSTAR
3. OUTROS
```

### Após execução (`AUTO` ou `MANUAL` autorizado)

Mostrar `COMMIT RESULT — <JIRA>` com um bloco por commit efetivamente criado:

```text
────────────────────────────────
COMMIT <N> — COMMITTED
────────────────────────────────
Tipo: <type>
Intenção: <razão do agrupamento>

Arquivos:
- ...

PT-BR:
<MESSAGE_PTBR>

EN — COMMITTED:
<MESSAGE_EN>

SHA:
<sha real>
```

Além disso, informar de forma compacta:

- modo e política técnica escolhidos;
- repos/branches;
- ferramentas e convenções detectadas;
- gates e validações executados;
- status do RED lock e do julgamento;
- arquivos incluídos/excluídos;
- critério de agrupamento semântico;
- política aplicada à memória `.ai/`;
- validações puladas e motivo;
- pendência que impeça arquivamento.
