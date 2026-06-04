"""
╔══════════════════════════════════════════════════════════════╗
║  CLAUDIO — Traductor Visual (Claudio → Swift)               ║
║  Mapeo estático línea-a-línea basado en tokens              ║
║  Curso: Teoría de Compiladores                              ║
║                                                             ║
║  Autores: Juan David Cárdenas Jiménez                       ║
║           María José Restrepo Ramírez                       ║
║           José Zuluaga                                      ║
╚══════════════════════════════════════════════════════════════╝

Módulo que traduce código Claudio a su representación equivalente
en Swift, aplicando reglas de mapeo token-a-token y reconociendo
patrones sintácticos comunes (declaraciones, condicionales, ciclos,
funciones, clases).

Este NO es un compilador completo — es una traducción visual que
muestra la correspondencia entre ambos lenguajes.
"""

import re
from typing import List, Tuple


# ─────────────────────────────────────────────
# § 1  MAPEO DE TIPOS
# ─────────────────────────────────────────────

TIPOS_SWIFT = {
    'entero':   'Int',
    'real':     'Double',
    'cadena':   'String',
    'booleano': 'Bool',
}

VALORES_DEFECTO_SWIFT = {
    'Int':    '0',
    'Double': '0.0',
    'String': '""',
    'Bool':   'false',
}

LITERALES_SWIFT = {
    'verdadero': 'true',
    'falso':     'false',
    'nulo':      'nil',
}


# ─────────────────────────────────────────────
# § 2  TRADUCCIÓN LÍNEA A LÍNEA
# ─────────────────────────────────────────────

def traducir_claudio_a_swift(codigo: str) -> str:
    """
    Traduce código Claudio a Swift línea por línea aplicando
    reglas de mapeo basadas en patrones de tokens.

    Retorna el código Swift equivalente como string.
    """
    lineas = codigo.split('\n')
    resultado = []

    for linea in lineas:
        traducida = _traducir_linea(linea)
        resultado.append(traducida)

    return '\n'.join(resultado)


def _traducir_linea(linea: str) -> str:
    """Traduce una línea individual de Claudio a Swift."""
    stripped = linea.strip()
    indent = linea[:len(linea) - len(linea.lstrip())]

    # Línea vacía
    if not stripped:
        return ''

    # ── Comentarios ──
    if stripped.startswith('//'):
        return linea  # Los comentarios se mantienen igual

    if stripped.startswith('/*'):
        return linea

    if stripped.endswith('*/'):
        return linea

    # ── Importación ──
    m = re.match(r'^importar\s+(\w+)$', stripped)
    if m:
        return f'{indent}import {m.group(1)}'

    # ── Declaración var con tipo ──
    m = re.match(r'^var\s+(\w+)\s+(\w+)\s*=\s*(.+)$', stripped)
    if m:
        tipo_cl, nombre, valor = m.group(1), m.group(2), m.group(3)
        tipo_sw = TIPOS_SWIFT.get(tipo_cl, tipo_cl)
        valor_sw = _traducir_expresion(valor)
        return f'{indent}var {nombre}: {tipo_sw} = {valor_sw}'

    # ── Declaración var sin inicialización ──
    m = re.match(r'^var\s+(\w+)\s+(\w+)$', stripped)
    if m:
        tipo_cl, nombre = m.group(1), m.group(2)
        tipo_sw = TIPOS_SWIFT.get(tipo_cl, tipo_cl)
        default = VALORES_DEFECTO_SWIFT.get(tipo_sw)
        if default is not None:
            return f'{indent}var {nombre}: {tipo_sw} = {default}'
        return f'{indent}var {nombre}: {tipo_sw}'

    # ── Declaración sea (let) con tipo ──
    m = re.match(r'^sea\s+(\w+)\s+(\w+)\s*=\s*(.+)$', stripped)
    if m:
        tipo_cl, nombre, valor = m.group(1), m.group(2), m.group(3)
        tipo_sw = TIPOS_SWIFT.get(tipo_cl, tipo_cl)
        valor_sw = _traducir_expresion(valor)
        return f'{indent}let {nombre}: {tipo_sw} = {valor_sw}'

    # ── Condicional si...entonces ──
    m = re.match(r'^si\s+(.+)\s+entonces$', stripped)
    if m:
        cond = _traducir_expresion(m.group(1))
        return f'{indent}if {cond} {{'

    # ── sino ──
    if stripped == 'sino':
        return f'{indent}}} else {{'

    # ── fin_si ──
    if stripped == 'fin_si':
        return f'{indent}}}'

    # ── Ciclo para ──
    m = re.match(
        r'^para\s+(\w+)\s+desde\s+(.+?)\s+hasta\s+(.+?)(?:\s+paso\s+(.+?))?\s+hacer$',
        stripped
    )
    if m:
        var = m.group(1)
        inicio = _traducir_expresion(m.group(2))
        fin = _traducir_expresion(m.group(3))
        paso = _traducir_expresion(m.group(4)) if m.group(4) else '1'
        return f'{indent}for {var} in stride(from: {inicio}, through: {fin}, by: {paso}) {{'

    # ── fin_para ──
    if stripped == 'fin_para':
        return f'{indent}}}'

    # ── Ciclo mientras ──
    m = re.match(r'^mientras\s+(.+)\s+hacer$', stripped)
    if m:
        cond = _traducir_expresion(m.group(1))
        return f'{indent}while {cond} {{'

    # ── fin_mientras ──
    if stripped == 'fin_mientras':
        return f'{indent}}}'

    # ── Función ──
    m = re.match(r'^funcion\s+(\w+)\s+(\w+)\((.*)?\)\s+hacer$', stripped)
    if m:
        tipo_ret, nombre, params = m.group(1), m.group(2), m.group(3) or ''
        tipo_sw = TIPOS_SWIFT.get(tipo_ret, tipo_ret)
        params_sw = _traducir_parametros(params)
        return f'{indent}func {nombre}({params_sw}) -> {tipo_sw} {{'

    # ── Función sin tipo de retorno ──
    m = re.match(r'^funcion\s+(\w+)\((.*)?\)\s+hacer$', stripped)
    if m:
        nombre, params = m.group(1), m.group(2) or ''
        params_sw = _traducir_parametros(params)
        return f'{indent}func {nombre}({params_sw}) {{'

    # ── fin_funcion ──
    if stripped == 'fin_funcion':
        return f'{indent}}}'

    # ── retornar ──
    m = re.match(r'^retornar\s+(.+)$', stripped)
    if m:
        return f'{indent}return {_traducir_expresion(m.group(1))}'

    if stripped == 'retornar':
        return f'{indent}return'

    # ── Clase ──
    m = re.match(r'^clase\s+(\w+)\s+hereda\s+(\w+)\s+hacer$', stripped)
    if m:
        return f'{indent}class {m.group(1)}: {m.group(2)} {{'

    m = re.match(r'^clase\s+(\w+)\s+hacer$', stripped)
    if m:
        return f'{indent}class {m.group(1)} {{'

    # ── fin_clase ──
    if stripped == 'fin_clase':
        return f'{indent}}}'

    # ── Atributo ──
    m = re.match(r'^atributo\s+(\w+)\s+(\w+)$', stripped)
    if m:
        tipo_cl, nombre = m.group(1), m.group(2)
        tipo_sw = TIPOS_SWIFT.get(tipo_cl, tipo_cl)
        default = VALORES_DEFECTO_SWIFT.get(tipo_sw)
        if default is not None:
            return f'{indent}var {nombre}: {tipo_sw} = {default}'
        return f'{indent}var {nombre}: {tipo_sw}'

    # ── Método ──
    m = re.match(r'^metodo\s+(\w+)\((.*)?\)\s+hacer$', stripped)
    if m:
        nombre, params = m.group(1), m.group(2) or ''
        params_sw = _traducir_parametros(params)
        return f'{indent}func {nombre}({params_sw}) {{'

    # ── imprimir ──
    m = re.match(r'^imprimir\((.+)\)$', stripped)
    if m:
        return f'{indent}print({_traducir_expresion(m.group(1))})'

    # ── romper / continuar ──
    if stripped == 'romper':
        return f'{indent}break'

    if stripped == 'continuar':
        return f'{indent}continue'

    # ── Asignación general ──
    m = re.match(r'^(.+?)\s*=\s*(.+)$', stripped)
    if m and '==' not in stripped and '!=' not in stripped and '<=' not in stripped and '>=' not in stripped:
        izq = _traducir_expresion(m.group(1))
        der = _traducir_expresion(m.group(2))
        # Reemplazar este. por self.
        izq = izq.replace('este.', 'self.')
        return f'{indent}{izq} = {der}'

    # ── Llamada a función/método ──
    expr_sw = _traducir_expresion(stripped)
    return f'{indent}{expr_sw}'


# ─────────────────────────────────────────────
# § 3  TRADUCCIÓN DE EXPRESIONES
# ─────────────────────────────────────────────

def _traducir_expresion(expr: str) -> str:
    """Traduce una expresión de Claudio a Swift."""
    expr = expr.strip()

    # Operadores lógicos: 'y', 'o', 'no' son palabras reservadas en Claudio
    # Reemplazar solo cuando están rodeadas de espacios (contexto de operador)
    expr = re.sub(r'\s+y\s+', ' && ', expr)
    expr = re.sub(r'\s+o\s+', ' || ', expr)
    expr = re.sub(r'\bno\s+', '!', expr)

    # Literales booleanos
    for cl, sw in LITERALES_SWIFT.items():
        expr = re.sub(rf'\b{cl}\b', sw, expr)

    # Potencia: a ** b → pow(Double(a), Double(b))
    pot_match = re.search(r'(\w+)\s*\*\*\s*(\w+)', expr)
    if pot_match:
        a, b = pot_match.group(1), pot_match.group(2)
        expr = expr.replace(pot_match.group(0), f'pow(Double({a}), Double({b}))')

    # nuevo X(...) → X(...)
    expr = re.sub(r'\bnuevo\s+(\w+)\(', r'\1(', expr)

    # este.x → self.x
    expr = expr.replace('este.', 'self.')

    return expr


def _traducir_parametros(params: str) -> str:
    """Traduce lista de parámetros: 'entero n, real x' → '_ n: Int, _ x: Double'"""
    if not params.strip():
        return ''

    partes = [p.strip() for p in params.split(',')]
    resultado = []
    for parte in partes:
        tokens = parte.split()
        if len(tokens) == 2:
            tipo_cl, nombre = tokens
            tipo_sw = TIPOS_SWIFT.get(tipo_cl, tipo_cl)
            resultado.append(f'_ {nombre}: {tipo_sw}')
        else:
            resultado.append(parte)
    return ', '.join(resultado)


# ─────────────────────────────────────────────
# § 4  FUNCIÓN DE UTILIDAD
# ─────────────────────────────────────────────

def obtener_mapeo_linea_a_linea(codigo: str) -> List[Tuple[str, str]]:
    """
    Retorna una lista de tuplas (linea_claudio, linea_swift)
    para visualización lado a lado.
    """
    lineas_cl = codigo.split('\n')
    swift = traducir_claudio_a_swift(codigo)
    lineas_sw = swift.split('\n')

    # Asegurar misma longitud
    max_len = max(len(lineas_cl), len(lineas_sw))
    lineas_cl.extend([''] * (max_len - len(lineas_cl)))
    lineas_sw.extend([''] * (max_len - len(lineas_sw)))

    return list(zip(lineas_cl, lineas_sw))
