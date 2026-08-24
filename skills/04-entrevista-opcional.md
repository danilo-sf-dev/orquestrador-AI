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
Após Jira + memória + discovery ainda houver ambiguidade capaz de mudar implementação ou aceite.

## Gatilhos
- critério contraditório;
- duas interpretações plausíveis;
- regra de negócio não presente no código/docs;
- contrato entre repos indefinido;
- arquitetura depende de escolha do time;
- comportamento esperado do bug não está claro;
- imagem essencial ilegível/incompleta.

## Não perguntar se
- a resposta está no código;
- a resposta está nos testes existentes;
- endpoint do Jira já permite rastrear o fluxo;
- dúvida é apenas curiosidade e não bloqueia a solução.

## Formato
Fazer o menor número de perguntas possível, preferencialmente uma rodada curta e objetiva.

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
1. ...
2. ...
```

Registrar respostas em `STATE.md` e tratá-las como decisão humana.
