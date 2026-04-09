"""
Arbol de analisis sintactico — Nodo + serializacion JSON.
Version backend: sin dependencias de tkinter.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Any


@dataclass
class NodoArbol:
    """Nodo del arbol de analisis sintactico."""
    simbolo: str
    lexema: str = ""
    hijos: List['NodoArbol'] = field(default_factory=list)
    es_terminal: bool = False
    es_epsilon: bool = False
    x: float = 0.0
    y: float = 0.0

    def agregar_hijo(self, hijo: 'NodoArbol'):
        self.hijos.append(hijo)
        return hijo

    def hoja(simbolo: str, lexema: str = "", fila: int = 0, col: int = 0) -> 'NodoArbol':
        return NodoArbol(simbolo=simbolo, lexema=lexema, es_terminal=True)

    def epsilon() -> 'NodoArbol':
        return NodoArbol(simbolo="ε", lexema="ε", es_terminal=True, es_epsilon=True)

    def to_dict(self) -> dict:
        """Serializa el arbol a un dict anidado para JSON."""
        d: dict[str, Any] = {
            "simbolo": self.simbolo,
            "lexema": self.lexema,
            "es_terminal": self.es_terminal,
            "es_epsilon": self.es_epsilon,
        }
        if self.hijos:
            d["hijos"] = [h.to_dict() for h in self.hijos]
        else:
            d["hijos"] = []
        return d

    def __repr__(self):
        if self.es_epsilon:
            return "ε"
        if self.es_terminal:
            return f"'{self.lexema}'"
        return f"<{self.simbolo}>"


def contar_nodos(nodo: NodoArbol) -> int:
    if nodo is None:
        return 0
    return 1 + sum(contar_nodos(h) for h in nodo.hijos)


def profundidad_arbol(nodo: NodoArbol) -> int:
    if nodo is None or not nodo.hijos:
        return 0
    return 1 + max(profundidad_arbol(h) for h in nodo.hijos)
