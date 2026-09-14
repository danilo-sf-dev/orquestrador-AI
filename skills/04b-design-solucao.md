---
name: design-solucao
role: solution_design
preferred_model_role: HEAD_STRONG
writes: [02-design.md, STATE.md]
context_loading: lazy
reads:
  - STATE.md
  - 00-jira.md
  - 01-discovery.md
  - 01-requirements.md
  - 01-quality-review.md # somente quando presente
  - related_feature_memory_selected_only
  - approved_human_decisions
  - recovery/judge-recovery-<N>.md_if_recovery_in_progress
  - source_code_relevant_read_only
forbidden_reads:
  - chat_transcript
  - raw_discovery_logs
  - unrelated_source_files
  - implementation_attempt_history
forbidden_writes:
  - source_code
  - tests
  - approved_solution
  - approved_plan
---

# Skill — Design da solução

## Objetivo

Desenhar a menor solução tecnicamente sólida para o contrato de requisitos, antes do gate humano da
solução. Esta skill adiciona o "senior approach check" sem transformar toda história em exercício de
arquitetura.

Ela não cria gate humano adicional. O gate continua pertencendo a `05-solucao-proposta.md`.

## Pré-condições

```yaml
REQUIREMENT_ANALYSIS_STATUS: COMPLETE
BLOCKING_OPEN_QUESTIONS: 0
```

Se uma pergunta bloqueante reaparecer, retornar para `REQUIREMENT_ANALYSIS`; não escolher por conta
própria.

## Modo recovery

Se `RECOVERY_STATUS=IN_PROGRESS` e `NEXT_ACTION=APPLY_RECOVERY_DESIGN_DELTA`, usar o finding atual e o
`02-design.md` existente como base. Reavaliar somente decisões, boundaries, contratos e riscos afetados
pelo delta; não redesenhar a solução inteira nem reabrir decisões que continuam válidas.

## Princípio

```text
seguir arquitetura válida existente por padrão
+ preferir a menor mudança suficiente
+ propor mudança estrutural somente com ganho material demonstrável
```

Consistência com o projeto não significa repetir um padrão que seja causa comprovada do problema.

## Senior Approach Check

Antes de fechar o design, responder com evidência:

1. Existe solução significativamente mais simples com o mesmo comportamento?
2. Existe padrão equivalente já usado corretamente no projeto?
3. A proposta cria acoplamento, abstração ou camada sem necessidade atual?
4. Há impacto material em contrato, segurança, transação, concorrência, integração, performance ou
   compatibilidade?
5. A proposta atravessa boundary de domínio/módulo/repositório? Se sim, o contrato e consumidores estão
   explícitos?
6. Há risco de corrigir o Jira criando efeito colateral previsível em outro fluxo?
7. Alguma melhoria encontrada é apenas estética/sintática ou fora de escopo?

Melhoria puramente estética não interrompe nem amplia a solução.

## Uso da revisão arquitetural existente

`18-qualidade-arquitetural.md` continua sendo revisão opcional especializada. Quando
`TECHNICAL_QUALITY_REVIEW_STATUS=COMPLETE`, consumir apenas findings relevantes ao requisito atual.

Se a análise de requisitos/discovery detectar gatilho estrutural ainda não revisado, rotear primeiro
para `TECHNICAL_QUALITY_REVIEW`. Não duplicar DDD, coupling, patterns ou baseline desta skill.

## Decisões de design

Para cada decisão material, registrar:

```text
DESIGN_ID: SD-<N>
REQUIREMENTS: [R-...]
PROBLEM:
CONSTRAINTS:
SELECTED_APPROACH:
WHY_THIS_APPROACH:
PROJECT_EVIDENCE:
ALTERNATIVES_CONSIDERED:
TRADE_OFFS:
BOUNDARIES_AFFECTED:
CONTRACT_IMPACT:
RISK:
VALIDATION:
CONFIDENCE: HIGH | MEDIUM | LOW
```

Não criar `SD-*` para detalhe trivial ou escolha sintática.

## Regras de arquitetura proporcional

Análise aprofundada é necessária somente quando houver decisão material sobre:

- contrato público ou cross-repo;
- persistência/migração;
- transação/concorrência;
- segurança;
- integração externa/mensageria;
- dependência nova;
- boundary de domínio/módulo;
- mudança difícil de reverter;
- performance com requisito/medição real.

Para CRUD/local change simples, design curto é resultado válido.

## Boundary / side-effect check

Quando houver boundary relevante, registrar:

```text
BOUNDARY:
CURRENT_CONTRACT:
CHANGE:
CONSUMERS:
SIDE_EFFECT_RISK:
COMPATIBILITY:
VALIDATION:
```

"Nenhum efeito colateral" não é suposição válida; demonstrar por contrato, testes, fluxo ou escopo.

## Refactoring

Refactor entra na solução somente quando:

- é necessário para implementar com segurança o requisito; ou
- é pequeno, localizado e reduz risco/duplicação diretamente criada pela mudança.

Refactor amplo, modernização, limpeza geral ou pattern "melhor" deve permanecer como
`OPTIONAL_IMPROVEMENT` fora do escopo.

## Saída `02-design.md`

Produzir:

```text
DESIGN_SUMMARY:
SENIOR_CHECK_RESULT: PASS | MATERIAL_ALTERNATIVE_FOUND | BLOCKED
SELECTED_APPROACH:
REQUIREMENT_LINKS: []
PROJECT_PATTERNS_REUSED: []
DESIGN_DECISIONS: []
BOUNDARIES_AND_CONTRACTS:
RISKS_AND_MITIGATIONS:
OPTIONAL_IMPROVEMENTS_NOT_SELECTED:
OPEN_BLOCKERS: 0
```

Se houver alternativa material com trade-off que não possa ser inferido das decisões aprovadas,
registrar as opções para `05-solucao-proposta.md` apresentar ao usuário. Não pedir aprovação aqui.

## Handoff

Ao concluir:

```yaml
SOLUTION_DESIGN_STATUS: COMPLETE
CURRENT_STATE: SOLUTION_REVIEW
NEXT_ACTION: REVIEW_AND_APPROVE_SOLUTION
NEXT_MODEL_ROLE: HEAD_STRONG
```

Se `RECOVERY_STATUS=IN_PROGRESS`, manter o recovery ativo até a reaprovação dos contratos downstream afetados.
