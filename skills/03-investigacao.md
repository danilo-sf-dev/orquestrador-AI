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
- contratos;
- testes existentes;
- comportamento atual;
- divergências com Jira;
- riscos observados;
- `DECISION_REQUIRED`;
- `UNKNOWN`.

## Regra de eficiência
Não persistir `cat/grep/log` bruto. Compactar evidências e apontar caminho/símbolo/linha quando possível. Tentativas sem valor não viram memória permanente.
