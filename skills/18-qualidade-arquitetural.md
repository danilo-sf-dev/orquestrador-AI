---
name: qualidade-arquitetural
role: technical_quality_review
preferred_model_role: HEAD_STRONG
writes: [01-quality-review.md, STATE.md]
context_loading: lazy
reads:
  - STATE.md
  - 00-jira.md
  - 01-discovery.md
  - 01-requirements.md
  - source_code_relevant_only
  - tests_relevant_only
  - project_quality_configuration_relevant_only
  - skills/references/quality/quality-baseline.md
forbidden_reads:
  - chat_transcript
  - raw_build_logs_unless_relevant
  - unrelated_source_files
  - bulk_feature_history
forbidden_writes:
  - source_code
  - tests
  - approved_specs
  - approved_plan
---

# Skill — Qualidade arquitetural

## Objetivo
Decidir, com evidência, se uma mudança precisa de melhoria estrutural além da solução local. `NO_CHANGE`
é resultado completo. Esta etapa é opcional: não é checklist geral nem autorização para modernização.

## Modo consultivo
Quando referenciada diretamente em modo somente leitura, sem Jira/`STATE.md`, não criar memória nem
editar arquivos. Usar somente o escopo fornecido e manter as mesmas exigências de evidência e simplicidade.

## Quando ativar
Ativar somente se ao menos uma condição for verdadeira:

1. solicitação pede explicitamente dívida técnica, qualidade, arquitetura ou Design Patterns;
2. discovery/requirement analysis comprova repetição em dois ou mais locais independentes que devem evoluir juntos;
3. há violação única de alto impacto em contrato público, segurança, transação, integração,
   desempenho medido ou fronteira de domínio;
4. a solução local manteria problema consistente e exige comparar alternativa estrutural.

Não ativar para bug/feature localizada, CRUD simples, configuração ou preferência estética. Tamanho de
arquivo, linhas, grep ou nome de pattern são apenas sinais para investigar.

Sem gatilho:

```yaml
TECHNICAL_QUALITY_REVIEW_STATUS: NOT_REQUIRED
```

Com gatilho, registrar `REQUIRED`; ao concluir, marcar `COMPLETE`. Esta skill não cria gate humano.

## Ordem de análise
1. Confirmar quais `R-*`/riscos motivam a revisão.
2. Identificar convenções e fronteiras válidas em código, testes e configurações ativas.
3. Descrever problema observável, repetição, impacto e risco de não mudar.
4. Considerar a menor correção local antes de abstração.
5. Só então comparar refactor, princípio, pattern ou mudança arquitetural.
6. Escolher a alternativa de menor complexidade total que preserve comportamento e requisitos.

Ler `references/quality/quality-baseline.md` para critérios mínimos. Ler
`pattern-and-architecture-selection.md` somente quando pattern, DDD, camadas, ports/adapters ou mudança
de fronteira forem candidatos reais.

## Regras de decisão
- consistência local válida vem antes de preferência técnica;
- não perpetuar convenção quando ela for causa comprovada do problema;
- interface, camada, factory, wrapper, DTO, pattern ou módulo novo precisa de benefício demonstrável;
- não criar duas arquiteturas concorrentes sem transição explícita;
- não usar DDD, Clean, Hexagonal ou SOLID como rótulo para reescrita;
- ganho de desempenho precisa de medição, contrato ou análise pertinente; hipótese é `INFERENCE`;
- duplicação pequena pode ser preferível a abstração que aumente acoplamento;
- comentário só deve registrar intenção/restrição/proveniência/motivo não evidente.

## Recorte Java/Spring
- preferir injeção por construtor para dependências relevantes;
- evitar `Object`, raw types, casts inseguros e `Map<String,Object>` como contrato quando tipo explícito for melhor;
- manter negócio fora de controller e infraestrutura fora do domínio quando essa fronteira já for válida;
- não exigir interface para todo service ou camada extra sem motivo;
- seguir JUnit/Mockito/Testcontainers/logging/build/formatter/análise estática já configurados;
- não registrar dados sensíveis em logs/exceções.

## Saída `01-quality-review.md`
Produzir somente findings relevantes:

```text
PROJECT_CONVENTIONS:
- <padrão válido + evidências>

FINDING_ID: TQ-<N>
REQUIREMENTS: [R-...]
CLASSIFICATION: FACT | INFERENCE | UNKNOWN
PROBLEM:
EVIDENCE: <arquivo:símbolo/linha, teste, configuração ou medição>
IMPACT: readability | maintainability | testability | correctness | performance | other
CONSISTENCY_WITH_PROJECT: preserves | corrects_existing_problem | diverges_with_justification
SIMPLEST_OPTION:
ALTERNATIVES_CONSIDERED:
RECOMMENDATION: NO_CHANGE | LOCAL_REFACTOR | DESIGN_PRINCIPLE | PATTERN | ARCHITECTURE_CHANGE
COMPLEXITY_COST: LOW | MEDIUM | HIGH
RISK_AND_MIGRATION:
VALIDATION:
CONFIDENCE: HIGH | MEDIUM | LOW
```

Limitar a cinco findings; em `CRITICAL`, no máximo dez. Não incluir catálogo de patterns sem ligação
com código/requisito.

## Handoff
Encaminhar `01-quality-review.md` para `SOLUTION_DESIGN`. `04b-design-solucao.md` decide se uma
recomendação compõe o design; `05-solucao-proposta.md` continua sendo o gate que promove decisões para
`DD-*`. Itens não escolhidos não seguem como obrigação.

```yaml
TECHNICAL_QUALITY_REVIEW_STATUS: COMPLETE
CURRENT_STATE: SOLUTION_DESIGN
NEXT_ACTION: DESIGN_SOLUTION
```
