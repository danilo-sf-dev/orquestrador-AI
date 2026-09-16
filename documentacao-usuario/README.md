# Manual do Usuário — Orquestrador

> **HUMAN_ONLY — documentação exclusiva do usuário.**
>
> Esta pasta existe para consulta humana e **não faz parte do contexto operacional dos agentes**.
> Nenhuma skill deve ler, buscar, indexar, resumir ou usar estes arquivos como evidência, memória,
> requisito ou fonte de decisão.

## Para que serve

Este manual explica em PT-BR o funcionamento do Orquestrador, especialmente os nomes canônicos em
inglês que aparecem durante a execução, como `INTAKE`, `REQUIREMENT_ANALYSIS`, `GREEN_VALIDATION` e
`JUDGE_RECOVERY`.

Os nomes em português deste manual são **traduções explicativas**. Eles não substituem os identificadores
canônicos usados pelo `STATE.md` e pelo `orquestrador.md`.

Exemplo:

```text
INTAKE — Triagem do Jira
```

- `INTAKE` = nome canônico usado pelo sistema;
- `Triagem do Jira` = nome humano para facilitar entendimento.

## Fonte de verdade

Este manual ajuda o usuário a entender o projeto, mas não define o comportamento dos agentes.

A precedência operacional é:

```text
orquestrador.md
-> skill atual
-> artefatos aprovados/permitidos da feature
-> código/testes/contratos relevantes
```

Se este manual divergir de uma regra técnica vigente, o contrato operacional acima prevalece e o
manual deve ser corrigido.

## Como procurar uma nomenclatura

No VS Code, abra esta pasta e use `Ctrl + Shift + F`, ou abra o arquivo indicado e use `Ctrl + F`.

Exemplos de busca:

```text
INTAKE
GREEN_VALIDATION
HEAD_STRONG
REOPEN RED
red-tests.lock
OPEN_QUESTION
```

## Índice

| Arquivo | Use quando quiser... |
|---|---|
| [01-primeiros-passos.md](01-primeiros-passos.md) | iniciar, retomar ou escolher QUICK/COMUM |
| [02-visao-geral.md](02-visao-geral.md) | entender arquitetura, peças e responsabilidades |
| [03-fluxos.md](03-fluxos.md) | visualizar os fluxos COMUM, QUICK e recovery |
| [04-estados-e-etapas.md](04-estados-e-etapas.md) | descobrir o significado de um estado/step |
| [05-papeis-e-modelos.md](05-papeis-e-modelos.md) | entender `HEAD_STRONG`, `EXECUTOR`, Judge e troca de modelo |
| [06-gates-e-comandos.md](06-gates-e-comandos.md) | saber o que responder em cada aprovação/comando |
| [07-memoria-e-artefatos.md](07-memoria-e-artefatos.md) | entender `.ai`, STATE, SPEC, RED lock e arquivos gerados |
| [08-recuperacao-e-erros.md](08-recuperacao-e-erros.md) | entender reprovação do Judge, GREEN FAIL, QUICK abortado e recovery |
| [09-glossario.md](09-glossario.md) | procurar rapidamente termos e traduções |

## Regra de manutenção

Quando o fluxo canônico mudar de forma material, atualizar primeiro o contrato técnico responsável e,
na mesma alteração, revisar os capítulos humanos afetados. Não adicionar ao manual comportamento que
não exista no projeto apenas para tornar a explicação mais completa.
