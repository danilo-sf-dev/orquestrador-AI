# Commit — integridade, convenções e segurança

Ler antes de stagear ou executar qualquer commit.

## Descoberta de comandos e convenções

Prioridade para comandos:

1. `04-implementation-plan.md` ou documentação canônica;
2. wrappers/scripts versionados;
3. arquivos de build/configuração;
4. CI como evidência de comandos usados;
5. convenção observada no repositório;
6. usuário, quando não houver escolha segura.

Prioridade para mensagem:

1. `CONTRIBUTING.md` ou documentação de engenharia;
2. commitlint/config/hook;
3. commits recentes do próprio repositório;
4. regra explícita do time/feature;
5. fallback Conventional Commits.

Fallback:

```text
<type>(<scope>): <description>
```

Tipos: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `chore`, `ci`.
Mensagens devem explicar a intenção; não usar `update`, `fix`, `changes` ou `WIP`. Respeitar a
convenção do projeto para Jira; sem convenção, preferir `Refs: <JIRA-ID>` no corpo/footer.

## Integridade RED/GREEN

Quando `RED_LOCKED=true`:

1. recalcular hashes dos testes selados sem alterá-los;
2. bloquear em `RED_LOCK_VIOLATION` se houver divergência não autorizada;
3. não corrigir teste nem lock nesta skill;
4. exigir `REOPEN RED`, novo lock, GREEN e Judge quando aplicável.

## Integridade do julgamento

Recomputar `JUDGEMENT_SCOPE_HASH` usando o método registrado em `08-judgement.md`. Divergência marca
`JUDGEMENT_STALE=true` e bloqueia commit final de implementação até novo GREEN/Judge. Alterações
somente em QA, docs ou memória fora do escopo julgado não invalidam o julgamento de código.

Requisitos mínimos:

| Conteúdo | Gate |
|---|---|
| Implementação/código | RED íntegro + GREEN válido + Judge PASS/risco aceito |
| Testes unitários | RED íntegro; pós-lock somente via `REOPEN RED` |
| QA final | QA aprovado ou `NOT_REQUIRED_WITH_REASON` no QUICK |
| Commit final completo | Judge + QA resolvido + escopo julgado íntegro |

## Atomicidade e cross-repo

- agrupar por intenção, não por tipo de arquivo;
- cada commit deve ser revisável e reversível;
- revisar `git diff --staged` antes de cada commit;
- cada repositório recebe commits próprios;
- validar todos os repos antes do primeiro commit seguro;
- respeitar contrato, compatibilidade e ordem cross-repo;
- se um repo não puder ser validado, registrar `CROSS_REPO_COMMIT_BLOCKED`.

## Proteção absoluta de `.ai/`

```text
AI_MEMORY_POLICY=LOCAL_ONLY
.ai/ NEVER_COMMIT
.ai/ NEVER_STAGE
.ai/ NEVER_PUSH
```

Em cada repositório:

1. garantir regra efetiva no `.gitignore`;
2. confirmar via Git que `.ai/` está ignorada;
3. verificar se há `.ai/**` tracked ou staged;
4. remover do stage sem apagar o arquivo local, se apenas staged;
5. bloquear se tracked;
6. repetir imediatamente antes de cada commit.

## Segurança

Revisar repo/branch, staged diff, untracked relevantes, exclusões, secrets, gates, mensagem final e
ordem cross-repo. Não incluir automaticamente:

- `.env*` com credenciais, tokens, chaves ou certificados privados;
- dumps, logs e builds não versionados;
- `.ai/**`;
- metadata de IDE não versionada;
- arquivos não relacionados.
