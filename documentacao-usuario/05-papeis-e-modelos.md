# 05 — Papéis e modelos

> HUMAN_ONLY. Este arquivo é para consulta do usuário e não deve ser carregado por agentes.

Os **papéis** representam responsabilidades no fluxo. Eles não são estados e não são nomes fixos de
modelo. O binding papel → modelo pertence à sessão/runtime e pode mudar sem alterar o projeto.

## Referência rápida

| Papel canônico | Tradução humana | Uso principal | Preset atual |
|---|---|---|---|
| `ECONOMICAL` | Modelo econômico | coleta, busca, memória, evidência, archive | DeepSeek V4 Flash 0731 |
| `HEAD_STRONG` | Analista principal | requisitos, design, arquitetura, solução, planejamento, recovery | DeepSeek V4 Pro 0813 |
| `EXECUTOR` | Executor | RED, implementação, GREEN, QA, commit | GPT-5.6 Luna Pro |
| `JUDGE_PRIMARY` | Juiz principal | julgamento independente | DeepSeek V4 Pro 0813 fresh/read-only |
| `JUDGE_SECONDARY` | Segundo juiz | reforço independente em risco alto/divergência | Gemini 3.7 Flash ou outro independente |
| `MULTIMODAL` | Modelo multimodal | leitura visual quando realmente necessária | Gemini 3.7 Flash |

Os modelos acima são sugestões atuais, não configuração persistida do projeto.

## `ECONOMICAL` — Modelo econômico

Usado quando a tarefa pede coleta e compactação mais do que raciocínio arquitetural pesado.

Exemplos:

- `JIRA_ACCESS`;
- `INTAKE`;
- `MEMORY_LOOKUP`;
- `DISCOVERY`;
- `READY_TO_ARCHIVE`.

A estratégia é gastar menos na coleta e reservar modelos mais fortes para decisões materiais.

## `HEAD_STRONG` — Analista principal

Usado quando o fluxo precisa desambiguar, desenhar ou revisar decisões importantes.

Exemplos:

- `REQUIREMENT_ANALYSIS`;
- `INTERVIEW_OPTIONAL`;
- `TECHNICAL_QUALITY_REVIEW`;
- `SOLUTION_DESIGN`;
- `SOLUTION_REVIEW`;
- `SPEC_PLAN_REVIEW`;
- `JUDGE_RECOVERY`.

Ele pode propor/estruturar decisões, mas não substitui gates humanos obrigatórios.

## `EXECUTOR` — Executor

Responsável por transformar o contrato aprovado em testes, código, evidência e entrega.

Exemplos:

- `RED_REVIEW`;
- `RED_EXECUTION`;
- `IMPLEMENTING`;
- `REWORK_IMPLEMENTATION`;
- `GREEN_VALIDATION`;
- `QA_REVIEW`;
- `COMMIT_REVIEW`;
- `PR_DESCRIPTION`;
- `QUICK_AUTOGO`.

O executor não pode redefinir silenciosamente requisitos, SPEC ou RED para fazer a implementação passar.

## `JUDGE_PRIMARY` — Juiz principal

É separado do executor para preservar independência.

Regras centrais:

- contexto novo/fresh;
- read-only para código, testes e contratos;
- pode rerodar testes não destrutivos quando necessário;
- não corrige implementação;
- não edita RED;
- não recebe histórico de tentativa do executor;
- aplica `evidence-or-zero`.

Depois de qualquer correção de código, a entrega passa novamente por GREEN e Judge fresh.

## `JUDGE_SECONDARY` — Segundo juiz

Pode ser usado como reforço da mesma fase em risco alto, produção, cross-repo ou divergência relevante.

Não cria automaticamente um novo gate humano. Se os juízes discordarem de forma material, o fluxo fica
bloqueado para decisão humana; não há votação automática.

## `MULTIMODAL` — Modelo multimodal

É usado quando informação visual é realmente necessária, como diagrama/print de arquitetura que não
pode ser interpretado textualmente.

Não deve ser acionado apenas porque existe uma imagem anexada; a imagem precisa ser relevante à decisão.

## `ROUTING_MODE=manual`

Quando o roteamento é manual, o usuário troca o modelo ao mudar de papel.

Exemplo:

```text
DISCOVERY
ROLE=ECONOMICAL
       ↓
handoff solicitado
       ↓
REQUIREMENT_ANALYSIS
ROLE=HEAD_STRONG
```

O `STATE.md` usa:

```text
CURRENT_MODEL_ROLE
NEXT_MODEL_ROLE
MODEL_HANDOFF_REQUIRED
```

Quando `MODEL_HANDOFF_REQUIRED=true`, a próxima fase não deve começar antes da confirmação da troca.

## `ROUTING_MODE=automatic`

Só deve ser tratado como automático quando o runtime realmente tiver capacidade técnica para fazer a
troca de modelo/papel. Na ausência dessa garantia, o projeto considera o roteamento manual.

## Papel não é estado

Exemplo correto:

```text
STATE=GREEN_VALIDATION
ROLE=EXECUTOR
```

`GREEN_VALIDATION` diz **o que está acontecendo**. `EXECUTOR` diz **quem deve executar**.
