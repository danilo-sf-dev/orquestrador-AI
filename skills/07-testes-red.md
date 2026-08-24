---
name: testes-red
role: test-design
preferred_model_role: EXECUTOR
writes: [05-red-tests.md, red-tests.lock, STATE.md]
source_edits: tests_only
context_loading: lazy
reads:
  - STATE.md
  - 00-jira.md
  - 03-prd.md
  - 04-implementation-plan.md
  - source_code_relevant_read_only
  - existing_tests_relevant_only
forbidden_reads:
  - chat_transcript
  - raw_discovery_logs
  - unrelated_source_files
forbidden_writes:
  - production_code
  - approved_prd
  - approved_plan
---

# Skill — Testes unitários RED

## Pré-condição
PRD e plano aprovados.

## Objetivo
Criar os testes que provam o comportamento exigido antes da implementação, cobrindo **happy path e edge cases aplicáveis**. Os testes RED funcionam como especificação executável da história.

## Regras
1. Alterar somente arquivos de teste nesta fase.
2. Cada teste deve mapear para um critério de aceite, regra de negócio ou risco explícito.
3. Para cada critério de aceite, identificar o happy path e os edge cases relevantes antes do gate de aprovação.
4. Cobrir, **quando aplicável ao domínio/fluxo**:
   - valores de fronteira/boundaries (mínimo, máximo, imediatamente abaixo/acima);
   - `null`, ausência e campos opcionais;
   - strings/coleções vazias;
   - valores inválidos e combinações inválidas;
   - branches condicionais e estados não permitidos;
   - erro, timeout ou resposta inesperada de dependências mockadas;
   - exceções e mapeamento de erro;
   - duplicidade/idempotência, quando o comportamento exigir;
   - mapping/serialização/conversões relevantes;
   - regressões adjacentes ao comportamento alterado.
5. Não criar edge cases artificiais sem relação com a história. Um cenário relevante não coberto deve ser registrado como `DEFERRED_WITH_REASON` ou `NOT_APPLICABLE`, com justificativa.
6. Para comportamento novo não implementado, o teste deve falhar pelo motivo esperado.
7. Se passar inesperadamente, investigar:
   - comportamento já existe;
   - teste não está atingindo a regra;
   - mock mascara o comportamento;
   - critério já está atendido.
8. Nunca enfraquecer assert para fabricar RED/GREEN.
9. Preferir asserts comportamentais claros; mocks não podem mascarar a regra que se pretende provar.
10. Mostrar ao usuário, antes de selar, o conjunto de testes **e a matriz de edge cases**.

## Documento `05-red-tests.md`
Registrar por teste:
- critério de aceite/regra/risco;
- tipo: `HAPPY_PATH` ou `EDGE_CASE`;
- classe/método de teste;
- comportamento esperado;
- motivo do RED atual;
- evidência de falha;
- observações.

Registrar também uma matriz de edge cases:
- cenário;
- origem (`AC`, regra, contrato, risco, bug/regressão);
- aplicabilidade: `COVERED`, `NOT_APPLICABLE` ou `DEFERRED_WITH_REASON`;
- teste associado ou justificativa.

## Gate
Solicitar `APROVAR RED`.


## Ponte RED -> QA

Para riscos de alta visibilidade no QA/E2E, identificar pelo menos um teste unitário representativo como `QA_SURROGATE=true` quando isso for tecnicamente possível. Registrar também `risk_if_missed`.

Regras:
- surrogate antecipa risco, mas nunca substitui o QA real;
- preferir um caso representativo de alto valor em vez de combinações redundantes;
- se o risco só puder ser provado integrado/E2E, registrar `QA_ONLY` com justificativa;
- o Judge deve considerar essa ponte ao responder se a implementação está pronta para QA.

## Lock após aprovação
Gerar `red-tests.lock` com:
- caminhos dos testes;
- hash SHA-256 ou `git hash-object` de cada arquivo;
- timestamp/commit base quando disponível.

Exemplo:
```text
RED_LOCK_VERSION=1
FILE=src/test/.../FooTest.java SHA256=...
FILE=src/test/.../BarTest.java SHA256=...
```

Marcar `RED_LOCKED=true`.

## Proibição futura
GREEN não pode modificar esses arquivos sem `REOPEN RED` + nova aprovação + novo lock.
