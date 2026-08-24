---
name: qa-pack
role: qa_delivery
preferred_model_role: EXECUTOR
context_loading: lazy
reads:
  - STATE.md
  - 00-jira.md
  - 03-prd.md
  - 04-implementation-plan.md
  - 08-judgement.md
  - approved_api_contracts
  - relevant_multimodal_assets_if_needed
writes:
  - 09-qa-tests.md
  - 10-qa-guide.md
  - qa/*
  - STATE.md
forbidden_reads:
  - chat_transcript
  - raw_discovery_logs
  - implementation_attempt_history
  - unrelated_source_files
forbidden_writes:
  - source_code
  - locked_red_tests
  - approved_prd
---

# Skill — QA Pack

## Pré-condição
Judge = `PASS` ou `PASS_WITH_RISKS` explicitamente aceito.

## Objetivo
Criar o material necessário para o QA validar a história em Postman/Insomnia e um guia Word passo a passo.

## `09-qa-tests.md`
Cada cenário deve conter:
- critério de aceite associado;
- pré-condição;
- endpoint/método;
- headers/auth;
- payload;
- sequência de requests;
- resultado esperado;
- cenário positivo/negativo;
- limpeza/reset quando necessário.

## Collection
Gerar Postman ou Insomnia conforme padrão do projeto/time.

Incluir, quando relevante:
- environment variables;
- base URL;
- auth placeholders seguros;
- scripts de preparação/testes;
- requests encadeados;
- exemplos de response.

Nunca inserir segredo real em arquivo versionado.

## Guia Word
A fonte canônica é `10-qa-guide.md`. O entregável é um `.docx` em `qa/` quando o ambiente suportar geração de DOCX.

Estrutura sugerida:
1. objetivo;
2. pré-requisitos;
3. ambiente;
4. como importar a collection;
5. variáveis;
6. passos por cenário;
7. resultados esperados;
8. evidências a capturar;
9. limitações/riscos conhecidos.

Se existir template corporativo, reutilizá-lo. Se não for possível gerar DOCX no ambiente, não fingir: deixar `10-qa-guide.md` pronto e registrar o bloqueio operacional.

## Gate
Solicitar obrigatoriamente `APROVAR QA` antes de avançar para commit.
