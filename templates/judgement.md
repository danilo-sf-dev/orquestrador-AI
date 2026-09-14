# Julgamento — <JIRA-ID>

## Contexto do juiz
- Fresh context: yes
- Read-only: yes
- Judge model role:
- FLOW_MODE: STANDARD_GATED | QUICK_AUTOGO
- CONTRACT_SOURCE: SPEC | QUICK_CONTRACT

## Preconditions

### STANDARD
- SPEC_STATUS:
- BLOCKING_OPEN_QUESTIONS:

### QUICK
- QUICK_CONTRACT_APPROVED:

### Ambos
- RED_LOCKED:
- GREEN_STATUS:

## Veredito
PASS | PASS_WITH_RISKS | FAIL | BLOCKED

## Evidence-or-zero

### STANDARD — por critério

| AC | Requisito | Resultado | Teste/Evidência | Código/Diff | Resultado observável | Gap/Risco |
|---|---|---|---|---|---|---|
| AC-01 | R-01 | PASS / FAIL / BLOCKED / PENDING_EXTERNAL | | | | |

### QUICK — por item do contrato

| Quick Contract item | Resultado | Teste/Evidência | Código/Diff | Resultado observável | Gap/Risco |
|---|---|---|---|---|---|
| QC-01 | PASS / FAIL / BLOCKED / PENDING_EXTERNAL | | | | |

> Usar somente a tabela correspondente ao fluxo. `PASS` exige evidência concreta suficiente; ausência de evidência não pode ser compensada por "parece correto".

## Integridade RED/GREEN

## Arquitetura/contratos

## Rastreabilidade

### STANDARD

| R/Jira | AC | DD | PLAN | Diff | Teste/evidência | Resultado |
|---|---|---|---|---|---|---|
| | | | | | | |

### QUICK

| Quick Contract item | Diff | Teste/evidência | Resultado |
|---|---|---|---|
| | | | |

## Qualidade técnica proporcional ao diff

| Dimensão aplicável | Resultado | Evidência | Risco |
|---|---|---|---|
| Segurança/erros/concorrência/desempenho/compatibilidade/manutenção | | | |

## Regressões/riscos

## Findings

| ID | Categoria | Severidade | Referência do contrato | Evidência | Esperado x atual | Confiança |
|---|---|---|---|---|---|---|
| | | | | | | |

## Conclusão para QA

## Selo do escopo julgado
- JUDGEMENT_SCOPE:
- JUDGEMENT_SCOPE_HASH_METHOD:
- JUDGEMENT_SCOPE_HASH:
