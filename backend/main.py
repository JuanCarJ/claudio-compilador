"""
╔══════════════════════════════════════════════════════════════╗
║  CLAUDIO — API Backend (FastAPI)                            ║
║  Endpoints para analisis lexico, sintactico y traduccion    ║
╚══════════════════════════════════════════════════════════════╝
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from lexer import Lexer, TokenType
from parser_rd import ParserDescendenteRecursivo, ErrorSintactico
from parser_ll1 import ParserPredictivoLL1
from arbol import contar_nodos, profundidad_arbol
from traductor import traducir_claudio_a_swift, obtener_mapeo_linea_a_linea
from programas import PROGRAMAS

app = FastAPI(
    title="Claudio Compiler API",
    description="API para el compilador fuente-a-fuente Claudio (Espanol) -> Swift",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# § 1  MODELOS
# ─────────────────────────────────────────────

class CodigoRequest(BaseModel):
    codigo: str


class TokenResponse(BaseModel):
    lexema: str
    tipo: str
    categoria: str
    fila: int
    columna: int


class ErrorLexicoResponse(BaseModel):
    lexema: str
    fila: int
    columna: int
    mensaje: str


class AnalisisLexicoResponse(BaseModel):
    tokens: list[TokenResponse]
    errores: list[ErrorLexicoResponse]
    tabla_simbolos: list[dict]
    total_tokens: int
    total_errores: int


class AnalisisRecursivoResponse(BaseModel):
    valido: bool
    arbol: Optional[dict] = None
    total_nodos: int = 0
    profundidad: int = 0
    errores: list[str] = []
    # Lexico incluido
    lexico: AnalisisLexicoResponse


class PasoTraza(BaseModel):
    paso: int
    pila: str
    entrada: str
    accion: str


class AnalisisLL1Response(BaseModel):
    valido: bool
    arbol: Optional[dict] = None
    total_nodos: int = 0
    profundidad: int = 0
    traza: list[PasoTraza] = []
    total_pasos: int = 0
    primero: dict[str, list[str]] = {}
    siguiente: dict[str, list[str]] = {}
    tabla_ll1: dict[str, dict[str, str]] = {}
    terminales: list[str] = []
    no_terminales: list[str] = []
    es_ll1: bool = True
    conflictos: list[str] = []
    # Lexico incluido
    lexico: AnalisisLexicoResponse


class TraduccionResponse(BaseModel):
    swift: str
    mapeo: list[dict]


class ProgramasResponse(BaseModel):
    programas: dict[str, str]


# ─────────────────────────────────────────────
# § 2  HELPERS
# ─────────────────────────────────────────────

def _categoria_token(tipo_name: str) -> str:
    if tipo_name.startswith("PR_"):
        return "Palabra Reservada"
    if tipo_name.startswith("OP_"):
        return "Operador"
    if tipo_name.startswith("LIT_"):
        return "Literal"
    categorias = {
        "IDENTIFICADOR": "Identificador",
        "PAREN_IZQ": "Delimitador", "PAREN_DER": "Delimitador",
        "COMA": "Delimitador", "DOS_PUNTOS": "Delimitador",
        "PUNTO": "Delimitador", "PUNTO_Y_COMA": "Delimitador",
        "CORCHETE_IZQ": "Delimitador", "CORCHETE_DER": "Delimitador",
        "COMENTARIO_LINEA": "Comentario", "COMENTARIO_BLOQUE": "Comentario",
        "FIN_DE_ARCHIVO": "Especial", "ERROR_LEXICO": "Error",
    }
    return categorias.get(tipo_name, "Otro")


def _analizar_lexico(codigo: str) -> tuple:
    """Ejecuta analisis lexico y retorna (tokens, errores, response)."""
    lexer = Lexer(codigo)
    tokens = lexer.analizar()
    errores = lexer.obtener_errores()

    tokens_resp = []
    for t in tokens:
        if t.tipo == TokenType.FIN_DE_ARCHIVO:
            continue
        tokens_resp.append(TokenResponse(
            lexema=t.lexema,
            tipo=t.tipo.name,
            categoria=_categoria_token(t.tipo.name),
            fila=t.fila,
            columna=t.columna,
        ))

    errores_resp = []
    for e in errores:
        errores_resp.append(ErrorLexicoResponse(
            lexema=e.lexema,
            fila=e.fila,
            columna=e.columna,
            mensaje=f"Caracter no reconocido '{e.lexema}' en fila {e.fila}, col {e.columna}",
        ))

    lexico_resp = AnalisisLexicoResponse(
        tokens=tokens_resp,
        errores=errores_resp,
        tabla_simbolos=lexer.tabla_simbolos(),
        total_tokens=len(tokens_resp),
        total_errores=len(errores_resp),
    )
    return tokens, errores, lexico_resp


# ─────────────────────────────────────────────
# § 3  ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "nombre": "Claudio Compiler API",
        "version": "2.0.0",
        "descripcion": "Compilador fuente-a-fuente Claudio (Espanol) -> Swift",
        "endpoints": [
            "POST /api/lexico",
            "POST /api/recursivo",
            "POST /api/ll1",
            "POST /api/traducir",
            "GET  /api/programas",
        ]
    }


@app.get("/api/programas", response_model=ProgramasResponse)
def obtener_programas():
    """Retorna los 15 programas de ejemplo predefinidos."""
    return ProgramasResponse(programas=PROGRAMAS)


@app.post("/api/lexico", response_model=AnalisisLexicoResponse)
def analizar_lexico(req: CodigoRequest):
    """Ejecuta el analisis lexico sobre el codigo fuente."""
    _, _, lexico = _analizar_lexico(req.codigo)
    return lexico


@app.post("/api/recursivo", response_model=AnalisisRecursivoResponse)
def analizar_recursivo(req: CodigoRequest):
    """Ejecuta analisis lexico + sintactico descendente recursivo."""
    tokens, errores_lex, lexico = _analizar_lexico(req.codigo)

    if errores_lex:
        return AnalisisRecursivoResponse(
            valido=False,
            errores=[f"Error lexico: {e.lexema} en fila {e.fila}, col {e.columna}"
                     for e in errores_lex],
            lexico=lexico,
        )

    parser = ParserDescendenteRecursivo(tokens)
    try:
        arbol = parser.analizar()
        return AnalisisRecursivoResponse(
            valido=True,
            arbol=arbol.to_dict(),
            total_nodos=contar_nodos(arbol),
            profundidad=profundidad_arbol(arbol),
            errores=[],
            lexico=lexico,
        )
    except ErrorSintactico as e:
        return AnalisisRecursivoResponse(
            valido=False,
            errores=[e.mensaje],
            lexico=lexico,
        )


@app.post("/api/ll1", response_model=AnalisisLL1Response)
def analizar_ll1(req: CodigoRequest):
    """Ejecuta analisis lexico + sintactico predictivo LL(1)."""
    tokens, errores_lex, lexico = _analizar_lexico(req.codigo)

    if errores_lex:
        return AnalisisLL1Response(
            valido=False,
            lexico=lexico,
        )

    parser = ParserPredictivoLL1(tokens)

    # FIRST / FOLLOW
    primero_raw = parser.obtener_primero()
    siguiente_raw = parser.obtener_siguiente()
    primero = {k: sorted(v) for k, v in primero_raw.items()}
    siguiente = {k: sorted(v) for k, v in siguiente_raw.items()}

    # Tabla LL(1) como dict de strings
    tabla_raw = parser.obtener_tabla()
    tabla = {}
    for nt, fila in tabla_raw.items():
        tabla[nt] = {}
        for terminal, prod in fila.items():
            tabla[nt][terminal] = " ".join(prod)

    # Ejecutar analisis
    pasos_raw, arbol, aceptado = parser.analizar()
    pasos = [PasoTraza(
        paso=p['paso'],
        pila=p['pila'],
        entrada=p['entrada'],
        accion=p['accion'],
    ) for p in pasos_raw]

    arbol_dict = arbol.to_dict() if arbol and aceptado else None
    n = contar_nodos(arbol) if arbol and aceptado else 0
    p = profundidad_arbol(arbol) if arbol and aceptado else 0

    return AnalisisLL1Response(
        valido=aceptado,
        arbol=arbol_dict,
        total_nodos=n,
        profundidad=p,
        traza=pasos,
        total_pasos=len(pasos),
        primero=primero,
        siguiente=siguiente,
        tabla_ll1=tabla,
        terminales=sorted(parser.obtener_terminales()),
        no_terminales=sorted(parser.obtener_no_terminales()),
        es_ll1=parser.es_ll1(),
        conflictos=parser.obtener_conflictos(),
        lexico=lexico,
    )


@app.post("/api/traducir", response_model=TraduccionResponse)
def traducir(req: CodigoRequest):
    """Traduce codigo Claudio a Swift."""
    swift = traducir_claudio_a_swift(req.codigo)
    mapeo_raw = obtener_mapeo_linea_a_linea(req.codigo)
    mapeo = [{"claudio": cl, "swift": sw} for cl, sw in mapeo_raw]
    return TraduccionResponse(swift=swift, mapeo=mapeo)
