# 01 — Primeiros passos

> HUMAN_ONLY. Este arquivo é para consulta do usuário e não deve ser carregado por agentes.

## Entrada principal

Quando o objetivo for executar uma história/bug de forma controlada, a entrada continua sendo o arquivo
da raiz:

```text
Leia e siga:
"<caminho>/orquestrador.md"

Jira: <ID ou URL>
Fluxo: QUICK | COMUM
```

O `orquestrador.md` decide retomada, fluxo, estado, skill, papel de modelo, contexto permitido e próximo
gate. Não é necessário chamar manualmente todas as skills.

## QUICK ou COMUM

### QUICK / AUTO-GO

Use para mudança pequena, localizada, inequívoca e de baixo risco. Em geral deve ser single-repo,
objetivamente testável e não exigir decisão arquitetural relevante.

O QUICK faz uma análise compacta antes da aprovação e, após `AUTO-GO`, executa RED, lock,
implementação e GREEN sem novas aprovações intermediárias até o handoff para o Judge.

Não é adequado quando houver sinal material de:

- banco/migração;
- mensageria;
- segurança;
- concorrência/transação relevante;
- contrato material entre serviços;
- cross-repo inesperado;
- regra de negócio ambígua;
- decisão estrutural/arquitetural.

Nesses casos o fluxo deve migrar para COMUM.

### COMUM / COMPLETA

Use quando a história precisa de investigação, análise de requisitos, desenho da solução, SPEC/plano,
RED, implementação, GREEN e julgamento completo.

Na dúvida entre QUICK e COMUM, prefira COMUM. QUICK reduz cerimônia; não reduz qualidade.

## FAST, STANDARD e CRITICAL

Esses valores representam **profundidade de execução**, não fluxos diferentes e não removem gates.

- `FAST`: mudança localizada, contrato conhecido e baixo risco;
- `STANDARD`: padrão para histórias e bugs comuns;
- `CRITICAL`: produção, cross-repo relevante, contrato público, persistência sensível, mensageria,
  concorrência, segurança ou alto potencial de regressão.

## NEW e RESUME

`NEW` significa iniciar uma feature nova.

`RESUME` significa retomar uma feature existente usando o `STATE.md`. O objetivo é continuar apenas a
partir de `NEXT_ACTION`, sem repetir fases já aprovadas salvo fato novo ou recovery formal.

A memória persistente da feature só nasce depois que o Jira é conhecido e a proteção de `.ai/` foi
confirmada.

## Acesso ao Jira

A skill `15-jira-access.md` recebe URL ou issue key, consulta o Jira usando credenciais locais e devolve
contexto efêmero. Ela não cria `.ai`, `STATE.md` ou `00-jira.md`.

Arquivo local esperado:

```text
infrastructure/jira/jira-auth.local.json
```

Credenciais não devem aparecer em logs, memória, commit ou PR.

## Uso consultivo de uma skill

Quando você quer apenas analisar algo sem executar a esteira completa, pode usar uma skill como
referência metodológica. Exemplos:

```text
skills/03-investigacao.md
→ entender fluxo ou investigar bug

skills/04a-analise-requisitos.md
→ encontrar lacunas e ambiguidades

skills/04b-design-solucao.md
→ desenhar/comparar solução

skills/18-qualidade-arquitetural.md
→ revisar arquitetura/patterns quando houver motivo real

skills/06-prd-plano.md
→ estruturar SPEC + plano

skills/10-juiz.md
→ revisão independente/evidence-or-zero
```

A pasta `documentacao-usuario/` não deve ser passada ao agente junto com essas skills.

## O que você normalmente controla

Você normalmente decide ou autoriza:

- QUICK ou COMUM;
- Jira/feature;
- respostas a perguntas realmente bloqueantes;
- `APROVAR SOLUÇÃO`;
- `APROVAR PRD/PLANO`;
- `APROVAR RED`;
- `GO` ou `AUTO-GO` conforme o fluxo;
- `REOPEN RED` quando recovery demonstrar necessidade real;
- `APROVAR QA`;
- modo de commit `AUTOMÁTICO | MANUAL | OUTROS`;
- se deseja descrição de PR;
- `ARQUIVAR` quando a entrega estiver resolvida;
- troca manual de modelo quando o runtime não fizer roteamento automático.

Veja [06-gates-e-comandos.md](06-gates-e-comandos.md) para a interpretação exata de cada comando.
