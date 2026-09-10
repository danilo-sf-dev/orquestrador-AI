---
name: investigacao
role: discovery
preferred_model_role: ECONOMICAL
writes: [01-discovery.md, STATE.md]
context_loading: lazy
reads:
  - STATE.md
  - 00-jira.md
  - related_feature_memory_selected_only
  - source_code_relevant_only
  - tests_relevant_only
  - git_history_targeted_only
forbidden_reads:
  - chat_transcript
  - raw_build_logs_unless_relevant
  - unrelated_source_files
  - bulk_feature_history
forbidden_writes:
  - source_code
  - tests
  - approved_specs
---

# Skill — Investigação dirigida

## Objetivo
Mapear fatos suficientes para decidir a solução com o menor contexto possível.

## Profundidade por `EXECUTION_LEVEL`

O nível vem de `STATE.md` e **não muda gates**:

- `FAST`: confirmar âncoras, fluxo local, testes relacionados e impactos diretos; parar quando houver evidência suficiente para solução segura;
- `STANDARD`: investigação normal seguindo dependências relevantes do fluxo;
- `CRITICAL`: ampliar evidência para contratos, integrações, persistência/transação, regressões adjacentes e cross-repo quando aplicável.

Mesmo em `CRITICAL`, continuar search-first e evitar leitura indiscriminada do workspace.

## Search-first
Antes de ler arquivos inteiros:

1. consultar memória relacionada;
2. listar arquivos versionados quando necessário (`git ls-files` ou equivalente);
3. buscar anchors com ferramenta textual/simbólica disponível (`rg`, IDE search etc.);
4. localizar endpoint/classe/interface;
5. ler somente trechos/arquivos conectados ao fluxo;
6. aprofundar conforme a hipótese atual.

Não inventar comandos: usar ferramentas disponíveis no ambiente.

## Exclusões padrão
Não ler automaticamente, salvo se diretamente relevantes:

```text
.git/ (conteúdo interno)
target/
build/
dist/
node_modules/
generated/
coverage/
logs/
binários
dumps
relatórios extensos
```

Git continua permitido de forma **pontual** (`log`, `show`, `diff`, `blame`) quando ajudar a hipótese.

## Ordem de investigação
1. Começar pelas `ANCHORS` do Jira.
2. Localizar endpoint/controller.
3. Seguir chamadas apenas do fluxo relevante.
4. Identificar contratos externos e persistência.
5. Encontrar testes existentes cedo.
6. Identificar repos impactados.
7. Registrar dúvidas que exigem decisão humana ou do Head.

## Contrato de evidência

Toda conclusão que influencie solução, escopo ou risco deve ser classificada:

```text
FACT       = confirmado em código, teste, configuração, contrato ou execução observável
INFERENCE  = conclusão provável apoiada por fatos, ainda não confirmada diretamente
UNKNOWN    = informação necessária que não pôde ser verificada
```

Para `FACT` e `INFERENCE`, registrar quando possível:

```text
CLAIM:
CLASSIFICATION: FACT | INFERENCE
EVIDENCE: <arquivo:linha, símbolo, teste, configuração ou comando não destrutivo>
CONFIDENCE: HIGH | MEDIUM | LOW
IMPACT_IF_WRONG:
```

Código executável e testes atuais têm precedência sobre README ou memória antiga. Configuração
versionada e contratos ativos vêm depois. Documentação e memória são pistas que precisam de
revalidação. Conflitos entre fontes devem aparecer no discovery; nunca escolher silenciosamente a
fonte mais conveniente.

## Investigação por hipóteses

Usar quando a causa ou o comportamento não forem evidentes, especialmente em bugs, concorrência,
transações, integrações, estado inconsistente ou falha intermitente. Não forçar este protocolo para
uma alteração simples já localizada.

1. Descrever sintoma observado e comportamento esperado.
2. Formular pelo menos duas causas plausíveis antes de concluir.
3. Definir qual evidência confirmaria ou eliminaria cada hipótese.
4. Buscar a menor evidência discriminante primeiro.
5. Marcar cada hipótese como `CONFIRMED`, `REJECTED` ou `INCONCLUSIVE`.
6. Quando confirmada, registrar a cadeia `trigger -> causa -> efeito -> sintoma`.

Uma hipótese não vira fato por repetição. Se hipóteses materialmente diferentes permanecerem
plausíveis, registrar `DECISION_REQUIRED` ou `UNKNOWN` para tratamento por `HEAD_STRONG`.

## Padrões do projeto

Extrair somente padrões que alterem a decisão de implementação. Um padrão válido deve:

- aparecer em pelo menos dois locais independentes, preferencialmente três;
- ser não óbvio e reutilizável;
- ter evidência em caminhos/símbolos reais;
- explicar quando aplicar e quando não aplicar.

Não promover uso isolado, detalhe de uma única feature ou comportamento padrão do framework a
"padrão do projeto". Limitar a cinco padrões relevantes por discovery; em `CRITICAL`, no máximo dez.

## Encaminhamento opcional de qualidade arquitetural

Esta investigação não prescreve Design Pattern. Marcar `TECHNICAL_QUALITY_REVIEW_STATUS=REQUIRED` e
encaminhar para `18-qualidade-arquitetural.md` somente quando houver pedido explícito de qualidade/
arquitetura ou evidência de problema estrutural: repetição em dois ou mais locais independentes que
devem evoluir juntos, ou violação única de alto impacto em contrato, segurança, transação, integração
ou desempenho medido.

Sinais como arquivo grande, método longo, muitos resultados no grep ou gosto arquitetural não bastam.
Sem gatilho, marcar `TECHNICAL_QUALITY_REVIEW_STATUS=NOT_REQUIRED` e seguir para a próxima fase normal.

## Heurística Java/Spring
Pesquisar, conforme aplicável:

- `@RequestMapping`, `@GetMapping`, `@PostMapping`, `@PutMapping`, `@PatchMapping`;
- RestController;
- Service/UseCase;
- ports/adapters;
- Feign, WebClient, RestTemplate;
- Kafka/Rabbit/SQS/SNS;
- DTOs, mappers, Bean Validation;
- `@Transactional` e boundaries;
- repositories/JPA/entities;
- handlers de erro;
- testes JUnit/Mockito/Testcontainers;
- configs/yaml/env.

## Cross-repo
Se o fluxo sair do repo atual, registrar:

```text
SOURCE_REPO:
TARGET_REPO:
CALL_TYPE: REST|EVENT|DB|OTHER
CONTRACT:
ENTRYPOINT_TARGET:
DEPLOY_COUPLING:
```

## Output `01-discovery.md`
- mapa do fluxo atual;
- arquivos realmente relevantes;
- evidências classificadas como `FACT`, `INFERENCE` ou `UNKNOWN`;
- hipóteses consideradas e seu estado, somente quando o protocolo for necessário;
- padrões existentes relevantes, com pelo menos duas evidências;
- contratos;
- testes existentes;
- comportamento atual;
- divergências com Jira;
- riscos observados;
- `DECISION_REQUIRED`;
- `UNKNOWN`.
- se a revisão opcional foi requerida e por qual evidência.

## Regra de eficiência
Não persistir `cat/grep/log` bruto. Compactar evidências e apontar caminho/símbolo/linha quando possível. Tentativas sem valor não viram memória permanente.

Parar quando houver evidência suficiente para distinguir a solução segura, os impactos e as
incertezas materiais. Investigação adicional sem capacidade de mudar a decisão é desperdício de
contexto.
