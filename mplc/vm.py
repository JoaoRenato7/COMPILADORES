"""
Entrega 4, terceira metade (sim, sao tres) — a maquina virtual.

Le o .mplb e executa. A maquina tem duas pilhas, e e bom nao confundir:

  - a PILHA DE OPERANDOS, onde as contas acontecem: EMPILHA e CARREGA poem
    valores nela, SOMA tira dois e poe um, GUARDA tira um e guarda numa vaga;

  - a PILHA DE CHAMADAS, com um REGISTRO DE ATIVACAO por chamada em andamento.
    Cada registro tem as vagas da funcao (parametros, variaveis, temporarios)
    e o ponto de volta. E isso que faz a recursao funcionar: em fatorial(5),
    ha cinco registros empilhados, cada um com o seu proprio n. Se as vagas
    fossem globais, a chamada de dentro apagaria o n da de fora.

A maquina nao usa a recursao do Python: a pilha de chamadas e uma lista, e o
estouro de pilha e detectado contando os registros.

Erros de execucao (divisao ou resto por zero, estouro de pilha) saem como
ErroMPL de fase 'execucao', na linha do comando que estava rodando; o
principal.py transforma isso em codigo de saida 2.
"""
from mplc.erros import ErroMPL

# Quantas chamadas podem estar abertas ao mesmo tempo antes do estouro de pilha.
LIMITE_DE_CHAMADAS = 100_000

ESCAPES = {'n': '\n', 't': '\t', '"': '"', '\\': '\\'}


class InfoFuncao:
    def __init__(self, nome, tipo, parametros, vagas, entrada):
        self.nome = nome
        self.tipo = tipo
        self.parametros = parametros   # quantos argumentos ela recebe
        self.vagas = vagas             # tamanho do registro de ativacao
        self.entrada = entrada         # indice da primeira instrucao


class RegistroAtivacao:
    """Uma chamada em andamento: as vagas dela e para onde voltar."""
    __slots__ = ('funcao', 'vagas', 'retorno')

    def __init__(self, funcao, vagas, retorno):
        self.funcao = funcao
        self.vagas = vagas
        self.retorno = retorno         # indice da instrucao seguinte ao CHAMA


# -- leitura do .mplb ------------------------------------------------------------

def _ler_texto(resto):
    """Le um texto entre aspas e desfaz os escapes: "a\\nb" vira a, quebra, b."""
    saida, i = [], 1
    while resto[i] != '"':
        if resto[i] == '\\':
            saida.append(ESCAPES[resto[i + 1]])
            i += 2
        else:
            saida.append(resto[i])
            i += 1
    return ''.join(saida)


def _ler_constante(tipo, valor):
    if tipo == 'inteiro':
        return int(valor)
    if tipo == 'real':
        return float(valor)
    if tipo == 'logico':
        return valor == 'verdadeiro'
    return _ler_texto(valor)


def _carregar(texto):
    """Transforma o texto do .mplb numa lista de instrucoes prontas para rodar."""
    funcoes, rotulos, codigo = {}, {}, []
    linha_fonte, coluna_fonte = 1, 1

    for numero, bruta in enumerate(texto.split('\n'), 1):
        linha = bruta.strip()
        try:
            if not linha or linha.startswith(';') or linha == '.fim':
                continue
            if linha.startswith('.funcao'):
                _, nome, tipo, parametros, vagas = linha.split()[:5]
                funcoes[nome] = InfoFuncao(nome, tipo, int(parametros), int(vagas),
                                           len(codigo))
                continue
            if linha.startswith('.linha'):
                _, l, c = linha.split()[:3]
                linha_fonte, coluna_fonte = int(l), int(c)
                continue
            if linha.endswith(':') and ' ' not in linha:
                rotulos[linha[:-1]] = len(codigo)
                continue

            if linha.startswith('EMPILHA texto'):
                op, arg = 'EMPILHA', _ler_texto(linha[len('EMPILHA texto'):].strip())
            else:
                partes = linha.split(';')[0].split()
                op, args = partes[0], partes[1:]
                if op == 'EMPILHA':
                    arg = _ler_constante(args[0], args[1])
                elif op in ('CARREGA', 'GUARDA'):
                    arg = int(args[0])
                elif op == 'CHAMA':
                    arg = (args[0], int(args[1]))
                else:
                    arg = args[0] if args else None
            codigo.append([op, arg, linha_fonte, coluna_fonte])
        except (ValueError, IndexError, KeyError) as e:
            raise ErroMPL('execucao', 1, 1,
                          f'.mplb invalido na linha {numero}: {repr(bruta.strip())} ({e})')

    # Segunda passada: rotulos e nomes de funcao viram enderecos.
    for ins in codigo:
        op, arg = ins[0], ins[1]
        if op in ('DESVIA', 'SE_FALSO'):
            ins[1] = rotulos[arg]
        elif op == 'CHAMA':
            ins[1] = (funcoes[arg[0]], arg[1])
    return funcoes, codigo


# -- as operacoes que precisam de cuidado -------------------------------------------

def _divide_inteiro(a, b):
    """Divisao inteira truncada em direcao a zero: -7 / 2 e -3 (o // do Python daria -4)."""
    q = abs(a) // abs(b)
    return -q if (a < 0) != (b < 0) else q


def _resto(a, b):
    """Resto com o sinal do DIVIDENDO: -7 % 3 e -1 (o % do Python daria 2)."""
    r = abs(a) % abs(b)
    return -r if a < 0 else r


def _formatar(valor, tipo):
    """A forma impressa de cada tipo, secao 4.5 da especificacao."""
    if tipo == 'inteiro':
        return str(valor)
    if tipo == 'real':
        return f'{valor:.6f}'
    if tipo == 'logico':
        return 'verdadeiro' if valor else 'falso'
    return valor


COMPARACOES = {
    'IGUAL': lambda a, b: a == b,
    'DIFERENTE': lambda a, b: a != b,
    'MENOR': lambda a, b: a < b,
    'MENOR_IGUAL': lambda a, b: a <= b,
    'MAIOR': lambda a, b: a > b,
    'MAIOR_IGUAL': lambda a, b: a >= b,
}


# -- o laco de execucao ----------------------------------------------------------

def executar(texto_mplb, saida):
    """Executa o bytecode. Escreve o que o programa imprimir em `saida`."""
    funcoes, codigo = _carregar(texto_mplb)

    principal = funcoes['principal']
    chamadas = [RegistroAtivacao(principal, [None] * principal.vagas, None)]
    vagas = chamadas[-1].vagas          # as vagas do registro do topo
    pilha = []                          # a pilha de operandos
    pc = principal.entrada              # a proxima instrucao

    while True:
        op, arg, linha, coluna = codigo[pc]
        pc += 1

        if op == 'CARREGA':
            pilha.append(vagas[arg])
        elif op == 'GUARDA':
            vagas[arg] = pilha.pop()
        elif op == 'EMPILHA':
            pilha.append(arg)

        elif op == 'SOMA':                     # numeros, ou dois textos
            b = pilha.pop(); pilha.append(pilha.pop() + b)
        elif op == 'SUBTRAI':
            b = pilha.pop(); pilha.append(pilha.pop() - b)
        elif op == 'MULTIPLICA':
            b = pilha.pop(); pilha.append(pilha.pop() * b)
        elif op in ('DIVIDE_INTEIRO', 'DIVIDE_REAL', 'RESTO'):
            b = pilha.pop(); a = pilha.pop()
            if b == 0:
                conta = 'resto' if op == 'RESTO' else 'divisao'
                raise ErroMPL('execucao', linha, coluna, f'{conta} por zero')
            if op == 'DIVIDE_INTEIRO':
                pilha.append(_divide_inteiro(a, b))
            elif op == 'DIVIDE_REAL':
                pilha.append(a / b)
            else:
                pilha.append(_resto(a, b))
        elif op == 'NEGA':
            pilha.append(-pilha.pop())
        elif op == 'PARA_REAL':
            pilha.append(float(pilha.pop()))

        elif op in COMPARACOES:
            b = pilha.pop(); a = pilha.pop()
            pilha.append(COMPARACOES[op](a, b))
        elif op == 'E':
            b = pilha.pop(); a = pilha.pop()
            pilha.append(a and b)
        elif op == 'OU':
            b = pilha.pop(); a = pilha.pop()
            pilha.append(a or b)
        elif op == 'NAO':
            pilha.append(not pilha.pop())

        elif op == 'DESVIA':
            pc = arg
        elif op == 'SE_FALSO':
            if not pilha.pop():
                pc = arg

        elif op == 'CHAMA':
            funcao, n = arg
            if len(chamadas) >= LIMITE_DE_CHAMADAS:
                raise ErroMPL('execucao', linha, coluna,
                              f'estouro de pilha: mais de {LIMITE_DE_CHAMADAS} '
                              f'chamadas abertas (recursao sem fim?)')
            # Um registro novo: os argumentos saem da pilha de operandos e
            # viram as primeiras vagas; o resto comeca vazio.
            novas = [None] * funcao.vagas
            if n:
                novas[:n] = pilha[-n:]
                del pilha[-n:]
            chamadas.append(RegistroAtivacao(funcao, novas, pc))
            vagas = novas
            pc = funcao.entrada

        elif op in ('RETORNA', 'RETORNA_VAZIO'):
            # O valor devolvido (se houver) ja esta no topo da pilha de operandos.
            registro = chamadas.pop()
            if not chamadas:            # voltou do principal: fim do programa
                return
            vagas = chamadas[-1].vagas
            pc = registro.retorno

        elif op == 'DESCARTA':
            pilha.pop()

        elif op == 'ESCREVA':
            saida.write(_formatar(pilha.pop(), arg) + '\n')

        else:
            raise ErroMPL('execucao', linha, coluna, f'instrucao desconhecida {repr(op)}')
