---
name: qa-pack
role: qa_delivery
preferred_model_role: EXECUTOR
context_loading: lazy
reads:
  - STATE.md
  - 00-jira.md
  - 03-spec.md_if_standard_gated
  - 04-implementation-plan.md_if_standard_gated
  - quick_contract_if_flow_mode_quick
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
  - approved_spec
---

# Skill — QA Pack

## Pré-condição
Judge = `PASS` ou `PASS_WITH_RISKS`.

`PASS_WITH_RISKS` não cria gate separado: riscos aceitos/pendências externas devem estar explícitos no pacote e permanecem visíveis no gate normal `APROVAR QA`.

## Política por fluxo

### `STANDARD_GATED`

QA é obrigatório e segue o gate `APROVAR QA`.

### `QUICK_AUTOGO`

Antes de materializar o pacote, decidir com o usuário se QA/documentação é necessário para a tarefa curta.

Se não for necessário, registrar justificativa objetiva:

```yaml
QA_STATUS: NOT_REQUIRED_WITH_REASON
CURRENT_STATE: COMMIT_REVIEW
NEXT_ACTION: PREPARE_COMMIT_PLAN
NEXT_MODEL_ROLE: EXECUTOR
```

Não criar arquivos de QA vazios apenas para cumprir estrutura.

Se QA for necessário, seguir normalmente e usar `APROVAR QA`.

## Objetivo
Criar o material necessário para o QA validar a história em Postman/Insomnia e um guia Word passo a passo.

No `STANDARD_GATED`, rastrear cenários para `AC-*`/SPEC. No `QUICK_AUTOGO`, rastrear para os itens/comportamentos do Quick Contract aprovado. Nunca exigir artefato STANDARD que o QUICK não cria.

## `09-qa-tests.md`
Cada cenário deve conter:
- critério de aceite ou item do Quick Contract associado;
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
Quando o pacote existir, solicitar obrigatoriamente `APROVAR QA` antes de avançar para commit.

Após aprovação:

```yaml
QA_STATUS: APPROVED
CURRENT_STATE: COMMIT_REVIEW
NEXT_ACTION: PREPARE_COMMIT_PLAN
NEXT_MODEL_ROLE: EXECUTOR
```
