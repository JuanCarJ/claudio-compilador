"""
╔══════════════════════════════════════════════════════════════╗
║  CLAUDIO — Analizador Léxico (Lexer)                        ║
║  Lenguaje fuente con palabras clave en español              ║
║  Lenguaje destino: Swift                                    ║
║  Curso: Teoría de Compiladores                              ║
║                                                             ║
║  Autores: Juan David Cárdenas Jiménez                       ║
║           María José Restrepo Ramírez                       ║
║           José Zuluaga                                      ║
╚══════════════════════════════════════════════════════════════╝

Módulo independiente y reutilizable que implementa el análisis
léxico del lenguaje Claudio. Produce una lista de tokens con
información de lexema, tipo, fila y columna.

Uso básico:
    from lexer import Lexer
    lexer = Lexer(codigo_fuente)
    tokens = lexer.analizar()
    errores = lexer.obtener_errores()

Para futuras entregas, el analizador sintáctico consumirá
directamente los tokens producidos por este módulo.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


# ─────────────────────────────────────────────
# § 1  CATEGORÍAS DE TOKENS (TokenType)
# ─────────────────────────────────────────────

class TokenType(Enum):
    """
    Enumeración de todas las categorías léxicas del lenguaje
    Claudio. Cada valor representa una categoría distinta
    reconocida por el lexer. Las 35 palabras reservadas usan
    el prefijo PR_.
    """

    # ── Palabras reservadas (35) ─────────────
    PR_SI            = auto()   # si
    PR_ENTONCES      = auto()   # entonces
    PR_SINO          = auto()   # sino
    PR_FIN_SI        = auto()   # fin_si
    PR_PARA          = auto()   # para
    PR_DESDE         = auto()   # desde
    PR_HASTA         = auto()   # hasta
    PR_PASO          = auto()   # paso
    PR_HACER         = auto()   # hacer
    PR_FIN_PARA      = auto()   # fin_para
    PR_MIENTRAS      = auto()   # mientras
    PR_FIN_MIENTRAS  = auto()   # fin_mientras
    PR_FUNCION       = auto()   # funcion
    PR_FIN_FUNCION   = auto()   # fin_funcion
    PR_RETORNAR      = auto()   # retornar
    PR_CLASE         = auto()   # clase
    PR_FIN_CLASE     = auto()   # fin_clase
    PR_NUEVO         = auto()   # nuevo
    PR_ESTE          = auto()   # este
    PR_VAR           = auto()   # var
    PR_SEA           = auto()   # sea
    PR_ENTERO        = auto()   # entero
    PR_REAL          = auto()   # real
    PR_CADENA        = auto()   # cadena
    PR_BOOLEANO      = auto()   # booleano
    PR_VERDADERO     = auto()   # verdadero
    PR_FALSO         = auto()   # falso
    PR_NULO          = auto()   # nulo
    PR_IMPRIMIR      = auto()   # imprimir
    PR_Y             = auto()   # y
    PR_O             = auto()   # o
    PR_NO            = auto()   # no
    PR_IMPORTAR      = auto()   # importar
    PR_HEREDA        = auto()   # hereda
    PR_METODO        = auto()   # metodo
    PR_ATRIBUTO      = auto()   # atributo
    PR_ROMPER        = auto()   # romper
    PR_CONTINUAR     = auto()   # continuar

    # ── Literales ────────────────────────────
    LIT_ENTERO       = auto()   # 42, 0, 1234
    LIT_REAL         = auto()   # 3.14, 0.5
    LIT_CADENA       = auto()   # "hola mundo"

    # ── Identificadores ──────────────────────
    IDENTIFICADOR    = auto()   # nombre, mi_variable, año

    # ── Operadores aritméticos ───────────────
    OP_SUMA          = auto()   # +
    OP_RESTA         = auto()   # -
    OP_MULT          = auto()   # *
    OP_DIV           = auto()   # /
    OP_MOD           = auto()   # %
    OP_POT           = auto()   # **

    # ── Operadores relacionales ──────────────
    OP_IGUAL         = auto()   # ==
    OP_DISTINTO      = auto()   # !=
    OP_MENOR         = auto()   # <
    OP_MAYOR         = auto()   # >
    OP_MENOR_IGUAL   = auto()   # <=
    OP_MAYOR_IGUAL   = auto()   # >=

    # ── Operador de asignación ───────────────
    OP_ASIGNACION    = auto()   # =

    # ── Delimitadores ────────────────────────
    PAREN_IZQ        = auto()   # (
    PAREN_DER        = auto()   # )
    COMA             = auto()   # ,
    DOS_PUNTOS       = auto()   # :
    PUNTO            = auto()   # .
    PUNTO_Y_COMA     = auto()   # ;
    CORCHETE_IZQ     = auto()   # [
    CORCHETE_DER     = auto()   # ]

    # ── Comentarios ──────────────────────────
    COMENTARIO_LINEA  = auto()  # // ...
    COMENTARIO_BLOQUE = auto()  # /* ... */

    # ── Especiales ───────────────────────────
    FIN_DE_ARCHIVO   = auto()   # EOF
    ERROR_LEXICO     = auto()   # Token inválido


# ─────────────────────────────────────────────
# § 2  ESTRUCTURA DEL TOKEN
# ─────────────────────────────────────────────

@dataclass
class Token:
    """
    Representa un token reconocido por el analizador léxico.

    Atributos:
        lexema   -- Texto exacto extraído del código fuente.
        tipo     -- Categoría léxica (valor de TokenType).
        fila     -- Línea donde inicia el token (1-indexed).
        columna  -- Columna donde inicia el token (1-indexed).
    """
    lexema: str
    tipo: TokenType
    fila: int
    columna: int

    def __repr__(self):
        return (f"Token({self.tipo.name}, '{self.lexema}', "
                f"fila={self.fila}, col={self.columna})")


# ─────────────────────────────────────────────
# § 3  TABLA DE PALABRAS RESERVADAS
# ─────────────────────────────────────────────

PALABRAS_RESERVADAS = {
    "si":            TokenType.PR_SI,
    "entonces":      TokenType.PR_ENTONCES,
    "sino":          TokenType.PR_SINO,
    "fin_si":        TokenType.PR_FIN_SI,
    "para":          TokenType.PR_PARA,
    "desde":         TokenType.PR_DESDE,
    "hasta":         TokenType.PR_HASTA,
    "paso":          TokenType.PR_PASO,
    "hacer":         TokenType.PR_HACER,
    "fin_para":      TokenType.PR_FIN_PARA,
    "mientras":      TokenType.PR_MIENTRAS,
    "fin_mientras":  TokenType.PR_FIN_MIENTRAS,
    "funcion":       TokenType.PR_FUNCION,
    "fin_funcion":   TokenType.PR_FIN_FUNCION,
    "retornar":      TokenType.PR_RETORNAR,
    "clase":         TokenType.PR_CLASE,
    "fin_clase":     TokenType.PR_FIN_CLASE,
    "nuevo":         TokenType.PR_NUEVO,
    "este":          TokenType.PR_ESTE,
    "var":           TokenType.PR_VAR,
    "sea":           TokenType.PR_SEA,
    "entero":        TokenType.PR_ENTERO,
    "real":          TokenType.PR_REAL,
    "cadena":        TokenType.PR_CADENA,
    "booleano":      TokenType.PR_BOOLEANO,
    "verdadero":     TokenType.PR_VERDADERO,
    "falso":         TokenType.PR_FALSO,
    "nulo":          TokenType.PR_NULO,
    "imprimir":      TokenType.PR_IMPRIMIR,
    "y":             TokenType.PR_Y,
    "o":             TokenType.PR_O,
    "no":            TokenType.PR_NO,
    "importar":      TokenType.PR_IMPORTAR,
    "hereda":        TokenType.PR_HEREDA,
    "metodo":        TokenType.PR_METODO,
    "atributo":      TokenType.PR_ATRIBUTO,
    "romper":        TokenType.PR_ROMPER,
    "continuar":     TokenType.PR_CONTINUAR,
}


# ─────────────────────────────────────────────
# § 4  CLASE LEXER — ANALIZADOR LÉXICO
# ─────────────────────────────────────────────

class Lexer:
    """
    Analizador léxico para el lenguaje Claudio.

    Recorre carácter a carácter la cadena de entrada y produce
    una lista de objetos Token. Cuando encuentra un carácter que
    no corresponde a ningún token válido, emite ERROR_LEXICO con
    la posición exacta y continúa sin abortar.

    Uso:
        lexer = Lexer(codigo_fuente)
        tokens = lexer.analizar()
        errores = lexer.obtener_errores()
        tabla = lexer.tabla_simbolos()
    """

    def __init__(self, fuente: str):
        self.fuente = fuente
        self.pos = 0
        self.fila = 1
        self.columna = 1
        self.tokens: List[Token] = []
        self.errores: List[Token] = []

    # ── Utilidades de lectura ────────────────

    def _caracter_actual(self) -> Optional[str]:
        """Devuelve el carácter en la posición actual, o None si EOF."""
        if self.pos < len(self.fuente):
            return self.fuente[self.pos]
        return None

    def _siguiente_caracter(self) -> Optional[str]:
        """Devuelve el siguiente carácter (peek ahead), o None."""
        if self.pos + 1 < len(self.fuente):
            return self.fuente[self.pos + 1]
        return None

    def _avanzar(self) -> str:
        """Consume el carácter actual y actualiza fila/columna."""
        c = self.fuente[self.pos]
        self.pos += 1
        if c == '\n':
            self.fila += 1
            self.columna = 1
        else:
            self.columna += 1
        return c

    def _es_letra_o_guion_bajo(self, c: str) -> bool:
        """Letra (incluyendo tildes, ñ) o guion bajo."""
        return (c.isalpha() or c == '_' or c == 'ñ' or c == 'Ñ'
                or c in 'áéíóúÁÉÍÓÚüÜ')

    def _es_alfanumerico(self, c: str) -> bool:
        """Letra, dígito o guion bajo."""
        return self._es_letra_o_guion_bajo(c) or c.isdigit()

    # ── Método principal ─────────────────────

    def analizar(self) -> List[Token]:
        """
        Ejecuta el análisis léxico completo de la cadena fuente.

        Retorna la lista de tokens, incluyendo ERROR_LEXICO para
        caracteres no reconocidos y FIN_DE_ARCHIVO al final.
        """
        self.tokens = []
        self.errores = []
        self.pos = 0
        self.fila = 1
        self.columna = 1

        while self.pos < len(self.fuente):
            c = self._caracter_actual()

            # Espacios en blanco → ignorar
            if c in ' \t\r\n':
                self._avanzar()
                continue

            # Comentario de línea
            if c == '/' and self._siguiente_caracter() == '/':
                self._leer_comentario_linea()
                continue

            # Comentario de bloque
            if c == '/' and self._siguiente_caracter() == '*':
                self._leer_comentario_bloque()
                continue

            # Cadena de texto
            if c == '"':
                self._leer_cadena()
                continue

            # Número (entero o real)
            if c.isdigit():
                self._leer_numero()
                continue

            # Identificador o palabra reservada
            if self._es_letra_o_guion_bajo(c):
                self._leer_identificador()
                continue

            # Operadores de dos caracteres
            if c == '*' and self._siguiente_caracter() == '*':
                f, col = self.fila, self.columna
                self._avanzar(); self._avanzar()
                self._agregar_token('**', TokenType.OP_POT, f, col)
                continue

            if c == '=' and self._siguiente_caracter() == '=':
                f, col = self.fila, self.columna
                self._avanzar(); self._avanzar()
                self._agregar_token('==', TokenType.OP_IGUAL, f, col)
                continue

            if c == '!' and self._siguiente_caracter() == '=':
                f, col = self.fila, self.columna
                self._avanzar(); self._avanzar()
                self._agregar_token('!=', TokenType.OP_DISTINTO, f, col)
                continue

            if c == '<' and self._siguiente_caracter() == '=':
                f, col = self.fila, self.columna
                self._avanzar(); self._avanzar()
                self._agregar_token('<=', TokenType.OP_MENOR_IGUAL, f, col)
                continue

            if c == '>' and self._siguiente_caracter() == '=':
                f, col = self.fila, self.columna
                self._avanzar(); self._avanzar()
                self._agregar_token('>=', TokenType.OP_MAYOR_IGUAL, f, col)
                continue

            # Operadores de un carácter
            operadores_simples = {
                '+': TokenType.OP_SUMA,
                '-': TokenType.OP_RESTA,
                '*': TokenType.OP_MULT,
                '/': TokenType.OP_DIV,
                '%': TokenType.OP_MOD,
                '=': TokenType.OP_ASIGNACION,
                '<': TokenType.OP_MENOR,
                '>': TokenType.OP_MAYOR,
            }
            if c in operadores_simples:
                f, col = self.fila, self.columna
                self._avanzar()
                self._agregar_token(c, operadores_simples[c], f, col)
                continue

            # Delimitadores
            delimitadores = {
                '(': TokenType.PAREN_IZQ,
                ')': TokenType.PAREN_DER,
                ',': TokenType.COMA,
                ':': TokenType.DOS_PUNTOS,
                '.': TokenType.PUNTO,
                ';': TokenType.PUNTO_Y_COMA,
                '[': TokenType.CORCHETE_IZQ,
                ']': TokenType.CORCHETE_DER,
            }
            if c in delimitadores:
                f, col = self.fila, self.columna
                self._avanzar()
                self._agregar_token(c, delimitadores[c], f, col)
                continue

            # ── Error léxico (no aborta el análisis) ──
            f, col = self.fila, self.columna
            self._avanzar()
            tok_error = Token(c, TokenType.ERROR_LEXICO, f, col)
            self.tokens.append(tok_error)
            self.errores.append(tok_error)

        # Token de fin de archivo
        self.tokens.append(Token('EOF', TokenType.FIN_DE_ARCHIVO,
                                 self.fila, self.columna))
        return self.tokens

    # ── Lectores especializados ──────────────

    def _agregar_token(self, lexema, tipo, fila, columna):
        """Crea un Token y lo agrega a la lista."""
        self.tokens.append(Token(lexema, tipo, fila, columna))

    def _leer_identificador(self):
        """
        Lee un identificador o palabra reservada.
        Soporta guion bajo en medio (fin_si, fin_para, etc.).
        """
        f, col = self.fila, self.columna
        inicio = self.pos
        while (self.pos < len(self.fuente)
               and self._es_alfanumerico(self.fuente[self.pos])):
            self._avanzar()
        lexema = self.fuente[inicio:self.pos]
        tipo = PALABRAS_RESERVADAS.get(lexema, TokenType.IDENTIFICADOR)
        self._agregar_token(lexema, tipo, f, col)

    def _leer_numero(self):
        """Lee un literal entero o real (con parte decimal)."""
        f, col = self.fila, self.columna
        inicio = self.pos
        es_real = False
        while self.pos < len(self.fuente) and self.fuente[self.pos].isdigit():
            self._avanzar()
        if (self.pos < len(self.fuente) and self.fuente[self.pos] == '.'
                and self.pos + 1 < len(self.fuente)
                and self.fuente[self.pos + 1].isdigit()):
            es_real = True
            self._avanzar()
            while (self.pos < len(self.fuente)
                   and self.fuente[self.pos].isdigit()):
                self._avanzar()
        lexema = self.fuente[inicio:self.pos]
        tipo = TokenType.LIT_REAL if es_real else TokenType.LIT_ENTERO
        self._agregar_token(lexema, tipo, f, col)

    def _leer_cadena(self):
        """Lee un literal de cadena entre comillas dobles."""
        f, col = self.fila, self.columna
        self._avanzar()  # comilla apertura
        inicio = self.pos
        contenido = '"'
        while self.pos < len(self.fuente):
            c = self.fuente[self.pos]
            if c == '"':
                contenido += self.fuente[inicio:self.pos] + '"'
                self._avanzar()
                self._agregar_token(contenido, TokenType.LIT_CADENA, f, col)
                return
            if c == '\\':
                self._avanzar()
                if self.pos < len(self.fuente):
                    self._avanzar()
                continue
            if c == '\n':
                break
            self._avanzar()
        contenido = '"' + self.fuente[inicio:self.pos]
        tok = Token(contenido, TokenType.ERROR_LEXICO, f, col)
        self.tokens.append(tok)
        self.errores.append(tok)

    def _leer_comentario_linea(self):
        """Lee comentario de línea (// hasta fin de línea)."""
        f, col = self.fila, self.columna
        inicio = self.pos
        while self.pos < len(self.fuente) and self.fuente[self.pos] != '\n':
            self._avanzar()
        self._agregar_token(self.fuente[inicio:self.pos],
                            TokenType.COMENTARIO_LINEA, f, col)

    def _leer_comentario_bloque(self):
        """Lee comentario de bloque (/* ... */). Error si no cierra."""
        f, col = self.fila, self.columna
        inicio = self.pos
        self._avanzar(); self._avanzar()  # consumir /*
        while self.pos < len(self.fuente):
            if (self.fuente[self.pos] == '*'
                    and self.pos + 1 < len(self.fuente)
                    and self.fuente[self.pos + 1] == '/'):
                self._avanzar(); self._avanzar()
                self._agregar_token(self.fuente[inicio:self.pos],
                                    TokenType.COMENTARIO_BLOQUE, f, col)
                return
            self._avanzar()
        lexema = self.fuente[inicio:self.pos]
        tok = Token(lexema, TokenType.ERROR_LEXICO, f, col)
        self.tokens.append(tok)
        self.errores.append(tok)

    # ── Utilidades de consulta ───────────────

    def obtener_errores(self) -> List[Token]:
        """Retorna la lista de tokens de tipo ERROR_LEXICO."""
        return self.errores

    def tabla_simbolos(self) -> List[dict]:
        """
        Genera la tabla de símbolos léxicos como lista de dicts.
        Incluye todos los tokens (excluyendo EOF y comentarios).
        Cada entrada: lexema, tipo, fila, columna.
        """
        tabla = []
        for t in self.tokens:
            if t.tipo in (TokenType.FIN_DE_ARCHIVO,
                          TokenType.COMENTARIO_LINEA,
                          TokenType.COMENTARIO_BLOQUE):
                continue
            tabla.append({
                'lexema': t.lexema,
                'tipo': t.tipo.name,
                'fila': t.fila,
                'columna': t.columna,
            })
        return tabla
