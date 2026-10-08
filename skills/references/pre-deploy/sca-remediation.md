# SCA remediation — rastrear origem e escolher a correção

Ler quando o gate de dependências acusar vulnerabilidade. O erro comum é atualizar a biblioteca
"culpada" sem descobrir **quem a introduz** — e então quebrar a compatibilidade da plataforma.

## 1. Descobrir a origem antes de mudar

Uma dependência vulnerável quase nunca é declarada diretamente: ela vem de forma transitiva. Rastreie:

```bash
# Maven
mvn dependency:tree -Dincludes=<groupId>:<artifactId>

# Gradle
gradlew dependencyInsight --dependency <nome>
```

Registre o **caminho completo** até a origem. A decisão de correção depende de quem introduz:

- **declarada diretamente** → atualizar é decisão direta e localizada;
- **transitiva de biblioteca interna** → atualizar a interna, se houver versão corrigida; senão,
  sobrescrever a transitiva explicitamente e justificar;
- **transitiva de BOM/plataforma** → alinhar pelo BOM é preferível a sobrescrever item a item.

## 2. Preferir a versão governada, não a mais recente

Ordene as opções por segurança, do mais conservador ao mais arriscado:

1. **A versão que a plataforma/BOM já governa** — se o BOM é mais novo que a versão resolvida, algo
   no projeto está forçando uma regressão. Remover a força é a correção mais limpa.
2. **Alinhar pelo BOM atualizado** — mudar a família inteira junto evita mistura de versões.
3. **Sobrescrever a dependência específica** — aceitável quando há versão corrigida compatível;
   registrar a justificativa no manifesto.
4. **Subir para a última versão disponível** — último recurso; costuma arrastar incompatibilidade.

Nunca atualize "para a última" indiscriminadamente: a plataforma (parent/BOM) existe para manter a
família coerente. Um override que faz **downgrade** ou deixa submódulo de uma família em versão
diferente é, ele mesmo, um risco que você está introduzindo.

## 3. Verificar compatibilidade antes de fixar

Antes de escolher a versão corrigida, confirmar que ela existe e combina com a família:

```text
- a versão corrigida existe no repositório usado pelo build? (Central/corporativo)
- qual versão da biblioteca irmã ela espera? (ex.: cliente HTTP e seu core)
- o BOM da plataforma já resolve para ela?
```

Se a correção exigir subir uma família inteira, isso deixa de ser "correção de vulnerabilidade" e
vira **mudança de plataforma**: trate como tarefa própria, com validação de regressão.

## 4. Distinguir achado de bloqueio

Nem todo achado de SCA bloqueia o deploy — depende da política da esteira. Antes de investir horas:

- confirme se o gate de SCA tem break build;
- se não tiver, reporte e priorize junto com o usuário (o bloqueio pode estar em outro gate).

## 5. Banco de dados comercial versus público

O scanner da esteira pode usar base comercial e reportar mais itens que as bases públicas
(NVD/advisories). Portanto:

- a contagem local **não precisa bater** com a da esteira;
- o que importa é o **delta** (o que saiu depois da correção) e se o gate ficou verde;
- valide o scanner local contra um caso conhecido antes de confiar nele;
- declare a limitação: "achei N; a esteira pode reportar mais".

## 6. Evidência de que resolveu

Para cada dependência alterada, registrar:

```text
DEPENDENCIA: <groupId:artifactId>
VERSAO_ANTES: <...>
VERSAO_DEPOIS: <...>
ORIGEM_DO_ACHADO: <caminho transitivo>
JUSTIFICATIVA: <por que esta versao>
COMPATIBILIDADE_VERIFICADA: <como>
RISCO_RESIDUAL: <o que ficou sem corrigir e por que>
```

Sempre **reexecutar** a resolução de dependências (e o build) depois da mudança: alterar versão sem
rodar o build é a forma mais rápida de trocar um bloqueio de segurança por uma falha de compilação.

## 7. O que não fazer

- Não suprimir/whitelistar um achado para passar na esteira sem decisão explícita e registrada do usuário.
- Não deixar família de biblioteca em versões mistas (ex.: um artefato sobrescrito, o irmão não).
- Não atualizar dependência não relacionada ao achado "aproveitando a passagem".
- Não afirmar que resolveu sem reexecutar o scan/build.
