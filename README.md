# Minha pequena linguagem

Trabalho semestral de **Compiladores** — Ciência da Computação, UNISAGRADO.
Prof. Luiz Ricardo Mantovani da Silva · 2026-2

Cada grupo escreve um **compilador completo** para a MPL, uma linguagem
pequena de palavras-chave em português. O compilador de vocês vai ler um
programa em `.mpl`, atravessar as quatro fases da disciplina e produzir um
arquivo que **roda de verdade** numa máquina virtual que vocês também vão
escrever.

No fim do semestre vocês executam um programa escrito por vocês, numa
linguagem compilada por vocês.

---

## Comece por aqui

```bash
git clone https://github.com/LuizRMSilva1973/compiladores-lab.git
cd compiladores-lab
```

```bash
make verificar E=1
```

Vai dar vermelho — é para dar. O esqueleto responde à linha de comando mas
ainda não tem nenhuma fase escrita. O vermelho é o seu ponto de partida, e
ele vai virando verde conforme vocês preenchem `mplc/`.

Não precisa instalar nada além do Python 3. Se o notebook de vocês der
trabalho, o [Google Cloud Shell](https://shell.cloud.google.com) já vem com
Python 3.12, Java 21 e git — e é o mesmo ambiente da correção.

---

## Os três documentos que mandam

| Arquivo | O que decide |
|---|---|
| [LINGUAGEM.md](LINGUAGEM.md) | **o que** o compilador aceita: a sintaxe e as regras de tipo da MPL |
| [CONTRATOS.md](CONTRATOS.md) | **como** ele se comunica: a linha de comando e o formato de cada despejo |
| [entregas/](entregas/) | o enunciado de cada entrega, com o que vale nota |

Quando a sua intuição discordar de um deles, é o arquivo que vale. Se o
arquivo estiver errado, me procurem — já aconteceu de eu escrever um exemplo
errado no contrato e só descobrir rodando.

---

## As entregas

| # | Entrega | Turma A (quarta) | Turma B (segunda) | Vale |
|---|---|---|---|---|
| [E1](entregas/E1.md) | Analisador léxico | 02/09 | 31/08 | 0,8 |
| [E2](entregas/E2.md) | Analisador sintático e árvore | 30/09 | 28/09 | 1,2 |
| [E3](entregas/E3.md) | Tabela de símbolos e tipos | 28/10 | 26/10 | 1,2 |
| [E4](entregas/E4.md) | Código intermediário, geração e VM | 18/11 | 16/11 | 1,8 |
| [Apres.](entregas/APRESENTACAO.md) | Demonstração e defesa | 25/11 | 23/11 | 1,0 |

São **quatro entregas sobre o mesmo compilador**, não quatro trabalhos. O que
vocês escreverem na E1 continua rodando na E4 — e o verificador da E4 confere
tudo o que veio antes. Deixar a E1 pela metade custa caro em novembro.

---

## Regras do jogo

**A entrega é o repositório, nunca a máquina de vocês.** A correção clona o
repositório numa máquina limpa e roda `make verificar E=n`. Se não passar
lá, não conta como entregue. Testem antes de entregar — de preferência na
Cloud Shell, que é o ambiente da correção.

**Grupos de até 3.** O mesmo grupo do começo ao fim. Mudança de grupo só até
a E1.

**Gerador de parser proibido nas Entregas 1 e 2.** ANTLR, PLY, yacc, lark e
parentes escondem exatamente a parte que está sendo ensinada. Da E3 em diante
o assunto é outro, e aí não faz diferença. Na apresentação vocês podem — e
devem — comparar o parser de vocês com o que um gerador produziria.

**A linguagem de implementação é de vocês, entre as que o ambiente da correção
já tem:** Python 3.12, Java 21, C e C++ (gcc 13), Ruby 3.2 ou PHP 8.3. O
verificador não olha para dentro — ele roda `./compilar` e `./executar` e
compara o que sai. O esqueleto em `mplc/` é Python porque é o caminho mais
curto, mas ninguém é obrigado a usá-lo.

A lista existe por um motivo prático: a correção roda numa Cloud Shell limpa, e
o que não estiver lá não roda. Querem outra linguagem? Falem comigo **antes** de
começar — o critério é ela existir no ambiente sem instalação. Em nenhum caso
dependam de biblioteca externa: só a biblioteca padrão.

**Escrever o compilador é a tarefa.** Usar IA para explicar um conceito,
revisar uma mensagem de erro ou entender um trecho é bem-vindo, e eu faço
isso também. Entregar um compilador que vocês não sabem alterar é outra
coisa — e a apresentação foi desenhada para separar os dois casos: cada grupo
recebe **uma alteração pequena na linguagem, na hora, com 10 minutos para
fazer**. Quem escreveu o compilador faz. Não é desconfiança; é o formato.

---

## O verificador

```bash
make verificar E=2      # confere a Entrega 2 e, junto, a 1
make verificar          # confere as quatro
make evidencias E=2     # grava evidencias/verificacao-2.txt, que vai na entrega
```

**Antes de entregar, rodem `make prova`.** Ele clona o repositório de vocês num
diretório limpo e verifica lá — que é exatamente o que a correção faz. É o
teste que pega o defeito mais comum de todos, e que não tem nada a ver com
compiladores: *funciona aqui e não no clone*. Arquivo esquecido fora do commit,
caminho absoluto, passo de compilação que ninguém roda. Vale para qualquer
linguagem, e é a única prova que realmente antecipa a correção.

Ele não lê o código de vocês. Ele roda o compilador e compara a saída com um
corpus de **10 programas válidos**, **26 programas que precisam ser
recusados na compilação** e **3 que precisam falhar na execução** — com a
fase e a linha do erro conferidas.

Os programas recusados são metade da nota escondida do trabalho. Um
compilador que aceita tudo passa em todos os testes positivos e não vale
nada: é por isso que o corpus tem mais programas errados do que certos.

**A correção usa um segundo corpus, que vocês não têm.** Mesma linguagem,
mesmas regras, programas diferentes. Um compilador de verdade passa nos dois
sem que vocês precisem fazer nada; um programa que apenas reproduza as saídas
esperadas deste corpus passa aqui e reprova lá. Estou dizendo isto abertamente
para ninguém perder tempo pelo caminho errado.

---

## Como entregar

1. `git push` no repositório do grupo.
2. Abram a [página do trabalho](https://profluiz.mantovanitec.com/disciplinas/aulas/compiladores/trabalho.html).
3. No formulário do fim da página: escolham a entrega, identifiquem os
   integrantes (nome, RA e e-mail), colem a URL do repositório e anexem o
   `evidencias/verificacao-N.txt`.
4. Cada integrante recebe uma cópia por e-mail. **Guardem esse e-mail**: é o
   comprovante.
   
## Tabela de tokens

| Tipo | Regex / autômato |
|---|---|
| `ID` | `[a-zA-Z_][a-zA-Z0-9_]*`, quando o lexema não bate com nenhuma palavra reservada |
| `FUNCAO` | `funcao` |
| `RETORNE` | `retorne` |
| `SE` | `se` |
| `SENAO` | `senao` |
| `ENQUANTO` | `enquanto` |
| `ESCREVA` | `escreva` |
| `TIPO_INTEIRO` | `inteiro` |
| `TIPO_REAL` | `real` |
| `TIPO_LOGICO` | `logico` |
| `TIPO_TEXTO` | `texto` |
| `TIPO_VAZIO` | `vazio` |
| `LOGICO` | `verdadeiro\|falso` |
| `E` | `e` |
| `OU` | `ou` |
| `NAO` | `nao` |
| `INTEIRO` | `[0-9]+` |
| `REAL` | `[0-9]+\.[0-9]+`; se houver `.` sem dígito depois, é erro léxico na coluna do `.` |
| `TEXTO` | `"([^"\\\n]\|\\[nt"\\])*"`; autômato abre→corpo→escape→corpo→fecha; escape inválido, quebra de linha ou fim de arquivo dentro do texto são erro léxico |
| `MAIS` | `\+` |
| `MENOS` | `-` |
| `VEZES` | `\*` |
| `DIVIDE` | `/` |
| `RESTO` | `%` |
| `IGUAL` | `==` |
| `ATRIBUI` | `=` |
| `DIFERENTE` | `!=` (o `!` sozinho é erro léxico) |
| `MENOR` | `<` |
| `MENOR_IGUAL` | `<=` (lookahead de 1 caractere após `<`) |
| `MAIOR` | `>` |
| `MAIOR_IGUAL` | `>=` (lookahead de 1 caractere após `>`) |
| `ABRE_PAR` | `\(` |
| `FECHA_PAR` | `\)` |
| `ABRE_CHAVE` | `\{` |
| `FECHA_CHAVE` | `\}` |
| `VIRGULA` | `,` |
| `PONTO_VIRGULA` | `;` |
| `FIM_ARQUIVO` | token sintético, sem regex; emitido ao fim do texto |
| *(ignorados)* espaço/tab/`\r`/`\n` | `[ \t\r\n]+` |
| *(ignorado)* comentário de linha | `//[^\n]*` |
| *(ignorado)* comentário de bloco | `/\*.*?\*/`, não aninhado, atravessa linhas; se não fechar, erro léxico na posição onde começou |


## Gramática

Gramática em EBNF implementada em `mplc/sintatico.py` por descida recursiva.
Cada regra corresponde a uma função com o mesmo nome no parser.

```ebnf
programa       = { funcao } FIM_ARQUIVO ;
funcao         = "funcao" tipo ID "(" [ parametro { "," parametro } ] ")" bloco ;
parametro      = tipo ID ;
tipo           = "inteiro" | "real" | "logico" | "texto" | "vazio" ;

bloco          = "{" { comando } "}" ;
comando        = bloco
               | declaracao
               | ID "=" expressao ";"
               | chamada ";"
               | "se" "(" expressao ")" bloco [ "senao" bloco ]
               | "enquanto" "(" expressao ")" bloco
               | "escreva" "(" expressao ")" ";"
               | "retorne" [ expressao ] ";" ;
declaracao     = tipo ID [ "=" expressao ] ";" ;

expressao      = ou ;
ou             = e { "ou" e } ;
e              = igualdade { "e" igualdade } ;
igualdade      = relacional { ( "==" | "!=" ) relacional } ;
relacional     = aditiva { ( "<" | "<=" | ">" | ">=" ) aditiva } ;
aditiva        = multiplicativa { ( "+" | "-" ) multiplicativa } ;
multiplicativa = unaria { ( "*" | "/" | "%" ) unaria } ;
unaria         = ( "nao" | "-" ) unaria | primaria ;
primaria       = INTEIRO | REAL | LOGICO | TEXTO | ID | chamada
               | "(" expressao ")" ;
chamada        = ID "(" [ expressao { "," expressao } ] ")" ;
```

**Como a precedência está codificada:** na hierarquia das regras de expressão.
Cada nível só se refere ao nível imediatamente mais forte, da mais fraca (`ou`)
para a mais forte (`primaria`), seguindo a seção 3.3 do `LINGUAGEM.md`; por isso
o operador mais forte sempre fica mais embaixo na árvore. A repetição
`{ op operando }` dos níveis binários é implementada como laço, o que dá
associatividade à esquerda (`10 - 4 - 3` vira `(10 - 4) - 3`), enquanto
`unaria` chama a si mesma, o que dá associatividade à direita para `nao` e `-`.

## Estrutura de escopos

Os escopos formam uma árvore de dicionários encadeados: cada escopo tem um
dicionário `nome → símbolo` e um ponteiro para o escopo pai, e a busca de um
nome sobe por esses ponteiros até o global, o que implementa o sombreamento.
Durante o percurso, o caminho do escopo atual até a raiz funciona como uma
pilha (abrir um bloco empilha, fechar desempilha), mas nenhum escopo é
destruído ao fechar: todos ficam numa lista, na ordem em que abriram.
Escolhemos assim porque o `--tabela` precisa imprimir todos os escopos no fim,
e porque a Entrega 4 vai precisar deles para transformar cada nome numa
posição de memória; com uma pilha que descarta os escopos, essa informação
se perderia.


## Código intermediário e máquina virtual

O `--ir` é código de três endereços, com no máximo um operador por linha.
Variáveis aparecem com o número do escopo onde vivem (`x.4` é o `x` do escopo 4
do `--tabela`), o que separa o `x` de dentro do `x` de fora; `t0`, `t1`, ... são
temporários e `L0`, `L1`, ... são rótulos. A conversão `inteiro → real` é uma
instrução própria (`t1 = real t0`), emitida **depois** da conta: por isso
`real x = 7 / 2;` divide como inteiro e guarda `3.000000`.

O gerador traduz cada linha de três endereços para uma **máquina de pilha** e dá
a cada nome de uma função uma vaga no registro de ativação (parâmetros primeiro).
O `.mplb` é texto: uma instrução por linha, com comentários dizendo qual nome
mora em cada vaga, e as diretivas `.funcao <nome> <tipo> <parametros> <vagas>`,
`.linha <linha> <coluna>` (posição do comando no fonte, usada nos erros de
execução), `.fim` e rótulos `L3:`.

A VM tem duas pilhas: a de **operandos**, onde as contas acontecem, e a de
**chamadas**, com um registro de ativação por chamada em andamento (as vagas da
função e o ponto de volta). É o registro próprio de cada chamada que faz a
recursão funcionar.

### Conjunto de instruções

Na coluna da pilha, o topo fica à direita: `a b → r` tira `b` e `a` e põe `r`.

| Instrução | Pilha de operandos | O que faz |
|---|---|---|
| `EMPILHA <tipo> <valor>` | `→ v` | empilha uma constante (`inteiro`, `real`, `logico` ou `texto`) |
| `CARREGA <n>` | `→ v` | empilha o valor da vaga `n` do registro de ativação atual |
| `GUARDA <n>` | `v →` | desempilha e guarda na vaga `n` do registro de ativação atual |
| `SOMA` | `a b → a+b` | soma dois números, ou junta dois textos |
| `SUBTRAI` | `a b → a-b` | subtração |
| `MULTIPLICA` | `a b → a*b` | multiplicação |
| `DIVIDE_INTEIRO` | `a b → a/b` | divisão inteira truncada em direção a zero (`-7 / 2` dá `-3`); `b = 0` é erro de execução |
| `DIVIDE_REAL` | `a b → a/b` | divisão real; `b = 0` é erro de execução |
| `RESTO` | `a b → a%b` | resto com o sinal do dividendo (`-7 % 3` dá `-1`); `b = 0` é erro de execução |
| `NEGA` | `a → -a` | troca o sinal |
| `PARA_REAL` | `i → r` | converte inteiro em real |
| `IGUAL` | `a b → l` | `verdadeiro` se `a == b` |
| `DIFERENTE` | `a b → l` | `verdadeiro` se `a != b` |
| `MENOR` | `a b → l` | `verdadeiro` se `a < b` |
| `MENOR_IGUAL` | `a b → l` | `verdadeiro` se `a <= b` |
| `MAIOR` | `a b → l` | `verdadeiro` se `a > b` |
| `MAIOR_IGUAL` | `a b → l` | `verdadeiro` se `a >= b` |
| `E` | `a b → l` | `e` lógico (os dois lados já foram calculados: sem curto-circuito) |
| `OU` | `a b → l` | `ou` lógico (idem) |
| `NAO` | `a → l` | `nao` lógico |
| `DESVIA <L>` | `→` | continua a execução no rótulo `L` |
| `SE_FALSO <L>` | `c →` | desempilha a condição; se for `falso`, continua no rótulo `L` |
| `CHAMA <f> <n>` | `a1 … an →` | desempilha os `n` argumentos, cria um registro de ativação para `f` com eles nas primeiras vagas, guarda o ponto de volta e salta para `f`; com 100 000 chamadas abertas, é estouro de pilha (erro de execução) |
| `RETORNA` | `v → v` | descarta o registro de ativação e volta para quem chamou; o valor devolvido continua no topo da pilha |
| `RETORNA_VAZIO` | `→` | descarta o registro e volta sem valor; no `principal`, termina o programa |
| `DESCARTA` | `v →` | joga fora o valor de uma função com retorno chamada como comando |
| `ESCREVA <tipo>` | `v →` | desempilha e imprime no formato do tipo (real com seis casas, lógico como `verdadeiro`/`falso`) |

### Programa do grupo

`exemplos/vitrine.mpl`, com a saída em `exemplos/vitrine.saida`. Como a MPL não
converte número em texto, o programa escreve essa conversão na própria MPL
(recursão com `/` e `%`) e a usa para mostrar o ano em binário, a Torre de Hanói
com a contagem de movimentos, as armadilhas da divisão e a raiz quadrada pelo
método de Newton.