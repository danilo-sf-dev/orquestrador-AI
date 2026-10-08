# Scanners — mapa de gates e equivalentes locais

Ler ao decidir **o que** reproduzir e **como** invocar, conforme o que a pipeline do projeto declarar.
Nada aqui é obrigatório: adapte à ferramenta que a esteira realmente usa.

## Descobrir os gates

Procure a definição de pipeline no repositório e extraia a política, não os passos:

```text
# onde costuma estar (varia por projeto)
Jenkinsfile, .gitlab-ci.yml, .github/workflows/*.yml, azure-pipelines.yml
build.gradle / pom.xml (plugins de scan)
scripts de pre-push (ex.: pre-push.sh)
```

O que interessa extrair:

- quais gates rodam e em que ordem;
- **quais falham o build** (`break build`, `fail on`, `--exit-code`, gate de política);
- quais ferramentas e versões;
- quais caminhos/severidades entram no gate.

Se houver um pre-push no projeto cujo passo de scan esteja comentado/desabilitado, isso é um
`FACT` relevante: a verificação local foi deliberadamente afrouxada em algum momento. Reporte.

## Equivalentes open source

| Categoria | Fonte na esteira | Equivalente local | Imagem / comando |
|---|---|---|---|
| IaC (Kubernetes, Compose, Terraform, Helm, Dockerfile) | Checkmarx **KICS** | o próprio KICS (é a mesma engine) | `checkmarx/kics:latest scan -p <path>` |
| SCA por imagem/SBOM | Checkmarx SCA, outros | Trivy / Grype + Syft | `aquasec/trivy fs <path>`, `anchore/grype`, `anchore/syft` |
| SCA por manifesto | idem | resolução do próprio build + base pública | dependency list do build + consulta a base de advisories |
| Secrets | Checkmarx SCS | KICS (queries de secret) + varredura por padrão | `checkmarx/kics` + regex contextual |
| SAST | Checkmarx SAST | — (proprietário) | não reproduzível localmente |
| Build / testes / cobertura | próprio projeto | toolchain do projeto | comando de verify do projeto |

## Montagem do container (receita segura)

```bash
# 1) relatório JSON em diretório separado, repositório somente leitura
mkdir -p <OUT>

docker run --rm \
  -v "<REPO>:/input:ro" \
  -v "<OUT>:/output" \
  <IMAGEM> <subcomando> -p /input --report-formats json -o /output

# 2) extrair números do JSON por script, nunca "olhando" a saída
```

Cuidados que evitam retrabalho:

- **excluir** diretórios de build/vendor/mock do scan (`target`, `node_modules`, `.git`, `.idea`,
  pastas de mock), senão o relatório enche de ruído que a esteira não vê;
- usar caminhos no formato aceito pelo runtime de container (no Windows, caminho absoluto tipo
  `C:/...`, e desabilitar a conversão de caminho do shell quando necessário);
- **nunca** montar `~/.ssh`, `~/.aws`, `.env` ou qualquer credencial dentro do container;
- se o scanner precisar baixar banco de dados, ele vai falhar atrás de proxy corporativo:
  isso é `NAO_VERIFICADO` (não um "passou"), e a alternativa é resolver por manifesto/SBOM.

## Escopo de varredura — a armadilha mais cara

A engine de IaC varre por **extensão de arquivo reconhecida**. Verificado experimentalmente
(mesmo conteúdo com segredo literal):

```text
values_prd.yaml      -> 1 achado   (detecta)
.values_prd.yaml     -> 1 achado   (detecta; dotfile NAO e o criterio)
.env                 -> 0 achados  (nao escaneado)
.env.example         -> 0 achados  (nao escaneado)
```

Consequência prática, **sempre informar ao usuário**: varredura limpa em `.env*` **não** prova que
não há segredo ali. Se esses arquivos estiverem versionados, a exposição é real mesmo com o gate verde.

## Volume de achados no SCA

O SCA proprietário costuma reportar mais itens que as bases públicas (banco comercial). Portanto:

- contagens absolutas **divergem** entre local e esteira; o que importa é **delta** e **bloqueio**;
- valide o scanner local contra um caso conhecido antes de confiar nele (ex.: uma versão antiga de
  biblioteca com vulnerabilidade icônica deve acusar);
- reporte a cobertura: "achei N com a base pública; a esteira pode reportar mais".
