# 07 — Memória e artefatos

> HUMAN_ONLY. Este arquivo é para consulta do usuário e não deve ser carregado por agentes.

## `.ai/` — memória operacional local

A pasta `.ai/` pertence à execução das features Jira e **não deve subir para o Git**.

Regras centrais:

```text
NEVER_STAGE
NEVER_COMMIT
NEVER_PUSH
```

Antes de criar/reusar `.ai/`, o fluxo deve confirmar que ela está efetivamente ignorada pelo Git. A
proteção é verificada novamente antes de commit.

A documentação humana é diferente: `documentacao-usuario/` é versionada no Git, mas proibida para
contexto dos agentes.

## Estrutura do fluxo COMUM

Uma feature COMUM pode ter:

```text
.ai/features/<JIRA-ID>/
  STATE.md
  00-jira.md
  01-discovery.md
  01-requirements.md
  01-quality-review.md     # opcional
  02-design.md
  02-solution.md
  03-prd.md                # SPEC canônica; nome físico legado
  04-implementation-plan.md
  05-red-tests.md
  red-tests.lock
  06-implementation-summary.md
  07-green-evidence.md
  08-judgement.md
  09-qa-tests.md            # quando QA existir
  10-qa-guide.md            # quando QA existir
  11-archive.md
  recovery/
  qa/
  delivery/
```

Nem todos os arquivos são obrigatórios em todos os cenários.

## Estrutura do QUICK

O QUICK evita criar artefatos completos apenas por cerimônia. Normalmente usa:

```text
STATE.md
00-jira.md
05-red-tests.md
red-tests.lock
06-implementation-summary.md
07-green-evidence.md
08-judgement.md
09-qa-tests.md       # se QA existir
10-qa-guide.md       # se QA existir
11-archive.md
delivery/
```

O contrato de comportamento aprovado é o Quick Contract.

## `STATE.md` — checkpoint operacional

É um arquivo curto para dizer onde a feature está e o que acontece depois.

Campos importantes:

```text
FLOW_MODE
LIFECYCLE
CURRENT_STATE
NEXT_ACTION
EXECUTION_LEVEL
CURRENT_MODEL_ROLE
NEXT_MODEL_ROLE
MODEL_HANDOFF_REQUIRED
SOLUTION_APPROVED
SPEC_STATUS
RED_APPROVED
RED_LOCKED
GREEN_STATUS
JUDGE_STATUS
QA_STATUS
COMMIT_STATUS
PR_STATUS
```

Ele não deve virar documentação completa da história. Detalhes ficam nos artefatos próprios.

## `00-jira.md` — snapshot normalizado do Jira

Guarda o contexto útil do card: título, descrição curta, critérios de aceite, anchors, referências de
arquitetura, repos/endpoints conhecidos, sinais de risco e perguntas iniciais.

Não guarda credenciais do Jira.

## `01-discovery.md` — evidência da investigação

Guarda o fluxo relevante descoberto, arquivos realmente importantes, fatos/inferências/desconhecidos,
contratos, testes existentes, riscos e lacunas.

Não deve conter dumps de grep/log/transcript.

## `01-requirements.md` — contrato de requisitos

Criado na análise de requisitos. Guarda:

- `R-*` requisitos explícitos/necessidades implícitas;
- `A-*` assumptions;
- `Q-*` open questions;
- `TR-*` riscos técnicos;
- `OI-*` melhorias opcionais;
- itens fora de escopo.

## `01-quality-review.md` — revisão técnica opcional

Só existe quando a revisão arquitetural é realmente ativada. Findings usam `TQ-*` e não viram
obrigação de implementação automaticamente.

## `02-design.md` — desenho técnico

Registra a abordagem selecionada, Senior Approach Check, decisões de design `SD-*`, boundaries,
contratos, riscos e alternativas materiais.

## `02-solution.md` — solução aprovada

Consolida a solução apresentada ao usuário no gate `APROVAR SOLUÇÃO`. Decisões arquiteturais materiais
promovidas usam `DD-*`.

## `03-prd.md` — SPEC canônica

O nome físico é legado por compatibilidade. O conteúdo atual representa a SPEC aprovada.

Ela define comportamento observável, ACs, constraints, assumptions aceitas, contratos, requisitos não
funcionais, decisões e riscos/validação.

Depois de `APROVAR PRD/PLANO`, a SPEC fica congelada. Mudança material posterior precisa voltar à fase
responsável; não pode ser feita silenciosamente pelo executor.

## `04-implementation-plan.md` — plano

Organiza unidades `PLAN-*`, dependências, ACs/requisitos relacionados, arquivos esperados/confirmados,
testes e forma de verificação.

## `05-red-tests.md` — contrato RED

Descreve os testes/evidências planejados e, após execução, registra a prova real de RED.

O teste deve falhar pelo motivo esperado. `UNEXPECTED_PASS` ou `WRONG_FAILURE` não são RED válido.

## `red-tests.lock` — proteção do RED

Registra os arquivos de teste protegidos e seus hashes. Depois de `RED_LOCKED=true`, implementação,
GREEN e rework normal não podem alterar esses testes.

Só `REOPEN RED`, após recovery formal, autoriza invalidar o lock e produzir um novo.

## `06-implementation-summary.md` — resumo da implementação

Registra arquivos alterados, comportamento implementado, origem no contrato/plano, desvios aprovados e
pendências/riscos. Não é diário de tentativas.

## `07-green-evidence.md` — evidência GREEN

Registra lock antes/depois, compilação, comandos de teste, falhas/erros/skips reportados, evidência do
contrato, regressão relacionada e limitações.

## `08-judgement.md` — julgamento

Contém veredito do Judge, avaliação por AC, findings e selo/hash do escopo efetivamente julgado.

Se o escopo de código julgado mudar depois, o julgamento fica stale e é necessário novo GREEN/Judge.

## QA

```text
09-qa-tests.md
10-qa-guide.md
qa/
```

Guarda cenários, guia e entregáveis de QA. DOCX é gerado quando o ambiente suporta; não deve ser
simulado quando não for possível gerar.

## `delivery/`

Guarda registros de entrega, como:

```text
delivery/commit.md
delivery/pull-request.md
delivery/pr/<repo>.md   # cross-repo quando necessário
```

## `11-archive.md` — memória final

É a memória pesquisável da feature concluída. Guarda apenas conhecimento reutilizável: decisões,
contratos, regras, classes/endpoints relevantes, testes, riscos e relações com outras features.

`13-archive.md` pode existir em versões antigas e é tratado como legado.

## `.ai/FEATURE_INDEX.md`

Índice pequeno para localizar features anteriores por Jira, endpoint, classe, domínio, integração,
repositório e tags sem carregar todo o histórico.
