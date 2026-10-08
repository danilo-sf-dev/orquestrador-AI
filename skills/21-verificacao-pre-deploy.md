---
name: verificacao-pre-deploy
description: >
  Roda a verificacao local de seguranca e integridade ANTES do deploy, para nao
  descobrir bloqueio na esteira. Executa um script reproduzivel que descobre o build,
  a pipeline e os arquivos de infraestrutura do projeto, roda a engine de IaC do
  Checkmarx (KICS), varre segredos versionados, resolve dependencias e roda
  build+testes, entregando um veredito OK / BLOQUEIA / PARCIAL. Use quando o usuario
  pedir "rodar a verificacao", "checar vulnerabilidades", "passar no Checkmarx",
  "a esteira bloqueou", "validar antes do deploy" ou "pre-deploy check".
preferred_model_role: EXECUTOR
context_loading: lazy

reads:
  - infrastructure/pre-deploy/pre-deploy-check.py
  - project_build_and_pipeline_config_relevant_only
  - iac_and_config_files_relevant_only
  - prior_scan_output_if_user_provided

forbidden_reads:
  - chat_transcript
  - unrelated_source_files
  - bulk_feature_history
  - documentacao-usuario/**

writes:
  - scan_report_ephemeral
  - .ai/verify/resultados-locais.md_only_if_user_requests_recording

forbidden_writes:
  - source_code
  - tests
  - dependency_manifest
  - pipeline_definition
  - .env
  - secrets
  - credentials
  - git_remote_state
---

# Skill — Verificação pré-deploy

## Objetivo

Rodar **antes do push/deploy** o que a esteira vai cobrar, para que o bloqueio apareça na sua
máquina e não na pipeline compartilhada.

O mecanismo é **um script**:

```text
infrastructure/pre-deploy/pre-deploy-check.py
```

Não é um guia para a pessoa seguir manualmente: é um comando que faz a verificação e devolve
veredito. Esta skill existe para o agente saber **como rodar**, **como interpretar a saída**,
**quando o Docker importa** e **como agir em cada tipo de achado**.

## Como rodar

```bash
# verificação completa (usa Docker se disponível; sem Docker, degrada e avisa)
python infrastructure/pre-deploy/pre-deploy-check.py --repo "<CAMINHO_DO_REPO>"

# triagem rápida, sem os passos pesados
python infrastructure/pre-deploy/pre-deploy-check.py --repo "<REPO>" --skip-build --skip-deps

# sem Docker (só o que roda no toolchain local)
python infrastructure/pre-deploy/pre-deploy-check.py --repo "<REPO>" --skip-docker

# relatório consolidado para anexar/registrar
python infrastructure/pre-deploy/pre-deploy-check.py --repo "<REPO>" --json <SAIDA>.json
```

Opções: `--repo`, `--out-dir`, `--json`, `--skip-docker`, `--skip-build`, `--skip-deps`.

Comportamento: **somente leitura** sobre o repositório. Por padrão grava o relatório bruto em diretório
temporário do sistema e o remove ao final, para não poluir o projeto; use `--out-dir` para preservar.
Retorna `1` quando há achado HIGH/CRITICAL ou falha de build — usável como gate automático.

> Rode **a cada troca de branch** e antes de cada push. O script relê o estado atual do repositório,
> então é ele que pega o caso de a correção existir em um branch e não no outro.

## O que o script faz

```text
1. DESCOBERTA    build (maven/gradle/npm/go/...), pipeline, arquivos de IaC, arquivos versionados
2. IaC           engine de IaC do Checkmarx (KICS) em container -> conta por severidade
3. SEGREDOS      varre arquivos versionados; classifica real vs local/placeholder; cobre .env*
4. DEPENDENCIAS  resolve a lista de dependencias (Maven/Gradle/npm)
5. BUILD         roda build + testes do proprio projeto
6. VEREDITO      OK | BLOQUEIA (possivelmente) | PARCIAL
```

O veredito separa três coisas que costumam ser confundidas:

- **bloqueia** — achado HIGH/CRITICAL ou build falhando;
- **achado menor** — aparece no relatório, normalmente não bloqueia;
- **`NAO_VERIFICADO`** — o que não pôde ser executado localmente (nunca tratado como sucesso).

## Docker é necessário?

O script decide e avisa. Regra:

| Precisa de Docker | Não precisa | Não é possível localmente |
|---|---|---|
| KICS (IaC), Trivy/Grype/Syft (SCA) | build + testes do projeto | Checkmarx One completo (SAST + SCA proprietário) |
| scanners que só existem como imagem | leitura de política/manifests; varredura de segredo | scanner cuja licença/banco vive no corporativo |

Sem Docker o script **não falha**: marca o passo como `NAO_VERIFICADO` e segue — nunca pula em
silêncio. Regras de segurança já embutidas: container `--rm`, repositório montado `:ro`, e nenhuma
credencial (`~/.aws`, `.env`, chaves) é montada dentro do container.

## Achado × bloqueio — o erro que custa mais caro

Antes de tentar corrigir qualquer coisa, confirme **qual gate tem break build**. Achado de severidade
alta em um gate **sem** bloqueio aparece no relatório e **não** derruba o deploy. Perseguir o alvo
errado é o retrabalho mais comum nesse cenário.

No log da esteira isso aparece na linha da política:

```text
Policy: Bloqueio IAC: Severidades Críticas e Altas | Break Build: true
Violated Rules: Vulnerabilidade Alta detectada _ Corrija os alertas de IAC abaixo para prosseguir
```

Se apenas **um** gate aparece com `Break Build: true`, é **ele** que precisa ficar verde.

## Casos reais já resolvidos

Leia [`references/pre-deploy/casos-reais.md`](references/pre-deploy/casos-reais.md) quando a saída do
script se parecer com um destes cenários: traz sintoma, causa raiz confirmada e a correção aplicada.

- **secret literal em configuração de deploy** — bloqueou a esteira; dev/hml foram corrigidos e o
  **PRD foi esquecido**; foi o PRD que derrubou o build;
- **hardening de `docker-compose`** — capabilities irrestritas, porta em `0.0.0.0`, healthcheck ausente;
- **correção presente em um branch e ausente em outro** — branch novo não herda a correção e o
  bloqueio volta (o script pega: o segredo literal reaparece no relatório);
- **`.env.example` versionado com segredo real** — fora do escopo do scanner, mas exposto no git.

Leia [`references/pre-deploy/scanners.md`](references/pre-deploy/scanners.md) para o mapa de gates,
equivalentes open source e a receita de montagem do container.
Leia [`references/pre-deploy/iac-hardening.md`](references/pre-deploy/iac-hardening.md) para aplicar
cada correção de IaC sabendo o trade-off.
Leia [`references/pre-deploy/sca-remediation.md`](references/pre-deploy/sca-remediation.md) para
rastrear a origem de dependência vulnerável e escolher a correção.

## Depois do relatório

- **`OK`** — pode seguir para commit/deploy. Se houver `NAO_VERIFICADO`, dizer explicitamente o que a
  esteira ainda pode acusar.
- **`BLOQUEIA`** — apresentar achado, severidade, evidência e correção sugerida. **Não** alterar
  código/manifesto/pipeline sem autorização; se for código do projeto, o retorno roteia para
  `REWORK_IMPLEMENTATION` no fluxo normal.
- Aplicada a correção, **reexecutar o script** e mostrar contagem antes/depois. Só a reexecução prova
  que o gate ficou verde.

## Limites

- Não corrigir automaticamente; relatar e aguardar autorização.
- Não silenciar/suprimir achado nem usar bypass de política como primeira resposta. Se o usuário pedir
  bypass, registrar como decisão explícita dele, com o risco.
- Não afirmar sucesso do que não rodou: o que não executou é `NAO_VERIFICADO`.
- Não versionar relatório com segredo literal; saída é efêmera por padrão.
- Não assumir que a contagem local bate com a da esteira: o SCA da esteira usa base comercial e pode
  reportar mais. O que importa é o **delta** e o **bloqueio**.
- Não presumir stack: o script descobre em runtime; se o projeto usar ferramenta não prevista, adaptar
  o passo mantendo o procedimento (descobrir → reproduzir → comparar com a política → relatar).
