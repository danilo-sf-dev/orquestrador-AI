# Workflow agêntico para Java/Spring Boot — V1.8.0

Este pacote define uma esteira agnóstica de modelos para histórias Jira, bugs, mudanças cross-repo, testes unitários, QA, commit e Pull Request.

## Foco da V1.8.0

1. **orquestrador pequeno**: estado + roteamento + gates + invariantes;
2. **lazy loading por contrato** (`reads/writes/forbidden_*`);
3. **RESUME entre sessões** sem reinvestigar;
4. **persistência somente após Jira conhecido** no fluxo NEW;
5. **handoff compacto** entre papéis/modelos;
6. discovery dirigido;
7. `FAST|STANDARD|CRITICAL` controlando **profundidade, nunca gates**;
8. **gates originais preservados**;
9. **QA original preservado**;
10. memória final compatível com `11-archive.md`;
11. observabilidade de custo/contexto por card.
12. discovery com evidência, confiança e hipóteses proporcionais ao risco;
13. decisões arquiteturais ADR-lite, sem overengineering;
14. plano rastreável `AC -> decisão -> unidade -> arquivo -> teste`;
15. Judge com revisão técnica proporcional ao diff;
16. skills principais abaixo de 400 linhas, com referências lazy-loaded quando necessário.
17. revisão de qualidade arquitetural opcional, acionada apenas por problema estrutural comprovado ou
    pedido explícito; busca simplicidade, manutenção e aderência ao padrão do projeto, não patterns
    por preferência.

A regra central é: **mesma ou maior qualidade com menos contexto fixo, menos releitura e menos reinvestigação**.

Para decidir entre pedido direto, fluxo `QUICK` e fluxo `COMUM`, consulte
[`guia-de-uso.md`](guia-de-uso.md). O guia também explica os papéis `ECONOMICAL`, `HEAD_STRONG`,
`EXECUTOR`, `JUDGE_*` e `MULTIMODAL`, com exemplos de bugs, planejamento, arquitetura e dívida
técnica.

---


### Regra crítica de execução por papel

A documentação de papel/modelo é executável, não apenas informativa.

Em `ROUTING_MODE=manual`, **toda transição entre papéis exige parada e troca manual de modelo antes da próxima skill**. O agente deve mostrar um `PHASE BANNER` com o estado canônico, skill, papel, modelo sugerido e ação do usuário.

Exemplo:

```text
STATE: RED_REVIEW
SKILL: 07-testes-red.md
ROLE: EXECUTOR
MODEL_SUGGESTED: GPT-5.6 Luna Pro
USER_ACTION: TROCAR PARA EXECUTOR E RESPONDER CONTINUAR RED
```

O agente não pode executar `RED_REVIEW` usando `ECONOMICAL` só porque a conversa já estava nesse modelo.

Os nomes canônicos dos estados também devem aparecer sem renomear/agrupar etapas. Isso evita divergência entre o que o orquestrador prescreve e o que a UI do agente comunica.

---

## Entrada única

No VS Code/Cursor, iniciar referenciando o arquivo:

```text
Leia e siga:
"E:\Program Cursor\orquestrador\orquestrador\orquestrador.md"
```

O orquestrador:

```text
resolve feature
-> RESUME ou NEW
-> confirma bindings de modelo da sessão
-> lê STATE
-> escolhe uma única skill
-> carrega somente o contexto permitido
-> executa a fase
-> respeita o gate fixo
-> salva NEXT_ACTION
-> faz handoff
```

A troca automática real de modelo depende do runtime/cliente suportar dispatcher por modelo. Sem isso, o mesmo contrato funciona por handoff manual.

---

## Papéis de modelo

- `HEAD_STRONG`
- `EXECUTOR`
- `ECONOMICAL`
- `MULTIMODAL`
- `JUDGE_PRIMARY`
- `JUDGE_SECONDARY`

Preset sugerido no bootstrap:

- `HEAD_STRONG`: DeepSeek V4 Pro 0813
- `EXECUTOR`: GPT-5.6 Luna Pro
- `ECONOMICAL`: DeepSeek V4 Flash 0731
- `MULTIMODAL`: Gemini 3.7 Flash
- `JUDGE_PRIMARY`: DeepSeek V4 Pro em fresh context/read-only

Não usar `.ai/config/model-profile.md`. O binding papel → modelo pertence à sessão/runtime.

---

## Lazy loading

Cada skill declara:

```yaml
context_loading: lazy
reads:
  - ...
writes:
  - ...
forbidden_reads:
  - ...
forbidden_writes:
  - ...
```

Durante uma fase, carregar apenas:

```text
orquestrador mínimo
+ STATE.md
+ skill atual
+ referência condicional indicada pela skill atual
+ reads permitidos
+ código/testes necessários
```

README, demais skills, todas as referências, cenários, templates, transcript e logs brutos não
entram automaticamente.

---

## RESUME

Cada feature usa `.ai/features/<JIRA-ID>/STATE.md` com:

```text
LIFECYCLE
CURRENT_STATE
NEXT_ACTION
SCENARIO
```

Pode existir mais de uma feature `ACTIVE|PAUSED`. Se `orquestrador.md` encontrar múltiplas candidatas sem Jira explícito, pergunta qual retomar.

Etapas aprovadas não são refeitas sem motivo explícito.

No fluxo `NEW`, `STATE.md` só é criado depois que o Jira for informado; o bootstrap anterior ao Jira permanece efêmero.

---

## Memória por feature

```text
.ai/
  FEATURE_INDEX.md
  features/
    JIRA-1234/
      STATE.md
      00-jira.md
      01-discovery.md
      01-quality-review.md  # somente quando a revisão opcional ocorrer
      02-solution.md
      03-prd.md
      04-implementation-plan.md
      05-red-tests.md
      red-tests.lock
      06-implementation-summary.md
      07-green-evidence.md
      08-judgement.md
      09-qa-tests.md
      10-qa-guide.md
      11-archive.md
      qa/
      delivery/
        commit.md
        pull-request.md
        pr/
```

`11-archive.md` permanece estável por compatibilidade. Commit e PR foram movidos para `delivery/`, portanto novas etapas de entrega não renumeram a memória histórica.

Leitura retrocompatível aceita `13-archive.md`, `11-commit.md` e `12-pull-request.md` de versões transitórias, mas novas gravações usam a estrutura acima.

---

## Fluxo

```text
JIRA_ACCESS [ECONOMICAL]
-> INTAKE [ECONOMICAL]
-> MEMORY_LOOKUP [ECONOMICAL]
-> DISCOVERY [ECONOMICAL]
-> HANDOFF para HEAD_STRONG quando necessário
-> INTERVIEW_OPTIONAL [HEAD_STRONG]
-> TECHNICAL_QUALITY_REVIEW [HEAD_STRONG] somente se evidência ou solicitação exigir
-> SOLUTION_REVIEW [HEAD_STRONG] [APROVAR SOLUÇÃO]
-> PRD_PLAN_REVIEW [HEAD_STRONG] [APROVAR PRD/PLANO]
-> HANDOFF para EXECUTOR
-> RED_REVIEW [EXECUTOR] [APROVAR RED]
-> RED_EXECUTION [EXECUTOR] [criar/executar RED + lock]
-> WAITING_GO [EXECUTOR] [GO]
-> IMPLEMENTING [EXECUTOR]
-> GREEN_VALIDATION [EXECUTOR]
-> HANDOFF para JUDGE_PRIMARY
-> JUDGING [JUDGE_PRIMARY]
-> HANDOFF para EXECUTOR
-> QA_REVIEW [EXECUTOR] [APROVAR QA]
-> COMMIT_REVIEW [EXECUTOR]
-> PR_DESCRIPTION [EXECUTOR] quando solicitado; somente título/descrição para input manual
-> READY_TO_ARCHIVE [ECONOMICAL]
```

`FAST`, `STANDARD` e `CRITICAL` existem apenas como níveis de **profundidade**. Eles reutilizam a mesma esteira e os mesmos gates: nenhum nível remove, agrupa ou pula aprovações. `STANDARD` é o default; sinais de risco impedem redução automática para `FAST`.

---

## Níveis de profundidade

- `FAST`: discovery/verificação mais curtos para mudança localizada e de baixo risco;
- `STANDARD`: default para histórias e bugs comuns;
- `CRITICAL`: investigação e julgamento mais profundos para produção, cross-repo, contratos, persistência, mensageria, concorrência, segurança e alto risco.

Os três níveis mantêm **Solução → PRD/Plano → RED → GO → GREEN → Judge → QA → Commit/Archive** com os mesmos gates.

---

## RED / GREEN

Testes RED devem incluir happy path e **edge cases aplicáveis** derivados de critérios, domínio, contratos e riscos.

A esteira separa explicitamente:

```text
RED_REVIEW    = desenhar/revisar o contrato + APROVAR RED
RED_EXECUTION = criar os testes aprovados + comprovar RED + gerar lock
```

Isso evita que a UI diga "RED aprovado" enquanto ainda está criando ou executando testes.

Após `RED_EXECUTION`, `red-tests.lock` sela os arquivos. GREEN/Rework não podem alterar RED para fabricar aprovação. `REOPEN RED` só pode ocorrer após recovery formal e autorização humana explícita com essa frase exata.

---

## Judge e recovery

Judge:

- inicia em contexto novo;
- recebe somente artefatos/evidências permitidos;
- não recebe transcript/tentativas do executor;
- não edita código ou testes;
- classifica todo `FAIL` antes do roteamento.

Classes:

```text
IMPLEMENTATION_DEFECT
RED_CONTRACT_DEFECT
DISCOVERY_GAP
REQUIREMENT_AMBIGUITY
```

`IMPLEMENTATION_DEFECT` vai para `REWORK_IMPLEMENTATION [EXECUTOR]`. As demais classes vão para `JUDGE_RECOVERY [HEAD_STRONG]`, executado por `skills/17-judge-recovery.md`. O recovery faz micro-investigação dirigida ao finding; não reinicia Discovery completo.

---

## QA

QA permanece como na esteira anterior:

- `09-qa-tests.md`;
- collection Postman/Insomnia;
- `10-qa-guide.md`;
- DOCX em `qa/` quando o ambiente suportar;
- gate obrigatório `APROVAR QA`.

---

## Commit e PR

- `skills/12-commit-workflow.md`: commit é empacotamento/rastreabilidade; preserva RED/GREEN/Judge, sempre faseia por intenção e oferece `AUTOMÁTICO`, `MANUAL` e `OUTROS`. AUTO executa grupos usando mensagem EN; MANUAL apresenta PT-BR + EN e aguarda aprovação/ajuste/outros. Registro: `delivery/commit.md`.
- `skills/13-pull-request-workflow.md`: `ABRIR PR` significa somente gerar título + descrição final para preenchimento manual. A skill não acessa provider remoto, não faz push e não cria PR/MR. Registro: `delivery/pull-request.md`.

Essas skills são lazy-loaded; o tamanho delas não entra no contexto normal da implementação.

---

## Handoff

`templates/handoff-packet.md` define o pacote compacto entre papéis/modelos. O handoff aponta para artefatos, em vez de copiar transcript ou contexto longo.

---

## Métricas

Quando disponíveis, acompanhar por card/fase/papel:

- `COST_USD`;
- `INPUT_TOKENS`;
- `CACHE_READ_TOKENS`;
- `OUTPUT_TOKENS`;
- `CACHE_HIT_RATIO`;
- `MODEL_ESCALATIONS`;
- duração;
- releituras/reinvestigação;
- findings do Judge;
- regressões.

Defaults:

```text
MONTHLY_BUDGET_USD=40
FEATURE_TARGET_USD=8
FEATURE_WARNING_USD=10
```

---

## Arquivos principais

- `guia-de-uso.md`: entrada recomendada por cenário e explicação dos papéis de modelo;
- `orquestrador.md`: core mínimo de estado/roteamento/gates/lazy loading;
- `skills/`: execução detalhada por fase;
- `skills/18-qualidade-arquitetural.md`: revisão opcional de qualidade, arquitetura e patterns;
- `skills/cenarios/`: overlays on-demand sem alterar gates;
- `templates/STATE.md`: memória operacional e RESUME;
- `templates/handoff-packet.md`: troca compacta de agente/modelo.


## Proteção da memória local `.ai/`

A pasta `.ai/` é sempre local e nunca deve subir para o Git. Ao criar ou reutilizar a pasta, o orquestrador deve garantir que `.ai/` está no `.gitignore` e confirmar que o Git realmente a ignora. A mesma validação é repetida obrigatoriamente antes de qualquer commit.


## Nomes canônicos de fase

Checklists e mensagens de progresso devem usar exatamente os estados definidos em `orquestrador.md`. Descrições amigáveis podem complementar, mas não substituir o nome canônico.

Isso é especialmente importante para que o usuário saiba quando precisa trocar de modelo em clientes sem roteamento automático.
