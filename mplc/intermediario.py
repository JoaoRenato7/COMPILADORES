"""
Entrega 4, primeira metade — codigo de tres enderecos.

Percorre a arvore ja conferida pela semantica e a achata numa lista de
instrucoes simples, uma por linha, com NO MAXIMO UM OPERADOR cada.
Uma expressao como a + b * c vira duas linhas, com um temporario no meio:

    t0 = b * c
    t1 = a + t0

Tres tipos de nome aparecem no codigo:
  - variaveis e parametros do fonte, com o numero do escopo onde vivem:
    x.4 e o x do escopo 4 do --tabela. E assim que o x de dentro e o x de
    fora deixam de se confundir (o programa 06-escopo tem tres x);
  - temporarios, t0, t1, ..., um por resultado intermediario;
  - rotulos, L0, L1, ..., os destinos de desvio.

Cada instrucao guarda a linha e a coluna do COMANDO que a gerou. O codigo
de tres enderecos nao usa isso, mas a maquina virtual precisa: o erro de
execucao e relatado na linha do comando que estava rodando.

Leiam antes: CONTRATOS.md secao 5.
"""


# -- os operandos ------------------------------------------------------------

def _real_txt(valor):
    """Um real escrito sem notacao cientifica: 1e-07 traria um '-' para a linha."""
    texto = repr(valor)
    if 'e' in texto or 'E' in texto:
        texto = f'{valor:.20f}'.rstrip('0')
        if texto.endswith('.'):
            texto += '0'
    return texto


class Const:
    """Uma constante, com o tipo dela. O texto guarda as aspas e os escapes."""

    def __init__(self, tipo, valor):
        self.tipo = tipo
        self.valor = valor

    def __str__(self):
        if self.tipo == 'inteiro':
            return str(self.valor)
        if self.tipo == 'real':
            return _real_txt(self.valor)
        if self.tipo == 'logico':
            return 'verdadeiro' if self.valor else 'falso'
        return self.valor            # texto: o lexema, "com aspas"


class Nome:
    """Uma variavel do fonte (x.4) ou um temporario (t3)."""

    def __init__(self, nome):
        self.nome = nome

    def __str__(self):
        return self.nome


VALOR_PADRAO = {
    'inteiro': Const('inteiro', 0),
    'real': Const('real', 0.0),
    'logico': Const('logico', False),
    'texto': Const('texto', '""'),
}


# -- as instrucoes -------------------------------------------------------------

class Instrucao:
    """
    Uma linha do codigo de tres enderecos. O campo `op` diz qual das formas:

      copia     destino = a
      binario   destino = a <oper> b          (tipo: o tipo do resultado)
      unario    destino = <oper> a            (oper: '-' ou 'nao')
      real      destino = real a              (a conversao inteiro -> real)
      rotulo    L:
      desvie    desvie L
      seFalso   seFalso a desvie L
      param     param a
      chama     [destino =] chama f n         (tipo: o retorno de f)
      retorne   retorne [a]
      escreva   escreva a                     (tipo: o tipo de a)
    """

    def __init__(self, op, destino=None, a=None, b=None, oper=None,
                 tipo=None, alvo=None, n=0, linha=0, coluna=0):
        self.op = op
        self.destino = destino
        self.a = a
        self.b = b
        self.oper = oper
        self.tipo = tipo
        self.alvo = alvo          # rotulo de desvio, ou nome da funcao chamada
        self.n = n                # quantos argumentos a chamada leva
        self.linha = linha
        self.coluna = coluna

    def __str__(self):
        op = self.op
        if op == 'rotulo':
            return f'{self.alvo}:'
        if op == 'copia':
            texto = f'{self.destino} = {self.a}'
        elif op == 'binario':
            texto = f'{self.destino} = {self.a} {self.oper} {self.b}'
        elif op == 'unario':
            texto = f'{self.destino} = {self.oper} {self.a}'
        elif op == 'real':
            texto = f'{self.destino} = real {self.a}'
        elif op == 'desvie':
            texto = f'desvie {self.alvo}'
        elif op == 'seFalso':
            texto = f'seFalso {self.a} desvie {self.alvo}'
        elif op == 'param':
            texto = f'param {self.a}'
        elif op == 'chama':
            texto = f'chama {self.alvo} {self.n}'
            if self.destino is not None:
                texto = f'{self.destino} = {texto}'
        elif op == 'retorne':
            texto = 'retorne' if self.a is None else f'retorne {self.a}'
        else:  # escreva
            texto = f'escreva {self.a}'
        return '  ' + texto


class Funcao:
    def __init__(self, nome, tipo, parametros, linha):
        self.nome = nome
        self.tipo = tipo
        self.parametros = parametros    # lista de (nome no codigo, tipo)
        self.linha = linha
        self.instrucoes = []


# -- a traducao da arvore ------------------------------------------------------

def _nome_de(no):
    """O nome de uma variavel ou parametro no codigo: nome.escopo."""
    simbolo = no.extra['simbolo']
    return f'{simbolo.nome}.{simbolo.escopo.numero}'


class _Tradutor:
    def __init__(self):
        self.funcoes = []
        self.proximo_rotulo = 0      # rotulos unicos no programa inteiro
        self.funcao = None
        self.proximo_temp = 0        # temporarios recomecam em cada funcao
        self.posicao = (0, 0)        # o comando que esta sendo traduzido

    # -- infraestrutura -----------------------------------------------------

    def emitir(self, op, **campos):
        linha, coluna = self.posicao
        ins = Instrucao(op, linha=linha, coluna=coluna, **campos)
        self.funcao.instrucoes.append(ins)
        return ins

    def temp(self):
        t = Nome(f't{self.proximo_temp}')
        self.proximo_temp += 1
        return t

    def rotulo(self):
        r = f'L{self.proximo_rotulo}'
        self.proximo_rotulo += 1
        return r

    def em(self, no):
        """A partir daqui, as instrucoes pertencem ao comando `no`."""
        self.posicao = (no.linha, no.coluna)

    # -- programa e funcoes -------------------------------------------------

    def programa(self, raiz):
        for f in raiz.filhos:
            self.traduzir_funcao(f)
        return self.funcoes

    def traduzir_funcao(self, no):
        parametros = [(_nome_de(p), p.extra['tipo']) for p in no.filhos[0].filhos]
        self.funcao = Funcao(no.extra['nome'], no.extra['tipo'], parametros, no.linha)
        self.funcoes.append(self.funcao)
        self.proximo_temp = 0

        self.bloco(no.filhos[1])

        # Uma funcao vazio pode terminar sem 'retorne': o retorno fica explicito.
        # Nas outras, a semantica ja garantiu um retorne em todo caminho.
        if self.funcao.tipo == 'vazio':
            self.em(no)
            self.emitir('retorne')

    # -- comandos -----------------------------------------------------------

    def bloco(self, no):
        for comando in no.filhos:
            self.comando(comando)

    def comando(self, no):
        tipo_no = no.rotulo.split()[0]
        self.em(no)

        if tipo_no == 'bloco':
            self.bloco(no)

        elif tipo_no == 'declaracao':
            # Sem valor inicial, a variavel recebe o padrao do tipo. Isso roda
            # toda vez que a declaracao roda: dentro de um laco, a cada volta.
            if no.filhos:
                valor = self.expressao(no.filhos[0])
            else:
                valor = VALOR_PADRAO[no.extra['tipo']]
            self.emitir('copia', destino=Nome(_nome_de(no)), a=valor)

        elif tipo_no == 'atribuicao':
            valor = self.expressao(no.filhos[0])
            self.emitir('copia', destino=Nome(_nome_de(no)), a=valor)

        elif tipo_no == 'se':
            cond = self.expressao(no.filhos[0])
            senao = self.rotulo()
            self.emitir('seFalso', a=cond, alvo=senao)
            self.bloco(no.filhos[1])
            if len(no.filhos) == 3:
                fim = self.rotulo()
                self.em(no)
                self.emitir('desvie', alvo=fim)
                self.emitir('rotulo', alvo=senao)
                self.bloco(no.filhos[2])
                self.emitir('rotulo', alvo=fim)
            else:
                self.emitir('rotulo', alvo=senao)

        elif tipo_no == 'enquanto':
            inicio, fim = self.rotulo(), self.rotulo()
            self.emitir('rotulo', alvo=inicio)
            cond = self.expressao(no.filhos[0])
            self.emitir('seFalso', a=cond, alvo=fim)
            self.bloco(no.filhos[1])
            self.em(no)
            self.emitir('desvie', alvo=inicio)
            self.emitir('rotulo', alvo=fim)

        elif tipo_no == 'escreva':
            expr = no.filhos[0]
            valor = self.expressao(expr)
            self.emitir('escreva', a=valor, tipo=expr.extra['tipo'])

        elif tipo_no == 'retorne':
            if no.filhos:
                self.emitir('retorne', a=self.expressao(no.filhos[0]))
            else:
                self.emitir('retorne')

        elif tipo_no == 'chamada':
            # Chamada como comando: se a funcao devolver algo, o valor e jogado fora.
            self.chamada(no, guardar=False)

    # -- expressoes: cada uma devolve o operando onde o resultado ficou --------

    def expressao(self, no):
        operando = self._valor(no)
        if no.extra.get('converter_para_real'):
            # A conversao vem DEPOIS de calcular o valor: em real x = 7 / 2,
            # a divisao e inteira (da 3) e so entao vira 3.0.
            if isinstance(operando, Const):
                return Const('real', float(operando.valor))
            t = self.temp()
            self.emitir('real', destino=t, a=operando)
            return t
        return operando

    def _valor(self, no):
        tipo_no = no.rotulo.split()[0]

        if tipo_no == 'literal':
            return Const(no.extra['tipo'], no.extra['valor'])

        if tipo_no == 'variavel':
            return Nome(_nome_de(no))

        if tipo_no == 'chamada':
            return self.chamada(no, guardar=True)

        if tipo_no == 'unario':
            a = self.expressao(no.filhos[0])
            t = self.temp()
            self.emitir('unario', destino=t, oper=no.extra['op'], a=a)
            return t

        # binario: os dois lados sao sempre calculados (a MPL nao tem
        # curto-circuito), entao 'e' e 'ou' sao operadores como os outros.
        a = self.expressao(no.filhos[0])
        b = self.expressao(no.filhos[1])
        t = self.temp()
        self.emitir('binario', destino=t, a=a, oper=no.extra['op'], b=b,
                    tipo=no.extra['tipo'])
        return t

    def chamada(self, no, guardar):
        funcao = no.extra['simbolo']
        # Primeiro todos os argumentos, depois todos os param: uma chamada
        # dentro de um argumento termina antes de a de fora comecar.
        args = [self.expressao(a) for a in no.filhos]
        for a in args:
            self.emitir('param', a=a)
        destino = self.temp() if guardar else None
        self.emitir('chama', destino=destino, alvo=funcao.nome, n=len(args),
                    tipo=funcao.tipo)
        return destino


def gerar(arvore, tabela):
    """Devolve o codigo de tres enderecos: uma lista de Funcao."""
    return _Tradutor().programa(arvore)


def despejar(codigo):
    """Devolve as linhas do --ir."""
    linhas = []
    for f in codigo:
        if linhas:
            linhas.append('')
        params = ', '.join(f'{nome} {tipo}' for nome, tipo in f.parametros)
        linhas.append(f'funcao {f.nome} {f.tipo} ({params})')
        linhas.extend(str(ins) for ins in f.instrucoes)
        linhas.append('fim')
    return linhas
