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
É o contrato central de execução: decide estado, fluxo, skill, papel/modelo, gate, próxima ação e contexto permitido.

### `skills/`
Cada skill descreve **como executar uma etapa específica**.

### `templates/`
Contém modelos para `STATE.md`, SPEC/plano, RED, julgamento, handoff e registros de entrega.

### `.ai/`
É a memória operacional local das features Jira. Deve permanecer fora do Git.

### `documentacao-usuario/`
É este manual. É versionado no repositório, porém `HUMAN_ONLY`.

## Cinco conceitos que não devem ser confundidos

### Estado / State
É onde o fluxo está agora. Exemplo: `CURRENT_STATE=REQUIREMENT_ANALYSIS`.

### Skill
É o arquivo que ensina o agente a executar a etapa, por exemplo `skills/04a-analise-requisitos.md`.

### Papel / Role
É a responsabilidade/modelo desejado para a etapa, por exemplo `HEAD_STRONG`.

### Gate
É uma autorização/parada explícita, como `APROVAR SOLUÇÃO`, `APROVAR SPEC/PLANO`, `APROVAR RED`, `GO` ou `REOPEN RED`.

### Artefato
É uma memória/contrato produzido durante a feature, como:

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

A melhoria mais importante da V1.9 está antes da execução: descobrir lacunas e tomar decisões técnicas
antes de RED/implementação, reduzindo retrabalho tardio.

## Fonte de verdade e precedência

```text
1. orquestrador.md para roteamento/invariantes
2. skill atual para regras da etapa
3. artefatos aprovados da feature para o contrato específico
4. código/testes/configuração/contratos reais para evidência técnica
```

README e este manual são documentos de apresentação/consulta humana, não substitutos do contrato operacional.

## Nota sobre features antigas

Em features arquivadas por versões anteriores, você pode encontrar `03-prd.md`, `PRD_PLAN_REVIEW` ou
`PRD_PLAN_APPROVED`. Eles representam a nomenclatura anterior do conceito hoje chamado SPEC + plano.
Novas features usam `03-spec.md`, `SPEC_PLAN_REVIEW` e `SPEC_PLAN_APPROVED`.

## Princípios de economia de contexto

O projeto economiza tokens por lazy loading, search-first, Codebase Recon, `STATE.md` curto, memória por
Jira, handoff compacto, papéis proporcionais, Judge em fresh context e exclusão absoluta de
`documentacao-usuario/**` do contexto dos agentes.
