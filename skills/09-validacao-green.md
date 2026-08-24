---
name: validacao-green
role: verification
preferred_model_role: EXECUTOR
writes: [07-green-evidence.md, STATE.md]
context_loading: lazy
reads:
  - STATE.md
  - 04-implementation-plan.md
  - 05-red-tests.md
  - red-tests.lock
  - 06-implementation-summary.md
  - source_code_changed_only
  - tests_locked_and_related
forbidden_reads:
  - chat_transcript
  - raw_discovery_logs
  - implementation_attempt_history
forbidden_writes:
  - locked_red_tests
  - source_code
  - tests
  - red-tests.lock
---

# Skill — Validação GREEN

## Objetivo
Demonstrar que a implementação atende os testes selados sem alterar a especificação de teste para induzir aprovação.

## Ordem
1. Validar hashes do `red-tests.lock` antes dos testes.
2. Compilar.
3. Rodar os testes unitários RED aprovados, incluindo happy path e edge cases selados.
4. Conferir que a matriz de edge cases aprovada continua representada pelos testes lockados.
5. Rodar testes relacionados/regressão proporcional ao risco.
6. Validar hashes novamente.
7. Verificar `git diff` dos arquivos de teste selados.

## Resultado inválido
Se qualquer teste selado tiver sido modificado sem reabertura RED:

```text
GREEN_STATUS=INVALID_GREEN
REASON=locked test modified
```

Não corrigir o lock para acomodar a alteração.

## Se o teste realmente precisar mudar
Voltar à skill RED:

```text
REOPEN_RED_REQUIRED=true
```

Explicar motivo, obter aprovação, gerar novo lock, então retomar.

## `07-green-evidence.md`
Registrar:
- comandos executados;
- build status;
- testes RED e resultados, separando happy path e edge cases;
- edge cases cobertos e eventuais `NOT_APPLICABLE`/`DEFERRED_WITH_REASON`;
- suite extra e resultados;
- hashes verificados;
- falhas restantes;
- limitações (ex.: integração não disponível);
- itens que QA ainda precisa validar.
