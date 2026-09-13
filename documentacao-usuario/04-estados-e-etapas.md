# 04 — Estados e etapas

> HUMAN_ONLY. Este arquivo é para consulta do usuário e não deve ser carregado por agentes.

Use este arquivo quando aparecer um nome como `INTAKE`, `PRD_PLAN_REVIEW` ou `GREEN_VALIDATION` e você
quiser saber rapidamente o que ele representa.

Os nomes em português são traduções humanas. O valor canônico continua sendo o nome em inglês.

## Referência rápida

| Estado canônico | Tradução humana | Skill principal | Papel |
|---|---|---|---|
| `MODEL_CONFIRMATION` | Confirmação de modelos | `00-bootstrap-modelos.md` | ORCHESTRATOR |
| `JIRA_ACCESS` | Acesso ao Jira | `15-jira-access.md` | `ECONOMICAL` |
| `INTAKE` | Triagem do Jira | `01-intake-jira.md` | `ECONOMICAL` |
| `MEMORY_LOOKUP` | Consulta de memória | `02-memoria-feature.md` | `ECONOMICAL` |
| `DISCOVERY` | Investigação | `03-investigacao.md` | `ECONOMICAL` |
| `REQUIREMENT_ANALYSIS` | Análise de requisitos | `04a-analise-requisitos.md` | `HEAD_STRONG` |
| `INTERVIEW_OPTIONAL` | Entrevista opcional | `04-entrevista-opcional.md` | `HEAD_STRONG` |
| `TECHNICAL_QUALITY_REVIEW` | Revisão de qualidade técnica | `18-qualidade-arquitetural.md` | `HEAD_STRONG` |
| `SOLUTION_DESIGN` | Desenho da solução | `04b-design-solucao.md` | `HEAD_STRONG` |
| `SOLUTION_REVIEW` | Revisão da solução | `05-solucao-proposta.md` | `HEAD_STRONG` |
| `PRD_PLAN_REVIEW` | Revisão da SPEC e plano | `06-prd-plano.md` | `HEAD_STRONG` |
| `RED_REVIEW` | Revisão do contrato RED | `07-testes-red.md` | `EXECUTOR` |
| `RED_EXECUTION` | Execução do RED | `07-testes-red.md` | `EXECUTOR` |
| `WAITING_GO` | Aguardando GO | `08-implementacao-go.md` | `EXECUTOR` |
| `IMPLEMENTING` | Implementação | `08-implementacao-go.md` | `EXECUTOR` |
| `REWORK_IMPLEMENTATION` | Correção da implementação | `08-implementacao-go.md` | `EXECUTOR` |
| `GREEN_VALIDATION` | Validação GREEN | `09-validacao-green.md` | `EXECUTOR` |
| `JUDGING` | Julgamento independente | `10-juiz.md` | `JUDGE_PRIMARY` |
| `JUDGE_RECOVERY` | Recuperação pós-Judge | `17-judge-recovery.md` | `HEAD_STRONG` |
| `QA_REVIEW` | Revisão de QA | `11-qa-pack.md` | `EXECUTOR` |
| `COMMIT_REVIEW` | Revisão/execução de commits | `12-commit-workflow.md` | `EXECUTOR` |
| `PR_DESCRIPTION` | Descrição de PR/MR | `13-pull-request-workflow.md` | `EXECUTOR` |
| `READY_TO_ARCHIVE` | Pronto para arquivar | `14-arquivamento.md` | `ECONOMICAL` |
| `QUICK_AUTOGO` | Execução rápida AUTO-GO | `16-quick-autogo.md` | `EXECUTOR` |

---

## `MODEL_CONFIRMATION` — Confirmação de modelos

**O que é:** bootstrap da sessão. Resolve se existe feature para retomar, confirma os bindings de papel
→ modelo e define roteamento manual ou automático.

**O que não faz:** não investiga código nem cria memória de feature nova antes de conhecer o Jira.

**Interação do usuário:** pode confirmar/alterar modelos e modo de roteamento.

---

## `JIRA_ACCESS` — Acesso ao Jira

**O que é:** recebe URL ou issue key, lê as credenciais locais e consulta a API do Jira.

**Saída:** contexto normalizado efêmero com `JIRA_CONTEXT_READY=true`.

**Importante:** não cria `.ai`, `STATE.md` ou `00-jira.md`; credenciais nunca entram na memória.

**Interação do usuário:** normalmente nenhuma, salvo erro de acesso ou anexo visual essencial.

---

## `INTAKE` — Triagem do Jira

**O que é:** transforma o contexto do Jira em ponto de partida da feature.

**Faz:** protege `.ai/` no Git, cria a pasta da feature, instancia `STATE.md`, persiste `00-jira.md`,
registra anchors, sinais de risco/cenário e nível de execução.

**Não faz:** não propõe implementação nem completa critérios ausentes por suposição.

**Próximo passo típico:** `MEMORY_LOOKUP`.

---

## `MEMORY_LOOKUP` — Consulta de memória

**O que é:** procura features anteriores relacionadas para evitar reinvestigação.

**Busca:** Jira, endpoint, classes, DTO/evento/tópico, domínio, repositórios e relações conhecidas.

**Regra:** memória ajuda, mas não substitui revalidação do código atual.

**Próximo passo típico:** `DISCOVERY`.

---

## `DISCOVERY` — Investigação

**O que é:** investigação dirigida do código e testes relevantes.

**Estratégia:** Codebase Recon `entry-point-first`, search-first e leitura mínima suficiente.

**Classificação de conclusões:** `FACT`, `INFERENCE`, `UNKNOWN`.

**Objetivo:** entregar fatos suficientes para requisitos e design sem mapear o repositório inteiro.

**Próximo passo típico:** `REQUIREMENT_ANALYSIS`, com troca para `HEAD_STRONG` quando o roteamento é manual.

---

## `REQUIREMENT_ANALYSIS` — Análise de requisitos

**O que é:** converte Jira + discovery em contrato de requisitos confiável antes do desenho da solução.

**Classifica itens materiais como:** `EXPLICIT_REQUIREMENT`, `IMPLICIT_NECESSITY`, `ASSUMPTION`,
`OPEN_QUESTION`, `TECHNICAL_RISK`, `OPTIONAL_IMPROVEMENT`.

**Pode bloquear?** Sim, somente se existir `OPEN_QUESTION` material que não possa ser resolvida com
segurança pelas evidências existentes.

**Saída:** `01-requirements.md`.

**Gate humano novo?** Não.

---

## `INTERVIEW_OPTIONAL` — Entrevista opcional

**O que é:** pergunta ao usuário somente o mínimo necessário para resolver uma questão realmente
bloqueante identificada na análise de requisitos.

**Não é:** uma rodada genérica de refinamento.

**Depois da resposta:** volta para `REQUIREMENT_ANALYSIS` para fechar/reclassificar o delta.

---

## `TECHNICAL_QUALITY_REVIEW` — Revisão de qualidade técnica

**O que é:** revisão arquitetural opcional e especializada.

**Quando aparece:** pedido explícito de arquitetura/qualidade ou evidência de problema estrutural
material. Arquivo grande, método longo ou preferência estética não bastam.

**Resultado válido:** `NO_CHANGE` também é conclusão completa.

**Saída:** `01-quality-review.md` quando ativada.

**Gate humano novo?** Não.

---

## `SOLUTION_DESIGN` — Desenho da solução

**O que é:** desenha a menor solução tecnicamente sólida antes do gate de solução.

**Senior Approach Check:** verifica alternativa mais simples, padrão equivalente existente,
acoplamento/abstração desnecessária, boundaries, contratos e efeitos colaterais.

**Regra principal:** seguir arquitetura válida existente e preferir a menor mudança suficiente.

**Saída:** `02-design.md`.

---

## `SOLUTION_REVIEW` — Revisão da solução

**O que é:** consolida requisitos + design + revisão arquitetural opcional em uma solução proposta.

**Valida:** cobertura dos requisitos, zero perguntas bloqueantes, assumptions materiais, contratos,
riscos, alternativas e ausência de scope creep.

**Gate:** `APROVAR SOLUÇÃO`.

**Saída aprovada:** `02-solution.md` e `SOLUTION_APPROVED=true`.

---

## `PRD_PLAN_REVIEW` — Revisão da SPEC e plano

**O que é:** cria a SPEC canônica e o plano de implementação.

**Observação:** o arquivo físico continua chamado `03-prd.md` por compatibilidade, mas seu significado é
SPEC canônica.

**Rastreabilidade:** `R-* -> AC-* -> DD-* -> PLAN-* -> arquivo/componente -> teste/evidência`.

**Gate:** `APROVAR PRD/PLANO`.

**Depois da aprovação:** a SPEC fica congelada para orientar RED, implementação, GREEN e Judge.

---

## `RED_REVIEW` — Revisão do contrato RED

**O que é:** planeja os testes/evidências que demonstrarão os critérios antes de editar os testes do
repositório.

**Importante:** neste estado ainda não se materializam os testes RED.

**Gate:** `APROVAR RED`.

**Validação mínima:** SPEC aprovada, zero questão bloqueante, todos os ACs com verificação planejada e
nenhum teste sem rastreabilidade.

---

## `RED_EXECUTION` — Execução do RED

**O que é:** materializa exatamente o contrato RED aprovado e comprova que os testes falham pelo motivo
esperado antes da implementação.

**Resultados inválidos:** `UNEXPECTED_PASS` ou `WRONG_FAILURE` não contam como RED válido.

**Ao final:** gera `red-tests.lock`, protege os testes e define `RED_LOCKED=true`.

**Próximo estado:** `WAITING_GO`.

---

## `WAITING_GO` — Aguardando GO

**O que é:** pausa explícita entre RED selado e implementação no fluxo COMUM.

**O que já aconteceu:** os testes RED foram aprovados, executados, falharam pelo motivo esperado e foram
protegidos pelo lock.

**O que falta:** autorização do usuário.

**Gate:** `GO`.

**Depois:** `IMPLEMENTING`.

---

## `IMPLEMENTING` — Implementação

**O que é:** implementação mínima necessária para satisfazer o contrato aprovado e levar os testes
selados a GREEN.

**No COMUM:** segue SPEC + plano + RED.

**No QUICK:** segue Quick Contract + RED.

**Proibido:** alterar testes RED selados ou redefinir requisitos para fazer a solução passar.

---

## `REWORK_IMPLEMENTATION` — Correção da implementação

**O que é:** correção técnica direcionada após Judge identificar `IMPLEMENTATION_DEFECT`, ou após
recovery concluir que somente a implementação precisa mudar.

**Não faz:** reinvestigação completa nem alteração do RED.

**Depois:** `GREEN_VALIDATION` e novo `JUDGING` fresh.

---

## `GREEN_VALIDATION` — Validação GREEN

**O que é:** prova mecanicamente que a implementação atende o contrato e preservou o RED lock.

**Verifica quando aplicável:** hashes do lock, compilação, testes RED, regressão, failures/skips
inesperados, evidência do contrato e diff dos testes selados.

**PASS não é interpretativo:** ausência de evidência vira `MISSING` ou `PENDING_EXTERNAL`, não PASS.

**Saída:** `07-green-evidence.md`.

---

## `JUDGING` — Julgamento independente

**O que é:** Judge avalia a entrega contra o contrato aprovado e as evidências observáveis.

**Contexto:** novo/fresh e read-only; não recebe histórico persuasivo do executor.

**Regra:** `sem evidência suficiente != PASS`.

**Vereditos:** `PASS`, `PASS_WITH_RISKS`, `FAIL`, `BLOCKED`.

**Se FAIL:** classifica a causa antes de rotear recuperação.

---

## `JUDGE_RECOVERY` — Recuperação pós-Judge

**O que é:** micro-fluxo para tratar `DISCOVERY_GAP`, `RED_CONTRACT_DEFECT` ou
`REQUIREMENT_AMBIGUITY` sem reiniciar a história inteira.

**Papel:** `HEAD_STRONG`.

**Pode concluir:** implementação apenas, decisão humana pendente ou necessidade real de reabrir RED.

**Se RED precisar mudar:** exige autorização humana exata `REOPEN RED`.

---

## `QA_REVIEW` — Revisão de QA

**O que é:** cria cenários de QA, collection Postman/Insomnia e guia para validação manual quando
aplicável.

**Gate:** `APROVAR QA`.

**Saídas típicas:** `09-qa-tests.md`, `10-qa-guide.md` e arquivos em `qa/`.

---

## `COMMIT_REVIEW` — Revisão/execução de commits

**O que é:** planeja e executa ou prepara commits de forma segura, agrupados por intenção.

**Modos:** `AUTOMÁTICO`, `MANUAL`, `OUTROS`.

**Regra:** commit é empacotamento/rastreabilidade, não fase para corrigir código.

**Proteção:** `.ai/` nunca pode ser stageada/commitada.

---

## `PR_DESCRIPTION` — Descrição de PR/MR

**O que é:** gera somente título e descrição final para o usuário copiar/colar manualmente.

**Não faz:** não acessa provider remoto, não cria PR/MR, não faz push, merge ou autenticação.

Mesmo a frase “abre o PR” significa, neste projeto, gerar a descrição para input manual.

---

## `READY_TO_ARCHIVE` — Pronto para arquivar

**O que é:** etapa final para transformar a entrega em memória reutilizável.

**Pré-condições:** Judge resolvido, QA resolvido conforme fluxo, commit resolvido, PR resolvido conforme
política e autorização `ARQUIVAR`.

**Saída:** `11-archive.md` e atualização do índice de features.

---

## `QUICK_AUTOGO` — Execução rápida AUTO-GO

**O que é:** fluxo compacto para tarefas simples.

**Antes do gate:** faz análise compacta de código, requisitos e solução e apresenta um Quick Contract.

**Gate:** `AUTO-GO`.

**Depois do AUTO-GO:** RED -> lock -> implementação -> GREEN sem novas aprovações intermediárias até o
handoff para Judge, salvo bloqueio real ou perda de elegibilidade do QUICK.
