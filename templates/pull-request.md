# Pull Request — <JIRA-ID> <Título>

> Template canônico interno da feature. Sempre criar este arquivo em
> `.ai/features/<JIRA-ID>/delivery/pull-request.md` quando o usuário solicitar abertura de PR.
> Se o repositório possuir template nativo de PR/MR, respeitar o template do projeto
> na publicação remota e usar este documento como fonte de verdade para preenchê-lo.

## Resumo

<!-- Objetivo do PR em 2–4 linhas, derivado do Jira/PRD e do resultado implementado. -->

## Contexto da feature

| Campo | Valor |
|---|---|
| Jira | <JIRA-ID ou link> |
| Feature | <título> |
| Repositório | <repo> |
| Source branch | <branch atual> |
| Target/Base branch | <branch solicitada pelo usuário> |
| Provider | <GitHub/GitLab/Azure DevOps/Bitbucket/outro> |
| PR/MR | <número e URL após criação> |

## Critérios de aceite

| AC | Status | Evidência principal |
|---|---|---|
| AC1 | PASS / RISK / BLOCKED | |

## O que foi alterado

<!-- Lista objetiva derivada do implementation summary + diff real. -->

-
-
-

## Testes unitários — RED → GREEN

- [ ] `red-tests.lock` íntegro
- [ ] Happy path relevante coberto
- [ ] Edge cases aplicáveis cobertos ou justificados
- [ ] Testes RED aprovados ficaram GREEN sem alteração indevida
- [ ] Testes relevantes executados com sucesso

### Cobertura dos critérios

<!-- Relacionar AC -> teste(s), sem inventar cobertura. -->

## Validação independente

- Judge: PASS | PASS_WITH_RISKS | FAIL | BLOCKED
- Judgement scope hash válido: yes | no
- Riscos aceitos:
- Findings pendentes:

## Validações técnicas

- [ ] Build/compilação relevante executado com sucesso
- [ ] Validações configuradas no projeto executadas quando aplicável
- [ ] Sem secrets/credenciais no diff
- [ ] Sem mudanças não relacionadas no escopo do PR

### Evidências

<!-- Saídas curtas, CI, comandos, links ou limitações. -->

## QA

- [ ] QA Pack aprovado
- Collection: <caminho/link>
- Guia QA: <caminho/link>
- Cenários/limitações relevantes:

## Commits

<!-- Preencher com git log source vs target/base. -->

- `<sha>` <mensagem>

## Compatibilidade e entrega

- Breaking change: yes | no
- Contratos afetados:
- Dependências cross-repo:
- Ordem de deploy, quando aplicável:
- Rollback/mitigação, quando aplicável:

## PRs relacionados — cross-repo

<!-- Preencher somente quando a história envolver mais de um repositório. -->

| Repo | PR/MR | Target | Status |
|---|---|---|---|
| | | | |

## Checklist final

- [ ] Escopo está alinhado ao Jira e ao PRD aprovado
- [ ] Critérios de aceite estão rastreáveis para código/testes/QA
- [ ] Não há mudança pós-Judge que invalide o julgamento
- [ ] Documentação foi atualizada quando aplicável
- [ ] Compatibilidade/risco relevante está documentado
- [ ] Branch remota contém os commits pretendidos
- [ ] Nenhum force push foi necessário para abrir o PR

## Observações para review

<!-- Riscos, limitações, pontos de atenção, decisões importantes e follow-ups. -->
