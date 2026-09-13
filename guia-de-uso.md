# Guia de uso diário do Orquestrador

Use `orquestrador.md` quando o trabalho deve virar **mudança controlada e entregável**: código, testes,
QA, commit, descrição de PR ou memória retomável por Jira.

Use uma skill diretamente como referência metodológica quando deseja apenas **entender, analisar,
comparar, planejar ou revisar**, sem implementar.

## Invocação

Fluxo completo:

```text
Leia e siga:
"<caminho>/orquestrador.md"

Jira: <ID ou URL>
Fluxo: QUICK | COMUM
```

Skill consultiva:

```text
Use como referência metodológica:
"<caminho>/skills/<skill>.md"

<objetivo e limites>
Não implemente.
```

## QUICK ou COMUM

| Sinal | QUICK | COMUM |
|---|---:|---:|
| Mudança localizada/inequívoca | Sim | Sim |
| Baixo risco/reversível | Sim | Sim |
| Causa do bug incerta | Não | Sim |
| Open question material | Não | Sim |
| API/contrato material | Não | Sim |
| Persistência/migração | Não | Sim |
| Concorrência/transação | Não | Sim |
| Segurança | Não | Sim |
| Cross-repo/ordem de deploy | Não | Sim |
| Bug de produção relevante | Não | Sim |
| Decisão arquitetural/refactor estrutural | Não | Sim |

Na dúvida, escolha `COMUM`. QUICK reduz cerimônia, não qualidade.

## Fluxo COMUM em linguagem simples

```text
Jira
-> entender o código relevante
-> analisar requisitos e lacunas
-> perguntar somente o que for realmente bloqueante
-> revisar qualidade arquitetural se houver motivo real
-> desenhar a solução proporcional
-> APROVAR SOLUÇÃO
-> consolidar SPEC + plano
-> APROVAR PRD/PLANO
-> RED
-> APROVAR RED
-> GO
-> implementação
-> GREEN
-> Judge independente
-> QA
-> commit / descrição de PR / archive
```

`REQUIREMENT_ANALYSIS` e `SOLUTION_DESIGN` não criam aprovações novas.

## Skills consultivas principais

### Entender código / investigar bug

```text
Use como referência metodológica:
"<caminho>/skills/03-investigacao.md"

Investigue em modo somente leitura. Comece pelo entry point mais próximo, siga apenas o fluxo
relevante, diferencie FACT/INFERENCE/UNKNOWN e cite evidências.
```

Discovery agora usa Codebase Recon: `anchor Jira -> entry point -> chamadas/dados relevantes ->
boundary/contrato necessário -> testes`. Expandir somente se a nova leitura puder mudar a decisão.

### Encontrar gaps no Jira

```text
Use como referência metodológica:
"<caminho>/skills/04a-analise-requisitos.md"

Separe requisitos explícitos, necessidades implícitas, assumptions, open questions, riscos e melhorias
opcionais. Não desenhe a solução ainda.
```

Classificações:

```text
EXPLICIT_REQUIREMENT
IMPLICIT_NECESSITY
ASSUMPTION
OPEN_QUESTION
TECHNICAL_RISK
OPTIONAL_IMPROVEMENT
```

Pergunta só bloqueia quando sua resposta pode mudar materialmente comportamento, contrato, negócio,
segurança, persistência, integração, efeito destrutivo ou desenho do RED.

### Desenhar/comparar solução

```text
Use como referência metodológica:
"<caminho>/skills/04b-design-solucao.md"

Desenhe a menor solução tecnicamente sólida. Faça o Senior Approach Check, respeite a arquitetura
existente e compare alternativas somente quando houver diferença material. Não implemente.
```

O Senior Approach Check pergunta: existe solução mais simples? padrão equivalente? acoplamento ou
abstração desnecessária? boundary/contrato material? efeito colateral previsível?

### Avaliar arquitetura / Design Patterns

```text
Use como referência metodológica:
"<caminho>/skills/18-qualidade-arquitetural.md"

Avalie problemas estruturais comprováveis. Recomende pattern ou mudança arquitetural somente quando a
solução mais simples não resolver. Não altere arquivos.
```

A skill 18 continua opcional e especializada; não usar como checklist obrigatório.

### Criar SPEC + plano

```text
Use como referência metodológica:
"<caminho>/skills/06-prd-plano.md"

Crie somente a SPEC e o plano. Não execute.
```

`03-prd.md` mantém o nome por compatibilidade, mas passa a ser a **SPEC canônica**: comportamento
observável, ACs, constraints, assumptions aceitas, contratos, decisões, riscos e evidência esperada.

### Revisar diff

```text
Use como referência metodológica:
"<caminho>/skills/10-juiz.md"

Revise em read-only. Use evidence-or-zero: não marque critério como PASS sem prova suficiente.
```

Dentro de uma feature real, deixe o orquestrador preparar o Judge fresh/read-only.

## Knowledge Verification Chain

Para decisões técnicas:

```text
1. código + testes atuais
2. configuração/contratos ativos
3. padrões comprovados + docs locais relevantes
4. documentação oficial externa somente se necessária
5. inferência explicitamente marcada
```

## Mechanical Gates

RED só avança quando a SPEC está aprovada, não há open question bloqueante, todos os ACs possuem
evidência planejada e testes estão rastreados à origem. O RED deve falhar pelo motivo esperado.

GREEN exige, quando aplicável:

```text
lock válido
compile PASS
RED tests PASS
regressão PASS
unexpected failures = 0
unexpected skipped = 0
ACs com evidência
locked test diff = CLEAN
```

Judge aplica:

```text
sem evidência suficiente != PASS
```

## QUICK

Antes do Quick Contract, a skill 16 executa versões compactas de:

```text
Codebase Recon
Requirement Gap Scan
Assumptions/Open Questions
Senior Solution Check
```

Blocker material ou decisão estrutural aborta QUICK para COMUM. Caso contrário, `AUTO-GO` autoriza
RED -> lock -> implementação -> GREEN até o handoff para Judge.

## Papéis

- `ECONOMICAL`: Jira, busca/recon, evidência, memória e archive.
- `HEAD_STRONG`: requirement analysis, solution design, arquitetura, SPEC/plano e recovery.
- `EXECUTOR`: RED, implementação, GREEN, QA e commit.
- `JUDGE_PRIMARY`: julgamento independente fresh/read-only.
- `JUDGE_SECONDARY`: reforço em risco alto/divergência.
- `MULTIMODAL`: quando visual é essencial.

## O que o usuário normalmente controla

- skill consultiva ou `orquestrador.md`;
- `QUICK` ou `COMUM`;
- Jira/feature;
- gates existentes: `APROVAR SOLUÇÃO`, `APROVAR PRD/PLANO`, `APROVAR RED`, `GO`, `APROVAR QA`;
- respostas a open questions realmente bloqueantes;
- troca manual de modelo quando solicitada;
- commit `AUTOMÁTICO | MANUAL | OUTROS`;
- se deseja descrição de PR.

## Resumo de bolso

| Quero... | Entrada |
|---|---|
| Entender código | `03-investigacao.md` |
| Investigar bug | `03-investigacao.md` |
| Encontrar gaps no Jira | `04a-analise-requisitos.md` |
| Desenhar/comparar solução | `04b-design-solucao.md` |
| Avaliar arquitetura/patterns | `18-qualidade-arquitetural.md` |
| Criar SPEC/plano | `06-prd-plano.md` |
| Revisar diff | `10-juiz.md` |
| Implementar história/bug | `orquestrador.md` |
| Entrega simples/segura | `orquestrador.md` + QUICK |
| Entrega ambígua/arriscada | `orquestrador.md` + COMUM |
| Retomar feature | `orquestrador.md` + Jira quando necessário |
