"""
Diagnosticos sintacticos estructurados para Claudio.

Este modulo centraliza el formato requerido por el Quiz 3:
ubicacion exacta, token encontrado, tokens esperados, sugerencia
deterministica y descripcion de la recuperacion aplicada.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from lexer import Token, TokenType


SYNC_TOKEN_TYPES = {
    TokenType.PR_SI,
    TokenType.PR_PARA,
    TokenType.PR_MIENTRAS,
    TokenType.PR_RETORNAR,
    TokenType.PR_IMPRIMIR,
    TokenType.PR_ROMPER,
    TokenType.PR_CONTINUAR,
    TokenType.PR_VAR,
    TokenType.PR_SEA,
    TokenType.PR_FUNCION,
    TokenType.PR_CLASE,
    TokenType.PR_IMPORTAR,
    TokenType.PR_SINO,
    TokenType.PR_FIN_SI,
    TokenType.PR_FIN_PARA,
    TokenType.PR_FIN_MIENTRAS,
    TokenType.PR_FIN_FUNCION,
    TokenType.PR_FIN_CLASE,
    TokenType.PAREN_DER,
    TokenType.COMA,
    TokenType.PUNTO_Y_COMA,
    TokenType.FIN_DE_ARCHIVO,
}

SYNC_TERMINALES = {
    "si",
    "para",
    "mientras",
    "retornar",
    "imprimir",
    "romper",
    "continuar",
    "var",
    "sea",
    "funcion",
    "clase",
    "importar",
    "sino",
    "fin_si",
    "fin_para",
    "fin_mientras",
    "fin_funcion",
    "fin_clase",
    ")",
    ",",
    ";",
    "$",
}


TOKEN_A_TERMINAL = {
    TokenType.PR_SI: "si",
    TokenType.PR_ENTONCES: "entonces",
    TokenType.PR_SINO: "sino",
    TokenType.PR_FIN_SI: "fin_si",
    TokenType.PR_PARA: "para",
    TokenType.PR_DESDE: "desde",
    TokenType.PR_HASTA: "hasta",
    TokenType.PR_PASO: "paso",
    TokenType.PR_HACER: "hacer",
    TokenType.PR_FIN_PARA: "fin_para",
    TokenType.PR_MIENTRAS: "mientras",
    TokenType.PR_FIN_MIENTRAS: "fin_mientras",
    TokenType.PR_FUNCION: "funcion",
    TokenType.PR_FIN_FUNCION: "fin_funcion",
    TokenType.PR_RETORNAR: "retornar",
    TokenType.PR_CLASE: "clase",
    TokenType.PR_FIN_CLASE: "fin_clase",
    TokenType.PR_NUEVO: "nuevo",
    TokenType.PR_ESTE: "este",
    TokenType.PR_VAR: "var",
    TokenType.PR_SEA: "sea",
    TokenType.PR_ENTERO: "entero",
    TokenType.PR_REAL: "real",
    TokenType.PR_CADENA: "cadena",
    TokenType.PR_BOOLEANO: "booleano",
    TokenType.PR_VERDADERO: "verdadero",
    TokenType.PR_FALSO: "falso",
    TokenType.PR_NULO: "nulo",
    TokenType.PR_IMPRIMIR: "imprimir",
    TokenType.PR_Y: "y",
    TokenType.PR_O: "o",
    TokenType.PR_NO: "no",
    TokenType.PR_IMPORTAR: "importar",
    TokenType.PR_HEREDA: "hereda",
    TokenType.PR_METODO: "metodo",
    TokenType.PR_ATRIBUTO: "atributo",
    TokenType.PR_ROMPER: "romper",
    TokenType.PR_CONTINUAR: "continuar",
    TokenType.IDENTIFICADOR: "ID",
    TokenType.LIT_ENTERO: "NUM_ENTERO",
    TokenType.LIT_REAL: "NUM_REAL",
    TokenType.LIT_CADENA: "CADENA_LIT",
    TokenType.OP_SUMA: "+",
    TokenType.OP_RESTA: "-",
    TokenType.OP_MULT: "*",
    TokenType.OP_DIV: "/",
    TokenType.OP_MOD: "%",
    TokenType.OP_POT: "**",
    TokenType.OP_IGUAL: "==",
    TokenType.OP_DISTINTO: "!=",
    TokenType.OP_MENOR: "<",
    TokenType.OP_MAYOR: ">",
    TokenType.OP_MENOR_IGUAL: "<=",
    TokenType.OP_MAYOR_IGUAL: ">=",
    TokenType.OP_ASIGNACION: "=",
    TokenType.PAREN_IZQ: "(",
    TokenType.PAREN_DER: ")",
    TokenType.COMA: ",",
    TokenType.PUNTO: ".",
    TokenType.PUNTO_Y_COMA: ";",
    TokenType.FIN_DE_ARCHIVO: "$",
}


TERMINAL_A_TEXTO = {
    "$": "fin de archivo",
    "ID": "identificador",
    "NUM_ENTERO": "numero entero",
    "NUM_REAL": "numero real",
    "CADENA_LIT": "cadena de texto",
    "si": "`si`",
    "entonces": "`entonces`",
    "sino": "`sino`",
    "fin_si": "`fin_si`",
    "para": "`para`",
    "desde": "`desde`",
    "hasta": "`hasta`",
    "paso": "`paso`",
    "hacer": "`hacer`",
    "fin_para": "`fin_para`",
    "mientras": "`mientras`",
    "fin_mientras": "`fin_mientras`",
    "funcion": "`funcion`",
    "fin_funcion": "`fin_funcion`",
    "clase": "`clase`",
    "fin_clase": "`fin_clase`",
    "var": "`var`",
    "sea": "`sea`",
    "=": "`=`",
    "(": "`(`",
    ")": "`)`",
    ",": "`,`",
    ".": "`.`",
}


def token_a_terminal(tok: Token) -> str:
    return TOKEN_A_TERMINAL.get(tok.tipo, tok.lexema)


def normalizar_esperados(esperados: Iterable[Any]) -> list[str]:
    resultado: list[str] = []
    for esperado in esperados:
        if isinstance(esperado, TokenType):
            valor = TOKEN_A_TERMINAL.get(esperado, esperado.name)
        else:
            valor = str(esperado)
        if valor not in resultado:
            resultado.append(valor)
    return resultado


def describir_esperados(esperados: Iterable[str], limite: int = 8) -> str:
    valores = list(esperados)
    if not valores:
        return "un token valido segun la gramatica"
    textos = [TERMINAL_A_TEXTO.get(v, f"`{v}`") for v in valores[:limite]]
    if len(valores) > limite:
        textos.append(f"{len(valores) - limite} opciones mas")
    return ", ".join(textos)


def _linea_fuente(codigo: str, fila: int) -> str:
    lineas = codigo.splitlines()
    if 1 <= fila <= len(lineas):
        return lineas[fila - 1]
    return ""


def _contexto_cercano(codigo: str, fila: int, radio: int = 2) -> list[dict[str, Any]]:
    lineas = codigo.splitlines()
    if not lineas:
        return []
    inicio = max(1, fila - radio)
    fin = min(len(lineas), fila + radio)
    return [
        {"fila": numero, "texto": lineas[numero - 1]}
        for numero in range(inicio, fin + 1)
    ]


def generar_sugerencia_deterministica(
    contexto: str,
    esperados: list[str],
    encontrado: str,
) -> str:
    ctx = contexto.lower()
    esperados_set = set(esperados)
    siguiente = describir_esperados(esperados, limite=6)
    espera_expresion = bool(esperados_set & {
        "NUM_ENTERO", "NUM_REAL", "CADENA_LIT", "ID",
        "verdadero", "falso", "nulo", "(", "nuevo",
    })

    if espera_expresion and "asignacion" in ctx:
        return (
            f"Siguiente esperado: {siguiente}. Falta el valor despues de `=` "
            "antes de continuar. Ejemplo: `var entero x = 0`."
        )
    if "=" in esperados_set:
        return f"Siguiente esperado: {siguiente}. Completa la asignacion usando `=` seguido de una expresion valida."
    if "sentencia" in ctx or "declaracion" in ctx or "bloque" in ctx:
        return f"Siguiente esperado: {siguiente}. Inicia una sentencia valida, por ejemplo `var`, `si`, `para`, `mientras`, `imprimir` o un identificador."
    if espera_expresion and (
        "operando" in ctx
        or encontrado in {"entonces", "hacer", ")", ",", "hasta", "paso"}
    ):
        ejemplo = "`si x > 5 entonces`" if encontrado == "entonces" else "`x + 1`"
        return (
            f"Siguiente esperado: {siguiente}. Falta un operando antes de "
            f"`{encontrado}`; completa la expresion. Ejemplo: {ejemplo}."
        )
    if espera_expresion and "condicion" in ctx:
        return (
            f"Siguiente esperado: {siguiente}. Completa la condicion con una "
            "expresion valida antes de la palabra que abre el bloque."
        )
    if espera_expresion and "argumento" in ctx:
        return (
            f"Siguiente esperado: {siguiente}. Agrega el argumento faltante o "
            "cierra la llamada solo si la gramatica permite lista vacia."
        )
    if espera_expresion and encontrado in {
        "var", "sea", "si", "para", "mientras", "imprimir",
        "retornar", "funcion", "clase", "importar",
    }:
        return (
            f"Siguiente esperado: {siguiente}. `{encontrado}` parece iniciar otra "
            "sentencia; probablemente falta una expresion justo antes de ese token."
        )
    if "entonces" in esperados_set or "sent_si" in ctx or "condicional" in ctx:
        return f"Siguiente esperado: {siguiente}. Completa la estructura condicional: `si <expresion> entonces ... fin_si`."
    if "hacer" in esperados_set and ("para" in ctx or "mientras" in ctx):
        return f"Siguiente esperado: {siguiente}. Agrega `hacer` despues de la condicion o rango para iniciar el bloque del ciclo."
    if "hacer" in esperados_set and ("funcion" in ctx or "clase" in ctx or "metodo" in ctx):
        return f"Siguiente esperado: {siguiente}. Agrega `hacer` antes del cuerpo de la funcion, metodo o clase."
    if "hacer" in esperados_set:
        return f"Siguiente esperado: {siguiente}. Agrega `hacer` para separar el encabezado de la estructura y su bloque de instrucciones."
    if ")" in esperados_set:
        return f"Siguiente esperado: {siguiente}. Cierra el parentesis abierto antes de continuar con la siguiente construccion."
    if esperados_set == {"ID"}:
        return f"Siguiente esperado: {siguiente}. Escribe el identificador que corresponde en esta posicion de la gramatica."
    if "ID" in esperados_set and ("tipo" in ctx or "variable" in ctx or "param" in ctx):
        return f"Siguiente esperado: {siguiente}. Despues del tipo debe aparecer el nombre identificador que quieres declarar."
    if {"entero", "real", "cadena", "booleano"} & esperados_set or "tipo" in ctx:
        return f"Siguiente esperado: {siguiente}. Usa un tipo valido antes del identificador: `entero`, `real`, `cadena`, `booleano` o una clase."
    if espera_expresion:
        return f"Siguiente esperado: {siguiente}. Completa la expresion con un literal, identificador, llamada, instancia o subexpresion entre parentesis."
    if esperados_set & {"fin_si", "fin_para", "fin_mientras", "fin_funcion", "fin_clase"}:
        return f"Siguiente esperado: {siguiente}. Cierra el bloque con la palabra reservada de cierre que corresponde a la estructura abierta."
    if encontrado == "EOF":
        return f"Siguiente esperado: {siguiente}. El codigo termino antes de cerrar una estructura; revisa bloques, parentesis y expresiones incompletas."
    return f"Siguiente esperado: {siguiente}. Revisa este punto de la produccion actual."


@dataclass
class SyntaxDiagnostic:
    indice: int
    fila: int
    columna: int
    lexema_encontrado: str
    tipo_encontrado: str
    esperados: list[str]
    contexto: str
    sugerencia_deterministica: str
    recuperacion: str
    sugerencia_ia: dict[str, Any] | None = None
    estado_ia: str = "pendiente"

    def to_dict(self) -> dict[str, Any]:
        return {
            "indice": self.indice,
            "fila": self.fila,
            "columna": self.columna,
            "lexema_encontrado": self.lexema_encontrado,
            "tipo_encontrado": self.tipo_encontrado,
            "esperados": self.esperados,
            "contexto": self.contexto,
            "sugerencia_deterministica": self.sugerencia_deterministica,
            "sugerencia_ia": self.sugerencia_ia,
            "estado_ia": self.estado_ia,
            "recuperacion": self.recuperacion,
        }

    def mensaje_legacy(self) -> str:
        esperado = describir_esperados(self.esperados)
        return (
            f"Error sintactico [{self.indice}] en fila {self.fila}, col {self.columna}: "
            f"encontrado '{self.lexema_encontrado}' ({self.tipo_encontrado}); "
            f"esperado: {esperado}. {self.sugerencia_deterministica}"
        )


def crear_diagnostico(
    indice: int,
    token: Token,
    esperados: Iterable[Any],
    contexto: str,
    recuperacion: str,
) -> SyntaxDiagnostic:
    esperados_norm = normalizar_esperados(esperados)
    lexema = "EOF" if token.tipo == TokenType.FIN_DE_ARCHIVO else token.lexema
    tipo = token.tipo.name
    sugerencia = generar_sugerencia_deterministica(contexto, esperados_norm, lexema)
    return SyntaxDiagnostic(
        indice=indice,
        fila=token.fila,
        columna=token.columna,
        lexema_encontrado=lexema,
        tipo_encontrado=tipo,
        esperados=esperados_norm,
        contexto=contexto,
        sugerencia_deterministica=sugerencia,
        recuperacion=recuperacion,
    )


def diagnosticos_para_ia(codigo: str, diagnosticos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    compactos = []
    for diag in diagnosticos:
        fila = int(diag.get("fila") or 0)
        compactos.append({
            "indice": diag.get("indice"),
            "fila": fila,
            "columna": diag.get("columna"),
            "linea": _linea_fuente(codigo, fila),
            "contexto_cercano": _contexto_cercano(codigo, fila),
            "lexema_encontrado": diag.get("lexema_encontrado"),
            "tipo_encontrado": diag.get("tipo_encontrado"),
            "esperados": diag.get("esperados", []),
            "contexto": diag.get("contexto", ""),
            "sugerencia_deterministica": diag.get("sugerencia_deterministica", ""),
        })
    return compactos
