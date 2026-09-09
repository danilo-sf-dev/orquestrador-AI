# PR manual — <JIRA-ID>

> Artefato local para input manual. Nunca representa PR/MR criado remotamente.

## Título

```text
<JIRA-ID> <Título curto e objetivo da história>
```

## Descrição

```markdown
## [<JIRA-ID>](<LINK_JIRA>) - <Título da história>

<Resumo funcional curto>:

- <mudança principal>
- <comportamento/integração relevante>
- <impacto funcional relevante>

<Outro assunto funcional, somente se necessário>:

- <alteração relacionada>
- <comportamento preservado>
- <regra/validação importante>

Testes:

- <teste/validação real>
- <cenário relevante>
- <regressão verificada>

História: [<JIRA-ID>](<LINK_JIRA>)
Relacionadas: [<JIRA-ID>](<LINK_JIRA>)
```

## Regras

- remover seções que não se aplicam;
- `Testes:` somente se houver teste/validação real;
- `Relacionadas:` somente se houver história relacionada real;
- preferir títulos funcionais específicos aos cabeçalhos genéricos;
- não incluir checklist;
- não incluir QA/Judge/commits/branches/provider;
- não incluir bloqueios operacionais;
- não dizer que o PR foi aberto;
- descrição curta, preferencialmente 10–25 linhas;
- conteúdo pronto para copiar/colar manualmente.
