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

Inicialização de uma feature nova.

### `RESUME`

Retomada de feature existente a partir do `STATE.md`/`NEXT_ACTION`.

## Profundidade

### `FAST`

Profundidade reduzida para mudança localizada e baixo risco. Não remove gates.

### `STANDARD`

Profundidade padrão para histórias/bugs comuns.

### `CRITICAL`

Profundidade ampliada para risco alto, produção, cross-repo, contratos, persistência, segurança etc.

## Requisitos

### `EXPLICIT_REQUIREMENT` — Requisito explícito

Está no Jira ou em decisão humana válida.

### `IMPLICIT_NECESSITY` — Necessidade implícita

Condição técnica necessária para satisfazer requisito explícito sem inventar comportamento de negócio.

### `ASSUMPTION` — Hipótese/assunção

Inferência razoável apoiada por evidência. Deve registrar impacto se estiver errada, reversibilidade e
confiança.

### `OPEN_QUESTION` — Questão em aberto

Decisão material que não pode ser inferida com segurança.

Só bloqueia quando puder mudar materialmente comportamento, contrato, negócio, segurança, persistência,
integração, efeito destrutivo ou desenho do RED.

### `TECHNICAL_RISK` — Risco técnico

Risco que precisa de mitigação/validação; não é automaticamente um novo requisito.

### `OPTIONAL_IMPROVEMENT` — Melhoria opcional

Melhoria possível fora do escopo atual. Não vira AC, plano, RED ou finding obrigatório sem aprovação.

## Evidência

### `FACT` — Fato

Confirmado por código, teste, configuração, contrato ou execução observável.

### `INFERENCE` — Inferência

Conclusão provável apoiada por fatos, ainda não confirmada diretamente.

### `UNKNOWN` — Desconhecido

Informação necessária que não pôde ser verificada. Não deve ser preenchida por plausibilidade.

### `evidence-or-zero`

Regra do Judge: sem evidência suficiente não existe PASS por interpretação.

### `PENDING_EXTERNAL`

Evidência prevista para fase externa/posterior, como QA ou validação integrada.

### `MISSING`

Evidência necessária que está ausente.

## Contrato e rastreabilidade

### `SPEC`

Contrato canônico da feature no fluxo COMUM. O arquivo atual é `03-spec.md`.

### `SPEC_PLAN_REVIEW`

Estado em que SPEC + plano são construídos/revisados antes do RED.

### `SPEC_PLAN_APPROVED`

Flag que registra aprovação da SPEC + plano.

### `R-*`

Identificador de requisito em `01-requirements.md`.

### `AC-*`

Acceptance Criterion / critério de aceite testável/observável da SPEC.

### `SD-*`

Decisão material do design técnico antes do gate de solução.

### `DD-*`

Design Decision promovida/aprovada na solução; funciona como ADR-lite proporcional.

### `PLAN-*`

Unidade implementável do plano com resultado observável e rastreabilidade.

### Rastreabilidade principal

```text
R/Jira -> AC -> DD -> PLAN -> arquivo/diff -> teste/evidência
```

## RED e GREEN

### `RED`

Fase em que testes do comportamento ainda não implementado devem falhar pelo motivo esperado.

### `RED_REVIEW`

Desenha/revisa o contrato de testes antes de editar testes no repositório.

### `RED_EXECUTION`

Materializa testes aprovados, executa e comprova RED válido.

### `red-tests.lock`

Selo dos arquivos RED protegidos. Impede alteração silenciosa dos testes após aprovação.

### `UNEXPECTED_PASS`

Teste planejado para RED passou antes da implementação. Não conta como RED válido.

### `WRONG_FAILURE`

Teste falhou, mas pelo motivo errado. Também não conta como RED válido.

### `GREEN`

Fase em que implementação + testes selados devem passar mantendo lock e rastreabilidade.

### `INVALID_GREEN`

GREEN inválido, por exemplo porque teste selado foi modificado sem `REOPEN RED`.

## Judge

### `fresh context`

Contexto novo, sem carregar o histórico de tentativa do executor.

### `read-only`

Judge pode ler/rerodar verificações não destrutivas, mas não pode corrigir código, teste, SPEC ou RED.

### `PASS`

Contrato atendido com evidência suficiente.

### `PASS_WITH_RISKS`

Contrato atendido, mas permanecem riscos/validações externas explícitas que não invalidam o aceite.

### `FAIL`

Há `CRITICAL`/`MAJOR` ou requisito não atendido.

### `BLOCKED`

Falta condição/evidência essencial para julgar.

### `IMPLEMENTATION_DEFECT` — Defeito de implementação

Código não atende; contrato/RED continuam válidos.

### `RED_CONTRACT_DEFECT` — Defeito do contrato RED

RED aprovado representa incorretamente o comportamento esperado.

### `DISCOVERY_GAP` — Lacuna de investigação

Fato técnico relevante não foi descoberto antes.

### `REQUIREMENT_AMBIGUITY` — Ambiguidade de requisito

Decisão material de produto/negócio não pode ser inferida com segurança.

## Eficiência e contexto

### `lazy loading` — Carregamento preguiçoso/seletivo

Carregar apenas o necessário para a fase atual, em vez de todo o projeto/histórico.

### `search-first` — Buscar antes de abrir

Localizar símbolos/anchors primeiro e ler somente os arquivos/trechos relevantes.

### `Codebase Recon`

Reconhecimento dirigido do código: anchor Jira -> entry point -> fluxo relevante -> boundary/contrato ->
testes -> dependências adjacentes somente se puderem mudar a decisão.

### `handoff`

Passagem compacta entre papéis/modelos. Deve apontar artefatos e decisões em vez de copiar transcript.

### `HUMAN_ONLY`

Classificação da pasta `documentacao-usuario/**`. Significa que o conteúdo é exclusivo do usuário e
está proibido para leitura, busca, indexação, handoff, memória e decisão dos agentes.

## QUICK

### `Quick Contract`

Contrato compacto apresentado antes de `AUTO-GO`, contendo entendimento, requisitos/assumptions
relevantes, escopo provável, abordagem, RED planejado e riscos/gatilhos de escalonamento.

### `AUTO-GO`

Autorização única do QUICK para RED -> lock -> implementação -> GREEN até Judge/bloqueio real.

## Legado `PRD`

Ao consultar features antigas, você pode encontrar `03-prd.md`, `PRD_PLAN_REVIEW`, `PRD_PLAN_APPROVED`
ou `APROVAR PRD/PLANO`. Eles são nomes históricos do conceito hoje representado por `03-spec.md`,
`SPEC_PLAN_REVIEW`, `SPEC_PLAN_APPROVED` e `APROVAR SPEC/PLANO`.

## Outros termos

### `boundary`

Fronteira relevante entre módulo, domínio, serviço, repositório ou contrato.

### `cross-repo`

Mudança cujo fluxo/contrato atravessa mais de um repositório.

### `scope creep`

Ampliação silenciosa do escopo além do Jira/decisões aprovadas.

### `recovery`

Micro-fluxo de recuperação dirigido por finding, evitando reiniciar a história inteira.

### `archive`

Memória final concisa e pesquisável da feature em `11-archive.md`.
