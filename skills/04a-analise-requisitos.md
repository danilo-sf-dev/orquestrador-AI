---
name: analise-requisitos
role: requirement_analysis
preferred_model_role: HEAD_STRONG
writes: [01-requirements.md, STATE.md]
context_loading: lazy
reads:
  - STATE.md
  - 00-jira.md
  - 01-discovery.md
  - approved_human_decisions
  - related_feature_memory_selected_only
forbidden_reads:
  - chat_transcript
  - raw_discovery_logs
  - unrelated_source_files
  - bulk_feature_history
forbidden_writes:
  - source_code
  - tests
  - approved_solution
  - approved_plan
---

# Skill — Análise de requisitos

## Objetivo

Converter Jira + discovery em um contrato de requisitos confiável antes de desenhar a solução. Esta
skill procura lacunas materiais, separa fatos de hipóteses e impede que decisões de produto sejam
inventadas pelo modelo.

Ela **não** cria um novo gate humano. Só bloqueia o fluxo quando existir uma pergunta material que
não possa ser resolvida por código, contrato, documentação válida ou decisão já aprovada.

## Pré-condições

```yaml
JIRA_CONTEXT_READY: true
CURRENT_STATE: REQUIREMENT_ANALYSIS
```

`01-discovery.md` deve existir no fluxo `STANDARD_GATED`.

## Ordem de análise

1. Ler critérios explícitos do Jira e comportamento atual confirmado no discovery.
2. Normalizar o comportamento observável esperado sem reescrever regra de negócio.
3. Executar um gap scan somente nas dimensões aplicáveis.
4. Classificar cada item relevante.
5. Separar `ASSUMPTION` de `OPEN_QUESTION`.
6. Determinar se alguma pergunta é bloqueante.
7. Produzir um contrato compacto para Solution Design e SPEC.

## Requirement Gap Scan

Verificar proporcionalmente ao tipo de mudança:

- validação de entrada e boundaries;
- ausência, `null`, vazio e valores inválidos;
- erros/status/exceções observáveis;
- autorização/autenticação quando o fluxo toca segurança;
- persistência, consistência e transação;
- idempotência, duplicidade, ordem e concorrência;
- timeout, retry, fallback e falha de dependência externa;
- compatibilidade de contrato e consumidores;
- paginação/limites/volume quando aplicável;
- observabilidade necessária para operação;
- transições de estado e branches relevantes;
- cross-repo/deploy quando o contrato atravessa repositórios.

Não transformar checklist em requisito. Dimensão não aplicável deve ser ignorada.

## Classificação obrigatória

Cada item material deve usar exatamente uma classe:

```text
EXPLICIT_REQUIREMENT
IMPLICIT_NECESSITY
ASSUMPTION
OPEN_QUESTION
TECHNICAL_RISK
OPTIONAL_IMPROVEMENT
```

Regras:

- `EXPLICIT_REQUIREMENT`: está no Jira/decisão humana válida.
- `IMPLICIT_NECESSITY`: condição técnica necessária para satisfazer requisito explícito sem alterar comportamento de negócio.
- `ASSUMPTION`: inferência razoável, apoiada por evidência, reversível se estiver errada.
- `OPEN_QUESTION`: decisão material que não pode ser inferida com segurança.
- `TECHNICAL_RISK`: risco que precisa de mitigação/validação, não novo requisito.
- `OPTIONAL_IMPROVEMENT`: ganho possível fora do escopo atual; não segue para implementação sem aprovação explícita.

## Assumptions x Open Questions

`ASSUMPTION` deve registrar:

```text
ID: A-<N>
CLAIM:
EVIDENCE:
IMPACT_IF_WRONG:
REVERSIBLE: YES | NO
CONFIDENCE: HIGH | MEDIUM | LOW
```

`OPEN_QUESTION` deve registrar:

```text
ID: Q-<N>
QUESTION:
WHY_NOT_INFERABLE:
DECISION_OWNER: PRODUCT | BUSINESS | ARCHITECTURE | EXTERNAL_SYSTEM | UNKNOWN
IMPACT:
BLOCKING: YES | NO
```

Uma pergunta é `BLOCKING=YES` somente se a resposta puder mudar materialmente comportamento externo,
contrato, regra de negócio, segurança, persistência, integração, efeito destrutivo ou desenho do RED.
Preferência estética, nomenclatura interna, detalhe reversível ou padrão já comprovado no projeto não
bloqueiam o fluxo.

## Escalonamento e transição

Se existir `OPEN_QUESTION BLOCKING=YES`:

```yaml
REQUIREMENT_ANALYSIS_STATUS: BLOCKED
CURRENT_STATE: INTERVIEW_OPTIONAL
NEXT_ACTION: ASK_BLOCKING_QUESTIONS
NEXT_MODEL_ROLE: HEAD_STRONG
```

Executar `04-entrevista-opcional.md` perguntando somente o mínimo necessário. Após resposta, voltar a
esta skill para fechar o delta; não repetir discovery completo.

Sem pergunta bloqueante, registrar:

```yaml
REQUIREMENT_ANALYSIS_STATUS: COMPLETE
```

Depois rotear de forma determinística:

```text
TECHNICAL_QUALITY_REVIEW_STATUS=REQUIRED
-> CURRENT_STATE=TECHNICAL_QUALITY_REVIEW
-> NEXT_ACTION=REVIEW_TECHNICAL_QUALITY

caso contrário
-> CURRENT_STATE=SOLUTION_DESIGN
-> NEXT_ACTION=DESIGN_SOLUTION
```

Em ambos os casos:

```yaml
NEXT_MODEL_ROLE: HEAD_STRONG
```

## Saída `01-requirements.md`

Produzir de forma compacta:

```text
OBJECTIVE:
OBSERVABLE_BEHAVIOR:

REQUIREMENTS:
- R-<N> | EXPLICIT_REQUIREMENT | <texto> | SOURCE=<Jira/decision>
- R-<N> | IMPLICIT_NECESSITY | <texto> | EVIDENCE=<...>

ASSUMPTIONS:
- A-<N> ...

OPEN_QUESTIONS:
- Q-<N> ...

TECHNICAL_RISKS:
- TR-<N> ...

OPTIONAL_IMPROVEMENTS:
- OI-<N> ...

OUT_OF_SCOPE:
- ...

BLOCKING_OPEN_QUESTIONS: <N>
```

Não copiar Jira ou discovery integralmente. Cada requisito deve apontar origem ou evidência.

## Regra anti-scope-creep

`IMPLICIT_NECESSITY` não autoriza feature adicional. `OPTIONAL_IMPROVEMENT` nunca vira AC, plano,
RED ou finding de Judge sem aprovação explícita. Quando houver dúvida entre necessidade e melhoria,
classificar conservadoramente e expor a incerteza.
