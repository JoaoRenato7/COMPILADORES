"""
Entrega 1 — analise lexica.

Transformar o texto do programa numa lista de tokens.

O que voces tem que devolver: uma lista de Token. O ultimo elemento e sempre
um token FIM_ARQUIVO. A regra de posicao dele esta em CONTRATOS.md, secao 7.

Leiam antes: LINGUAGEM.md secao 2, e CONTRATOS.md secao 2.
"""
from mplc.erros import ErroMPL


class Token:
    __slots__ = ('tipo', 'lexema', 'linha', 'coluna')

    def __init__(self, tipo, lexema, linha, coluna):
        self.tipo = tipo          
        self.lexema = lexema      
        self.linha = linha
        self.coluna = coluna      

    def __str__(self):
        
        return f"{self.linha},{self.coluna},{self.tipo},{self.lexema}"

    def __repr__(self):
        return f"Token({self.tipo!r}, {self.lexema!r}, {self.linha}, {self.coluna})"



PALAVRAS_RESERVADAS = {
    'funcao': 'FUNCAO',
    'retorne': 'RETORNE',
    'se': 'SE',
    'senao': 'SENAO',
    'enquanto': 'ENQUANTO',
    'escreva': 'ESCREVA',
    'inteiro': 'TIPO_INTEIRO',
    'real': 'TIPO_REAL',
    'logico': 'TIPO_LOGICO',
    'texto': 'TIPO_TEXTO',
    'vazio': 'TIPO_VAZIO',
    'verdadeiro': 'LOGICO',   
    'falso': 'LOGICO',
    'e': 'E',
    'ou': 'OU',
    'nao': 'NAO',
}


ESCAPES_VALIDOS = {'n', 't', '"', '\\'}


def _eh_letra(c):
    
    return ('a' <= c <= 'z') or ('A' <= c <= 'Z') or c == '_'


def _eh_digito(c):
    return '0' <= c <= '9'


def _eh_alfanum(c):
    return _eh_letra(c) or _eh_digito(c)


class _Lexer:
    """Estado do varredor: posicao no texto e a linha/coluna atuais."""

    def __init__(self, fonte):
        self.fonte = fonte
        self.pos = 0
        self.linha = 1
        self.coluna = 1

    # -- infraestrutura de varredura ------------------------------------

    def _fim(self):
        return self.pos >= len(self.fonte)

    def _peek(self, offset=0):
        i = self.pos + offset
        if i >= len(self.fonte):
            return None
        return self.fonte[i]

    def _avancar(self):
        """Consome um caractere e atualiza linha/coluna corretamente."""
        c = self.fonte[self.pos]
        self.pos += 1
        if c == '\n':
            self.linha += 1
            self.coluna = 1
        else:
            self.coluna += 1
        return c

    # -- laco principal --------------------------------------------------

    def tokenizar(self):
        tokens = []
        while True:
            self._pular_espacos_e_comentarios()
            if self._fim():
                break
            tokens.append(self._proximo_token())
        
        tokens.append(Token('FIM_ARQUIVO', '', self.linha, self.coluna))
        return tokens

    def _pular_espacos_e_comentarios(self):
        while not self._fim():
            c = self._peek()
            if c in (' ', '\t', '\r', '\n'):
                self._avancar()
                continue
            if c == '/' and self._peek(1) == '/':
                while not self._fim() and self._peek() != '\n':
                    self._avancar()
                continue
            if c == '/' and self._peek(1) == '*':
                linha0, col0 = self.linha, self.coluna
                self._avancar()  # '/'
                self._avancar()  # '*'
                fechado = False
                while not self._fim():
                    if self._peek() == '*' and self._peek(1) == '/':
                        self._avancar()
                        self._avancar()
                        fechado = True
                        break
                    self._avancar()
                if not fechado:
                    
                    raise ErroMPL('lexico', linha0, col0,
                                   'comentario de bloco nao fechado')
                continue
            break

    def _proximo_token(self):
        c = self._peek()
        if _eh_letra(c):
            return self._identificador_ou_palavra()
        if _eh_digito(c):
            return self._numero()
        if c == '"':
            return self._texto()
        return self._operador_ou_delimitador()

    # -- cada tipo de token -----------------------------------------------

    def _identificador_ou_palavra(self):
        linha0, col0 = self.linha, self.coluna
        letras = []
        while not self._fim() and _eh_alfanum(self._peek()):
            letras.append(self._avancar())
        lexema = ''.join(letras)
        tipo = PALAVRAS_RESERVADAS.get(lexema, 'ID')
        return Token(tipo, lexema, linha0, col0)

    def _numero(self):
        linha0, col0 = self.linha, self.coluna
        digitos = []
        while not self._fim() and _eh_digito(self._peek()):
            digitos.append(self._avancar())

        if not self._fim() and self._peek() == '.':
            prox = self._peek(1)
            if prox is not None and _eh_digito(prox):
                digitos.append(self._avancar())  # o ponto
                while not self._fim() and _eh_digito(self._peek()):
                    digitos.append(self._avancar())
                return Token('REAL', ''.join(digitos), linha0, col0)
            
            ponto_linha, ponto_col = self.linha, self.coluna
            raise ErroMPL('lexico', ponto_linha, ponto_col,
                           'numero real mal formado: esperava digito depois do ponto')

        return Token('INTEIRO', ''.join(digitos), linha0, col0)

    def _texto(self):
        linha0, col0 = self.linha, self.coluna
        self._avancar()  # abre aspas
        partes = ['"']
        while True:
            if self._fim():
                raise ErroMPL('lexico', linha0, col0, 'texto nao fechado')
            c = self._peek()
            if c == '\n':
                raise ErroMPL('lexico', linha0, col0,
                               'texto nao fechado antes do fim da linha')
            if c == '"':
                self._avancar()
                partes.append('"')
                break
            if c == '\\':
                barra_linha, barra_col = self.linha, self.coluna
                self._avancar()
                if self._fim():
                    raise ErroMPL('lexico', barra_linha, barra_col,
                                   'escape incompleto no fim do arquivo')
                prox = self._peek()
                if prox in ESCAPES_VALIDOS:
                    
                    partes.append('\\')
                    partes.append(prox)
                    self._avancar()
                else:
                    raise ErroMPL('lexico', barra_linha, barra_col,
                                   f"escape invalido '\\{prox}'")
            else:
                partes.append(c)
                self._avancar()
        return Token('TEXTO', ''.join(partes), linha0, col0)

    def _operador_ou_delimitador(self):
        linha0, col0 = self.linha, self.coluna
        c = self._avancar()

        def com_igual(tipo_duplo, tipo_simples):
            
            if not self._fim() and self._peek() == '=':
                self._avancar()
                return Token(tipo_duplo, c + '=', linha0, col0)
            if tipo_simples is None:
                raise ErroMPL('lexico', linha0, col0,
                               f"caractere inesperado '{c}'")
            return Token(tipo_simples, c, linha0, col0)

        if c == '<':
            return com_igual('MENOR_IGUAL', 'MENOR')
        if c == '>':
            return com_igual('MAIOR_IGUAL', 'MAIOR')
        if c == '=':
            return com_igual('IGUAL', 'ATRIBUI')
        if c == '!':
            
            return com_igual('DIFERENTE', None)

        simples = {
            '+': 'MAIS', '-': 'MENOS', '*': 'VEZES', '/': 'DIVIDE', '%': 'RESTO',
            '(': 'ABRE_PAR', ')': 'FECHA_PAR',
            '{': 'ABRE_CHAVE', '}': 'FECHA_CHAVE',
            ',': 'VIRGULA', ';': 'PONTO_VIRGULA',
        }
        if c in simples:
            return Token(simples[c], c, linha0, col0)

        raise ErroMPL('lexico', linha0, col0, f"caractere inesperado '{c}'")


def analisar(fonte):
    """Recebe o texto do programa. Devolve a lista de Token."""
    return _Lexer(fonte).tokenizar()