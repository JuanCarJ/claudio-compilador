"""
╔══════════════════════════════════════════════════════════════╗
║  CLAUDIO — Parser Descendente Recursivo (Metodo 1)          ║
║  Una funcion por cada no-terminal de la gramatica BNF       ║
║  Construye arbol de analisis sintactico (NodoArbol)         ║
╚══════════════════════════════════════════════════════════════╝

Consume tokens producidos por lexer.py y construye el arbol
de derivacion. Reporta el primer error sintactico encontrado.
"""

from typing import List, Optional
from lexer import Token, TokenType
from arbol import NodoArbol


# ─────────────────────────────────────────────
# § 1  EXCEPCION DE ERROR SINTACTICO
# ─────────────────────────────────────────────

class ErrorSintactico(Exception):
    def __init__(self, mensaje: str, fila: int = 0, columna: int = 0):
        self.mensaje = mensaje
        self.fila = fila
        self.columna = columna
        super().__init__(mensaje)


# ─────────────────────────────────────────────
# § 2  CONJUNTOS FIRST PARA DESPACHO
# ─────────────────────────────────────────────

# Tokens que inician una sentencia
FIRST_SENTENCIA = {
    TokenType.IDENTIFICADOR, TokenType.PR_ESTE,
    TokenType.PR_SI, TokenType.PR_PARA, TokenType.PR_MIENTRAS,
    TokenType.PR_RETORNAR, TokenType.PR_IMPRIMIR,
    TokenType.PR_ROMPER, TokenType.PR_CONTINUAR,
    TokenType.PR_VAR, TokenType.PR_SEA,
}

# Tokens que inician una declaracion (superset de sentencia)
FIRST_DECLARACION = FIRST_SENTENCIA | {
    TokenType.PR_FUNCION, TokenType.PR_CLASE, TokenType.PR_IMPORTAR,
}

# Tokens que inician una expresion
FIRST_EXPRESION = {
    TokenType.IDENTIFICADOR,
    TokenType.LIT_ENTERO, TokenType.LIT_REAL, TokenType.LIT_CADENA,
    TokenType.PR_VERDADERO, TokenType.PR_FALSO, TokenType.PR_NULO,
    TokenType.PR_NUEVO, TokenType.PR_NO,
    TokenType.OP_RESTA,  # unario negativo
    TokenType.PAREN_IZQ,
    TokenType.PR_ESTE,
}

# Tokens de tipo basico
TIPOS_BASICOS = {
    TokenType.PR_ENTERO, TokenType.PR_REAL,
    TokenType.PR_CADENA, TokenType.PR_BOOLEANO,
}

# Tokens que cierran un bloque (FOLLOW de bloque)
CIERRE_BLOQUE = {
    TokenType.PR_FIN_SI, TokenType.PR_SINO,
    TokenType.PR_FIN_PARA, TokenType.PR_FIN_MIENTRAS,
    TokenType.PR_FIN_FUNCION, TokenType.PR_FIN_CLASE,
    TokenType.FIN_DE_ARCHIVO,
}


# ─────────────────────────────────────────────
# § 3  PARSER DESCENDENTE RECURSIVO
# ─────────────────────────────────────────────

class ParserDescendenteRecursivo:
    """
    Analizador sintactico descendente recursivo para Claudio.
    Cada no-terminal tiene su propia funcion de parse.
    """

    def __init__(self, tokens: List[Token]):
        # Filtrar comentarios
        self.tokens = [t for t in tokens
                       if t.tipo not in (TokenType.COMENTARIO_LINEA,
                                         TokenType.COMENTARIO_BLOQUE,
                                         TokenType.ERROR_LEXICO)]
        self.pos = 0
        self.errores: List[str] = []

    # ── Utilidades de tokens ────────────────

    def _actual(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token("EOF", TokenType.FIN_DE_ARCHIVO, 0, 0)

    def _avanzar(self) -> Token:
        tok = self._actual()
        if self.pos < len(self.tokens):
            self.pos += 1
        return tok

    def _verificar(self, *tipos: TokenType) -> bool:
        return self._actual().tipo in tipos

    def _esperar(self, tipo: TokenType, contexto: str = "") -> Token:
        tok = self._actual()
        if tok.tipo == tipo:
            return self._avanzar()
        esperado = tipo.name
        encontrado = tok.tipo.name
        msg = (f"Error sintactico en fila {tok.fila}, col {tok.columna}: "
               f"se esperaba {esperado} pero se encontro '{tok.lexema}' ({encontrado})")
        if contexto:
            msg += f" en {contexto}"
        self.errores.append(msg)
        raise ErrorSintactico(msg, tok.fila, tok.columna)

    def _crear_nodo(self, simbolo: str) -> NodoArbol:
        return NodoArbol(simbolo=simbolo)

    def _crear_hoja(self, token: Token) -> NodoArbol:
        return NodoArbol(
            simbolo=token.tipo.name,
            lexema=token.lexema,
            es_terminal=True
        )

    def _crear_epsilon(self) -> NodoArbol:
        return NodoArbol(simbolo="ε", lexema="ε", es_terminal=True, es_epsilon=True)

    # ── Punto de entrada ────────────────────

    def analizar(self) -> NodoArbol:
        """Ejecuta el analisis sintactico. Retorna la raiz del arbol."""
        arbol = self._programa()
        if not self._verificar(TokenType.FIN_DE_ARCHIVO):
            tok = self._actual()
            msg = (f"Error sintactico en fila {tok.fila}, col {tok.columna}: "
                   f"tokens sobrantes despues del programa: '{tok.lexema}'")
            self.errores.append(msg)
            raise ErrorSintactico(msg, tok.fila, tok.columna)
        return arbol

    # ── § 3.1  Programa y declaraciones ─────

    def _programa(self) -> NodoArbol:
        """programa → declaracion programa | ε"""
        nodo = self._crear_nodo("programa")
        while self._verificar(*FIRST_DECLARACION):
            nodo.agregar_hijo(self._declaracion())
        if not nodo.hijos:
            nodo.agregar_hijo(self._crear_epsilon())
        return nodo

    def _declaracion(self) -> NodoArbol:
        """declaracion → def_funcion | def_clase | sentencia | importacion"""
        nodo = self._crear_nodo("declaracion")
        tok = self._actual()
        if tok.tipo == TokenType.PR_FUNCION:
            nodo.agregar_hijo(self._def_funcion())
        elif tok.tipo == TokenType.PR_CLASE:
            nodo.agregar_hijo(self._def_clase())
        elif tok.tipo == TokenType.PR_IMPORTAR:
            nodo.agregar_hijo(self._importacion())
        elif tok.tipo in FIRST_SENTENCIA:
            nodo.agregar_hijo(self._sentencia())
        else:
            msg = (f"Error sintactico en fila {tok.fila}, col {tok.columna}: "
                   f"declaracion inesperada: '{tok.lexema}'")
            self.errores.append(msg)
            raise ErrorSintactico(msg, tok.fila, tok.columna)
        return nodo

    def _importacion(self) -> NodoArbol:
        """importacion → importar ID"""
        nodo = self._crear_nodo("importacion")
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_IMPORTAR)))
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.IDENTIFICADOR, "importacion")))
        return nodo

    # ── § 3.2  Variables ────────────────────

    def _decl_variable(self) -> NodoArbol:
        """decl_variable → (var | sea) tipo ID = expresion"""
        nodo = self._crear_nodo("decl_variable")
        # var o sea
        nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
        nodo.agregar_hijo(self._tipo())
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.IDENTIFICADOR, "declaracion de variable")))
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.OP_ASIGNACION, "declaracion de variable")))
        nodo.agregar_hijo(self._expresion())
        return nodo

    # ── § 3.3  Funciones ───────────────────

    def _def_funcion(self) -> NodoArbol:
        """def_funcion → funcion tipo_ret ID ( parametros ) hacer bloque fin_funcion"""
        nodo = self._crear_nodo("def_funcion")
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_FUNCION)))

        # tipo_ret: si el siguiente token es un tipo basico, consumirlo
        nodo_tipo_ret = self._crear_nodo("tipo_ret")
        if self._verificar(*TIPOS_BASICOS):
            nodo_tipo_ret.agregar_hijo(self._tipo_basico())
        else:
            nodo_tipo_ret.agregar_hijo(self._crear_epsilon())
        nodo.agregar_hijo(nodo_tipo_ret)

        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.IDENTIFICADOR, "definicion de funcion")))
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PAREN_IZQ, "definicion de funcion")))
        nodo.agregar_hijo(self._parametros())
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PAREN_DER, "definicion de funcion")))
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_HACER, "definicion de funcion")))
        nodo.agregar_hijo(self._bloque())
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_FIN_FUNCION, "definicion de funcion")))
        return nodo

    def _parametros(self) -> NodoArbol:
        """parametros → param_lista | ε"""
        nodo = self._crear_nodo("parametros")
        if self._verificar(*TIPOS_BASICOS, TokenType.IDENTIFICADOR):
            nodo.agregar_hijo(self._param_lista())
        else:
            nodo.agregar_hijo(self._crear_epsilon())
        return nodo

    def _param_lista(self) -> NodoArbol:
        """param_lista → tipo ID param_resto"""
        nodo = self._crear_nodo("param_lista")
        nodo.agregar_hijo(self._tipo())
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.IDENTIFICADOR, "parametro")))
        nodo.agregar_hijo(self._param_resto())
        return nodo

    def _param_resto(self) -> NodoArbol:
        """param_resto → , tipo ID param_resto | ε"""
        nodo = self._crear_nodo("param_resto")
        if self._verificar(TokenType.COMA):
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
            nodo.agregar_hijo(self._tipo())
            nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.IDENTIFICADOR, "parametro")))
            nodo.agregar_hijo(self._param_resto())
        else:
            nodo.agregar_hijo(self._crear_epsilon())
        return nodo

    # ── § 3.4  Clases ──────────────────────

    def _def_clase(self) -> NodoArbol:
        """def_clase → clase ID herencia_opt hacer cuerpo_clase fin_clase"""
        nodo = self._crear_nodo("def_clase")
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_CLASE)))
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.IDENTIFICADOR, "definicion de clase")))
        nodo.agregar_hijo(self._herencia_opt())
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_HACER, "definicion de clase")))
        nodo.agregar_hijo(self._cuerpo_clase())
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_FIN_CLASE, "definicion de clase")))
        return nodo

    def _herencia_opt(self) -> NodoArbol:
        """herencia_opt → hereda ID | ε"""
        nodo = self._crear_nodo("herencia_opt")
        if self._verificar(TokenType.PR_HEREDA):
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
            nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.IDENTIFICADOR, "herencia")))
        else:
            nodo.agregar_hijo(self._crear_epsilon())
        return nodo

    def _cuerpo_clase(self) -> NodoArbol:
        """cuerpo_clase → miembro_clase cuerpo_clase | ε"""
        nodo = self._crear_nodo("cuerpo_clase")
        while self._verificar(TokenType.PR_ATRIBUTO, TokenType.PR_METODO):
            nodo.agregar_hijo(self._miembro_clase())
        if not nodo.hijos:
            nodo.agregar_hijo(self._crear_epsilon())
        return nodo

    def _miembro_clase(self) -> NodoArbol:
        """miembro_clase → def_atributo | def_metodo"""
        nodo = self._crear_nodo("miembro_clase")
        if self._verificar(TokenType.PR_ATRIBUTO):
            nodo.agregar_hijo(self._def_atributo())
        elif self._verificar(TokenType.PR_METODO):
            nodo.agregar_hijo(self._def_metodo())
        return nodo

    def _def_atributo(self) -> NodoArbol:
        """def_atributo → atributo tipo ID"""
        nodo = self._crear_nodo("def_atributo")
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_ATRIBUTO)))
        nodo.agregar_hijo(self._tipo())
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.IDENTIFICADOR, "atributo")))
        return nodo

    def _def_metodo(self) -> NodoArbol:
        """def_metodo → metodo ID ( parametros ) hacer bloque fin_funcion"""
        nodo = self._crear_nodo("def_metodo")
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_METODO)))
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.IDENTIFICADOR, "metodo")))
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PAREN_IZQ, "metodo")))
        nodo.agregar_hijo(self._parametros())
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PAREN_DER, "metodo")))
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_HACER, "metodo")))
        nodo.agregar_hijo(self._bloque())
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_FIN_FUNCION, "metodo")))
        return nodo

    # ── § 3.5  Bloque y sentencias ─────────

    def _bloque(self) -> NodoArbol:
        """bloque → sentencia bloque'    donde bloque' → sentencia bloque' | ε"""
        nodo = self._crear_nodo("bloque")
        if self._verificar(*FIRST_SENTENCIA):
            nodo.agregar_hijo(self._sentencia())
        else:
            tok = self._actual()
            msg = (f"Error sintactico en fila {tok.fila}, col {tok.columna}: "
                   f"se esperaba una sentencia pero se encontro '{tok.lexema}'")
            self.errores.append(msg)
            raise ErrorSintactico(msg, tok.fila, tok.columna)
        # bloque' → sentencia bloque' | ε
        while self._verificar(*FIRST_SENTENCIA):
            nodo.agregar_hijo(self._sentencia())
        return nodo

    def _sentencia(self) -> NodoArbol:
        """sentencia → sent_id | sent_si | sent_para | sent_mientras
                     | sent_retornar | sent_imprimir | sent_romper
                     | sent_continuar | decl_variable"""
        nodo = self._crear_nodo("sentencia")
        tok = self._actual()

        if tok.tipo in (TokenType.PR_VAR, TokenType.PR_SEA):
            nodo.agregar_hijo(self._decl_variable())
        elif tok.tipo in (TokenType.IDENTIFICADOR, TokenType.PR_ESTE):
            nodo.agregar_hijo(self._sent_id())
        elif tok.tipo == TokenType.PR_SI:
            nodo.agregar_hijo(self._sent_si())
        elif tok.tipo == TokenType.PR_PARA:
            nodo.agregar_hijo(self._sent_para())
        elif tok.tipo == TokenType.PR_MIENTRAS:
            nodo.agregar_hijo(self._sent_mientras())
        elif tok.tipo == TokenType.PR_RETORNAR:
            nodo.agregar_hijo(self._sent_retornar())
        elif tok.tipo == TokenType.PR_IMPRIMIR:
            nodo.agregar_hijo(self._sent_imprimir())
        elif tok.tipo == TokenType.PR_ROMPER:
            nodo.agregar_hijo(self._sent_romper())
        elif tok.tipo == TokenType.PR_CONTINUAR:
            nodo.agregar_hijo(self._sent_continuar())
        else:
            msg = (f"Error sintactico en fila {tok.fila}, col {tok.columna}: "
                   f"sentencia inesperada: '{tok.lexema}'")
            self.errores.append(msg)
            raise ErrorSintactico(msg, tok.fila, tok.columna)
        return nodo

    # ── § 3.6  sent_id (fusionado: asignacion + llamada) ──

    def _sent_id(self) -> NodoArbol:
        """
        sent_id → (ID | este) resto_id
        resto_id → = expresion
                  | . ID resto_id
                  | ( argumentos )
                  | ε
        """
        nodo = self._crear_nodo("sent_id")
        # Aceptar ID o este (para este.campo = valor)
        tok = self._actual()
        if tok.tipo in (TokenType.IDENTIFICADOR, TokenType.PR_ESTE):
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
        else:
            nodo.agregar_hijo(self._crear_hoja(
                self._esperar(TokenType.IDENTIFICADOR)))
        self._resto_id(nodo)
        return nodo

    def _consumir_miembro(self) -> Token:
        """Consume un identificador o palabra reservada usada como nombre de miembro."""
        tok = self._actual()
        if tok.tipo == TokenType.IDENTIFICADOR or tok.tipo.name.startswith("PR_"):
            return self._avanzar()
        return self._esperar(TokenType.IDENTIFICADOR, "acceso a miembro")

    def _resto_id(self, nodo: NodoArbol):
        """Parsea el sufijo despues de un ID en una sentencia."""
        if self._verificar(TokenType.OP_ASIGNACION):
            # Asignacion: ID = expresion
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
            nodo.agregar_hijo(self._expresion())
        elif self._verificar(TokenType.PUNTO):
            # Acceso miembro: ID . miembro resto_id
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
            nodo.agregar_hijo(self._crear_hoja(self._consumir_miembro()))
            self._resto_id(nodo)
        elif self._verificar(TokenType.PAREN_IZQ):
            # Llamada: ID ( argumentos )
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
            nodo.agregar_hijo(self._argumentos())
            nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PAREN_DER, "llamada a funcion")))
        # else: ε (sentencia de solo ID, permitido)

    # ── § 3.7  Condicional ─────────────────

    def _sent_si(self) -> NodoArbol:
        """sent_si → si expresion entonces bloque rama_sino fin_si"""
        nodo = self._crear_nodo("sent_si")
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_SI)))
        nodo.agregar_hijo(self._expresion())
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_ENTONCES, "condicional si")))
        nodo.agregar_hijo(self._bloque())
        nodo.agregar_hijo(self._rama_sino())
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_FIN_SI, "condicional si")))
        return nodo

    def _rama_sino(self) -> NodoArbol:
        """rama_sino → sino bloque | ε"""
        nodo = self._crear_nodo("rama_sino")
        if self._verificar(TokenType.PR_SINO):
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
            nodo.agregar_hijo(self._bloque())
        else:
            nodo.agregar_hijo(self._crear_epsilon())
        return nodo

    # ── § 3.8  Ciclos ──────────────────────

    def _sent_para(self) -> NodoArbol:
        """sent_para → para ID desde expresion hasta expresion paso_opt hacer bloque fin_para"""
        nodo = self._crear_nodo("sent_para")
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_PARA)))
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.IDENTIFICADOR, "ciclo para")))
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_DESDE, "ciclo para")))
        nodo.agregar_hijo(self._expresion())
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_HASTA, "ciclo para")))
        nodo.agregar_hijo(self._expresion())
        nodo.agregar_hijo(self._paso_opt())
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_HACER, "ciclo para")))
        nodo.agregar_hijo(self._bloque())
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_FIN_PARA, "ciclo para")))
        return nodo

    def _paso_opt(self) -> NodoArbol:
        """paso_opt → paso expresion | ε"""
        nodo = self._crear_nodo("paso_opt")
        if self._verificar(TokenType.PR_PASO):
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
            nodo.agregar_hijo(self._expresion())
        else:
            nodo.agregar_hijo(self._crear_epsilon())
        return nodo

    def _sent_mientras(self) -> NodoArbol:
        """sent_mientras → mientras expresion hacer bloque fin_mientras"""
        nodo = self._crear_nodo("sent_mientras")
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_MIENTRAS)))
        nodo.agregar_hijo(self._expresion())
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_HACER, "ciclo mientras")))
        nodo.agregar_hijo(self._bloque())
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_FIN_MIENTRAS, "ciclo mientras")))
        return nodo

    # ── § 3.9  Sentencias simples ──────────

    def _sent_retornar(self) -> NodoArbol:
        """sent_retornar → retornar expresion"""
        nodo = self._crear_nodo("sent_retornar")
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_RETORNAR)))
        nodo.agregar_hijo(self._expresion())
        return nodo

    def _sent_imprimir(self) -> NodoArbol:
        """sent_imprimir → imprimir ( expresion )"""
        nodo = self._crear_nodo("sent_imprimir")
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_IMPRIMIR)))
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PAREN_IZQ, "imprimir")))
        nodo.agregar_hijo(self._expresion())
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PAREN_DER, "imprimir")))
        return nodo

    def _sent_romper(self) -> NodoArbol:
        """sent_romper → romper"""
        nodo = self._crear_nodo("sent_romper")
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_ROMPER)))
        return nodo

    def _sent_continuar(self) -> NodoArbol:
        """sent_continuar → continuar"""
        nodo = self._crear_nodo("sent_continuar")
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_CONTINUAR)))
        return nodo

    # ── § 3.10  Argumentos ─────────────────

    def _argumentos(self) -> NodoArbol:
        """argumentos → arg_lista | ε"""
        nodo = self._crear_nodo("argumentos")
        if self._verificar(*FIRST_EXPRESION):
            nodo.agregar_hijo(self._arg_lista())
        else:
            nodo.agregar_hijo(self._crear_epsilon())
        return nodo

    def _arg_lista(self) -> NodoArbol:
        """arg_lista → expresion arg_resto"""
        nodo = self._crear_nodo("arg_lista")
        nodo.agregar_hijo(self._expresion())
        nodo.agregar_hijo(self._arg_resto())
        return nodo

    def _arg_resto(self) -> NodoArbol:
        """arg_resto → , expresion arg_resto | ε"""
        nodo = self._crear_nodo("arg_resto")
        if self._verificar(TokenType.COMA):
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
            nodo.agregar_hijo(self._expresion())
            nodo.agregar_hijo(self._arg_resto())
        else:
            nodo.agregar_hijo(self._crear_epsilon())
        return nodo

    # ── § 3.11  Expresiones ────────────────

    def _expresion(self) -> NodoArbol:
        """expresion → expr_or"""
        nodo = self._crear_nodo("expresion")
        nodo.agregar_hijo(self._expr_or())
        return nodo

    def _expr_or(self) -> NodoArbol:
        """expr_or → expr_and expr_or'"""
        nodo = self._crear_nodo("expr_or")
        nodo.agregar_hijo(self._expr_and())
        nodo.agregar_hijo(self._expr_or_prima())
        return nodo

    def _expr_or_prima(self) -> NodoArbol:
        """expr_or' → o expr_and expr_or' | ε"""
        nodo = self._crear_nodo("expr_or'")
        if self._verificar(TokenType.PR_O):
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
            nodo.agregar_hijo(self._expr_and())
            nodo.agregar_hijo(self._expr_or_prima())
        else:
            nodo.agregar_hijo(self._crear_epsilon())
        return nodo

    def _expr_and(self) -> NodoArbol:
        """expr_and → expr_rel expr_and'"""
        nodo = self._crear_nodo("expr_and")
        nodo.agregar_hijo(self._expr_rel())
        nodo.agregar_hijo(self._expr_and_prima())
        return nodo

    def _expr_and_prima(self) -> NodoArbol:
        """expr_and' → y expr_rel expr_and' | ε"""
        nodo = self._crear_nodo("expr_and'")
        if self._verificar(TokenType.PR_Y):
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
            nodo.agregar_hijo(self._expr_rel())
            nodo.agregar_hijo(self._expr_and_prima())
        else:
            nodo.agregar_hijo(self._crear_epsilon())
        return nodo

    def _expr_rel(self) -> NodoArbol:
        """expr_rel → expr_add expr_rel'"""
        nodo = self._crear_nodo("expr_rel")
        nodo.agregar_hijo(self._expr_add())
        nodo.agregar_hijo(self._expr_rel_prima())
        return nodo

    def _expr_rel_prima(self) -> NodoArbol:
        """expr_rel' → op_rel expr_add | ε"""
        nodo = self._crear_nodo("expr_rel'")
        ops_rel = {TokenType.OP_IGUAL, TokenType.OP_DISTINTO,
                   TokenType.OP_MENOR, TokenType.OP_MAYOR,
                   TokenType.OP_MENOR_IGUAL, TokenType.OP_MAYOR_IGUAL}
        if self._verificar(*ops_rel):
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
            nodo.agregar_hijo(self._expr_add())
        else:
            nodo.agregar_hijo(self._crear_epsilon())
        return nodo

    def _expr_add(self) -> NodoArbol:
        """expr_add → expr_mul expr_add'"""
        nodo = self._crear_nodo("expr_add")
        nodo.agregar_hijo(self._expr_mul())
        nodo.agregar_hijo(self._expr_add_prima())
        return nodo

    def _expr_add_prima(self) -> NodoArbol:
        """expr_add' → + expr_mul expr_add' | - expr_mul expr_add' | ε"""
        nodo = self._crear_nodo("expr_add'")
        if self._verificar(TokenType.OP_SUMA, TokenType.OP_RESTA):
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
            nodo.agregar_hijo(self._expr_mul())
            nodo.agregar_hijo(self._expr_add_prima())
        else:
            nodo.agregar_hijo(self._crear_epsilon())
        return nodo

    def _expr_mul(self) -> NodoArbol:
        """expr_mul → expr_pot expr_mul'"""
        nodo = self._crear_nodo("expr_mul")
        nodo.agregar_hijo(self._expr_pot())
        nodo.agregar_hijo(self._expr_mul_prima())
        return nodo

    def _expr_mul_prima(self) -> NodoArbol:
        """expr_mul' → * expr_pot expr_mul' | / expr_pot expr_mul' | % expr_pot expr_mul' | ε"""
        nodo = self._crear_nodo("expr_mul'")
        if self._verificar(TokenType.OP_MULT, TokenType.OP_DIV, TokenType.OP_MOD):
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
            nodo.agregar_hijo(self._expr_pot())
            nodo.agregar_hijo(self._expr_mul_prima())
        else:
            nodo.agregar_hijo(self._crear_epsilon())
        return nodo

    def _expr_pot(self) -> NodoArbol:
        """expr_pot → expr_unaria expr_pot'"""
        nodo = self._crear_nodo("expr_pot")
        nodo.agregar_hijo(self._expr_unaria())
        nodo.agregar_hijo(self._expr_pot_prima())
        return nodo

    def _expr_pot_prima(self) -> NodoArbol:
        """expr_pot' → ** expr_unaria expr_pot' | ε"""
        nodo = self._crear_nodo("expr_pot'")
        if self._verificar(TokenType.OP_POT):
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
            nodo.agregar_hijo(self._expr_unaria())
            nodo.agregar_hijo(self._expr_pot_prima())
        else:
            nodo.agregar_hijo(self._crear_epsilon())
        return nodo

    def _expr_unaria(self) -> NodoArbol:
        """expr_unaria → no expr_unaria | - expr_unaria | expr_primaria"""
        nodo = self._crear_nodo("expr_unaria")
        if self._verificar(TokenType.PR_NO):
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
            nodo.agregar_hijo(self._expr_unaria())
        elif self._verificar(TokenType.OP_RESTA):
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
            nodo.agregar_hijo(self._expr_unaria())
        else:
            nodo.agregar_hijo(self._expr_primaria())
        return nodo

    def _expr_primaria(self) -> NodoArbol:
        """
        expr_primaria → NUM_ENTERO | NUM_REAL | CADENA
                       | verdadero | falso | nulo
                       | nuevo ID ( argumentos )
                       | este sufijo_id
                       | ID sufijo_id
                       | ( expresion )
        """
        nodo = self._crear_nodo("expr_primaria")
        tok = self._actual()

        if tok.tipo in (TokenType.LIT_ENTERO, TokenType.LIT_REAL, TokenType.LIT_CADENA):
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
        elif tok.tipo in (TokenType.PR_VERDADERO, TokenType.PR_FALSO, TokenType.PR_NULO):
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
        elif tok.tipo == TokenType.PR_NUEVO:
            nodo.agregar_hijo(self._instanciacion())
        elif tok.tipo == TokenType.PR_ESTE:
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
            nodo.agregar_hijo(self._sufijo_id())
        elif tok.tipo == TokenType.IDENTIFICADOR:
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
            nodo.agregar_hijo(self._sufijo_id())
        elif tok.tipo == TokenType.PAREN_IZQ:
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
            nodo.agregar_hijo(self._expresion())
            nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PAREN_DER, "expresion entre parentesis")))
        else:
            msg = (f"Error sintactico en fila {tok.fila}, col {tok.columna}: "
                   f"expresion inesperada: '{tok.lexema}'")
            self.errores.append(msg)
            raise ErrorSintactico(msg, tok.fila, tok.columna)
        return nodo

    def _instanciacion(self) -> NodoArbol:
        """instanciacion → nuevo ID ( argumentos )"""
        nodo = self._crear_nodo("instanciacion")
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PR_NUEVO)))
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.IDENTIFICADOR, "instanciacion")))
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PAREN_IZQ, "instanciacion")))
        nodo.agregar_hijo(self._argumentos())
        nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PAREN_DER, "instanciacion")))
        return nodo

    def _sufijo_id(self) -> NodoArbol:
        """sufijo_id → ( argumentos ) | . ID sufijo_id | ε"""
        nodo = self._crear_nodo("sufijo_id")
        if self._verificar(TokenType.PAREN_IZQ):
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
            nodo.agregar_hijo(self._argumentos())
            nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.PAREN_DER, "llamada")))
        elif self._verificar(TokenType.PUNTO):
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
            nodo.agregar_hijo(self._crear_hoja(self._esperar(TokenType.IDENTIFICADOR, "acceso miembro")))
            nodo.agregar_hijo(self._sufijo_id())
        else:
            nodo.agregar_hijo(self._crear_epsilon())
        return nodo

    # ── § 3.12  Tipos ──────────────────────

    def _tipo(self) -> NodoArbol:
        """tipo → entero | real | cadena | booleano | ID"""
        nodo = self._crear_nodo("tipo")
        if self._verificar(*TIPOS_BASICOS):
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
        elif self._verificar(TokenType.IDENTIFICADOR):
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
        else:
            tok = self._actual()
            msg = (f"Error sintactico en fila {tok.fila}, col {tok.columna}: "
                   f"se esperaba un tipo pero se encontro '{tok.lexema}'")
            self.errores.append(msg)
            raise ErrorSintactico(msg, tok.fila, tok.columna)
        return nodo

    def _tipo_basico(self) -> NodoArbol:
        """tipo_basico → entero | real | cadena | booleano"""
        nodo = self._crear_nodo("tipo_basico")
        if self._verificar(*TIPOS_BASICOS):
            nodo.agregar_hijo(self._crear_hoja(self._avanzar()))
        else:
            tok = self._actual()
            msg = (f"Error sintactico en fila {tok.fila}, col {tok.columna}: "
                   f"se esperaba un tipo basico pero se encontro '{tok.lexema}'")
            self.errores.append(msg)
            raise ErrorSintactico(msg, tok.fila, tok.columna)
        return nodo
