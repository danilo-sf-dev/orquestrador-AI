# 09 — Glossário PT-BR

> HUMAN_ONLY. Este arquivo é para consulta do usuário e não deve ser carregado por agentes.

Use `Ctrl + F` para procurar o termo exibido pelo Orquestrador. As traduções são explicativas; os nomes
canônicos continuam sendo os identificadores usados pelo sistema.

## Estados / steps

| Termo canônico | Tradução / significado rápido |
|---|---|
| `MODEL_CONFIRMATION` | confirmação de modelos/papéis da sessão |
| `JIRA_ACCESS` | acesso e leitura do Jira |
| `INTAKE` | triagem e inicialização da feature Jira |
| `MEMORY_LOOKUP` | consulta de memória de features relacionadas |
| `DISCOVERY` | investigação dirigida do código |
| `REQUIREMENT_ANALYSIS` | análise de requisitos, lacunas e ambiguidades |
| `INTERVIEW_OPTIONAL` | pergunta humana mínima para resolver bloqueio real |
| `TECHNICAL_QUALITY_REVIEW` | revisão técnica/arquitetural opcional |
| `SOLUTION_DESIGN` | desenho técnico da solução |
| `SOLUTION_REVIEW` | consolidação e aprovação da solução |
| `SPEC_PLAN_REVIEW` | criação/revisão da SPEC canônica e plano |
| `RED_REVIEW` | planejamento/revisão do contrato RED |
| `RED_EXECUTION` | criação e comprovação dos testes RED + lock |
| `WAITING_GO` | RED pronto; aguardando autorização `GO` |
| `IMPLEMENTING` | implementação |
| `REWORK_IMPLEMENTATION` | correção dirigida da implementação |
| `GREEN_VALIDATION` | validação mecânica do GREEN |
| `JUDGING` | julgamento independente |
| `JUDGE_RECOVERY` | recuperação após reprovação não trivial do Judge |
| `QA_REVIEW` | criação/revisão do material de QA |
| `COMMIT_REVIEW` | planejamento/execução segura dos commits |
| `PR_DESCRIPTION` | geração manual-input do título/descrição de PR/MR |
| `READY_TO_ARCHIVE` | pronto para gerar memória final |
| `QUICK_AUTOGO` | fluxo rápido com uma aprovação `AUTO-GO` |

Detalhes: [04-estados-e-etapas.md](04-estados-e-etapas.md).

## Papéis

| Termo | Tradução / significado |
|---|---|
| `ECONOMICAL` | papel econômico para coleta, busca, memória e compactação |
| `HEAD_STRONG` | analista principal para decisões materiais |
| `EXECUTOR` | executor de RED, código, GREEN, QA e commit |
| `JUDGE_PRIMARY` | juiz independente principal |
| `JUDGE_SECONDARY` | segundo juiz independente para reforço |
| `MULTIMODAL` | papel para informação visual essencial |

## Modos de fluxo

### `STANDARD_GATED`
Fluxo COMUM/COMPLETO com análise de requisitos, design, SPEC/plano e gates completos.

### `QUICK_AUTOGO`
Fluxo curto para tarefa simples, localizada e de baixo risco.

### `NEW`
Inicialização de feature nova.

### `RESUME`
Retomada de feature existente a partir de `STATE.md`/`NEXT_ACTION`.

## Profundidade

`FAST`, `STANDARD` e `CRITICAL` controlam profundidade, nunca removem gates.

## Requisitos

### `EXPLICIT_REQUIREMENT`
Requisito explícito no Jira ou decisão humana válida.

### `IMPLICIT_NECESSITY`
Condição técnica necessária para satisfazer requisito explícito.

### `ASSUMPTION`
Inferência apoiada por evidência; deve registrar impacto, reversibilidade e confiança.

### `OPEN_QUESTION`
Decisão material que não pode ser inferida com segurança. Só bloqueia quando muda comportamento,
contrato, negócio, segurança, persistência, integração, efeito destrutivo ou RED.

### `TECHNICAL_RISK`
Risco que precisa de mitigação/validação; não é automaticamente requisito novo.

### `OPTIONAL_IMPROVEMENT`
Melhoria fora do escopo; não vira AC/plano/RED/finding obrigatório sem aprovação.

## Evidência

### `FACT`
Confirmado por código, teste, configuração, contrato ou execução observável.

### `INFERENCE`
Conclusão provável apoiada por fatos, ainda não confirmada diretamente.

### `UNKNOWN`
Informação necessária que não pôde ser verificada.

### `evidence-or-zero`
Sem evidência suficiente não existe PASS por interpretação.

### `PENDING_EXTERNAL`
Evidência prevista para fase posterior, como QA/integration/external validation.

### `MISSING`
Evidência necessária ausente.

## Contrato e rastreabilidade

### `SPEC`
Contrato canônico da feature no fluxo COMUM. O arquivo atual é `03-spec.md`.

### `SPEC_PLAN_REVIEW`
Estado em que SPEC + plano são construídos/revisados antes do RED.

### `SPEC_PLAN_APPROVED`
Flag que registra aprovação da SPEC + plano.

### `R-*`
Identificador de requisito.

### `AC-*`
Critério de aceite testável/observável da SPEC.

### `SD-*`
Decisão material do design técnico.

### `DD-*`
Design Decision aprovada; ADR-lite proporcional.

### `PLAN-*`
Unidade implementável do plano.

### Rastreabilidade principal

```text
R/Jira -> AC -> DD -> PLAN -> arquivo/diff -> teste/evidência
```

## RED e GREEN

`RED_REVIEW` planeja; `RED_EXECUTION` materializa/comprova; `red-tests.lock` protege; `GREEN_VALIDATION`
prova implementação sem alterar contrato.

`UNEXPECTED_PASS` e `WRONG_FAILURE` não são RED válido. `INVALID_GREEN` indica GREEN inválido, por exemplo
por alteração de teste selado sem `REOPEN RED`.

## Judge

`fresh context` = contexto novo. `read-only` = Judge não corrige código/teste/SPEC.
Vereditos: `PASS`, `PASS_WITH_RISKS`, `FAIL`, `BLOCKED`.

Classes de FAIL: `IMPLEMENTATION_DEFECT`, `RED_CONTRACT_DEFECT`, `DISCOVERY_GAP`, `REQUIREMENT_AMBIGUITY`.

## Eficiência e contexto

`lazy loading` = carregar só o necessário; `search-first` = buscar antes de abrir; `Codebase Recon` =
seguir entry point/fluxo relevante; `handoff` = passagem compacta; `HUMAN_ONLY` = documentação exclusiva
do usuário, proibida para contexto operacional.

## QUICK

`Quick Contract` é contrato compacto antes de `AUTO-GO`. `AUTO-GO` autoriza RED -> lock -> implementação
-> GREEN até Judge/bloqueio real.

## Legado `PRD`

Ao consultar features antigas, você pode encontrar `03-prd.md`, `PRD_PLAN_REVIEW`, `PRD_PLAN_APPROVED`
ou `APROVAR PRD/PLANO`. Eles são nomes históricos do conceito hoje representado por `03-spec.md`,
`SPEC_PLAN_REVIEW`, `SPEC_PLAN_APPROVED` e `APROVAR SPEC/PLANO`.

## Outros termos

`boundary` = fronteira entre módulo/domínio/serviço/repo/contrato; `cross-repo` = mudança atravessa mais
de um repositório; `scope creep` = ampliação silenciosa do escopo; `recovery` = micro-fluxo dirigido por
finding; `archive` = memória final em `11-archive.md`.
