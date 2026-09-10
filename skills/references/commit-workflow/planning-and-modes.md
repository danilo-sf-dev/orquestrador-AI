# Commit — planejamento e modos

Ler ao iniciar `COMMIT_REVIEW`, analisar diff ou preparar o `COMMIT PLAN`.

## Planejamento semântico

Antes de `git add`, analisar o diff completo de cada repositório e decidir quantas intenções lógicas
existem. Um único commit é correto quando todo o diff possui a mesma razão de mudança.

Agrupar arquivos quando:

- possuem a mesma intenção funcional/técnica;
- formam uma unidade coerente de revisão;
- podem ser revertidos juntos;
- não incorporam mudança independente.

Separar feature de refactor oportunista, correção de limpeza autônoma, tooling sem relação, docs
independentes ou comportamentos revisáveis separadamente. Não separar automaticamente `src`, testes
e configuração: a razão da mudança decide o grupo.

## Formato do plano

```text
COMMIT PLAN — <JIRA>

COMMIT <N>
TYPE:
INTENT:
FILES:
  -
MESSAGE_PTBR:
MESSAGE_EN:
DEPENDS_ON:

ORDER: 1 -> 2
EXCLUDED_OR_UNRELATED_FILES:
  -
```

Para cada grupo confirmar:

```text
SAME_INTENT=true
REVIEWABLE_UNIT=true
REVERTABLE_UNIT=true
UNRELATED_CHANGES=false
```

`MESSAGE_PTBR` serve à revisão do usuário. Apenas `MESSAGE_EN` pode ser executada no Git.

## Escolha do modo

Se `COMMIT_MODE` ainda não estiver definido, sempre oferecer:

| Opção | Comportamento |
|---|---|
| `AUTOMÁTICO` | Congela e executa o plano faseado após as validações; entrega SHAs e resumo. |
| `MANUAL` | Apresenta plano PT-BR + EN antes de mutar e aguarda decisão. |
| `OUTROS` | Usuário define o comportamento; não autoriza commit implicitamente. |

Persistir `COMMIT_MODE=AUTO | MANUAL | OTHER`.

### Automático

A escolha explícita já autoriza os grupos do plano congelado. Não pedir confirmação entre commits.
Se o plano mudar materialmente, parar e devolver a decisão ao usuário.

### Manual

Depois de apresentar o plano, parar e oferecer:

```text
1. POSSO COMITAR
2. PRECISA AJUSTAR
3. OUTROS
```

- `POSSO COMITAR`: executa exatamente o plano apresentado;
- `PRECISA AJUSTAR`: não muta Git, gera novo plano e reapresenta as opções;
- `OUTROS`: segue a instrução literal, inclusive adiar ou delegar ao usuário.

Qualquer alteração material após `POSSO COMITAR` exige novo plano e nova decisão.

## Política técnica

Modo controla autorização; política técnica controla o que será feito.

| Política | Regra |
|---|---|
| Commit seguro | Valida gates e não altera código/testes. Default de entrega final. |
| Revalidar e commit | Formatter/auto-fix somente se detectado e autorizado. Mudança julgada exige novo GREEN/Judge. |
| Commit parcial | Escopo explícito; preserva gates aplicáveis e registra feature incompleta. |
| Outros | Converte pedido em passos, pulos e riscos; pede confirmação para mutações ambíguas. |

Em commit parcial, não misturar arquivos apenas porque já estão no working tree. Código/testes exigem
GREEN e Judge aplicáveis; QA final exige aprovação de QA. Commit intermediário fora dos gates deve
ser tratado como `Outros`, com incompletude explícita.

## Mudança durante a execução

Parar quando:

- arquivo entrar/sair de grupo;
- surgir arquivo relevante;
- mensagem ou ordem mudar materialmente;
- commit precisar ser dividido/fundido;
- diff divergir do plano;
- qualquer gate ou integridade falhar.

No `AUTO`, a autorização termina. No `MANUAL`, reapresentar o plano e as três opções.
