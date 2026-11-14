"""
Entrega 4, segunda metade — geracao do codigo executavel.

Traduz o codigo de tres enderecos para as instrucoes de uma MAQUINA DE PILHA.
E aqui que os nomes viram posicoes de memoria: cada variavel, parametro e
temporario de uma funcao ganha um numero de vaga no registro de ativacao
(os parametros primeiro, na ordem, depois os demais na ordem em que aparecem).

Cada linha de tres enderecos vira poucas instrucoes de pilha. Por exemplo,
t3 = n.1 * t2 vira:

    CARREGA 0        ; n.1
    CARREGA 2        ; t2
    MULTIPLICA
    GUARDA 3         ; t3

O .mplb e texto puro, uma instrucao por linha, com comentarios que dizem qual
nome mora em cada vaga. Diretivas (comecam com ponto):

    .funcao <nome> <tipo> <parametros> <vagas>   abre uma funcao
    .linha <L> <C>                               posicao no fonte do comando
    .fim                                         fecha a funcao
    L3:                                          um rotulo

O conjunto completo de instrucoes esta no README.

Leiam antes: CONTRATOS.md secao 6.
"""
from mplc.intermediario import Const

OPCODES_BINARIOS = {
    '+': 'SOMA', '-': 'SUBTRAI', '*': 'MULTIPLICA', '%': 'RESTO',
    '==': 'IGUAL', '!=': 'DIFERENTE',
    '<': 'MENOR', '<=': 'MENOR_IGUAL', '>': 'MAIOR', '>=': 'MAIOR_IGUAL',
    'e': 'E', 'ou': 'OU',
}

CABECALHO = [
    '; MPL bytecode, gerado por ./compilar. Roda com ./executar.',
    '; Maquina de pilha: uma instrucao por linha; ";" comeca um comentario.',
    '; .funcao <nome> <tipo> <parametros> <vagas>   .linha <linha> <coluna>',
]


def _constante(c):
    """O texto de uma constante no .mplb. O real usa repr: volta exatamente igual."""
    if c.tipo == 'real':
        return 'real ' + repr(c.valor)
    return f'{c.tipo} {c}'


class _Funcao:
    """Gera o corpo de uma funcao e conta as vagas do registro de ativacao."""

    def __init__(self, funcao):
        self.funcao = funcao
        self.vagas = {}                       # nome -> numero da vaga
        for nome, _tipo in funcao.parametros:
            self.vaga(nome)
        self.linhas = []

    def vaga(self, nome):
        if nome not in self.vagas:
            self.vagas[nome] = len(self.vagas)
        return self.vagas[nome]

    def escrever(self, instrucao, comentario=None):
        if comentario:
            self.linhas.append(f'    {instrucao:<24}; {comentario}')
        else:
            self.linhas.append(f'    {instrucao}')

    def empilhar(self, operando):
        if isinstance(operando, Const):
            self.escrever(f'EMPILHA {_constante(operando)}')
        else:
            self.escrever(f'CARREGA {self.vaga(operando.nome)}', operando.nome)

    def guardar(self, destino):
        self.escrever(f'GUARDA {self.vaga(destino.nome)}', destino.nome)

    def traduzir(self, ins):
        op = ins.op
        if op == 'copia':
            self.empilhar(ins.a)
            self.guardar(ins.destino)

        elif op == 'binario':
            self.empilhar(ins.a)
            self.empilhar(ins.b)
            if ins.oper == '/':
                # O tipo do resultado decide qual divisao: 7 / 2 inteiro e 3.
                self.escrever('DIVIDE_INTEIRO' if ins.tipo == 'inteiro' else 'DIVIDE_REAL')
            else:
                self.escrever(OPCODES_BINARIOS[ins.oper])
            self.guardar(ins.destino)

        elif op == 'unario':
            self.empilhar(ins.a)
            self.escrever('NEGA' if ins.oper == '-' else 'NAO')
            self.guardar(ins.destino)

        elif op == 'real':
            self.empilhar(ins.a)
            self.escrever('PARA_REAL')
            self.guardar(ins.destino)

        elif op == 'desvie':
            self.escrever(f'DESVIA {ins.alvo}')

        elif op == 'seFalso':
            self.empilhar(ins.a)
            self.escrever(f'SE_FALSO {ins.alvo}')

        elif op == 'param':
            self.empilhar(ins.a)

        elif op == 'chama':
            self.escrever(f'CHAMA {ins.alvo} {ins.n}')
            if ins.destino is not None:
                self.guardar(ins.destino)
            elif ins.tipo != 'vazio':
                self.escrever('DESCARTA', 'valor devolvido e nao usado')

        elif op == 'retorne':
            if ins.a is None:
                self.escrever('RETORNA_VAZIO')
            else:
                self.empilhar(ins.a)
                self.escrever('RETORNA')

        elif op == 'escreva':
            self.empilhar(ins.a)
            self.escrever(f'ESCREVA {ins.tipo}')

    def gerar(self):
        posicao = None
        for ins in self.funcao.instrucoes:
            if ins.op == 'rotulo':
                self.linhas.append(f'{ins.alvo}:')
                continue
            if (ins.linha, ins.coluna) != posicao:
                posicao = (ins.linha, ins.coluna)
                self.linhas.append(f'.linha {ins.linha} {ins.coluna}')
            self.traduzir(ins)

        f = self.funcao
        cabecalho = f'.funcao {f.nome} {f.tipo} {len(f.parametros)} {len(self.vagas)}'
        mapa = ', '.join(f'{v}={nome}' for nome, v in self.vagas.items())
        return [cabecalho, f'; vagas: {mapa}' if mapa else '; vagas: nenhuma'] \
            + self.linhas + ['.fim']


def gerar(codigo_intermediario):
    """Devolve as linhas do arquivo .mplb."""
    linhas = list(CABECALHO)
    for funcao in codigo_intermediario:
        linhas.append('')
        linhas.extend(_Funcao(funcao).gerar())
    return linhas
