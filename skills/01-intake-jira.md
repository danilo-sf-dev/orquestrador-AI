---
name: intake-jira
role: intake
preferred_model_role: ECONOMICAL
context_loading: lazy
reads:
  - STATE.md_if_exists
  - jira_input
  - user_provided_assets
writes:
  - 00-jira.md
  - STATE.md
forbidden_reads:
  - all_source_code
  - unrelated_features
  - chat_transcript
forbidden_writes:
  - source_code
  - tests
---

# Skill — Intake do Jira

## Entrada mínima
- número do card Jira;
- breve descrição.

## Persistência NEW

No fluxo `NEW`, somente após o `JIRA-ID` estar conhecido:

1. criar `.ai/features/<JIRA-ID>/`;
2. instanciar `STATE.md` a partir do template;
3. registrar `CURRENT_STATE=INTAKE` e a próxima ação;
4. persistir o snapshot em `00-jira.md`.

Nunca criar um `STATE.md` órfão antes de conhecer o Jira.

## Extrair, quando disponível
- título;
- descrição;
- critérios de aceite;
- subtasks relevantes;
- endpoints/URLs;
- payloads e schemas;
- referências de arquitetura;
- imagens/diagramas/prints;
- dependências/links;
- contexto de bug;
- ambiente afetado;
- evidências/logs.

## Regra de âncoras
Se o card trouxer `/v1/orcamento/api-unica`, nomes de controller, evento, tópico, tabela, classe ou imagem arquitetural, registrar como `ANCHORS` e usá-los na investigação dirigida.

## Sinais de cenário
Registrar apenas fatos úteis para carregar um overlay on-demand, por exemplo:
- `PRODUCTION_BUG`;
- `CROSS_REPO`;
- `KNOWN_CHANGE_LOCATION`;
- `STANDARD_STORY`.

Esses sinais **não alteram os gates globais**. Servem somente para profundidade de investigação, contexto e recomendações adicionais (por exemplo, segundo Judge em produção/cross-repo).

## Nível de execução (profundidade)

Classificar inicialmente como `FAST`, `STANDARD` ou `CRITICAL` e registrar em `STATE.md`. A classificação controla apenas profundidade de discovery/verificação; **não altera gates**.

- `FAST`: mudança localizada, contrato conhecido, baixo risco, poucos arquivos/fluxo bem delimitado;
- `STANDARD`: default para histórias e bugs comuns;
- `CRITICAL`: produção, cross-repo relevante, contrato público, persistência sensível, mensageria, concorrência, segurança ou alto potencial de regressão.

Na dúvida, usar `STANDARD`. Nunca reduzir automaticamente para `FAST` quando existir sinal material de risco.

## Saída `00-jira.md`

```text
JIRA_ID:
TITLE:
SHORT_DESCRIPTION:
ACCEPTANCE_CRITERIA:
ANCHORS:
ARCHITECTURE_REFERENCES:
KNOWN_REPOS:
KNOWN_ENDPOINTS:
RISK_SIGNALS:
SCENARIO_SIGNAL:
OPEN_QUESTIONS:
```

## Não fazer
- não propor implementação;
- não entrevistar prematuramente;
- não completar critérios ausentes por suposição;
- não agrupar ou remover gates por considerar a tarefa simples.
