"""
Entrega 2 — analise sintatica.

Transformar a lista de tokens numa arvore.

Sugestao forte: descida recursiva, uma funcao por nivel de precedencia, na
ordem da secao 3.3 da especificacao. E como voces vao enxergar a precedencia
virar formato de arvore.

Gerador de parser (ANTLR, PLY, yacc) esta proibido nesta entrega e na
anterior — o objetivo e entender, e o gerador esconde exatamente a parte
que esta sendo ensinada.

Leiam antes: LINGUAGEM.md secoes 3 a 5, e CONTRATOS.md secao 3.
"""
from mplc.erros import ErroMPL


class No:
    """Um no da arvore. O rotulo e o que sai no --ast."""

    def __init__(self, rotulo, filhos=None, linha=0, coluna=0, **extra):
        self.rotulo = rotulo      # 'binario +', 'literal inteiro 1', 'bloco', ...
        self.filhos = filhos or []
        self.linha = linha
        self.coluna = coluna
        self.extra = extra        # o que a semantica quiser pendurar depois


# Tipos que podem aparecer numa declaracao, num parametro ou no retorno.
# O 'vazio' passa pela sintaxe; quem recusa 'vazio x;' e a semantica (E3).
TIPOS = {
    'TIPO_INTEIRO': 'inteiro',
    'TIPO_REAL': 'real',
    'TIPO_LOGICO': 'logico',
    'TIPO_TEXTO': 'texto',
    'TIPO_VAZIO': 'vazio',
}

# Cada nivel binario: tipo do token -> simbolo que sai no rotulo 'binario <op>'.
OPS_OU = {'OU': 'ou'}
OPS_E = {'E': 'e'}
OPS_IGUALDADE = {'IGUAL': '==', 'DIFERENTE': '!='}
OPS_RELACIONAL = {'MENOR': '<', 'MENOR_IGUAL': '<=',
                  'MAIOR': '>', 'MAIOR_IGUAL': '>='}
OPS_ADITIVO = {'MAIS': '+', 'MENOS': '-'}
OPS_MULTIPLICATIVO = {'VEZES': '*', 'DIVIDE': '/', 'RESTO': '%'}


def _descrever(tok):
    """Como o token aparece na mensagem de erro."""
    if tok.tipo == 'FIM_ARQUIVO':
        return 'o fim do arquivo'
    return f"'{tok.lexema}'"


class _Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0

    # -- infraestrutura ---------------------------------------------------

    def atual(self):
        return self.tokens[self.i]

    def proximo(self):
        """Um token de lookahead alem do atual (para decidir ID = ... ou ID(...))."""
        if self.i + 1 < len(self.tokens):
            return self.tokens[self.i + 1]
        return self.tokens[-1]

    def olha(self, *tipos):
        return self.atual().tipo in tipos

    def avancar(self):
        tok = self.atual()
        if tok.tipo != 'FIM_ARQUIVO':
            self.i += 1
        return tok

    def erro(self, esperado):
        """Erro no token que APARECEU no lugar do esperado (CONTRATOS secao 7)."""
        tok = self.atual()
        raise ErroMPL('sintatico', tok.linha, tok.coluna,
                      f"esperava {esperado}, mas apareceu {_descrever(tok)}")

    def consumir(self, tipo, esperado):
        if not self.olha(tipo):
            self.erro(esperado)
        return self.avancar()

    def tipo(self):
        if not self.olha(*TIPOS):
            self.erro('um tipo (inteiro, real, logico, texto ou vazio)')
        return TIPOS[self.avancar().tipo]

    # -- programa e funcoes -----------------------------------------------

    def programa(self):
        # programa -> funcao* FIM_ARQUIVO
        funcoes = []
        while not self.olha('FIM_ARQUIVO'):
            funcoes.append(self.funcao())
        return No('programa', funcoes, 1, 1)

    def funcao(self):
        # funcao -> 'funcao' tipo ID '(' parametros ')' bloco
        inicio = self.consumir('FUNCAO', "'funcao'")
        tipo = self.tipo()
        nome = self.consumir('ID', 'o nome da funcao').lexema
        self.consumir('ABRE_PAR', "'('")
        params = self.parametros()
        self.consumir('FECHA_PAR', "')'")
        corpo = self.bloco()
        return No(f'funcao {nome} {tipo}', [params, corpo],
                  inicio.linha, inicio.coluna, nome=nome, tipo=tipo)

    def parametros(self):
        # parametros -> ( parametro (',' parametro)* )?
        tok = self.atual()
        lista = []
        if not self.olha('FECHA_PAR'):
            lista.append(self.parametro())
            while self.olha('VIRGULA'):
                self.avancar()
                lista.append(self.parametro())
        return No('parametros', lista, tok.linha, tok.coluna)

    def parametro(self):
        # parametro -> tipo ID
        tok = self.atual()
        tipo = self.tipo()
        nome = self.consumir('ID', 'o nome do parametro').lexema
        return No(f'parametro {nome} {tipo}', [], tok.linha, tok.coluna,
                  nome=nome, tipo=tipo)

    # -- comandos ---------------------------------------------------------

    def bloco(self):
        # bloco -> '{' comando* '}'
        inicio = self.consumir('ABRE_CHAVE', "'{'")
        comandos = []
        while not self.olha('FECHA_CHAVE'):
            if self.olha('FIM_ARQUIVO'):
                self.erro("'}'")
            comandos.append(self.comando())
        self.avancar()  # '}'
        return No('bloco', comandos, inicio.linha, inicio.coluna)

    def comando(self):
        # comando -> declaracao | atribuicao | chamada ';' | se | enquanto
        #          | escreva | retorne | bloco
        if self.olha('ABRE_CHAVE'):
            return self.bloco()     # bloco solto: abre escopo (LINGUAGEM 4.7)
        if self.olha(*TIPOS):
            return self.declaracao()
        if self.olha('SE'):
            return self.se()
        if self.olha('ENQUANTO'):
            return self.enquanto()
        if self.olha('ESCREVA'):
            return self.escreva()
        if self.olha('RETORNE'):
            return self.retorne()
        if self.olha('ID'):
            if self.proximo().tipo == 'ABRE_PAR':
                no = self.chamada()
                self.consumir('PONTO_VIRGULA', "';'")
                return no
            return self.atribuicao()
        self.erro('um comando')

    def declaracao(self):
        # declaracao -> tipo ID ('=' expressao)? ';'
        tok = self.atual()
        tipo = self.tipo()
        nome = self.consumir('ID', 'o nome da variavel').lexema
        filhos = []
        if self.olha('ATRIBUI'):
            self.avancar()
            filhos.append(self.expressao())
        self.consumir('PONTO_VIRGULA', "';'")
        return No(f'declaracao {nome} {tipo}', filhos, tok.linha, tok.coluna,
                  nome=nome, tipo=tipo)

    def atribuicao(self):
        # atribuicao -> ID '=' expressao ';'
        tok = self.avancar()  # o ID
        self.consumir('ATRIBUI', "'=' ou '('")
        valor = self.expressao()
        self.consumir('PONTO_VIRGULA', "';'")
        return No(f'atribuicao {tok.lexema}', [valor], tok.linha, tok.coluna,
                  nome=tok.lexema)

    def se(self):
        # se -> 'se' '(' expressao ')' bloco ('senao' bloco)?
        tok = self.avancar()
        self.consumir('ABRE_PAR', "'(' depois do se")
        cond = self.expressao()
        self.consumir('FECHA_PAR', "')'")
        filhos = [cond, self.bloco()]
        if self.olha('SENAO'):
            self.avancar()
            filhos.append(self.bloco())
        return No('se', filhos, tok.linha, tok.coluna)

    def enquanto(self):
        # enquanto -> 'enquanto' '(' expressao ')' bloco
        tok = self.avancar()
        self.consumir('ABRE_PAR', "'(' depois do enquanto")
        cond = self.expressao()
        self.consumir('FECHA_PAR', "')'")
        return No('enquanto', [cond, self.bloco()], tok.linha, tok.coluna)

    def escreva(self):
        # escreva -> 'escreva' '(' expressao ')' ';'
        tok = self.avancar()
        self.consumir('ABRE_PAR', "'(' depois do escreva")
        valor = self.expressao()
        self.consumir('FECHA_PAR', "')'")
        self.consumir('PONTO_VIRGULA', "';'")
        return No('escreva', [valor], tok.linha, tok.coluna)

    def retorne(self):
        # retorne -> 'retorne' expressao? ';'
        tok = self.avancar()
        filhos = []
        if not self.olha('PONTO_VIRGULA'):
            filhos.append(self.expressao())
        self.consumir('PONTO_VIRGULA', "';'")
        return No('retorne', filhos, tok.linha, tok.coluna)

    # -- expressoes: um nivel por funcao, do mais fraco ao mais forte -------

    def expressao(self):
        return self.ou()

    def _binario(self, operadores, proximo_nivel):
        """Nivel binario associativo a ESQUERDA.

        Le um operando do nivel de baixo e, enquanto houver operador deste
        nivel, junta o que ja leu (esquerda) com o proximo operando (direita).
        O laco -- e nao a recursao a direita -- e o que faz
        10 - 4 - 3 virar (10 - 4) - 3.
        """
        esquerda = proximo_nivel()
        while self.olha(*operadores):
            op = self.avancar()
            direita = proximo_nivel()
            esquerda = No(f'binario {operadores[op.tipo]}', [esquerda, direita],
                          op.linha, op.coluna, op=operadores[op.tipo])
        return esquerda

    def ou(self):             # nivel 1
        return self._binario(OPS_OU, self.e)

    def e(self):              # nivel 2
        return self._binario(OPS_E, self.igualdade)

    def igualdade(self):      # nivel 3
        return self._binario(OPS_IGUALDADE, self.relacional)

    def relacional(self):     # nivel 4
        return self._binario(OPS_RELACIONAL, self.aditiva)

    def aditiva(self):        # nivel 5
        return self._binario(OPS_ADITIVO, self.multiplicativa)

    def multiplicativa(self): # nivel 6
        return self._binario(OPS_MULTIPLICATIVO, self.unaria)

    def unaria(self):         # nivel 7: associativo a DIREITA
        # unaria -> ('nao' | '-') unaria | primaria
        if self.olha('NAO', 'MENOS'):
            op = self.avancar()
            simbolo = 'nao' if op.tipo == 'NAO' else '-'
            operando = self.unaria()   # chama a si mesma: nao nao x
            return No(f'unario {simbolo}', [operando], op.linha, op.coluna,
                      op=simbolo)
        return self.primaria()

    def primaria(self):       # nivel 8
        # primaria -> INTEIRO | REAL | LOGICO | TEXTO | ID | chamada
        #           | '(' expressao ')'
        tok = self.atual()
        if tok.tipo == 'INTEIRO':
            self.avancar()
            return No(f'literal inteiro {int(tok.lexema)}', [], tok.linha,
                      tok.coluna, tipo='inteiro', valor=int(tok.lexema))
        if tok.tipo == 'REAL':
            self.avancar()
            valor = float(tok.lexema)
            return No(f'literal real {valor:.6f}', [], tok.linha, tok.coluna,
                      tipo='real', valor=valor)
        if tok.tipo == 'LOGICO':
            self.avancar()
            return No(f'literal logico {tok.lexema}', [], tok.linha, tok.coluna,
                      tipo='logico', valor=(tok.lexema == 'verdadeiro'))
        if tok.tipo == 'TEXTO':
            self.avancar()
            return No(f'literal texto {tok.lexema}', [], tok.linha, tok.coluna,
                      tipo='texto', valor=tok.lexema)
        if tok.tipo == 'ID':
            if self.proximo().tipo == 'ABRE_PAR':
                return self.chamada()
            self.avancar()
            return No(f'variavel {tok.lexema}', [], tok.linha, tok.coluna,
                      nome=tok.lexema)
        if tok.tipo == 'ABRE_PAR':
            # Os parenteses so agrupam: nao viram no, a arvore ja mostra a ordem.
            self.avancar()
            dentro = self.expressao()
            self.consumir('FECHA_PAR', "')'")
            return dentro
        self.erro('uma expressao')

    def chamada(self):
        # chamada -> ID '(' ( expressao (',' expressao)* )? ')'
        tok = self.avancar()  # o nome
        self.consumir('ABRE_PAR', "'('")
        args = []
        if not self.olha('FECHA_PAR'):
            args.append(self.expressao())
            while self.olha('VIRGULA'):
                self.avancar()
                args.append(self.expressao())
        self.consumir('FECHA_PAR', "')' ou ','")
        return No(f'chamada {tok.lexema}', args, tok.linha, tok.coluna,
                  nome=tok.lexema)


def analisar(tokens):
    """Recebe a lista de Token. Devolve a raiz da arvore (um No 'programa')."""
    return _Parser(tokens).programa()


def despejar(no, nivel=0, saida=None):
    """Imprime a arvore no formato do --ast. Ja esta pronto: dois espacos por nivel."""
    saida = saida if saida is not None else []
    saida.append('  ' * nivel + no.rotulo)
    for f in no.filhos:
        despejar(f, nivel + 1, saida)
    return saida
