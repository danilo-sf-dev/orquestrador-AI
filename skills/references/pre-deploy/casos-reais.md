# Casos reais — sintoma, causa raiz e correção

Cada caso abaixo foi observado em um repositório real e confirmado por evidência (log da esteira,
saída de scanner ou `git`). Use como referência de diagnóstico quando a saída do script se parecer
com um deles. O projeto é citado como contexto; o **padrão** é o que importa.

---

## Caso 1 — Secret literal no arquivo de configuração de deploy (BLOQUEIA)

**Sintoma na esteira**

```text
Policy Management Violation - Break Build Enabled:
  Policy: Bloqueio IAC: Severidades Críticas e Altas | Break Build: true
  Violated Rules: Vulnerabilidade Alta detectada _ Corrija os alertas de IAC abaixo para prosseguir
...
ERROR: Bloqueio Checkmarx
Finished: ABORTED
```

Todas as etapas seguintes (`Build + Testes`, `Sonar`, `Build Imagem`, `Registrar Imagem`) aparecem
como `skipped due to earlier failure(s)` — ou seja, **nada foi construído**.

**O que o scanner aponta**

```text
Passwords And Secrets - Generic Secret  |  HIGH  |  CWE-798
  > config/values_prd.yaml:30  FORMA_PAGAMENTO_CLIENT_SECRET: <uuid-literal>
```

**Causa raiz confirmada (a parte que engana)**

O gate **IaC** era o único com `Break Build: true`. O gate **SCA** reportava 5 Critical + 7 High e
**não bloqueava**. O erro mais caro é supor que todo achado de severidade alta derruba o deploy —
nesse caso, só o de IaC derrubava.

E havia um detalhe de processo: os arquivos de **dev** e **hml** já haviam sido convertidos para
variável de ambiente em um commit anterior, mas o **PRD foi esquecido**. O build falhou pelo PRD.

**Correção aplicada**

```yaml
# antes
secrets:
  FORMA_PAGAMENTO_CLIENT_SECRET: 00000000-0000-0000-0000-000000000000

# depois — resolvido pelo ambiente de deploy
secrets:
  FORMA_PAGAMENTO_CLIENT_SECRET: ${FORMA_PAGAMENTO_CLIENT_SECRET_PRD}
```

**Lição transferível**

1. Ao corrigir um segredo, **varrer todos os arquivos por ambiente** (`dev`/`hml`/`prd`) no mesmo
   commit. Corrigir um e esquecer outro é o erro mais comum.
2. Confirmar no log **qual** gate tem break build antes de otimizar qualquer coisa.
3. O valor exposto já está no histórico do git: além de corrigir o arquivo, encaminhar **rotação**
   do segredo na origem.

---

## Caso 2 — Hardening de `docker-compose` (NÃO bloqueia, mas gera ruído)

**Sintoma**

Achados de severidade média no relatório de IaC, disputando atenção com o achado que realmente
bloqueia.

```text
Container Capabilities Unrestricted             | MEDIUM | CWE-400
Container Traffic Not Bound To Host Interface   | MEDIUM | CWE-693
Healthcheck Not Set                             | MEDIUM | CWE-703
Shared Volumes Between Containers               | INFO   | CWE-693
```

**Correção aplicada**

```yaml
services:
  servico:
    image: <imagem>
    cap_drop:                 # reduz capabilities ao mínimo
      - ALL
    security_opt:
      - no-new-privileges:true
    ports:
      - "127.0.0.1:8080:8080" # antes: "8080:8080" (expunha em 0.0.0.0)
    healthcheck:
      test: ["CMD-SHELL", "<comando-existente-na-imagem> || exit 1"]
      interval: 5s
      timeout: 3s
      retries: 20
```

Cuidados que evitaram retrabalho:

- **verificar a ferramenta dentro da imagem** antes de escrever o healthcheck (`curl` pode não existir);
- jobs **one-shot** (container que inicializa e termina) precisam de healthcheck que reflita
  "terminou" — usar arquivo marcador criado ao final do comando;
- `cap_drop: ALL` pode impedir o serviço de subir: **testar o `up` local** depois de aplicar;
- bind em `127.0.0.1` só vale para consumo local; se outro host precisa acessar, não aplicar.

**Lição transferível**

Achado de severidade média sem break build **não bloqueia**. Corrigir o que tem bloqueio primeiro;
o resto é melhoria incremental. Mas `cap_drop`/`127.0.0.1` só são correção se o ambiente continuar
funcionando — sempre subir local para validar.

---

## Caso 3 — Correção em um branch e ausente em outro (bloqueio volta)

**Sintoma**

A verificação passa, o push é feito, e em outro momento a esteira bloqueia de novo pelo **mesmo**
motivo. O relatório do script volta a mostrar o segredo literal.

**Causa raiz**

A correção foi commitada em um branch. O branch de trabalho seguinte **não** continha aquele commit
(`git merge-base --is-ancestor` negativo). O merge uniu linhagens diferentes e o arquivo corrigido
voltou ao estado anterior.

**Como detectar**

```bash
# a correção está presente no branch atual?
git merge-base --is-ancestor <SHA_DA_CORRECAO> HEAD && echo "presente" || echo "AUSENTE"

# estado do arquivo versionado
git show HEAD:<caminho/do/arquivo> | grep -n "<chave>"
```

**Correção aplicada**

Reaplicar a correção no branch atual e, ao trocar de branch, rodar o script **antes** de commitar.

**Lição transferível**

Verificação pré-deploy não é evento único: rode **a cada troca de branch** e antes de cada push. O
script pega esse caso porque relê o **estado atual** do repositório, não o histórico.

---

## Caso 4 — `.env.example` versionado com segredo real (não bloqueia, mas expõe)

**Sintoma**

Varredura limpa em `.env.example`, mesmo contendo credencial real. O achado **não aparece** no
relatório da esteira.

**Causa raiz — escopo de varredura (verificado experimentalmente)**

A engine de IaC cobre **extensão de arquivo reconhecida**. Mesmo conteúdo com segredo literal:

```text
values_prd.yaml      -> 1 achado   (detecta)
.values_prd.yaml     -> 1 achado   (detecta; arquivo oculto NAO e o criterio)
.env                 -> 0 achados  (nao escaneado)
.env.example         -> 0 achados  (nao escaneado)
```

Portanto: **zero achados em `.env*` não prova ausência de segredo.**

Segundo problema, independente do scanner: um arquivo **já rastreado** continua rastreado mesmo que
seja adicionado ao `.gitignore` depois. O `.gitignore` só impede rastrear arquivos novos.

```bash
git check-ignore -v .env.example   # pode dizer "NAO ignorado" se ja estiver tracked
git ls-files --error-unmatch .env.example
```

**Correção**

- versionar `.env.example` **somente com placeholders**, nunca com valor real;
- para retirar do rastreamento: `git rm --cached <arquivo>` e confirmar `.gitignore`;
- encaminhar rotação dos valores que já estiveram no histórico.

**Lição transferível**

O script tem um passo dedicado a esse caso: ele varre os arquivos versionados **incluindo `.env*`**,
que o scanner não cobre, e classifica o valor como `real`, `local` ou `placeholder` para separar
risco real de ruído.

---

## Padrões que se repetem

| Padrão | Consequência | Como o script ajuda |
|---|---|---|
| Corrigir segredo em um ambiente e esquecer outro | bloqueio persiste | aponta arquivo:linha de cada ocorrência |
| Assumir que todo achado bloqueia | retrabalho no alvo errado | separa "bloqueia" de "achado menor" |
| Correção no branch errado | bloqueio volta | relê o estado atual do repositório |
| Confiar em varredura limpa de `.env*` | segredo exposto passa batido | passo dedicado a arquivos fora do escopo |
| Aplicar hardening sem testar | ambiente local para de subir | orientação de validar o `up` após a mudança |
| Corrigir versão de dependência sem rerodar build | troca bloqueio por falha de build | roda build + testes no mesmo comando |
