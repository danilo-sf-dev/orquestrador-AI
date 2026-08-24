# Workflow agêntico para Java/Spring Boot — V1.5

Este pacote define uma esteira agnóstica de modelos para histórias Jira, bugs, mudanças cross-repo, testes unitários, QA, commit e Pull Request.

## Foco da V1.5

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

A regra central é: **mesma ou maior qualidade com menos contexto fixo, menos releitura e menos reinvestigação**.

---

## Entrada única

```text
/orquestrador
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

- `HEAD_STRONG`: DeepSeek V4 Pro
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
+ reads permitidos
+ código/testes necessários
```

README, demais skills, cenários, templates, transcript e logs brutos não entram automaticamente.

---

## RESUME

Cada feature usa `.ai/features/<JIRA-ID>/STATE.md` com:

```text
LIFECYCLE
CURRENT_STATE
NEXT_ACTION
SCENARIO
```

Pode existir mais de uma feature `ACTIVE|PAUSED`. Se `/orquestrador` encontrar múltiplas candidatas sem Jira explícito, pergunta qual retomar.

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
Jira
-> Memory
-> Discovery
-> Interview somente se necessário
-> Solution [APROVAR SOLUÇÃO]
-> PRD/Plan [APROVAR PRD/PLANO]
-> RED happy path + edge cases [APROVAR RED + LOCK]
-> GO
-> Implementation
-> GREEN
-> Judge fresh-context/read-only
-> QA Pack [APROVAR QA]
-> Commit [CONFIRMAR]
-> PR quando solicitado
-> Archive [ARQUIVAR]
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

Após aprovação, `red-tests.lock` sela os arquivos. GREEN não pode alterar RED para fabricar aprovação. Se um teste aprovado estiver errado, usar `REOPEN RED`.

---

## Judge

Judge:

- inicia em contexto novo;
- recebe somente artefatos/evidências permitidos;
- não recebe transcript/tentativas do executor;
- não edita código ou testes;
- em `FAIL`, devolve findings e retorna para implementação.

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

- `skills/12-commit-workflow.md`: commit é empacotamento/rastreabilidade; preserva RED/GREEN/Judge e exige confirmação final. Registro novo: `delivery/commit.md`.
- `skills/13-pull-request-workflow.md`: PR/MR somente sob pedido explícito (`ABRIR PR PARA develop`); respeita template corporativo e nunca faz merge/force push automaticamente. Registro novo: `delivery/pull-request.md`.

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

- `orquestrador.md`: core mínimo de estado/roteamento/gates/lazy loading;
- `skills/`: execução detalhada por fase;
- `skills/cenarios/`: overlays on-demand sem alterar gates;
- `templates/STATE.md`: memória operacional e RESUME;
- `templates/handoff-packet.md`: troca compacta de agente/modelo.
