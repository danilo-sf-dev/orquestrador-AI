---
name: pull-request-workflow
role: pull_request_description
summary: >-
  Gera somente o título e a descrição final de Pull Request/Merge Request para
  preenchimento manual pelo usuário. Nunca acessa provider remoto, nunca cria PR/MR,
  nunca faz push e nunca tenta autenticar em GitLab/GitHub/Azure/Bitbucket.
preferred_model_role: EXECUTOR
context_loading: lazy
reads:
  - STATE.md
  - 00-jira.md
  - 06-implementation-summary.md
  - 07-green-evidence.md
  - 09-qa-tests.md_if_exists
  - 10-qa-guide.md_if_exists
  - delivery/commit.md_if_exists
  - local_git_diff_or_history_if_needed
writes:
  - delivery/pull-request.md
  - delivery/pr/<repo>.md_if_cross_repo
  - STATE.md
forbidden_reads:
  - chat_transcript
  - raw_discovery_logs
  - implementation_attempt_history
  - unrelated_feature_artifacts
  - remote_provider_state
forbidden_writes:
  - source_code
  - tests
  - approved_specs
  - remote_git_provider
remote_access: forbidden
remote_writes: forbidden
source_edits: none
---

# Skill — Pull Request / Merge Request Description

## 1. Contrato principal

Nesta arquitetura, expressões do usuário como:

```text
abre o PR
abrir PR dessa história
cria o PR
monta o PR
faz o merge request
abre o PR para develop
```

significam **somente**:

```text
GERAR TÍTULO + DESCRIÇÃO FINAL PARA INPUT MANUAL
```

Nunca significam criar/publicar um PR/MR remotamente.

### Regra absoluta

Esta skill **NUNCA**:

- acessa GitLab, GitHub, Azure DevOps, Bitbucket ou outro provider;
- chama API de provider;
- usa `glab`, `gh`, `az repos` ou ferramenta equivalente;
- autentica em provider remoto;
- faz `git push` por causa do PR;
- cria Pull Request/Merge Request remotamente;
- consulta reviewers, labels, pipelines ou número/URL de PR remoto;
- faz merge, squash, rebase, force push ou deleção de branch;
- afirma que o PR/MR foi aberto.

Mesmo se o usuário escrever literalmente `pode abrir o PR`, o comportamento continua sendo **description-only / manual-input**.

Se o usuário quiser alguma ação remota no futuro, isso exigirá outra skill e um contrato explícito separado. Esta skill não possui fallback remoto.

---

## 2. Objetivo

Gerar uma descrição curta, funcional e pronta para copiar/colar manualmente no GitLab/GitHub, baseada somente no contexto real da história.

Prioridades:

1. título e objetivo do Jira;
2. comportamento implementado;
3. impactos funcionais relevantes;
4. comportamento preservado;
5. validações/tratamento de erros importantes;
6. testes/validações realmente executados;
7. histórias relacionadas somente quando existirem no contexto.

Não inventar informação para "completar" o PR.

---

## 3. Pré-condição

A descrição normalmente é gerada depois do commit, mas a skill não depende de acesso remoto.

Antes de gerar:

1. identificar Jira ativo;
2. ler `00-jira.md`;
3. ler o resumo final da implementação;
4. usar GREEN/testes apenas para saber quais validações realmente existem;
5. usar `delivery/commit.md` ou Git local somente se ajudar a confirmar o escopo;
6. em cross-repo, separar a descrição por repositório quando as mudanças forem diferentes.

Não reabrir implementação, RED, Judge ou QA para escrever texto de PR.

---

## 4. Título

Gerar um título curto no estilo:

```text
<JIRA-ID> <Título curto e objetivo da história>
```

Exemplo:

```text
SGJA-75 Estímulo gravação formas de pagamento
```

Regras:

- usar o Jira como prefixo;
- usar o título/objetivo da história como base;
- não adicionar `feat:`, `fix:` ou Conventional Commit salvo se o usuário exigir;
- não inventar WIP, Draft, reviewer ou target branch;
- não incluir status de QA, Judge ou commit.

---

## 5. Descrição — estilo obrigatório

A descrição deve ser **funcional, curta e organizada por assunto**.

Não usar um template corporativo gigante, checklist técnico ou relatório de pipeline.

Estrutura conceitual esperada:

```markdown
## [JIRA-ID](LINK_JIRA) - Título da história

Resumo curto do objetivo da alteração:

- ponto principal da mudança
- comportamento ou integração adicionada
- impacto funcional relevante

Ajustes em outro contexto funcional:

- alteração realizada
- comportamento preservado
- regra ou validação importante

Testes:

- teste ou validação realizada
- cobertura de cenários relevantes
- regressões verificadas

História: [JIRA-ID](LINK_JIRA)
Relacionadas: [JIRA-ID](LINK_JIRA) e [JIRA-ID](LINK_JIRA)
```

A estrutura acima é uma referência de estilo, **não uma obrigação de criar todas as seções**.

### Organização por assunto

Preferir títulos funcionais específicos, como:

```text
Integração da API-Unica com o serviço de Orçamento:
Ajustes no fluxo de formas de pagamento:
Ajustes de validação e tratamento de erros:
Testes:
```

Não usar rótulos genéricos como:

```text
Ajustes da task
Melhorias diversas
Alterações necessárias
Correções gerais
Pontos considerados
```

---

## 6. Regras de conteúdo

1. Gerar somente conteúdo final útil para o PR.
2. Não explicar como a descrição foi criada.
3. Não incluir checklist.
4. Não incluir status de QA.
5. Não incluir status do Judge.
6. Não incluir lista de commits/SHA.
7. Não incluir branch/source/target.
8. Não incluir provider ou ferramenta Git.
9. Não incluir bloqueios operacionais.
10. Não dizer que o PR foi aberto.
11. Não inventar informação fora do contexto fornecido.
12. Usar título e objetivo da história Jira como base.
13. Organizar alterações por assuntos, agrupando itens relacionados.
14. Incluir `Testes:` somente quando houver testes ou validações reais informados.
15. Incluir histórias relacionadas somente quando existirem no contexto.
16. Preservar nomes de classes, serviços, endpoints e componentes quando forem relevantes para entender a mudança.
17. Não repetir o mesmo item em mais de uma seção.
18. Usar Markdown simples.
19. Manter a descrição curta, preferencialmente entre 10 e 25 linhas de conteúdo.
20. Escrever em português, preservando nomes técnicos no idioma original quando necessário.

---

## 7. Link do Jira

Prioridade:

1. usar o link Jira real existente em `00-jira.md`;
2. se houver apenas o ID, usar:

```text
https://portoseguro.atlassian.net/browse/<JIRA-ID>
```

Não inventar outro domínio.

---

## 8. Como interpretar o contexto

Identificar, quando disponíveis:

- Jira e título da história;
- problema/necessidade atendida;
- serviços, APIs ou módulos envolvidos;
- comportamento novo;
- comportamento preservado;
- validações e tratamento de erro;
- alterações de configuração relevantes;
- banco, filas, mocks ou infraestrutura quando realmente fizerem parte da história;
- testes realizados;
- histórias relacionadas;
- subtasks/histórias que originaram parte da implementação, somente quando relevantes para a descrição.

### Não confundir

Não transformar automaticamente:

- subtasks em critérios de aceite;
- detalhes internos de TDD em descrição funcional;
- status operacional em conteúdo do PR;
- findings antigos já resolvidos em "riscos" do PR.

---

## 9. Cross-repo

Quando a história alterar mais de um repositório:

- gerar uma descrição por repositório **se o conteúdo funcional de cada PR for diferente**;
- não misturar arquivos/alterações de outro repo apenas para preencher contexto;
- manter o mesmo Jira;
- mencionar relação entre serviços somente quando ela for relevante para entender aquela mudança.

Persistência recomendada:

```text
.ai/features/<JIRA-ID>/delivery/pull-request.md
.ai/features/<JIRA-ID>/delivery/pr/<repo-a>.md
.ai/features/<JIRA-ID>/delivery/pr/<repo-b>.md
```

`delivery/pull-request.md` pode funcionar como índice quando houver múltiplos repos.

---

## 10. Saída para o usuário

Entregar somente o necessário para preenchimento manual:

```text
TÍTULO
<titulo final>

DESCRIÇÃO
<markdown final>
```

Não adicionar instruções sobre GitLab/GitHub, push ou comandos.

Após gerar:

```yaml
PR_STATUS: DESCRIPTION_READY
NEXT_ACTION: MANUAL_PR_INPUT
```

O usuário é responsável por abrir/preencher o PR/MR no provider.

A skill nunca muda o status para `OPENED`, pois não acessa o provider remoto.
