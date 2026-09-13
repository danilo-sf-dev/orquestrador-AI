---
name: entrevista-opcional
role: clarification
preferred_model_role: HEAD_STRONG
writes: [STATE.md]
context_loading: lazy
reads:
  - STATE.md
  - 00-jira.md
  - 01-discovery.md
  - 01-requirements.md
  - approved_human_decisions
forbidden_reads:
  - chat_transcript
  - raw_discovery_logs
  - unrelated_source_files
forbidden_writes:
  - source_code
  - tests
---

# Skill — Entrevista opcional

## Executar somente se

`04a-analise-requisitos.md` registrou ao menos uma `OPEN_QUESTION` com `BLOCKING=YES`, ou surgiu
ambiguidade equivalente capaz de mudar materialmente implementação, contrato, aceite ou desenho do RED.

## Fonte das perguntas

Perguntar prioritariamente os IDs `Q-*` de `01-requirements.md`. Não abrir nova rodada genérica de
refinamento se a pergunta bloqueante já estiver formulada.

Gatilhos válidos:
- critério contraditório;
- duas interpretações plausíveis com efeito diferente;
- regra de negócio não presente no código/docs;
- contrato entre repos indefinido;
- comportamento esperado do bug não está claro;
- decisão arquitetural que pertence ao time e muda contrato/risco;
- imagem essencial ilegível/incompleta.

## Não perguntar se
- resposta está no código/teste/contrato ativo;
- dúvida é resolvível por padrão comprovado do projeto;
- diferença é sintática, estética ou facilmente reversível;
- item foi classificado como `ASSUMPTION` de baixo impacto;
- item é `OPTIONAL_IMPROVEMENT` fora do escopo.

## Formato

Fazer o menor número de perguntas possível, preferencialmente uma rodada curta. Para cada pergunta,
informar `Q-*` e por que a resposta muda a implementação/aceite.

## Saída

Se não necessária:

```text
INTERVIEW_SKIPPED=true
REASON=contexto suficiente
```

Se necessária:

```text
INTERVIEW_REQUIRED=true
QUESTIONS:
- Q-<N>: ...
```

Registrar a resposta como decisão humana resumida no `STATE.md`/artefato apropriado, sem copiar o
transcript. Em seguida voltar para:

```yaml
CURRENT_STATE: REQUIREMENT_ANALYSIS
NEXT_ACTION: RESOLVE_REQUIREMENT_DELTA
```

A skill de análise de requisitos fecha/reclassifica os `Q-*`; a entrevista não altera a SPEC ou o RED diretamente.
