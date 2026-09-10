# Referência — Seleção proporcional de patterns e arquitetura

Ler somente quando uma alternativa estrutural for necessária. Pattern é meio; o objetivo é reduzir a
complexidade total e manter o projeto compreensível.

## Escada de decisão

1. corrigir localmente;
2. extrair método, classe ou módulo coeso;
3. reorganizar responsabilidades existentes;
4. aplicar princípio de design ou fronteira pequena;
5. aplicar Design Pattern;
6. alterar arquitetura ou iniciar migração.

Avançar de nível apenas se o anterior não resolver o problema de modo claro e sustentável.

## Candidatos comuns

| Evidência consistente | Candidato | Não usar quando |
|---|---|---|
| Variações de comportamento crescem e condicionais mudam juntos | Strategy ou State | há poucos casos estáveis e uma extração local resolve |
| Integração externa vaza modelos, erros ou vocabulário para o domínio | Adapter ou camada anticorrupção | o contrato externo já é o contrato interno e a conversão seria só repasse |
| Cliente precisa conhecer muitas operações de subsistema | Facade | a nova API esconderia operações que os clientes realmente precisam |
| Construção possui invariantes, muitos parâmetros ou etapas opcionais complexas | Factory ou Builder | construtor/factory local simples é legível |
| I/O externo impede teste, acopla o núcleo ou pode variar | port com adapter | a dependência é estável, local e a abstração não reduz acoplamento |
| Domínio complexo tem regras próprias, vocabulário e fronteiras que evoluem separadamente | DDD tático ou bounded context | é CRUD simples ou a linguagem de domínio ainda não foi entendida |

## Arquitetura

- Camadas, Clean e Hexagonal são opções para controlar direção de dependências e proteger regras de
  negócio; não são estrutura padrão obrigatória.
- Antes de mudar arquitetura, identificar fronteiras atuais, dependências proibidas, pontos de entrada,
  integrações e plano de migração compatível.
- Em Java/Spring, não introduzir controller-service-repository, ports/adapters ou interfaces em massa
  apenas porque a estrutura é conhecida. Manter a convenção existente quando ela resolve o problema.
- Se a arquitetura atual tiver problema comprovado, preferir migração incremental e compatível a uma
  reescrita ampla.

## Evidência de desempenho

Só recomendar mudança por desempenho quando houver métrica, perfil, SLO/SLA, volume conhecido ou
análise de complexidade aplicável. Comparar custo de CPU, memória, I/O, latência, contenção, queries ou
alocação conforme o caso. "Parece mais rápido" é insuficiente.

## Resultado aceitável

`NO_CHANGE` ou `LOCAL_REFACTOR` é preferível a Pattern/Architecture Change quando resolve o problema
com menos conceito novo, menos migração e menor risco operacional.
