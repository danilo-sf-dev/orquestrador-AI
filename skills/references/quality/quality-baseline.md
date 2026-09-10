# Referência — Qualidade simples e sustentável

Use para avaliar um diff ou uma proposta quando a skill 18 for ativada. Não use como checklist
universal para reescrever código saudável.

## Prioridade

1. comportamento correto, segurança e contratos;
2. convenções válidas já adotadas pelo projeto e framework;
3. solução pequena, coesa e fácil de modificar;
4. teste executável e observável;
5. otimização comprovada, quando desempenho for requisito.

Uma convenção existente prevalece sobre esta referência, exceto quando for causa demonstrada de dano.

## Obrigatório (`MUST`)

- Preservar comportamento e contratos não alterados.
- Seguir convenções válidas de estrutura, nomenclatura, build, formatter, análise estática, testes e
  logging do projeto.
- Usar nomes que revelem responsabilidade e distingam conceitos de domínio; evitar nomes genéricos
  quando escondem significado.
- Manter tipos e contratos claros para dados que atravessam fronteiras relevantes.
- Cobrir comportamento novo relevante; correção de bug exige teste de regressão quando viável.
- Não expor segredo, dado pessoal ou credencial em log, exceção ou evidência.
- Justificar qualquer abstração, dependência ou mudança de fronteira que aumente o custo cognitivo.

## Orientação (`SHOULD`)

- Preferir métodos e módulos coesos a arquivos centrais que acumulam responsabilidades.
- Preferir retornos antecipados quando reduzirem aninhamento sem esconder o fluxo.
- Eliminar duplicação de regra de negócio que precisará evoluir em conjunto.
- Comentar intenção, restrição, decisão ou proveniência; remover comentário redundante ou desatualizado.
- Isolar I/O externo e dependências variáveis quando isso reduz acoplamento ou torna testes confiáveis.
- Manter comando de teste/build reproduzível pelos meios documentados do projeto.

## Sinais para investigar (`HEURISTIC`)

- método longo, arquivo grande, aninhamento profundo ou muitos resultados no grep;
- controller, service ou entidade com responsabilidades misturadas;
- vários condicionais que mudam juntos quando uma nova variante é adicionada;
- repetição de transformação, validação ou tratamento de erro em fluxos independentes;
- uso amplo de tipos genéricos, estado global ou chamadas diretas a infraestrutura;
- teste frágil, dependente de ambiente manual ou difícil de executar.

Esses sinais não justificam mudança sozinhos. Confirmar impacto, recorrência e alternativa simples.

## Java/Spring

- Preferir injeção por construtor para colaboração real; não criar interface para uma classe simples sem
  motivo de fronteira, variação ou teste.
- Preferir DTO, record, enum ou tipo de valor a mapas genéricos usados como contrato.
- Usar o padrão de tratamento de erro e logging existente; adicionar contexto útil sem dados sensíveis.
- Respeitar as convenções já estabelecidas para controller, serviço, persistência, transação e testes.
- Não migrar arquitetura por rótulo. Melhorar apenas a responsabilidade ou dependência que tem dano
  comprovado.
