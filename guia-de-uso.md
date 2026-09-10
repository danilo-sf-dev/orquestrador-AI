# Guia de uso diário do Orquestrador

Este guia responde duas perguntas:

1. quando iniciar o fluxo completo referenciando `orquestrador.md`;
2. quando referenciar diretamente uma skill para análise, plano, diagnóstico ou arquitetura.

## Regra principal

Referencie `orquestrador.md` quando o trabalho deve virar **mudança controlada e entregável**: código,
testes, QA, commit, descrição de PR ou memória retomável por Jira.

Referencie a skill correspondente e descreva o pedido em linguagem natural quando deseja somente
**entender, investigar, planejar, comparar ou revisar**, sem executar a mudança e sem entrar na
esteira.

```text
Quero apenas conhecimento/decisão, sem alterar arquivos?
-> referenciar a skill apropriada em modo consultivo

Quero implementar e entregar uma mudança rastreada?
-> referenciar orquestrador.md
```

## Como invocar no VS Code/Cursor

Os arquivos deste projeto não aparecem automaticamente como comandos no chat. Informe o caminho do
arquivo que contém o comportamento desejado.

A entrada do fluxo completo é:

```text
Leia e siga:
"E:\Program Cursor\orquestrador\orquestrador\orquestrador.md"

Quero iniciar uma nova entrega.
Jira: <ID ou URL>
Fluxo: QUICK | COMUM
```

Para uma operação isolada, referencie a skill específica:

```text
Use como referência metodológica:
"E:\Program Cursor\orquestrador\orquestrador\skills\<skill>.md"

<descreva o objetivo, escopo, limites e saída esperada>
```

Use `Leia e siga` quando deseja executar a skill conforme seu contrato. Use `como referência
metodológica` quando quer somente aproveitar o método, sem criar `.ai/`, aplicar gates ou alterar
arquivos.

## Árvore de decisão rápida

```text
1. Você quer alterar código/configuração/testes?
   NÃO -> faça um pedido consultivo direto.
   SIM -> continue.

2. A mudança precisa de Jira, memória, gates, QA, commit ou PR?
   SIM -> referencie orquestrador.md.
   NÃO -> referencie a skill adequada e limite explicitamente o escopo.

3. O comportamento é claro, localizado, reversível e de baixo risco?
   SIM -> ao iniciar orquestrador.md, escolha QUICK.
   NÃO ou NÃO SEI -> escolha COMUM.
```

Na dúvida entre `QUICK` e `COMUM`, escolha `COMUM`. O custo adicional é menor que o rework de uma
mudança subestimada.

## Quando referenciar `orquestrador.md`

Use quando existir pelo menos uma destas necessidades:

- implementar uma história ou bug do Jira;
- alterar código com testes RED/GREEN;
- preservar decisões e permitir `RESUME` em outra sessão;
- coordenar mais de um repositório;
- alterar contrato, persistência, mensageria ou integração;
- produzir QA, commit ou descrição de PR;
- exigir Judge independente;
- tratar dívida técnica que será implementada e entregue.

Fluxo de entrada:

```text
Leia e siga:
"E:\Program Cursor\orquestrador\orquestrador\orquestrador.md"

Quero iniciar ou retomar uma entrega.
Jira: <ID ou URL>
Fluxo: QUICK | COMUM
```

Não é necessário pedir manualmente `investigação`, `plano`, `arquitetura` ou `Judge`. O estado da
feature decide qual skill será carregada.

## Quando referenciar uma skill diretamente

Não é necessário iniciar a esteira para:

- entender um trecho de código;
- investigar um bug sem corrigir;
- mapear arquitetura existente;
- comparar opções técnicas;
- avaliar qualidade arquitetural, débito técnico ou necessidade real de Design Pattern;
- produzir um plano preliminar;
- revisar um diff sem alterar arquivos;
- estimar impacto de uma ideia;
- explicar uma tecnologia;
- localizar onde determinada regra está implementada.

Nesses casos, informe o caminho da skill adequada e declare a fronteira, por exemplo: `somente
leitura`, `não implemente`, `não crie memória da feature` ou `entregue apenas o plano`.

## Cenários do dia a dia

### 1. Investigar um bug sem corrigir

```text
Use como referência metodológica:
"E:\Program Cursor\orquestrador\orquestrador\skills\03-investigacao.md"

Investigue este bug em modo somente leitura. Levante hipóteses, elimine-as com evidências e apresente
a causa raiz, o impacto e uma proposta de correção. Não altere arquivos.
```

Resultado esperado: diagnóstico consultivo, sem `.ai/`, RED, implementação ou commit.

### 2. Corrigir e entregar um bug

```text
Leia e siga:
"E:\Program Cursor\orquestrador\orquestrador\orquestrador.md"

Quero corrigir o bug <JIRA-ID>.
Fluxo: QUICK | COMUM
```

Depois:

- `QUICK`: bug localizado, comportamento claro, baixo risco e sem mudança de contrato;
- `COMUM`: causa incerta, produção, persistência, integração, segurança, concorrência, cross-repo ou
  risco relevante.

O fluxo executará discovery, solução, plano, RED, implementação, GREEN e Judge conforme necessário.

### 3. Criar somente um plano

```text
Use como referência metodológica:
"E:\Program Cursor\orquestrador\orquestrador\skills\06-prd-plano.md"

Analise esta demanda e crie somente um plano de implementação. Inclua dependências, arquivos
confirmados/esperados, riscos, critérios ligados a cada unidade e estratégia de testes. Não execute.
```

Se o plano será aprovado e implementado como uma entrega Jira, referencie `orquestrador.md`, porque
ele preservará solução, plano, gates e retomada.

### 4. Mapear a arquitetura existente

```text
Use como referências metodológicas:
"E:\Program Cursor\orquestrador\orquestrador\skills\03-investigacao.md"
"E:\Program Cursor\orquestrador\orquestrador\skills\05-solucao-proposta.md"

Mapeie a arquitetura deste repositório em modo somente leitura. Mostre componentes, dependências,
contratos, fluxo de dados e padrões comprovados, citando arquivos e símbolos. Diferencie fato,
inferência e desconhecido. Não proponha reescrita ainda.
```

Mapeamento é descoberta da arquitetura atual. Decidir uma nova arquitetura para uma feature que será
implementada é trabalho do fluxo `COMUM` iniciado por `orquestrador.md`.

### 5. Comparar alternativas de arquitetura

```text
Use como referência metodológica:
"E:\Program Cursor\orquestrador\orquestrador\skills\05-solucao-proposta.md"

Compare as alternativas A e B para este contexto. Avalie aderência aos padrões existentes,
complexidade, manutenção, segurança, desempenho, reversibilidade e riscos. Recomende uma opção, sem
implementar.
```

Se a decisão fizer parte de uma entrega, referencie `orquestrador.md`; a decisão será registrada como
`DD-*` na solução aprovada e ligada ao plano.

### 6. Dívida técnica

- Apenas inventariar/priorizar dívida: referenciar `03-investigacao.md`, somente leitura.
- Corrigir dívida localizada com Jira e baixo risco: referenciar `orquestrador.md` e escolher `QUICK`.
- Refactor amplo, dependências, contrato ou arquitetura: referenciar `orquestrador.md` e escolher `COMUM`.

Exemplo consultivo:

```text
Use como referência metodológica:
"E:\Program Cursor\orquestrador\orquestrador\skills\03-investigacao.md"

Identifique dívidas técnicas neste módulo, com evidência, impacto, risco e prioridade. Não altere o
código e não transforme preferência estética em dívida.
```

### 7. Avaliar qualidade, arquitetura ou Design Patterns

Para uma análise consultiva, use a skill opcional:

```text
Use como referência metodológica:
"E:\Program Cursor\orquestrador\orquestrador\skills\18-qualidade-arquitetural.md"

Avalie este módulo para identificar problemas consistentes de manutenção, legibilidade, acoplamento,
testabilidade ou desempenho. Primeiro identifique e respeite os padrões válidos já adotados pelo
projeto. Recomende um Design Pattern ou mudança arquitetural somente se houver evidência concreta de
que a solução mais simples não resolve. Não altere arquivos.
```

No fluxo completo, mencione a necessidade na solicitação ao `orquestrador.md`. A revisão é acionada
somente se houver pedido explícito ou evidência de problema estrutural; ela pode concluir que nenhuma
mudança arquitetural é necessária. Melhoria estrutural não é compatível com `QUICK`; use `COMUM`.

### 8. Revisar código ou diff

Para revisão isolada sem fluxo:

```text
Use como referência metodológica:
"E:\Program Cursor\orquestrador\orquestrador\skills\10-juiz.md"

Revise este diff em modo somente leitura. Aponte apenas findings com evidência e impacto concreto,
classificados por severidade. Não edite arquivos.
```

Não invoque manualmente o Judge para uma feature fora da esteira. O Judge depende dos artefatos
aprovados, RED lock e GREEN evidence. Dentro do fluxo, `orquestrador.md` fará o handoff automaticamente.

### 9. Retomar trabalho existente

```text
Leia e siga:
"E:\Program Cursor\orquestrador\orquestrador\orquestrador.md"

Retome a feature <JIRA-ID> a partir do STATE.md e execute somente NEXT_ACTION.
```

Informe o Jira se houver mais de uma feature ativa. O orquestrador lê `STATE.md` e continua da
`NEXT_ACTION`; não repita discovery ou planejamento já aprovados sem um motivo explícito.

## QUICK ou COMUM

| Sinal | QUICK | COMUM |
|---|---:|---:|
| Mudança localizada e conhecida | Sim | Sim |
| Comportamento completamente claro | Sim | Sim |
| Baixo risco e fácil reversão | Sim | Sim |
| Causa do bug incerta | Não | Sim |
| Mudança de API/contrato | Não | Sim |
| Persistência/migração | Não | Sim |
| Concorrência/transação | Não | Sim |
| Segurança/permissão/dados sensíveis | Não | Sim |
| Cross-repo ou ordem de deploy | Não | Sim |
| Bug de produção relevante | Não | Sim |
| Decisão arquitetural nova | Não | Sim |

`QUICK` reduz interações, não qualidade. RED, GREEN e Judge continuam existindo. Se surgir ambiguidade
ou risco incompatível, o fluxo QUICK deve abortar e migrar para o fluxo comum.

## O que significa modelo forte, executor ou econômico

Não existe simplesmente "modelo bom" e "modelo ruim". Existem responsabilidades diferentes.

### `ECONOMICAL`

Indicado para trabalho predominantemente mecânico ou de leitura dirigida:

- acessar e resumir Jira;
- localizar arquivos e símbolos;
- coletar evidências;
- recuperar memória;
- arquivar estado.

Ele deve ser econômico porque não precisa decidir arquitetura. Se a evidência for ambígua, entrega a
incerteza ao papel forte em vez de inventar uma conclusão.

### `HEAD_STRONG`

Indicado quando a qualidade do raciocínio muda o resultado:

- solução e arquitetura;
- hipóteses concorrentes;
- planejamento com dependências e riscos;
- contratos, segurança, concorrência e transações;
- recovery após um finding estrutural do Judge.

Modelo forte não deve permanecer ativo para alterações mecânicas depois que a decisão difícil estiver
resolvida.

### `EXECUTOR`

Indicado para aplicar uma decisão já aprovada:

- escrever RED;
- implementar unidades `PLAN-*`;
- rodar GREEN;
- preparar QA e commits.

Executor não deve redesenhar silenciosamente a solução. Ambiguidade material volta ao papel forte.

### `JUDGE_PRIMARY`

Modelo de julgamento independente. Deve executar em contexto novo e read-only, sem receber o
raciocínio ou as tentativas do executor. Avalia requisitos, decisões, plano, diff e evidências.

### `JUDGE_SECONDARY`

Segundo julgamento para risco alto, produção, cross-repo ou divergência. Não substitui decisão humana
quando os juízes discordam.

### `MULTIMODAL`

Usado quando imagem, diagrama, screenshot ou outro conteúdo visual for essencial para compreender a
demanda. Não é automaticamente mais forte para arquitetura ou implementação.

## Forte ou econômico: regra prática

```text
Coletar/localizar/resumir -> ECONOMICAL
Decidir/arquitetar/desambiguar -> HEAD_STRONG
Executar plano aprovado -> EXECUTOR
Julgar independentemente -> JUDGE_PRIMARY
Interpretar visual essencial -> MULTIMODAL
```

O objetivo é minimizar o custo total: um modelo econômico que erra e exige três tentativas pode sair
mais caro que uma decisão forte feita uma vez. Da mesma forma, usar modelo forte para toda busca e
edição mecânica desperdiça orçamento.

## O que o usuário precisa controlar

O usuário normalmente decide apenas:

- skill consultiva ou `orquestrador.md`;
- `QUICK` ou `COMUM`;
- Jira/feature;
- gates apresentados (`APROVAR SOLUÇÃO`, `APROVAR PRD/PLANO`, `APROVAR RED`, `GO`, `APROVAR QA`);
- troca manual de modelo quando o runtime solicitar;
- modo de commit (`AUTOMÁTICO`, `MANUAL`, `OUTROS`);
- se deseja descrição de PR.

Não é necessário escolher estados internos. Fora do fluxo completo, basta apontar a skill adequada e
declarar se ela será executada integralmente ou usada apenas como referência metodológica.

## Resumo de bolso

| Quero... | Entrada recomendada |
|---|---|
| Entender código | Referenciar `03-investigacao.md`, somente leitura |
| Investigar bug sem corrigir | Referenciar `03-investigacao.md`, hipótese + evidência |
| Criar plano preliminar | Referenciar `06-prd-plano.md`, `não execute` |
| Mapear arquitetura | Referenciar `03-investigacao.md` + `05-solucao-proposta.md` |
| Avaliar qualidade/patterns | Referenciar `18-qualidade-arquitetural.md`, somente leitura |
| Comparar arquitetura | Referenciar `05-solucao-proposta.md`, trade-offs |
| Revisar diff | Referenciar `10-juiz.md` como metodologia read-only |
| Implementar história/bug/dívida | Referenciar `orquestrador.md` |
| Entrega simples e segura | Referenciar `orquestrador.md` e escolher `QUICK` |
| Entrega ambígua ou arriscada | Referenciar `orquestrador.md` e escolher `COMUM` |
| Retomar feature | Referenciar `orquestrador.md` + Jira quando necessário |
| Commit isolado | Referenciar `12-commit-workflow.md` |
| QA/PR rastreado | Continuar pelo `orquestrador.md` |
