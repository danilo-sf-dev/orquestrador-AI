# IaC hardening — correções típicas com trade-offs

Ler quando o gate de IaC acusar achados. Cada correção abaixo tem um custo: aplicar sem entender o
trade-off pode quebrar o ambiente local/gate. Sempre apresentar o trade-off ao usuário.

## Segredo literal em arquivo de configuração

**Achado típico:** `Passwords And Secrets - Generic Secret` (severidade High), valor literal em YAML
de configuração de deploy.

**Por que é o achado mais perigoso:** é o que costuma ter associação direta com a política de
bloqueio. E, quando existe, o segredo normalmente **já está no histórico do git** — remover do
arquivo atual não apaga a exposição.

**Correção:**

```yaml
# antes
secrets:
  ALGUM_SEGREDO: 00000000-0000-0000-0000-000000000000

# depois — referência resolvida pelo ambiente de deploy
secrets:
  ALGUM_SEGREDO: ${ALGUM_SEGREDO_<AMBIENTE>}
```

**Trade-off:** a variável precisa existir no ambiente de deploy. Padronize o nome por ambiente
(`_DEV` / `_HML` / `_PRD`) e garanta que o pipeline injeta o valor — senão a aplicação sobe sem o
segredo.

**Detalhe que causa retrabalho:** corrigir um ambiente e esquecer os outros. Quando houver múltiplos
arquivos por ambiente, **conferir todos** antes de fechar a tarefa.

**Follow-up obrigatório de segurança** (relatar, não fazer silenciosamente): o valor exposto deve ser
**rotacionado** na origem e o arquivo deve sair do versionamento (`git rm --cached`). Escrever o valor
em `.gitignore` só é eficaz para arquivos **nunca comitados** — se já está rastreado, continua rastreado.

## Container com capabilities irrestritas

**Achado típico:** `Container Capabilities Unrestricted` (Medium).

**Correção:** remover o que não é necessário.

```yaml
cap_drop:
  - ALL
```

Se o serviço realmente precisa de alguma capability, adicionar de volta só ela (`cap_add`) e registrar
o motivo.

**Trade-off:** alguns serviços dependem de capabilities para iniciar. **Testar o subir local** depois
da mudança — uma correção que impede o ambiente de subir não é uma correção.

## Porta publicada em todas as interfaces

**Achado típico:** `Container Traffic Not Bound To Host Interface` (Medium). Porta no formato
`"porta:porta"` fica exposta em `0.0.0.0`.

**Correção:** restringir ao loopback quando o consumo é local.

```yaml
ports:
  - "127.0.0.1:8080:8080"
```

**Trade-off:** só faz sentido para serviço de desenvolvimento local. Se algo fora da máquina precisa
acessar (outro host, outro container da rede externa), **não** aplicar — a correção seria exposição
consciente e documentada, não silenciada.

## Healthcheck ausente

**Achado típico:** `Healthcheck Not Set` (Medium).

**Correção:** declarar healthcheck usando ferramenta **existente na imagem** (verificar antes, não
assumir que `curl` existe).

```yaml
healthcheck:
  test: ["CMD-SHELL", "<comando-disponivel> || exit 1"]
  interval: 5s
  timeout: 3s
  retries: 20
```

**Cuidado com jobs one-shot** (containers que inicializam e terminam): o healthcheck precisa refletir
"terminou", não "está servindo". Um padrão que funciona é o job criar um arquivo marcador ao concluir
e o healthcheck testar a existência dele.

## Ruído de severidade

Nem todo achado é bloqueio. Reportar sempre **severidade + se aquele gate falha o build**. Itens de
severidade informativa (ex.: volumes compartilhados entre containers) aparecem no relatório e
normalmente **não** bloqueiam — não gastar esforço do usuário com eles sem explicar isso.

## Ordem recomendada de trabalho

1. Corrigir primeiro o que pertence a um gate **com** bloqueio (é o que impede o deploy).
2. Corrigir depois o que é barato e seguro, se o usuário quiser reduzir ruído.
3. Registrar o resto com o trade-off, para decisão consciente.

Depois de cada rodada, **reexecutar o scan** e reportar a contagem antes/depois — só a reexecução
prova que o gate ficou verde.
