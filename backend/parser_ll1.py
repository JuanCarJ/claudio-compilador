"""
╔══════════════════════════════════════════════════════════════╗
║  CLAUDIO — Parser Predictivo Descendente LL(1) (Metodo 2)   ║
║  Motor FIRST/FOLLOW/Tabla + Algoritmo de pila               ║
║  Construye arbol de analisis sintactico (NodoArbol)         ║
╚══════════════════════════════════════════════════════════════╝

Calcula automaticamente los conjuntos PRIMERO y SIGUIENTE,
construye la tabla LL(1), y ejecuta el analisis con pila
explicita mostrando la traza paso a paso.
"""

from typing import List, Dict, Set, Tuple, Optional
from lexer import Token, TokenType
from arbol import NodoArbol


# ─────────────────────────────────────────────
# § 1  MAPEO TOKEN → TERMINAL
# ─────────────────────────────────────────────

TERMINAL_MAP: Dict[TokenType, str] = {
    TokenType.PR_SI:            "si",
    TokenType.PR_ENTONCES:      "entonces",
    TokenType.PR_SINO:          "sino",
    TokenType.PR_FIN_SI:        "fin_si",
    TokenType.PR_PARA:          "para",
    TokenType.PR_DESDE:         "desde",
    TokenType.PR_HASTA:         "hasta",
    TokenType.PR_PASO:          "paso",
    TokenType.PR_HACER:         "hacer",
    TokenType.PR_FIN_PARA:      "fin_para",
    TokenType.PR_MIENTRAS:      "mientras",
    TokenType.PR_FIN_MIENTRAS:  "fin_mientras",
    TokenType.PR_FUNCION:       "funcion",
    TokenType.PR_FIN_FUNCION:   "fin_funcion",
    TokenType.PR_RETORNAR:      "retornar",
    TokenType.PR_CLASE:         "clase",
    TokenType.PR_FIN_CLASE:     "fin_clase",
    TokenType.PR_NUEVO:         "nuevo",
    TokenType.PR_ESTE:          "este",
    TokenType.PR_VAR:           "var",
    TokenType.PR_SEA:           "sea",
    TokenType.PR_ENTERO:        "entero",
    TokenType.PR_REAL:          "real",
    TokenType.PR_CADENA:        "cadena",
    TokenType.PR_BOOLEANO:      "booleano",
    TokenType.PR_VERDADERO:     "verdadero",
    TokenType.PR_FALSO:         "falso",
    TokenType.PR_NULO:          "nulo",
    TokenType.PR_IMPRIMIR:      "imprimir",
    TokenType.PR_Y:             "y",
    TokenType.PR_O:             "o",
    TokenType.PR_NO:            "no",
    TokenType.PR_IMPORTAR:      "importar",
    TokenType.PR_HEREDA:        "hereda",
    TokenType.PR_METODO:        "metodo",
    TokenType.PR_ATRIBUTO:      "atributo",
    TokenType.PR_ROMPER:        "romper",
    TokenType.PR_CONTINUAR:     "continuar",
    TokenType.IDENTIFICADOR:    "ID",
    TokenType.LIT_ENTERO:       "NUM_ENTERO",
    TokenType.LIT_REAL:         "NUM_REAL",
    TokenType.LIT_CADENA:       "CADENA_LIT",
    TokenType.OP_SUMA:          "+",
    TokenType.OP_RESTA:         "-",
    TokenType.OP_MULT:          "*",
    TokenType.OP_DIV:           "/",
    TokenType.OP_MOD:           "%",
    TokenType.OP_POT:           "**",
    TokenType.OP_IGUAL:         "==",
    TokenType.OP_DISTINTO:      "!=",
    TokenType.OP_MENOR:         "<",
    TokenType.OP_MAYOR:         ">",
    TokenType.OP_MENOR_IGUAL:   "<=",
    TokenType.OP_MAYOR_IGUAL:   ">=",
    TokenType.OP_ASIGNACION:    "=",
    TokenType.PAREN_IZQ:        "(",
    TokenType.PAREN_DER:        ")",
    TokenType.COMA:             ",",
    TokenType.PUNTO:            ".",
    TokenType.FIN_DE_ARCHIVO:   "$",
}

def token_a_terminal(tok: Token) -> str:
    return TERMINAL_MAP.get(tok.tipo, tok.lexema)


# ─────────────────────────────────────────────
# § 2  GRAMATICA LL(1) DE CLAUDIO
# ─────────────────────────────────────────────
# Formato: { no_terminal: [ [simbolo1, simbolo2, ...], [alternativa2], ... ] }
# "ε" representa la cadena vacia

EPSILON = "ε"
SIMBOLO_INICIO = "programa"

GRAMATICA: Dict[str, List[List[str]]] = {
    # -- Programa y declaraciones --
    "programa":       [["declaracion", "programa"],
                       [EPSILON]],

    "declaracion":    [["def_funcion"],
                       ["def_clase"],
                       ["sentencia"],
                       ["importacion"]],

    "importacion":    [["importar", "ID"]],

    # -- Variables --
    "decl_variable":  [["var", "tipo", "ID", "=", "expresion"],
                       ["sea", "tipo", "ID", "=", "expresion"]],

    # -- Funciones --
    "def_funcion":    [["funcion", "tipo_ret", "ID", "(", "parametros", ")",
                        "hacer", "bloque", "fin_funcion"]],

    "tipo_ret":       [["tipo_basico"],
                       [EPSILON]],

    "tipo_basico":    [["entero"], ["real"], ["cadena"], ["booleano"]],

    "parametros":     [["param_lista"],
                       [EPSILON]],

    "param_lista":    [["tipo", "ID", "param_resto"]],

    "param_resto":    [[",", "tipo", "ID", "param_resto"],
                       [EPSILON]],

    # -- Clases --
    "def_clase":      [["clase", "ID", "herencia_opt", "hacer",
                        "cuerpo_clase", "fin_clase"]],

    "herencia_opt":   [["hereda", "ID"],
                       [EPSILON]],

    "cuerpo_clase":   [["miembro_clase", "cuerpo_clase"],
                       [EPSILON]],

    "miembro_clase":  [["def_atributo"],
                       ["def_metodo"]],

    "def_atributo":   [["atributo", "tipo", "ID"]],

    "def_metodo":     [["metodo", "ID", "(", "parametros", ")",
                        "hacer", "bloque", "fin_funcion"]],

    # -- Bloque y sentencias --
    "bloque":         [["sentencia", "bloque_rest"]],

    "bloque_rest":    [["sentencia", "bloque_rest"],
                       [EPSILON]],

    "sentencia":      [["sent_si"],
                       ["sent_para"],
                       ["sent_mientras"],
                       ["sent_retornar"],
                       ["sent_imprimir"],
                       ["sent_romper"],
                       ["sent_continuar"],
                       ["decl_variable"],
                       ["sent_id"]],

    # -- sent_id (fusionado: asignacion + llamada) --
    "sent_id":        [["ID", "resto_id"],
                       ["este", "resto_id"]],

    "resto_id":       [["=", "expresion"],
                       [".", "ID", "resto_id"],
                       ["(", "argumentos", ")"],
                       [EPSILON]],

    # -- Condicional --
    "sent_si":        [["si", "expresion", "entonces", "bloque",
                        "rama_sino", "fin_si"]],

    "rama_sino":      [["sino", "bloque"],
                       [EPSILON]],

    # -- Ciclos --
    "sent_para":      [["para", "ID", "desde", "expresion", "hasta",
                        "expresion", "paso_opt", "hacer", "bloque", "fin_para"]],

    "paso_opt":       [["paso", "expresion"],
                       [EPSILON]],

    "sent_mientras":  [["mientras", "expresion", "hacer", "bloque",
                        "fin_mientras"]],

    # -- Sentencias simples --
    "sent_retornar":  [["retornar", "expresion"]],
    "sent_imprimir":  [["imprimir", "(", "expresion", ")"]],
    "sent_romper":    [["romper"]],
    "sent_continuar": [["continuar"]],

    # -- Argumentos --
    "argumentos":     [["arg_lista"],
                       [EPSILON]],

    "arg_lista":      [["expresion", "arg_resto"]],

    "arg_resto":      [[",", "expresion", "arg_resto"],
                       [EPSILON]],

    # -- Expresiones --
    "expresion":      [["expr_or"]],

    "expr_or":        [["expr_and", "expr_or_p"]],
    "expr_or_p":      [["o", "expr_and", "expr_or_p"],
                       [EPSILON]],

    "expr_and":       [["expr_rel", "expr_and_p"]],
    "expr_and_p":     [["y", "expr_rel", "expr_and_p"],
                       [EPSILON]],

    "expr_rel":       [["expr_add", "expr_rel_p"]],
    "expr_rel_p":     [["op_rel", "expr_add"],
                       [EPSILON]],

    "op_rel":         [["=="], ["!="], ["<"], [">"], ["<="], [">="]],

    "expr_add":       [["expr_mul", "expr_add_p"]],
    "expr_add_p":     [["+", "expr_mul", "expr_add_p"],
                       ["-", "expr_mul", "expr_add_p"],
                       [EPSILON]],

    "expr_mul":       [["expr_pot", "expr_mul_p"]],
    "expr_mul_p":     [["*", "expr_pot", "expr_mul_p"],
                       ["/", "expr_pot", "expr_mul_p"],
                       ["%", "expr_pot", "expr_mul_p"],
                       [EPSILON]],

    "expr_pot":       [["expr_unaria", "expr_pot_p"]],
    "expr_pot_p":     [["**", "expr_unaria", "expr_pot_p"],
                       [EPSILON]],

    "expr_unaria":    [["no", "expr_unaria"],
                       ["-", "expr_unaria"],
                       ["expr_primaria"]],

    "expr_primaria":  [["NUM_ENTERO"],
                       ["NUM_REAL"],
                       ["CADENA_LIT"],
                       ["verdadero"],
                       ["falso"],
                       ["nulo"],
                       ["instanciacion"],
                       ["este", "sufijo_id"],
                       ["ID", "sufijo_id"],
                       ["(", "expresion", ")"]],

    "instanciacion":  [["nuevo", "ID", "(", "argumentos", ")"]],

    "sufijo_id":      [["(", "argumentos", ")"],
                       [".", "ID", "sufijo_id"],
                       [EPSILON]],

    # -- Tipos --
    "tipo":           [["entero"], ["real"], ["cadena"], ["booleano"], ["ID"]],
}


# ─────────────────────────────────────────────
# § 3  MOTOR LL(1)
# ─────────────────────────────────────────────

class MotorLL1:
    """Calcula FIRST, FOLLOW y tabla LL(1) para una gramatica dada."""

    def __init__(self, gramatica: Dict[str, List[List[str]]], inicio: str):
        self.gramatica = gramatica
        self.inicio = inicio
        self.no_terminales: Set[str] = set(gramatica.keys())
        self.terminales: Set[str] = set()
        for prods in gramatica.values():
            for prod in prods:
                for s in prod:
                    if s != EPSILON and s not in self.no_terminales:
                        self.terminales.add(s)
        self.terminales.add("$")

        self.primero: Dict[str, Set[str]] = {}
        self.siguiente: Dict[str, Set[str]] = {}
        self.tabla: Dict[str, Dict[str, Optional[List[str]]]] = {}
        self.conflictos: List[str] = []

        self._calcular_primero()
        self._calcular_siguiente()
        self._construir_tabla()

    def _calcular_primero(self):
        """Calcula conjuntos FIRST para todos los simbolos."""
        for t in self.terminales:
            self.primero[t] = {t}
        self.primero[EPSILON] = {EPSILON}

        for nt in self.no_terminales:
            self.primero[nt] = set()

        cambio = True
        while cambio:
            cambio = False
            for nt, prods in self.gramatica.items():
                for prod in prods:
                    primero_prod = self._primero_de_cadena(prod)
                    antes = len(self.primero[nt])
                    self.primero[nt] |= primero_prod
                    if len(self.primero[nt]) > antes:
                        cambio = True

    def _primero_de_cadena(self, cadena: List[str]) -> Set[str]:
        """FIRST de una cadena de simbolos."""
        resultado = set()
        for simbolo in cadena:
            primero_s = self.primero.get(simbolo, set())
            resultado |= (primero_s - {EPSILON})
            if EPSILON not in primero_s:
                return resultado
        resultado.add(EPSILON)
        return resultado

    def _calcular_siguiente(self):
        """Calcula conjuntos FOLLOW para todos los no-terminales."""
        for nt in self.no_terminales:
            self.siguiente[nt] = set()
        self.siguiente[self.inicio].add("$")

        cambio = True
        while cambio:
            cambio = False
            for nt, prods in self.gramatica.items():
                for prod in prods:
                    for i, simbolo in enumerate(prod):
                        if simbolo in self.no_terminales:
                            resto = prod[i + 1:]
                            if resto:
                                primero_resto = self._primero_de_cadena(resto)
                                antes = len(self.siguiente[simbolo])
                                self.siguiente[simbolo] |= (primero_resto - {EPSILON})
                                if EPSILON in primero_resto:
                                    self.siguiente[simbolo] |= self.siguiente[nt]
                                if len(self.siguiente[simbolo]) > antes:
                                    cambio = True
                            else:
                                antes = len(self.siguiente[simbolo])
                                self.siguiente[simbolo] |= self.siguiente[nt]
                                if len(self.siguiente[simbolo]) > antes:
                                    cambio = True

    def _construir_tabla(self):
        """Construye la tabla M[A, a] para analisis LL(1)."""
        self.conflictos = []
        for nt in self.no_terminales:
            self.tabla[nt] = {}

        for nt, prods in self.gramatica.items():
            for prod in prods:
                primero_prod = self._primero_de_cadena(prod)
                for terminal in primero_prod:
                    if terminal != EPSILON:
                        if terminal in self.tabla[nt] and self.tabla[nt][terminal] != prod:
                            self.conflictos.append(
                                f"Conflicto en M[{nt}, {terminal}]: "
                                f"{self.tabla[nt][terminal]} vs {prod}")
                        self.tabla[nt][terminal] = prod
                if EPSILON in primero_prod:
                    for terminal in self.siguiente.get(nt, set()):
                        if terminal in self.tabla[nt] and self.tabla[nt][terminal] != prod:
                            self.conflictos.append(
                                f"Conflicto en M[{nt}, {terminal}]: "
                                f"{self.tabla[nt][terminal]} vs {prod}")
                        self.tabla[nt][terminal] = prod

    def es_ll1(self) -> bool:
        return len(self.conflictos) == 0


# ─────────────────────────────────────────────
# § 4  PARSER PREDICTIVO LL(1)
# ─────────────────────────────────────────────

class ParserPredictivoLL1:
    """
    Analizador sintactico predictivo descendente con tabla LL(1).
    Usa una pila explicita y registra la traza paso a paso.
    """

    def __init__(self, tokens: List[Token]):
        # Filtrar comentarios y errores
        self.tokens_orig = [t for t in tokens
                            if t.tipo not in (TokenType.COMENTARIO_LINEA,
                                              TokenType.COMENTARIO_BLOQUE,
                                              TokenType.ERROR_LEXICO)]
        self.motor = MotorLL1(GRAMATICA, SIMBOLO_INICIO)

    def obtener_primero(self) -> Dict[str, Set[str]]:
        resultado = {}
        for nt in sorted(self.motor.no_terminales):
            resultado[nt] = self.motor.primero[nt]
        return resultado

    def obtener_siguiente(self) -> Dict[str, Set[str]]:
        resultado = {}
        for nt in sorted(self.motor.no_terminales):
            resultado[nt] = self.motor.siguiente[nt]
        return resultado

    def obtener_tabla(self) -> Dict[str, Dict[str, Optional[List[str]]]]:
        return self.motor.tabla

    def obtener_conflictos(self) -> List[str]:
        return self.motor.conflictos

    def obtener_terminales(self) -> Set[str]:
        return self.motor.terminales

    def obtener_no_terminales(self) -> Set[str]:
        return self.motor.no_terminales

    def es_ll1(self) -> bool:
        return self.motor.es_ll1()

    def analizar(self) -> Tuple[List[dict], Optional[NodoArbol], bool]:
        """
        Ejecuta el analisis con pila explicita.

        Retorna:
            pasos: lista de dicts con {paso, pila, entrada, accion}
            arbol: NodoArbol raiz (o None si falla)
            aceptado: bool
        """
        # Preparar entrada como lista de terminales
        entrada = [token_a_terminal(t) for t in self.tokens_orig]
        tokens_info = list(self.tokens_orig)

        # Pila: lista de (simbolo, nodo_arbol)
        raiz = NodoArbol(simbolo=SIMBOLO_INICIO)
        pila: List[Tuple[str, NodoArbol]] = [("$", None), (SIMBOLO_INICIO, raiz)]

        pasos = []
        idx = 0
        paso_num = 0
        max_pasos = 10000  # proteccion contra loops

        while pila and paso_num < max_pasos:
            paso_num += 1
            tope_simbolo, tope_nodo = pila[-1]
            actual = entrada[idx] if idx < len(entrada) else "$"
            actual_lexema = (tokens_info[idx].lexema
                            if idx < len(tokens_info) else "$")

            pila_str = " ".join(s for s, _ in reversed(pila) if s != "$")
            if not pila_str:
                pila_str = "$"
            entrada_str = " ".join(entrada[idx:min(idx+5, len(entrada))])
            if not entrada_str:
                entrada_str = "$"

            if tope_simbolo == "$" and actual == "$":
                pasos.append({
                    'paso': paso_num,
                    'pila': "$",
                    'entrada': "$",
                    'accion': "ACEPTAR"
                })
                return pasos, raiz, True

            if tope_simbolo == "$":
                pasos.append({
                    'paso': paso_num,
                    'pila': pila_str,
                    'entrada': entrada_str,
                    'accion': f"ERROR: pila vacia pero queda entrada '{actual_lexema}'"
                })
                return pasos, raiz, False

            # Terminal en tope de pila
            if tope_simbolo not in self.motor.no_terminales:
                if tope_simbolo == actual:
                    pasos.append({
                        'paso': paso_num,
                        'pila': pila_str,
                        'entrada': entrada_str,
                        'accion': f"Emparejar '{actual_lexema}'"
                    })
                    pila.pop()
                    if tope_nodo is not None:
                        tope_nodo.lexema = actual_lexema
                    idx += 1
                else:
                    pasos.append({
                        'paso': paso_num,
                        'pila': pila_str,
                        'entrada': entrada_str,
                        'accion': (f"ERROR: se esperaba '{tope_simbolo}' "
                                   f"pero se encontro '{actual_lexema}'")
                    })
                    return pasos, raiz, False
            else:
                # No-terminal: consultar tabla
                prod = self.motor.tabla.get(tope_simbolo, {}).get(actual)
                if prod is None:
                    esperados = list(self.motor.tabla.get(tope_simbolo, {}).keys())
                    pasos.append({
                        'paso': paso_num,
                        'pila': pila_str,
                        'entrada': entrada_str,
                        'accion': (f"ERROR: no hay produccion para "
                                   f"M[{tope_simbolo}, {actual_lexema}]. "
                                   f"Se esperaba: {', '.join(sorted(esperados)[:8])}")
                    })
                    return pasos, raiz, False

                # Registrar produccion
                prod_str = (f"{tope_simbolo} → {' '.join(prod)}"
                            if prod != [EPSILON]
                            else f"{tope_simbolo} → ε")
                pasos.append({
                    'paso': paso_num,
                    'pila': pila_str,
                    'entrada': entrada_str,
                    'accion': prod_str
                })

                pila.pop()

                if prod == [EPSILON]:
                    # Epsilon: agregar hoja epsilon al nodo
                    if tope_nodo is not None:
                        tope_nodo.agregar_hijo(
                            NodoArbol(simbolo="ε", lexema="ε",
                                      es_terminal=True, es_epsilon=True))
                else:
                    # Crear hijos y apilar en orden inverso
                    hijos_nodos = []
                    for simbolo in prod:
                        if simbolo in self.motor.no_terminales:
                            hijo = NodoArbol(simbolo=simbolo)
                        else:
                            hijo = NodoArbol(simbolo=simbolo, lexema="",
                                             es_terminal=True)
                        hijos_nodos.append(hijo)
                        if tope_nodo is not None:
                            tope_nodo.agregar_hijo(hijo)

                    for simbolo, hijo in reversed(list(zip(prod, hijos_nodos))):
                        pila.append((simbolo, hijo))

        # Timeout
        pasos.append({
            'paso': paso_num,
            'pila': "...",
            'entrada': "...",
            'accion': "ERROR: se excedio el limite de pasos"
        })
        return pasos, raiz, False
