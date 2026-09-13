# 02 — Visão geral do projeto

> HUMAN_ONLY. Este arquivo é para consulta do usuário e não deve ser carregado por agentes.

## O que é o Orquestrador

O projeto é um harness pessoal de desenvolvimento orientado por Jira. Ele combina investigação,
memória por feature, papéis de modelo, gates humanos, TDD com RED lock, validação GREEN, Judge
independente, QA e entrega Git.

O objetivo não é usar o maior modelo em todas as etapas. É entregar com qualidade mantendo contexto e
custo sob controle.

## Peças principais

### `orquestrador.md`

É o contrato central de execução. Decide:

- estado atual;
- fluxo;
- skill;
- papel/modelo;
- gate;
- próxima ação;
- contexto permitido.

### `skills/`

Cada skill descreve **como executar uma etapa específica**. O orquestrador não deve duplicar todas as
regras dessas skills.

### `templates/`

Contém modelos para artefatos operacionais como `STATE.md`, SPEC/plano, RED, julgamento, handoff e
registro de commit.

### `.ai/`

É a memória operacional local das features Jira. Deve permanecer fora do Git.

### `documentacao-usuario/`

É este manual. É versionado no repositório, porém `HUMAN_ONLY`: não pertence ao contexto dos agentes.

## Cinco conceitos que não devem ser confundidos

### Estado / State

É onde o fluxo está agora. Exemplo:

```text
CURRENT_STATE=REQUIREMENT_ANALYSIS
```

Significa que a feature está na etapa de análise de requisitos.

### Skill

É o arquivo que ensina o agente a executar aquela etapa. Exemplo:

```text
skills/04a-analise-requisitos.md
```

### Papel / Role

É o tipo de responsabilidade/modelo desejado para a etapa. Exemplo:

```text
HEAD_STRONG
```

Não é um estado e não é uma skill.

### Gate

É uma autorização/parada explícita que impede avanço automático. Exemplos:

```text
APROVAR SOLUÇÃO
APROVAR SPEC/PLANO
APROVAR RED
GO
REOPEN RED
```

### Artefato

É uma memória/contrato produzido durante a feature. Exemplos:

```text
01-requirements.md
03-spec.md
05-red-tests.md
07-green-evidence.md
08-judgement.md
```

## Arquitetura conceitual do fluxo COMUM

```text
CONTEXTO
Jira + código + memória + contratos
        ↓
RACIOCÍNIO
Discovery + Requirements + Design
        ↓
CONTRATO
Solution + SPEC + Plan + RED
        ↓
EXECUÇÃO E PROVA
Implementação + GREEN + Judge + QA
        ↓
ENTREGA E MEMÓRIA
Commit + descrição de PR + Archive
```

A melhoria mais importante da V1.9 está antes da execução: o sistema tenta descobrir lacunas e tomar
decisões técnicas antes de RED/implementação, reduzindo retrabalho tardio.

## Fonte de verdade e precedência

Para uma feature em execução, a interpretação correta deve vir de:

```text
1. orquestrador.md para roteamento/invariantes
2. skill atual para regras da etapa
3. artefatos aprovados da feature para o contrato específico
4. código/testes/configuração/contratos reais para evidência técnica
```

README e este manual são documentos de apresentação/consulta humana, não substitutos do contrato
operacional.

## Nota sobre features antigas

Em features arquivadas por versões anteriores, você pode encontrar `03-prd.md`, `PRD_PLAN_REVIEW`,
`PRD_PLAN_APPROVED` ou o gate `APROVAR PRD/PLANO`. Eles são nomes históricos do conceito que hoje é
representado por `03-spec.md`, `SPEC_PLAN_REVIEW`, `SPEC_PLAN_APPROVED` e `APROVAR SPEC/PLANO`.

Essa nota serve apenas para interpretação de memória antiga. Novas features usam exclusivamente a
nomenclatura SPEC.

## Princípios de economia de contexto

O projeto economiza tokens principalmente por:

- lazy loading;
- search-first;
- Codebase Recon orientado a entry point;
- `STATE.md` curto;
- memória por Jira;
- handoff apontando artefatos em vez de copiar transcript;
- papéis/modelos proporcionais à tarefa;
- Judge em fresh context;
- exclusão absoluta de `documentacao-usuario/**` do contexto dos agentes.
