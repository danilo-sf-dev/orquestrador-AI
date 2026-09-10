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

Decidir, com evidência, se uma mudança precisa de melhoria estrutural além da solução local. A saída
pode recomendar nenhuma mudança arquitetural. Esta é uma etapa opcional: não é um checklist geral
nem autorização para modernização ampla.

## Modo consultivo

Quando for referenciada diretamente em modo somente leitura, sem Jira/`STATE.md`, não criar memória
nem editar arquivos. Usar apenas o escopo fornecido e apresentar a estrutura de saída no chat. As
mesmas exigências de evidência, simplicidade e aderência ao projeto continuam válidas.

## Quando ativar

Ativar somente se ao menos uma condição for verdadeira:

1. a solicitação pede explicitamente avaliar dívida técnica, qualidade, arquitetura ou Design Patterns;
2. o discovery comprova repetição em dois ou mais locais independentes que devem evoluir juntos;
3. há uma violação única, mas de alto impacto, em contrato público, segurança, transação, integração,
   desempenho medido ou fronteira de domínio;
4. a solução local manteria um problema consistente e a decisão exige comparar uma alternativa estrutural.

Não ativar para bug ou feature localizada, CRUD simples, ajuste de configuração ou preferência estética.
Não ativar por tamanho de arquivo, número de linhas, número de ocorrências no grep ou nome de padrão
isoladamente: são sinais para investigar, não evidência suficiente.

Se não houver gatilho, `03-investigacao.md` registra:

```yaml
TECHNICAL_QUALITY_REVIEW_STATUS: NOT_REQUIRED
```

Se houver, registrar `REQUIRED`, fazer handoff para esta skill e, ao concluir, marcar `COMPLETE`.
Esta skill não cria um gate humano adicional; decisões que alteram a solução continuam sujeitas a
`APROVAR SOLUÇÃO` na skill 05.

## Ordem de análise

1. Identificar convenções e fronteiras válidas do projeto em código, testes e configurações ativas.
2. Descrever o problema observável, sua repetição, impacto e risco de não mudar.
3. Considerar a menor correção local antes de qualquer abstração.
4. Só então comparar refactor, princípio de design, pattern ou mudança arquitetural.
5. Escolher a alternativa de menor complexidade total que preserve comportamento, padrões válidos e
   requisitos não funcionais.

Ler [quality-baseline.md](references/quality/quality-baseline.md) para os critérios mínimos. Ler
[pattern-and-architecture-selection.md](references/quality/pattern-and-architecture-selection.md)
somente se um padrão, DDD, camadas, ports/adapters ou uma mudança de fronteira for candidato real.

## Regras de decisão

- Consistência local vem antes de preferência técnica. Reutilizar convenções válidas do projeto.
- Não perpetuar uma convenção quando ela for a causa comprovada do problema; delimitar migração,
  compatibilidade e coexistência temporária.
- Interface, camada, factory, wrapper, DTO, pattern ou módulo novo precisa ter responsabilidade e
  benefício demonstráveis. "Pode ser útil no futuro" não basta.
- Não criar duas arquiteturas concorrentes sem plano explícito de transição.
- Não usar DDD, Clean, Hexagonal ou SOLID como rótulo para uma reescrita. Aplicar apenas a parte que
  resolve o problema encontrado.
- Ganho de desempenho precisa de perfil, benchmark, contrato de latência/volume ou análise de
  complexidade pertinente. Hipótese de desempenho é `INFERENCE`, não fato.
- Uma duplicação pequena pode ser aceitável se a abstração compartilhada ocultar diferenças de domínio
  ou aumentar acoplamento.
- Um comentário só deve permanecer ou ser criado quando registra intenção, restrição, proveniência ou
  motivo não evidente. Não preservar comentário redundante por ser antigo ou gerado por agente.

## Recorte Java/Spring

Aplicar os princípios ao projeto, não a uma receita universal:

- preferir injeção por construtor para dependências externas, variáveis ou relevantes para teste;
- evitar `Object`, raw types, casts inseguros e `Map<String, Object>` como contrato quando um tipo de
  domínio, DTO, record ou enum expressar melhor o significado;
- manter regra de negócio fora de controller e detalhes de infraestrutura fora do domínio quando isso
  já for uma fronteira válida no projeto;
- não exigir interface para todo service, repositório sobre Spring Data ou camada extra sem motivo;
- seguir JUnit, Mockito, Testcontainers, logging, build, formatter e análise estática já configurados;
- não registrar dados sensíveis em exceções ou logs.

## Saída `01-quality-review.md`

Produzir somente findings relevantes:

```text
PROJECT_CONVENTIONS:
- <padrão válido + evidências>

FINDING_ID: TQ-<N>
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

`NO_CHANGE` é uma recomendação completa. Limitar a cinco findings; em `CRITICAL`, no máximo dez.
Não transformar todo sinal em finding nem incluir catálogo de patterns sem ligação com o código.

## Handoff

Encaminhar `01-quality-review.md` para `SOLUTION_REVIEW`. A skill 05 decide se uma recomendação vira
`DD-*` e entra no plano. Itens não escolhidos não seguem para implementação ou Judge como obrigação.
No fluxo completo, registrar `TECHNICAL_QUALITY_REVIEW_STATUS=COMPLETE` e
`NEXT_ACTION=SOLUTION_REVIEW`.
