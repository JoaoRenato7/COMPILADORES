"""
Entrega 3 — analise semantica.

Tabela de simbolos, escopos aninhados e verificacao de tipos.

Tres coisas que costumam ser esquecidas e valem nota:
  - o corpo de uma funcao abre DOIS escopos (o dos parametros e o do bloco);
  - uma funcao pode ser chamada antes de aparecer no arquivo, entao a
    primeira passada so coleta assinaturas;
  - funcao com retorno declarado precisa garantir o retorno em TODOS os
    caminhos.

Leiam antes: LINGUAGEM.md secoes 3 a 5, e CONTRATOS.md secao 4.
"""
from mplc.erros import ErroMPL
 
NUMERICOS = ('inteiro', 'real')
 
 
class Simbolo:
    """Um nome declarado: funcao, parametro ou variavel."""
 
    def __init__(self, nome, categoria, tipo, linha, escopo, parametros=None):
        self.nome = nome
        self.categoria = categoria    # 'funcao', 'parametro' ou 'variavel'
        self.tipo = tipo              # o tipo; numa funcao, o tipo de retorno
        self.linha = linha
        self.escopo = escopo          # o Escopo onde o nome vive
        self.parametros = parametros or []   # so funcao: tipos dos parametros
 
 
class Escopo:
    def __init__(self, numero, descricao, pai):
        self.numero = numero
        self.descricao = descricao    # 'global', 'funcao <nome>' ou 'bloco'
        self.pai = pai                # o Escopo de fora (None no global)
        self.simbolos = {}            # nome -> Simbolo; o dict guarda a ordem
 
    def buscar(self, nome):
        """Procura aqui e, se nao achar, sobe pelos pais (sombreamento)."""
        escopo = self
        while escopo is not None:
            if nome in escopo.simbolos:
                return escopo.simbolos[nome]
            escopo = escopo.pai
        return None
 
 
class Tabela:
    """O resultado da analise: todos os escopos, na ordem em que abriram."""
 
    def __init__(self):
        self.escopos = []
        self.global_ = self.novo_escopo('global', None)
 
    def novo_escopo(self, descricao, pai):
        escopo = Escopo(len(self.escopos), descricao, pai)
        self.escopos.append(escopo)
        return escopo
 
 
def _erro(no, mensagem):
    raise ErroMPL('semantico', no.linha, no.coluna, mensagem)
 
 
def _cabe(origem, destino):
    """A unica conversao implicita da MPL: inteiro vira real (secao 3.1)."""
    return origem == destino or (origem == 'inteiro' and destino == 'real')
 
 
def _converter_se_preciso(no, tipo_no, destino):
    """Marca no no da arvore a conversao inteiro -> real, para a Entrega 4."""
    if tipo_no == 'inteiro' and destino == 'real':
        no.extra['converter_para_real'] = True
 
 
class _Analisador:
    def __init__(self):
        self.tabela = Tabela()
        self.atual = self.tabela.global_
        self.funcao_atual = None      # Simbolo da funcao sendo analisada
 
    # -- escopos ------------------------------------------------------------
 
    def abrir(self, descricao):
        self.atual = self.tabela.novo_escopo(descricao, self.atual)
        return self.atual
 
    def fechar(self):
        self.atual = self.atual.pai
 
    def declarar(self, no, nome, categoria, tipo, parametros=None):
        if nome in self.atual.simbolos:
            _erro(no, f"'{nome}' ja foi declarado neste escopo")
        simbolo = Simbolo(nome, categoria, tipo, no.linha, self.atual, parametros)
        self.atual.simbolos[nome] = simbolo
        no.extra['simbolo'] = simbolo
        return simbolo
 
    # -- programa -----------------------------------------------------------
 
    def programa(self, raiz):
        funcoes = raiz.filhos
 
        # Passada 1: so as assinaturas, no escopo 0.
        for f in funcoes:
            parametros = [p.extra['tipo'] for p in f.filhos[0].filhos]
            self.declarar(f, f.extra['nome'], 'funcao', f.extra['tipo'], parametros)
 
        principal = self.tabela.global_.simbolos.get('principal')
        if principal is None:
            raise ErroMPL('semantico', 1, 1, "falta a funcao 'principal'")
        no_principal = next(f for f in funcoes if f.extra['nome'] == 'principal')
        if principal.parametros:
            _erro(no_principal, "'principal' nao pode receber parametros")
        if principal.tipo != 'vazio':
            _erro(no_principal, "'principal' tem que devolver vazio")
 
        # Passada 2: o corpo de cada funcao.
        for f in funcoes:
            self.funcao(f)
        return self.tabela
 
    def funcao(self, no):
        self.funcao_atual = no.extra['simbolo']
        parametros, corpo = no.filhos
 
        self.abrir(f"funcao {no.extra['nome']}")        # escopo dos parametros
        for p in parametros.filhos:
            if p.extra['tipo'] == 'vazio':
                _erro(p, f"o parametro '{p.extra['nome']}' nao pode ser vazio")
            self.declarar(p, p.extra['nome'], 'parametro', p.extra['tipo'])
        self.bloco(corpo)                               # escopo do corpo
        self.fechar()
 
        if self.funcao_atual.tipo != 'vazio' and not self.garante_retorno(corpo):
            _erro(no, f"a funcao '{no.extra['nome']}' nao retorna em todos os caminhos")
 
    # -- garantia de retorno: olha a ESTRUTURA, nunca o valor das condicoes ---
 
    def garante_retorno(self, no):
        rotulo = no.rotulo
        if rotulo == 'retorne':
            return True
        if rotulo == 'bloco':
            return any(self.garante_retorno(c) for c in no.filhos)
        if rotulo == 'se':
            # So um se COM senao, e com os dois lados garantindo.
            return (len(no.filhos) == 3
                    and self.garante_retorno(no.filhos[1])
                    and self.garante_retorno(no.filhos[2]))
        return False   # enquanto pode rodar zero vezes; o resto nao retorna
 
    # -- comandos -------------------------------------------------------------
 
    def bloco(self, no):
        no.extra['escopo'] = self.abrir('bloco')
        for comando in no.filhos:
            self.comando(comando)
        self.fechar()
 
    def comando(self, no):
        tipo_no = no.rotulo.split()[0]
 
        if tipo_no == 'bloco':
            self.bloco(no)
 
        elif tipo_no == 'declaracao':
            nome, tipo = no.extra['nome'], no.extra['tipo']
            if tipo == 'vazio':
                _erro(no, f"a variavel '{nome}' nao pode ser vazio")
            if no.filhos:
                # O valor inicial e conferido ANTES de declarar: em
                # 'inteiro x = x + 1;' o x da direita e o de fora.
                valor = no.filhos[0]
                t = self.expressao(valor)
                if not _cabe(t, tipo):
                    _erro(no, f"nao da para guardar {t} na variavel '{nome}', que e {tipo}")
                _converter_se_preciso(valor, t, tipo)
            self.declarar(no, nome, 'variavel', tipo)
 
        elif tipo_no == 'atribuicao':
            nome = no.extra['nome']
            simbolo = self.atual.buscar(nome)
            if simbolo is None:
                _erro(no, f"a variavel '{nome}' nao foi declarada")
            if simbolo.categoria == 'funcao':
                _erro(no, f"'{nome}' e uma funcao, nao da para atribuir a ela")
            no.extra['simbolo'] = simbolo
            valor = no.filhos[0]
            t = self.expressao(valor)
            if not _cabe(t, simbolo.tipo):
                _erro(no, f"nao da para guardar {t} em '{nome}', que e {simbolo.tipo}")
            _converter_se_preciso(valor, t, simbolo.tipo)
 
        elif tipo_no == 'se':
            self.condicao(no.filhos[0], 'se')
            self.bloco(no.filhos[1])
            if len(no.filhos) == 3:
                self.bloco(no.filhos[2])
 
        elif tipo_no == 'enquanto':
            self.condicao(no.filhos[0], 'enquanto')
            self.bloco(no.filhos[1])
 
        elif tipo_no == 'escreva':
            self.expressao(no.filhos[0])   # vazio ja e recusado dentro dela
 
        elif tipo_no == 'retorne':
            esperado = self.funcao_atual.tipo
            if esperado == 'vazio':
                if no.filhos:
                    _erro(no, f"a funcao '{self.funcao_atual.nome}' e vazio e nao devolve valor")
            else:
                if not no.filhos:
                    _erro(no, f"a funcao '{self.funcao_atual.nome}' tem que devolver {esperado}")
                t = self.expressao(no.filhos[0])
                if not _cabe(t, esperado):
                    _erro(no, f"devolvendo {t}, mas a funcao devolve {esperado}")
                _converter_se_preciso(no.filhos[0], t, esperado)
 
        elif tipo_no == 'chamada':
            # Chamada como comando: aqui, e so aqui, uma funcao vazio e aceita.
            self.chamada(no)
 
    def condicao(self, no, comando):
        t = self.expressao(no)
        if t != 'logico':
            _erro(no, f"a condicao do {comando} tem que ser logico, mas e {t}")
 
    # -- expressoes: devolvem o tipo e o anotam em no.extra['tipo'] ----------
 
    def expressao(self, no):
        tipo = self._tipo_de(no)
        if tipo == 'vazio':
            _erro(no, f"a funcao '{no.extra['nome']}' e vazio e nao pode estar numa expressao")
        no.extra['tipo'] = tipo
        return tipo
 
    def _tipo_de(self, no):
        tipo_no = no.rotulo.split()[0]
 
        if tipo_no == 'literal':
            return no.extra['tipo']
 
        if tipo_no == 'variavel':
            nome = no.extra['nome']
            simbolo = self.atual.buscar(nome)
            if simbolo is None:
                _erro(no, f"a variavel '{nome}' nao foi declarada")
            if simbolo.categoria == 'funcao':
                _erro(no, f"'{nome}' e uma funcao; faltou chamar com ( )")
            no.extra['simbolo'] = simbolo
            return simbolo.tipo
 
        if tipo_no == 'chamada':
            return self.chamada(no)
 
        if tipo_no == 'unario':
            op = no.extra['op']
            t = self.expressao(no.filhos[0])
            if op == 'nao':
                if t != 'logico':
                    _erro(no, f"'nao' precisa de logico, mas recebeu {t}")
                return 'logico'
            if t not in NUMERICOS:
                _erro(no, f"o '-' unario precisa de numero, mas recebeu {t}")
            return t
 
        # binario
        op = no.extra['op']
        esq, dir_ = no.filhos
        te, td = self.expressao(esq), self.expressao(dir_)
 
        if op in ('e', 'ou'):
            if te != 'logico' or td != 'logico':
                _erro(no, f"'{op}' precisa de logico dos dois lados, veio {te} e {td}")
            return 'logico'
 
        if op in ('==', '!='):
            if not (_cabe(te, td) or _cabe(td, te)):
                _erro(no, f"nao da para comparar {te} com {td}")
            self._igualar_numeros(esq, te, dir_, td)
            return 'logico'
 
        if op == '+' and te == 'texto' and td == 'texto':
            return 'texto'
 
        if op == '%':
            if te != 'inteiro' or td != 'inteiro':
                _erro(no, f"'%' so aceita inteiro e inteiro, veio {te} e {td}")
            return 'inteiro'
 
        # + - * / < <= > >=
        if te not in NUMERICOS or td not in NUMERICOS:
            _erro(no, f"'{op}' nao aceita {te} e {td}")
        self._igualar_numeros(esq, te, dir_, td)
        if op in ('<', '<=', '>', '>='):
            return 'logico'
        return 'inteiro' if te == td == 'inteiro' else 'real'
 
    def _igualar_numeros(self, esq, te, dir_, td):
        """Num operador com inteiro de um lado e real do outro, o inteiro vira real."""
        if te == 'inteiro' and td == 'real':
            _converter_se_preciso(esq, te, 'real')
        if td == 'inteiro' and te == 'real':
            _converter_se_preciso(dir_, td, 'real')
 
    def chamada(self, no):
        nome = no.extra['nome']
        simbolo = self.atual.buscar(nome)
        if simbolo is None:
            _erro(no, f"a funcao '{nome}' nao existe")
        if simbolo.categoria != 'funcao':
            _erro(no, f"'{nome}' e uma variavel, nao uma funcao")
        no.extra['simbolo'] = simbolo
 
        args, params = no.filhos, simbolo.parametros
        if len(args) != len(params):
            _erro(no, f"'{nome}' espera {len(params)} argumento(s), recebeu {len(args)}")
        for i, (arg, tipo_param) in enumerate(zip(args, params), start=1):
            t = self.expressao(arg)
            if not _cabe(t, tipo_param):
                _erro(arg, f"o argumento {i} de '{nome}' tem que ser {tipo_param}, mas e {t}")
            _converter_se_preciso(arg, t, tipo_param)
        return simbolo.tipo
 
 
def analisar(arvore):
    """Percorre a arvore, monta a tabela e confere os tipos. Devolve a tabela."""
    return _Analisador().programa(arvore)
 
 
def despejar(tabela):
    """Devolve as linhas do --tabela, no formato da secao 4 do contrato."""
    linhas = []
    for escopo in tabela.escopos:
        if escopo.pai is None:
            linhas.append(f'escopo {escopo.numero} {escopo.descricao}')
        else:
            linhas.append(f'escopo {escopo.numero} {escopo.descricao} pai {escopo.pai.numero}')
        for s in escopo.simbolos.values():
            if s.categoria == 'funcao':
                tipo = f"{s.tipo}({','.join(s.parametros)})"
            else:
                tipo = s.tipo
            linhas.append(f'  {s.nome}|{s.categoria}|{tipo}|{s.linha}')
    return linhas