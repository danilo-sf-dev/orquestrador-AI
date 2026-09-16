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
| `JUDGE_RECOVERY` | recovery dirigido de contrato, antes ou depois do Judge |
| `QA_REVIEW` | criação/revisão do material de QA |
| `COMMIT_REVIEW` | planejamento/execução segura dos commits |
| `PR_DESCRIPTION` | geração manual-input do título/descrição de PR/MR |
| `READY_TO_ARCHIVE` | pronto para gerar memória final |
| `QUICK_AUTOGO` | fluxo rápido com uma aprovação `AUTO-GO` |

Detalhes: [04-estados-e-etapas.md](04-estados-e-etapas.md).

## State machine / retomada

### `CURRENT_STATE`
Estado canônico cuja skill deve ser carregada numa execução ou `RESUME`.

### `NEXT_ACTION`
Ação mínima que informa o que a skill atual/próxima deve fazer. Na V1.9.3, cada fase concluída precisa
deixar `CURRENT_STATE + NEXT_ACTION` suficientes para retomada sem histórico do chat.

### `MODEL_ROLES_CONFIRMED_THIS_SESSION`
Confirmação dos bindings da sessão atual. É resetado a `false` ao iniciar uma nova sessão e não deve ser
herdado como verdade da sessão anterior.

## Papéis

| Termo | Tradução / significado |
|---|---|
| `ECONOMICAL` | coleta, busca, memória e compactação |
| `HEAD_STRONG` | análise/decisão material, design e recovery |
| `EXECUTOR` | RED, código, GREEN, QA e commit |
| `JUDGE_PRIMARY` | juiz independente principal |
| `JUDGE_SECONDARY` | segundo juiz independente para reforço |
| `MULTIMODAL` | informação visual essencial |

## Modos de fluxo

### `STANDARD_GATED`
Fluxo COMUM/COMPLETO com Requirements, Design, SPEC/plano e gates canônicos.

### `QUICK_AUTOGO`
Fluxo curto para tarefa simples, localizada e de baixo risco.

### `NEW`
Inicialização de feature nova.

### `RESUME`
Retomada por `STATE.md`, `CURRENT_STATE` e `NEXT_ACTION`.

## Profundidade

### `FAST`
Profundidade reduzida; não remove gates.

### `STANDARD`
Profundidade padrão.

### `CRITICAL`
Profundidade ampliada para produção, cross-repo, contrato, persistência, segurança etc.

## Requisitos

### `EXPLICIT_REQUIREMENT`
Requisito explícito no Jira ou decisão humana válida.

### `IMPLICIT_NECESSITY`
Condição técnica necessária para satisfazer requisito explícito sem inventar regra de negócio.

### `ASSUMPTION`
Inferência apoiada por evidência, com impacto/reversibilidade/confiança registrados.

### `OPEN_QUESTION`
Decisão material que não pode ser inferida com segurança. Só bloqueia quando muda comportamento,
contrato, negócio, segurança, persistência, integração ou desenho do RED.

### `TECHNICAL_RISK`
Risco que precisa de mitigação/validação; não é automaticamente novo requisito.

### `OPTIONAL_IMPROVEMENT`
Melhoria fora do escopo. Não vira AC/plano/RED/finding obrigatório sem aprovação.

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
Evidência prevista para fase externa/posterior.

### `MISSING`
Evidência necessária ausente.

## Contrato e rastreabilidade

### `SPEC`
Contrato canônico da feature no COMUM. Arquivo: `03-spec.md`.

### `SPEC_PLAN_REVIEW`
Estado em que SPEC + plano são construídos/revisados.

### `SPEC_PLAN_APPROVED`
Flag de aprovação da SPEC + plano.

### `R-*`
Requisito em `01-requirements.md`.

### `AC-*`
Critério de aceite testável/observável da SPEC.

### `SD-*`
Decisão material do design antes do gate de solução.

### `DD-*`
Design Decision aprovada; ADR-lite proporcional.

### `PLAN-*`
Unidade implementável do plano.

### `QC-*`
Referência a item material do Quick Contract quando templates RED/Judge estão no QUICK.

### Rastreabilidade STANDARD

```text
R/Jira -> AC -> DD -> PLAN -> arquivo/diff -> teste/evidência
```

### Rastreabilidade QUICK

```text
Quick Contract item -> arquivo/diff -> teste/evidência
```

## RED e GREEN

### `RED_REVIEW`
Desenha/revisa contrato de testes antes de editar testes do repositório.

### `RED_EXECUTION`
Materializa testes aprovados e comprova RED válido.

### `red-tests.lock`
Selo dos testes protegidos.

### `UNEXPECTED_PASS`
Teste planejado para RED passou antes da implementação; RED inválido.

### `WRONG_FAILURE`
Teste falhou pelo motivo errado; RED inválido.

### `GREEN_VALIDATION`
Validação mecânica de lock, compile, testes, regressão e evidência.

### `INVALID_GREEN`
GREEN inválido, por exemplo porque teste selado mudou sem `REOPEN RED`.

## Judge

### `fresh context`
Contexto novo, sem histórico de tentativa do executor.

### `read-only`
Judge lê/reroda verificações não destrutivas, mas não corrige código/teste/SPEC/RED.

### `PASS`
Contrato atendido com evidência suficiente.

### `PASS_WITH_RISKS`
Contrato atendido, com riscos/validações externas explícitas. Não cria novo gate; riscos seguem para QA.

### `FAIL`
Há requisito/comportamento material não atendido.

### `BLOCKED`
Falta condição/evidência essencial para julgar.

### `IMPLEMENTATION_DEFECT`
Código não atende; contrato/RED continuam válidos.

### `RED_CONTRACT_DEFECT`
RED aprovado representa incorretamente o comportamento esperado.

### `DISCOVERY_GAP`
Fato técnico relevante não foi descoberto antes.

### `REQUIREMENT_AMBIGUITY`
Decisão material de negócio/produto não pode ser inferida.

## Recovery

### `JUDGE_RECOVERY`
Nome canônico do micro-fluxo de recovery. Na V1.9.3 pode ser acionado antes ou depois do Judge.

### `RECOVERY_SOURCE`
Origem do finding:

```text
RED_EXECUTION | IMPLEMENTATION | GREEN_VALIDATION | QUICK_AUTOGO | JUDGE
```

### `RECOVERY_CLASS`
Classificação operacional do problema pré/pós-Judge, como `CONTRACT_MISMATCH`, `RED_CONTRACT_DEFECT`,
`DISCOVERY_GAP` ou `REQUIREMENT_AMBIGUITY`.

### `RECOVERY_RED_REOPEN_REQUIRED`
Indica que contratos superiores foram/serão revalidados, mas um RED já lockado ainda precisa do gate
humano `REOPEN RED` antes de ser alterado.

### `REOPEN RED`
Autorização humana exata para invalidar lock e aplicar somente o delta RED aprovado em recovery.

## Eficiência e contexto

### `lazy loading`
Carregar apenas o necessário para a fase atual.

### `search-first`
Localizar símbolos/anchors antes de abrir arquivos inteiros.

### `Codebase Recon`
Anchor Jira -> entry point -> fluxo relevante -> boundary/contrato -> testes -> dependências somente se
puderem mudar a decisão.

### `handoff`
Passagem compacta entre papéis. Aponta artefatos/decisões e não copia transcript.

### `HUMAN_ONLY`
`documentacao-usuario/**` é proibida para leitura, busca, indexação, handoff, memória e decisão dos agentes.

## QUICK

### `Quick Contract`
Contrato compacto aprovado antes de `AUTO-GO`.

### `AUTO-GO`
Autoriza RED -> lock -> implementação -> GREEN até Judge/bloqueio real.

### `NOT_REQUIRED_WITH_REASON`
No QUICK, QA pode ser dispensado quando não fizer sentido, mas a justificativa fica explícita antes de
seguir para commit.

## Legado `PRD`

`03-prd.md`, `PRD_PLAN_REVIEW`, `PRD_PLAN_APPROVED` e `APROVAR PRD/PLANO` são nomes históricos do conceito
hoje representado por SPEC. Novas features usam somente a nomenclatura SPEC.

## Outros termos

### `boundary`
Fronteira entre módulo, domínio, serviço, repositório ou contrato.

### `cross-repo`
Mudança cujo fluxo/contrato atravessa mais de um repositório.

### `scope creep`
Ampliação silenciosa do escopo além do Jira/decisões aprovadas.

### `archive`
Memória final concisa em `11-archive.md`.
