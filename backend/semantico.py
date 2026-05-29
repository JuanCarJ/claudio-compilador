"""
╔══════════════════════════════════════════════════════════════╗
║  CLAUDIO — Analizador Semántico                             ║
║  7 reglas semánticas implementadas sobre el AST            ║
║  Fase independiente: pasada sobre el árbol de derivación   ║
╚══════════════════════════════════════════════════════════════╝

Reglas semánticas implementadas:
  SEM-1  Declaración duplicada en el mismo ámbito
  SEM-2  Uso de identificador no declarado
  SEM-3  Reasignación de constante (sea)
  SEM-4  Incompatibilidad de tipo en declaración
  SEM-5  Incompatibilidad de tipo en asignación
  SEM-6  Condición de si/mientras no es booleana
  SEM-7  Límites del ciclo para no son numéricos

Tabla de símbolos:
  Almacena por cada identificador: nombre, tipo, inmutable,
  inicializado, ámbito (nivel de anidamiento), fila, columna.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from arbol import NodoArbol


# ─────────────────────────────────────────────
# § 1  TABLA DE SÍMBOLOS
# ─────────────────────────────────────────────

@dataclass
class EntradaSimbolo:
    """Entrada de la tabla de símbolos."""
    nombre: str
    tipo: str           # "entero", "real", "cadena", "booleano", "funcion", "clase", …
    inmutable: bool     # True si fue declarado con 'sea'
    inicializado: bool
    ambito: int         # nivel de anidamiento (0 = global)
    fila: int
    columna: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "nombre": self.nombre,
            "tipo": self.tipo,
            "inmutable": self.inmutable,
            "inicializado": self.inicializado,
            "ambito": self.ambito,
            "fila": self.fila,
            "columna": self.columna,
        }


class TablaSimbolos:
    """
    Tabla de símbolos con manejo de ámbitos anidados.
    Usa una pila de diccionarios: cada nivel corresponde a un ámbito.
    """

    def __init__(self):
        self._pilas: list[dict[str, EntradaSimbolo]] = [{}]
        self._historial: list[EntradaSimbolo] = []

    def entrar_ambito(self):
        self._pilas.append({})

    def salir_ambito(self):
        if len(self._pilas) > 1:
            self._pilas.pop()

    @property
    def nivel_actual(self) -> int:
        return len(self._pilas) - 1

    def declarar(
        self,
        nombre: str,
        tipo: str,
        inmutable: bool,
        fila: int,
        columna: int,
    ) -> Optional[EntradaSimbolo]:
        """
        Declara un identificador en el ámbito actual.
        Retorna None si ya existía en este ámbito (duplicado → SEM-1).
        """
        ambito_actual = self._pilas[-1]
        if nombre in ambito_actual:
            return None
        entrada = EntradaSimbolo(
            nombre=nombre,
            tipo=tipo,
            inmutable=inmutable,
            inicializado=True,
            ambito=self.nivel_actual,
            fila=fila,
            columna=columna,
        )
        ambito_actual[nombre] = entrada
        self._historial.append(entrada)
        return entrada

    def buscar(self, nombre: str) -> Optional[EntradaSimbolo]:
        """Busca del ámbito más interno al más externo."""
        for ambito in reversed(self._pilas):
            if nombre in ambito:
                return ambito[nombre]
        return None

    def buscar_en_ambito_actual(self, nombre: str) -> Optional[EntradaSimbolo]:
        return self._pilas[-1].get(nombre)

    def como_lista(self) -> list[dict[str, Any]]:
        return [e.to_dict() for e in self._historial]


# ─────────────────────────────────────────────
# § 2  DIAGNÓSTICO SEMÁNTICO
# ─────────────────────────────────────────────

@dataclass
class SemanticDiagnostic:
    """Error semántico detectado durante el análisis."""
    indice: int
    fila: int
    columna: int
    lexema: str
    regla: str      # "SEM-1" … "SEM-7"
    mensaje: str
    sugerencia: str
    sugerencia_ia: Optional[dict[str, Any]] = None
    estado_ia: str = "pendiente"

    def to_dict(self) -> dict[str, Any]:
        return {
            "indice": self.indice,
            "fila": self.fila,
            "columna": self.columna,
            "lexema": self.lexema,
            "regla": self.regla,
            "mensaje": self.mensaje,
            "sugerencia": self.sugerencia,
            "sugerencia_ia": self.sugerencia_ia,
            "estado_ia": self.estado_ia,
        }


# ─────────────────────────────────────────────
# § 3  HELPERS DE TIPOS
# ─────────────────────────────────────────────

_SIMBOLO_A_TIPO: dict[str, str] = {
    "PR_ENTERO":   "entero",
    "PR_REAL":     "real",
    "PR_CADENA":   "cadena",
    "PR_BOOLEANO": "booleano",
}

_LITERAL_A_TIPO: dict[str, str] = {
    "LIT_ENTERO":   "entero",
    "LIT_REAL":     "real",
    "LIT_CADENA":   "cadena",
    "PR_VERDADERO": "booleano",
    "PR_FALSO":     "booleano",
}

_TIPOS_NUMERICOS = {"entero", "real"}
_TIPOS_VALIDOS   = {"entero", "real", "cadena", "booleano"}


def _tipos_compatibles(tipo_declarado: str, tipo_valor: Optional[str]) -> bool:
    """
    ¿Puede tipo_valor asignarse a tipo_declarado?
    None → desconocido → se acepta (evita falsos positivos).
    Regla de widening: entero es compatible con real.
    """
    if tipo_valor is None:
        return True
    if tipo_declarado == tipo_valor:
        return True
    if tipo_declarado == "real" and tipo_valor == "entero":
        return True
    return False


# ─────────────────────────────────────────────
# § 4  ANALIZADOR SEMÁNTICO
# ─────────────────────────────────────────────

class AnalizadorSemantico:
    """
    Realiza una pasada sobre el AST (NodoArbol) aplicando las
    reglas semánticas. Completamente independiente del parser.

    Uso:
        analizador = AnalizadorSemantico()
        errores, tabla = analizador.analizar(arbol)
    """

    def __init__(self):
        self._tabla = TablaSimbolos()
        self._errores: list[SemanticDiagnostic] = []
        self._funcion_activa: Optional[str] = None

    # ── Punto de entrada ────────────────────

    def analizar(
        self, arbol: NodoArbol
    ) -> tuple[list[SemanticDiagnostic], TablaSimbolos]:
        self._tabla = TablaSimbolos()
        self._errores = []
        self._funcion_activa = None
        self._visitar(arbol)
        return self._errores, self._tabla

    # ── Registro de errores ─────────────────

    def _error(
        self,
        fila: int,
        columna: int,
        lexema: str,
        regla: str,
        mensaje: str,
        sugerencia: str,
    ):
        self._errores.append(SemanticDiagnostic(
            indice=len(self._errores) + 1,
            fila=fila,
            columna=columna,
            lexema=lexema,
            regla=regla,
            mensaje=mensaje,
            sugerencia=sugerencia,
        ))

    # ── Visitante principal ─────────────────

    def _visitar(self, nodo: Optional[NodoArbol]):
        if nodo is None or nodo.es_epsilon:
            return
        s = nodo.simbolo
        dispatch = {
            "programa":      self._visitar_hijos,
            "declaracion":   self._visitar_hijos,
            "sentencia":     self._visitar_hijos,
            "bloque":        self._visitar_bloque,
            "rama_sino":     self._visitar_hijos,
            "cuerpo_clase":  self._visitar_hijos,
            "miembro_clase": self._visitar_hijos,
            "decl_variable": self._visitar_decl_variable,
            "def_funcion":   self._visitar_def_funcion,
            "def_clase":     self._visitar_def_clase,
            "sent_id":       self._visitar_sent_id,
            "sent_si":       self._visitar_sent_si,
            "sent_mientras": self._visitar_sent_mientras,
            "sent_para":     self._visitar_sent_para,
            "sent_retornar": self._visitar_sent_retornar,
            "sent_imprimir": self._visitar_expr_en_hijos,
            "def_atributo":  self._visitar_def_atributo,
            "def_metodo":    self._visitar_def_metodo,
        }
        fn = dispatch.get(s)
        if fn:
            fn(nodo)
        elif not nodo.es_terminal:
            self._visitar_hijos(nodo)

    def _visitar_hijos(self, nodo: NodoArbol):
        for hijo in nodo.hijos:
            self._visitar(hijo)

    def _visitar_bloque(self, nodo: NodoArbol):
        self._tabla.entrar_ambito()
        self._visitar_hijos(nodo)
        self._tabla.salir_ambito()

    def _visitar_noop(self, _nodo: NodoArbol):
        pass

    def _declarar_o_reportar(
        self,
        nombre: str,
        tipo: str,
        inmutable: bool,
        fila: int,
        columna: int,
        clase: str = "identificador",
    ) -> Optional[EntradaSimbolo]:
        existente = self._tabla.buscar_en_ambito_actual(nombre)
        if existente is not None:
            self._error(
                fila, columna, nombre,
                "SEM-1",
                f"El {clase} '{nombre}' ya fue declarado en este ámbito "
                f"(primera declaración en fila {existente.fila}, columna {existente.columna}).",
                f"Usa un nombre diferente o elimina la declaración duplicada de '{nombre}'.",
            )
            return None
        return self._tabla.declarar(nombre, tipo, inmutable, fila, columna)

    def _visitar_expr_en_hijos(self, nodo: NodoArbol):
        for hijo in nodo.hijos:
            self._buscar_ids_en_expr(hijo)

    # ── SEM-1 / SEM-4  Declaración de variable ──

    def _visitar_decl_variable(self, nodo: NodoArbol):
        """
        SEM-1  Declaración duplicada en el mismo ámbito
          Atributo sintetizado: id.nombre
          Restricción: nombre ∉ tabla_simbolos[ámbito_actual]
          Acción: SI duplicado → reportar error con fila/columna de la nueva declaración

        SEM-4  Incompatibilidad de tipo en declaración
          Atributo sintetizado: decl.tipo_declarado, expr.tipo_inferido
          Restricción: tipos compatibles según _tipos_compatibles()
          Acción: SI incompatible → reportar error indicando tipos involucrados
        """
        hijos = nodo.hijos
        if len(hijos) < 5:
            return  # Árbol incompleto por error sintáctico previo

        declarador = hijos[0]   # PR_VAR o PR_SEA
        nodo_tipo  = hijos[1]   # nodo 'tipo'
        nodo_id    = hijos[2]   # terminal IDENTIFICADOR
        # hijos[3] = OP_ASIGNACION
        nodo_expr  = hijos[4]   # nodo 'expresion'

        inmutable = declarador.lexema == "sea"
        nombre    = nodo_id.lexema
        tipo_str  = self._extraer_tipo(nodo_tipo)
        fila      = nodo_id.fila
        columna   = nodo_id.columna

        # ── SEM-1: Declaración duplicada ──────────────────────────────────
        existente = self._tabla.buscar_en_ambito_actual(nombre)
        if existente is not None:
            self._error(
                fila, columna, nombre,
                "SEM-1",
                f"La variable '{nombre}' ya fue declarada en este ámbito "
                f"(primera declaración en fila {existente.fila}, columna {existente.columna}).",
                f"Elimina esta declaración duplicada o elige un nombre diferente para la variable.",
            )
            # No interrumpe: se registra igual para seguir analizando
        else:
            # ── SEM-4: Incompatibilidad de tipo en declaración ─────────────
            if tipo_str in _TIPOS_VALIDOS:
                tipo_expr = self._tipo_expresion(nodo_expr)
                if tipo_expr is not None and not _tipos_compatibles(tipo_str, tipo_expr):
                    self._error(
                        fila, columna, nombre,
                        "SEM-4",
                        f"Tipo incompatible en la declaración de '{nombre}': "
                        f"se declaró '{tipo_str}' pero el valor asignado es de tipo '{tipo_expr}'.",
                        f"Cambia el valor a un literal de tipo '{tipo_str}' "
                        f"o ajusta el tipo declarado a '{tipo_expr}'.",
                    )

            self._tabla.declarar(nombre, tipo_str or "desconocido", inmutable, fila, columna)

        # Visitar expresión (detecta SEM-2 dentro de ella)
        self._buscar_ids_en_expr(nodo_expr)

    # ── SEM-2 / SEM-3 / SEM-5  sent_id ──────────

    def _visitar_sent_id(self, nodo: NodoArbol):
        """
        SEM-2  Identificador no declarado
          Atributo sintetizado: id.tipo (búsqueda en tabla)
          Restricción: nombre ∈ tabla_simbolos (cualquier ámbito activo)
          Acción: SI no existe → error con fila/columna/lexema

        SEM-3  Reasignación de constante (sea)
          Atributo heredado: id.inmutable (de tabla_simbolos)
          Restricción: id.inmutable == False
          Acción: SI inmutable → error indicando dónde fue declarado

        SEM-5  Incompatibilidad de tipo en asignación
          Atributo heredado: id.tipo (de tabla_simbolos)
          Atributo sintetizado: expr.tipo_inferido
          Restricción: tipos compatibles
          Acción: SI incompatible → error indicando ambos tipos
        """
        hijos = nodo.hijos
        if not hijos:
            return

        nodo_id = hijos[0]
        nombre  = nodo_id.lexema
        fila    = nodo_id.fila
        columna = nodo_id.columna

        # Ignorar 'este' (acceso a miembro propio — no validado aquí)
        if nodo_id.simbolo == "PR_ESTE":
            for h in hijos[1:]:
                self._buscar_ids_en_expr(h)
            return

        # Acceso a miembro: ID.campo…  — sólo validar que el objeto base existe
        if len(hijos) > 1 and hijos[1].simbolo == "PUNTO":
            entrada = self._tabla.buscar(nombre)
            if entrada is None:
                self._error(fila, columna, nombre, "SEM-2",
                    f"El identificador '{nombre}' no ha sido declarado.",
                    f"Declara '{nombre}' con 'var' o 'sea' antes de acceder a sus miembros.",
                )
            # Visitar resto de hijos (argumentos dentro de llamadas de miembro)
            for h in hijos[2:]:
                self._buscar_ids_en_expr(h)
            return

        # Llamada a función: ID(args) — validar existencia (no tipo de retorno)
        if len(hijos) > 1 and hijos[1].simbolo == "PAREN_IZQ":
            entrada = self._tabla.buscar(nombre)
            if entrada is None:
                self._error(fila, columna, nombre, "SEM-2",
                    f"El identificador '{nombre}' no ha sido declarado.",
                    f"Declara la función o clase '{nombre}' antes de llamarla.",
                )
            for h in hijos[1:]:
                self._buscar_ids_en_expr(h)
            return

        # Asignación: ID = expresion
        if len(hijos) >= 3 and hijos[1].simbolo == "OP_ASIGNACION":
            nodo_expr = hijos[2]

            # ── SEM-2 ──────────────────────────────────────────────────────
            entrada = self._tabla.buscar(nombre)
            if entrada is None:
                self._error(fila, columna, nombre, "SEM-2",
                    f"El identificador '{nombre}' no ha sido declarado.",
                    f"Declara '{nombre}' con 'var tipo {nombre} = valor' antes de asignarlo.",
                )
                self._buscar_ids_en_expr(nodo_expr)
                return

            # ── SEM-3 ──────────────────────────────────────────────────────
            if entrada.inmutable:
                self._error(fila, columna, nombre, "SEM-3",
                    f"No se puede reasignar la constante '{nombre}' "
                    f"(declarada con 'sea' en fila {entrada.fila}).",
                    f"Cambia 'sea' por 'var' en la declaración de '{nombre}' "
                    f"si necesitas modificarla.",
                )

            # ── SEM-5 ──────────────────────────────────────────────────────
            if entrada.tipo in _TIPOS_VALIDOS:
                tipo_expr = self._tipo_expresion(nodo_expr)
                if tipo_expr is not None and not _tipos_compatibles(entrada.tipo, tipo_expr):
                    self._error(fila, columna, nombre, "SEM-5",
                        f"Tipo incompatible en la asignación a '{nombre}': "
                        f"la variable es de tipo '{entrada.tipo}' "
                        f"pero el valor asignado es de tipo '{tipo_expr}'.",
                        f"Usa un valor de tipo '{entrada.tipo}' o convierte la expresión.",
                    )

            self._buscar_ids_en_expr(nodo_expr)
            return

        # Identificador usado sin asignación (expresión de solo lectura):
        # solo verificamos que exista (SEM-2)
        entrada = self._tabla.buscar(nombre)
        if entrada is None:
            self._error(fila, columna, nombre, "SEM-2",
                f"El identificador '{nombre}' no ha sido declarado.",
                f"Declara '{nombre}' con 'var' o 'sea' antes de usarlo.",
            )
        for h in hijos[1:]:
            self._buscar_ids_en_expr(h)

    # ── SEM-6  Condición no booleana ─────────────

    def _visitar_sent_si(self, nodo: NodoArbol):
        """
        SEM-6  La condición del 'si' debe ser booleana
          Atributo sintetizado: cond.tipo_inferido
          Restricción: tipo_inferido == "booleano" (si se puede determinar)
          Dominio: {booleano}  — se rechaza si se infiere entero o cadena
          Acción: SI tipo conocido ≠ booleano → error con fila del 'si'
        """
        hijos = nodo.hijos
        nodo_cond = next((h for h in hijos if h.simbolo == "expresion"), None)

        if nodo_cond:
            tipo_cond = self._tipo_expresion(nodo_cond)
            if tipo_cond is not None and tipo_cond != "booleano":
                tok_si = hijos[0] if hijos else None
                self._error(
                    tok_si.fila if tok_si else 0,
                    tok_si.columna if tok_si else 0,
                    "si", "SEM-6",
                    f"La condición del 'si' es de tipo '{tipo_cond}', "
                    f"pero debe ser de tipo 'booleano'.",
                    f"Usa una expresión relacional (==, !=, <, >, <=, >=) "
                    f"o un literal booleano (verdadero/falso) como condición.",
                )
            self._buscar_ids_en_expr(nodo_cond)

        for h in hijos:
            if h.simbolo in ("bloque", "rama_sino"):
                self._visitar(h)

    def _visitar_sent_mientras(self, nodo: NodoArbol):
        """
        SEM-6  La condición del 'mientras' debe ser booleana
          Mismos atributos y restricciones que en sent_si.
        """
        hijos = nodo.hijos
        nodo_cond = next((h for h in hijos if h.simbolo == "expresion"), None)

        if nodo_cond:
            tipo_cond = self._tipo_expresion(nodo_cond)
            if tipo_cond is not None and tipo_cond != "booleano":
                tok_m = hijos[0] if hijos else None
                self._error(
                    tok_m.fila if tok_m else 0,
                    tok_m.columna if tok_m else 0,
                    "mientras", "SEM-6",
                    f"La condición del 'mientras' es de tipo '{tipo_cond}', "
                    f"pero debe ser de tipo 'booleano'.",
                    f"Usa una expresión relacional o un literal booleano como condición del bucle.",
                )
            self._buscar_ids_en_expr(nodo_cond)

        for h in hijos:
            if h.simbolo == "bloque":
                self._visitar(h)

    # ── SEM-7  Límites del para ──────────────────

    def _visitar_sent_para(self, nodo: NodoArbol):
        """
        SEM-7  Los límites (desde/hasta) y el paso del ciclo 'para'
               deben ser de tipo numérico (entero o real)
          Atributos sintetizados: desde.tipo, hasta.tipo, paso.tipo
          Dominio: {entero, real}
          Acción: SI tipo conocido ∉ {entero, real} → error indicando qué límite falla

        Adicionalmente registra la variable del ciclo como entero en un ámbito propio.
        """
        hijos = nodo.hijos
        tok_para = next((h for h in hijos if h.simbolo == "PR_PARA"), None)
        tok_id   = next((h for h in hijos if h.simbolo == "IDENTIFICADOR"), None)

        self._tabla.entrar_ambito()

        # Registrar variable del ciclo como entero implícito
        if tok_id:
            self._declarar_o_reportar(
                tok_id.lexema, "entero", False,
                tok_id.fila, tok_id.columna,
                "variable de ciclo",
            )

        # Expresiones de límites (desde / hasta) en orden de aparición
        expresiones = [h for h in hijos if h.simbolo == "expresion"]
        etiquetas   = ["desde", "hasta"]

        for i, expr in enumerate(expresiones[:2]):
            tipo = self._tipo_expresion(expr)
            if tipo is not None and tipo not in _TIPOS_NUMERICOS:
                etiqueta = etiquetas[i] if i < len(etiquetas) else "expresion"
                self._error(
                    tok_para.fila if tok_para else 0,
                    tok_para.columna if tok_para else 0,
                    "para", "SEM-7",
                    f"El límite '{etiqueta}' del ciclo 'para' debe ser de tipo numérico "
                    f"(entero o real), pero se encontró '{tipo}'.",
                    f"Usa un valor entero o real como límite '{etiqueta}' del ciclo.",
                )
            self._buscar_ids_en_expr(expr)

        # Expresión del paso (dentro de paso_opt)
        paso_opt = next((h for h in hijos if h.simbolo == "paso_opt"), None)
        if paso_opt:
            expr_paso = next((h for h in paso_opt.hijos if h.simbolo == "expresion"), None)
            if expr_paso:
                tipo_paso = self._tipo_expresion(expr_paso)
                if tipo_paso is not None and tipo_paso not in _TIPOS_NUMERICOS:
                    self._error(
                        tok_para.fila if tok_para else 0,
                        tok_para.columna if tok_para else 0,
                        "para", "SEM-7",
                        f"El 'paso' del ciclo 'para' debe ser de tipo numérico, "
                        f"pero se encontró '{tipo_paso}'.",
                        f"Usa un entero o real como valor de 'paso'.",
                    )
                self._buscar_ids_en_expr(expr_paso)

        # Visitar bloque del ciclo
        for h in hijos:
            if h.simbolo == "bloque":
                self._visitar(h)

        self._tabla.salir_ambito()

    # ── Retornar ─────────────────────────────────

    def _visitar_sent_retornar(self, nodo: NodoArbol):
        for h in nodo.hijos:
            self._buscar_ids_en_expr(h)

    # ── Funciones y clases ───────────────────────

    def _visitar_def_funcion(self, nodo: NodoArbol):
        hijos = nodo.hijos
        tok_nombre = next((h for h in hijos if h.simbolo == "IDENTIFICADOR"), None)
        nombre_fun = tok_nombre.lexema if tok_nombre else "<funcion>"

        # Registrar la función en el ámbito global
        if tok_nombre:
            self._declarar_o_reportar(
                nombre_fun, "funcion", False,
                tok_nombre.fila, tok_nombre.columna,
                "función",
            )

        prev_fun = self._funcion_activa
        self._funcion_activa = nombre_fun
        self._tabla.entrar_ambito()

        # Registrar parámetros en el ámbito de la función
        nodo_params = next((h for h in hijos if h.simbolo == "parametros"), None)
        if nodo_params:
            self._registrar_parametros(nodo_params)

        # Visitar cuerpo
        bloque = next((h for h in hijos if h.simbolo == "bloque"), None)
        if bloque:
            self._visitar(bloque)

        self._tabla.salir_ambito()
        self._funcion_activa = prev_fun

    def _visitar_def_metodo(self, nodo: NodoArbol):
        hijos = nodo.hijos
        tok_nombre = next((h for h in hijos if h.simbolo == "IDENTIFICADOR"), None)
        if tok_nombre:
            self._declarar_o_reportar(
                tok_nombre.lexema, "funcion", False,
                tok_nombre.fila, tok_nombre.columna,
                "método",
            )
        self._tabla.entrar_ambito()
        nodo_params = next((h for h in hijos if h.simbolo == "parametros"), None)
        if nodo_params:
            self._registrar_parametros(nodo_params)
        bloque = next((h for h in hijos if h.simbolo == "bloque"), None)
        if bloque:
            self._visitar(bloque)
        self._tabla.salir_ambito()

    def _visitar_def_atributo(self, nodo: NodoArbol):
        hijos = nodo.hijos
        if len(hijos) < 3:
            return
        tipo_str = self._extraer_tipo(hijos[1])
        tok_id = hijos[2]
        self._declarar_o_reportar(
            tok_id.lexema,
            tipo_str or "desconocido",
            False,
            tok_id.fila,
            tok_id.columna,
            "atributo",
        )

    def _registrar_parametros(self, nodo: NodoArbol):
        """Registra recursivamente los parámetros de una función."""
        if nodo.simbolo == "parametros":
            for h in nodo.hijos:
                self._registrar_parametros(h)
        elif nodo.simbolo == "param_lista":
            # hijos: [tipo, IDENTIFICADOR, param_resto]
            if len(nodo.hijos) >= 2:
                tipo_str = self._extraer_tipo(nodo.hijos[0])
                tok_id   = nodo.hijos[1]
                self._declarar_o_reportar(
                    tok_id.lexema, tipo_str or "desconocido", False,
                    tok_id.fila, tok_id.columna,
                    "parámetro",
                )
                if len(nodo.hijos) > 2:
                    self._registrar_parametros(nodo.hijos[2])
        elif nodo.simbolo == "param_resto":
            if nodo.hijos and not nodo.hijos[0].es_epsilon:
                # hijos: [COMA, tipo, IDENTIFICADOR, param_resto]
                if len(nodo.hijos) >= 3:
                    tipo_str = self._extraer_tipo(nodo.hijos[1])
                    tok_id   = nodo.hijos[2]
                    self._declarar_o_reportar(
                        tok_id.lexema, tipo_str or "desconocido", False,
                        tok_id.fila, tok_id.columna,
                        "parámetro",
                    )
                    if len(nodo.hijos) > 3:
                        self._registrar_parametros(nodo.hijos[3])

    def _visitar_def_clase(self, nodo: NodoArbol):
        hijos = nodo.hijos
        tok_nombre = next((h for h in hijos if h.simbolo == "IDENTIFICADOR"), None)
        if tok_nombre:
            self._declarar_o_reportar(
                tok_nombre.lexema, "clase", False,
                tok_nombre.fila, tok_nombre.columna,
                "clase",
            )
        self._tabla.entrar_ambito()
        cuerpo = next((h for h in hijos if h.simbolo == "cuerpo_clase"), None)
        if cuerpo:
            self._visitar(cuerpo)
        self._tabla.salir_ambito()

    # ── Búsqueda de identificadores en expresiones (SEM-2) ──

    def _buscar_ids_en_expr(self, nodo: Optional[NodoArbol]):
        """
        Recorre recursivamente una expresión y reporta SEM-2 para
        cualquier IDENTIFICADOR que no esté en la tabla de símbolos.
        Evita duplicar errores ya reportados por otros visitors.
        """
        if nodo is None or nodo.es_epsilon:
            return
        if nodo.es_terminal:
            if nodo.simbolo == "IDENTIFICADOR":
                nombre = nodo.lexema
                if self._tabla.buscar(nombre) is None:
                    self._error(
                        nodo.fila, nodo.columna, nombre, "SEM-2",
                        f"El identificador '{nombre}' no ha sido declarado.",
                        f"Declara '{nombre}' con 'var tipo {nombre} = valor' antes de usarlo.",
                    )
            return
        for hijo in nodo.hijos:
            self._buscar_ids_en_expr(hijo)

    # ── Inferencia de tipos ──────────────────────

    def _extraer_tipo(self, nodo_tipo: Optional[NodoArbol]) -> Optional[str]:
        """Extrae el string de tipo de un nodo 'tipo'."""
        if nodo_tipo is None:
            return None
        for h in nodo_tipo.hijos:
            if h.es_terminal:
                if h.simbolo in _SIMBOLO_A_TIPO:
                    return _SIMBOLO_A_TIPO[h.simbolo]
                if h.simbolo == "IDENTIFICADOR":
                    return h.lexema
        return None

    def _es_epsilon_nodo(self, nodo: Optional[NodoArbol]) -> bool:
        if nodo is None:
            return True
        if nodo.es_epsilon:
            return True
        return bool(nodo.hijos and nodo.hijos[0].es_epsilon)

    def _tipo_expresion(self, nodo: Optional[NodoArbol]) -> Optional[str]:
        """
        Infiere el tipo de una expresión de forma conservadora.
        Retorna None si no puede determinarse con certeza
        (se prefieren los falsos negativos sobre los falsos positivos).
        """
        if nodo is None or nodo.es_epsilon:
            return None

        s = nodo.simbolo

        # ── Terminal ────────────────────────────────────────────────────────
        if nodo.es_terminal:
            if s in _LITERAL_A_TIPO:
                return _LITERAL_A_TIPO[s]
            if s == "IDENTIFICADOR":
                ent = self._tabla.buscar(nodo.lexema)
                return ent.tipo if ent else None
            return None

        # ── expr_primaria ────────────────────────────────────────────────────
        if s == "expr_primaria":
            hijos = nodo.hijos
            if not hijos:
                return None
            primer = hijos[0]
            if primer.es_terminal:
                if primer.simbolo in _LITERAL_A_TIPO:
                    return _LITERAL_A_TIPO[primer.simbolo]
                if primer.simbolo == "PAREN_IZQ":
                    return self._tipo_expresion(hijos[1] if len(hijos) > 1 else None)
                if primer.simbolo == "IDENTIFICADOR":
                    ent = self._tabla.buscar(primer.lexema)
                    # Si tiene sufijo con paréntesis → llamada de función, tipo desconocido
                    sufijo = hijos[1] if len(hijos) > 1 else None
                    if sufijo and sufijo.simbolo == "sufijo_id":
                        if sufijo.hijos and sufijo.hijos[0].simbolo == "PAREN_IZQ":
                            return None  # llamada — tipo de retorno no rastreado
                    return ent.tipo if ent else None
            return None

        # ── Operadores lógicos → booleano ───────────────────────────────────
        if s in ("expr_or'", "expr_and'"):
            return "booleano" if not self._es_epsilon_nodo(nodo) else None

        # ── Operadores relacionales → booleano ──────────────────────────────
        if s == "expr_rel'":
            return "booleano" if not self._es_epsilon_nodo(nodo) else None

        if s == "expr_rel":
            prima = nodo.hijos[1] if len(nodo.hijos) > 1 else None
            if prima and not self._es_epsilon_nodo(prima):
                return "booleano"
            return self._tipo_expresion(nodo.hijos[0] if nodo.hijos else None)

        if s == "expr_and":
            prima = nodo.hijos[1] if len(nodo.hijos) > 1 else None
            if prima and not self._es_epsilon_nodo(prima):
                return "booleano"
            return self._tipo_expresion(nodo.hijos[0] if nodo.hijos else None)

        if s == "expr_or":
            prima = nodo.hijos[1] if len(nodo.hijos) > 1 else None
            if prima and not self._es_epsilon_nodo(prima):
                return "booleano"
            return self._tipo_expresion(nodo.hijos[0] if nodo.hijos else None)

        # ── Operaciones aritméticas ──────────────────────────────────────────
        if s in ("expr_add", "expr_mul", "expr_pot"):
            tipo_izq = self._tipo_expresion(nodo.hijos[0] if nodo.hijos else None)
            prima    = nodo.hijos[1] if len(nodo.hijos) > 1 else None
            if prima and not self._es_epsilon_nodo(prima):
                tipo_der = self._tipo_expresion(prima)
                return self._combinar_numericos(tipo_izq, tipo_der)
            return tipo_izq

        if s in ("expr_add'", "expr_mul'", "expr_pot'"):
            if not self._es_epsilon_nodo(nodo):
                return self._tipo_expresion(nodo.hijos[1] if len(nodo.hijos) > 1 else None)
            return None

        # ── Operador unario ──────────────────────────────────────────────────
        if s == "expr_unaria":
            hijos = nodo.hijos
            if hijos and hijos[0].simbolo == "PR_NO":
                return "booleano"
            if hijos and hijos[0].simbolo == "OP_RESTA":
                t = self._tipo_expresion(hijos[1] if len(hijos) > 1 else None)
                return t if t in _TIPOS_NUMERICOS else None
            return self._tipo_expresion(hijos[0] if hijos else None)

        # ── Nodos envolventes: delegar al primer hijo ────────────────────────
        if nodo.hijos:
            return self._tipo_expresion(nodo.hijos[0])
        return None

    def _combinar_numericos(
        self, t1: Optional[str], t2: Optional[str]
    ) -> Optional[str]:
        """Combina tipos en operaciones aritméticas: real > entero."""
        if t1 is None or t2 is None:
            return t1 or t2
        if "real" in (t1, t2):
            return "real"
        if t1 == t2:
            return t1
        return None
