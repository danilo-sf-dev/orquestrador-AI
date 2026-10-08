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
| `JUDGE_PRIMARY` | Juiz principal | julgamento read-only/evidence-isolated | DeepSeek V4 Pro 0813 |
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

É separado do executor para preservar independência de responsabilidade, não obrigatoriamente de conversa.

Regras centrais:

- read-only para código, testes e contratos;
- aplica `evidence-or-zero`;
- ignora conclusões persuasivas do executor;
- não usa histórico de tentativa/erro como evidência;
- pode rerodar testes não destrutivos quando necessário;
- não corrige implementação;
- não edita RED.

Por padrão, o Judge pode continuar **no mesmo chat**, após a troca para o modelo `JUDGE_PRIMARY`.

Se o chat estiver grande/poluído, mas as decisões ainda forem úteis, pode-se usar `COMPACT_CONTEXT` antes do
Judge. No VS Code isso corresponde a `/compact` quando disponível.

`FRESH_CONTEXT` fica reservado para situações em que isolamento extra realmente ajude: loops grandes,
contexto muito contaminado, auditoria independente, divergência entre juízes ou escolha explícita do usuário.

Depois de qualquer correção de código, a entrega passa novamente por GREEN e Judge.

## `JUDGE_SECONDARY` — Segundo juiz

Pode ser usado como reforço da mesma fase em risco alto, produção, cross-repo ou divergência relevante.

Não cria automaticamente um novo gate humano. Se os juízes discordarem de forma material, o fluxo fica
bloqueado para decisão humana; não há votação automática.

Para uma auditoria realmente independente entre juízes, `FRESH_CONTEXT` é recomendado, mas não é o padrão obrigatório de toda troca de modelo.

## `MULTIMODAL` — Modelo multimodal

É usado quando informação visual é realmente necessária, como diagrama/print de arquitetura que não
pode ser interpretado textualmente.

Não deve ser acionado apenas porque existe uma imagem anexada; a imagem precisa ser relevante à decisão.

## `MODEL_SWITCH` — Trocar modelo no mesmo chat

Esse é o comportamento padrão do Orquestrador.

```text
DISCOVERY [ECONOMICAL]
        ↓ selecionar outro modelo no mesmo chat
REQUIREMENT_ANALYSIS [HEAD_STRONG]
        ↓ selecionar outro modelo no mesmo chat
RED / IMPLEMENTATION / GREEN [EXECUTOR]
        ↓ selecionar outro modelo no mesmo chat
JUDGING [JUDGE_PRIMARY]
```

A conversa continua sendo a mesma. O Orquestrador apenas muda o papel/modelo responsável pela próxima fase.

## `COMPACT_CONTEXT` — Limpar parte do contexto sem sair da sessão

Use quando quiser continuar o mesmo Jira/chat, mas reduzir histórico antigo, outputs repetidos e exploração que
já não precisa ocupar a janela de contexto.

No VS Code/Copilot Chat, quando disponível:

```text
/compact
```

Também é possível orientar a compactação, por exemplo:

```text
/compact preserve SPEC, approved decisions, RED lock, CURRENT_STATE and NEXT_ACTION
```

A compactação **resume** o histórico; não é um reset total.

## `FRESH_CONTEXT` — Novo chat/contexto

É uma decisão separada da troca de modelo.

Usar quando houver motivo explícito, por exemplo:

- contexto extremamente poluído;
- recovery/loops grandes;
- necessidade de auditoria realmente independente;
- divergência relevante entre modelos;
- escolha manual do usuário.

No VS Code, `/clear` inicia uma nova sessão; portanto ele se comporta como `FRESH_CONTEXT`, não como
`COMPACT_CONTEXT`.

Quando `FRESH_CONTEXT` for usado, o agente recebe um handoff mínimo baseado em artefatos, não o transcript inteiro.

## `ROUTING_MODE=manual`

Quando o roteamento é manual, o usuário troca o modelo ao mudar de papel.

Exemplo:

```text
DISCOVERY
ROLE=ECONOMICAL
       ↓
MODEL_SWITCH no mesmo chat
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
Esse flag significa **trocar o modelo/papel**, não abrir um novo chat.

## `ROUTING_MODE=automatic`

Só deve ser tratado como automático quando o runtime realmente tiver capacidade técnica para fazer a
troca de modelo/papel. Na ausência dessa garantia, o projeto considera o roteamento manual.

Mesmo no modo automático, trocar modelo não implica `FRESH_CONTEXT`.

## Papel não é estado

Exemplo correto:

```text
STATE=GREEN_VALIDATION
ROLE=EXECUTOR
```

`GREEN_VALIDATION` diz **o que está acontecendo**. `EXECUTOR` diz **quem deve executar**.
