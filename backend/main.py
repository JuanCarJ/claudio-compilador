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
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

from lexer import Lexer, TokenType
from parser_rd import ParserDescendenteRecursivo, ErrorSintactico
from parser_ll1 import ParserPredictivoLL1
from arbol import contar_nodos, profundidad_arbol
from traductor import traducir_claudio_a_swift, obtener_mapeo_linea_a_linea
from programas import PROGRAMAS
from ai_suggestions import generar_sugerencias_ia

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
    esperado: str = ""
    simbolo_probable: str = ""
    sugerencia_deterministica: str = ""


class AnalisisLexicoResponse(BaseModel):
    tokens: list[TokenResponse]
    errores: list[ErrorLexicoResponse]
    tabla_simbolos: list[dict]
    total_tokens: int
    total_errores: int


class SugerenciaIAResponse(BaseModel):
    indice: int
    explicacion_usuario: str = ""
    correccion_sugerida: str = ""
    mini_ejemplo: str = ""
    confianza: float = 0.0
    estado_ia: str = "pendiente"


class ErrorSintacticoResponse(BaseModel):
    indice: int
    fila: int
    columna: int
    lexema_encontrado: str
    tipo_encontrado: str
    esperados: list[str]
    contexto: str
    sugerencia_deterministica: str
    sugerencia_ia: Optional[SugerenciaIAResponse] = None
    estado_ia: str = "pendiente"
    recuperacion: str


class AnalisisRecursivoResponse(BaseModel):
    valido: bool
    arbol: Optional[dict] = None
    arbol_parcial: Optional[dict] = None
    total_nodos: int = 0
    profundidad: int = 0
    errores: list[str] = []
    errores_sintacticos: list[ErrorSintacticoResponse] = []
    total_errores_sintacticos: int = 0
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
    arbol_parcial: Optional[dict] = None
    total_nodos: int = 0
    profundidad: int = 0
    errores: list[str] = []
    traza: list[PasoTraza] = []
    total_pasos: int = 0
    primero: dict[str, list[str]] = {}
    siguiente: dict[str, list[str]] = {}
    tabla_ll1: dict[str, dict[str, str]] = {}
    terminales: list[str] = []
    no_terminales: list[str] = []
    es_ll1: bool = True
    conflictos: list[str] = []
    errores_sintacticos: list[ErrorSintacticoResponse] = []
    total_errores_sintacticos: int = 0
    # Lexico incluido
    lexico: AnalisisLexicoResponse


class TraduccionResponse(BaseModel):
    swift: str
    mapeo: list[dict]


class ProgramasResponse(BaseModel):
    programas: dict[str, str]


class SugerenciasIARequest(BaseModel):
    codigo: str
    diagnosticos: list[dict]


class SugerenciasIAResponse(BaseModel):
    estado: str
    sugerencias: list[SugerenciaIAResponse]


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
        detalle = _detalle_error_lexico(e)
        errores_resp.append(ErrorLexicoResponse(
            lexema=e.lexema,
            fila=e.fila,
            columna=e.columna,
            **detalle,
        ))

    lexico_resp = AnalisisLexicoResponse(
        tokens=tokens_resp,
        errores=errores_resp,
        tabla_simbolos=lexer.tabla_simbolos(),
        total_tokens=len(tokens_resp),
        total_errores=len(errores_resp),
    )
    return tokens, errores, lexico_resp


def _recortar_lexema(lexema: str, limite: int = 28) -> str:
    if len(lexema) <= limite:
        return lexema
    return f"{lexema[:limite - 1]}..."


def _detalle_error_lexico(error) -> dict[str, str]:
    if error.lexema.startswith('"'):
        contenido = _recortar_lexema(error.lexema[1:] or "texto")
        return {
            "mensaje": (
                f"Cadena de texto sin cerrar en fila {error.fila}, col {error.columna}: "
                "se esperaba una comilla doble de cierre antes del salto de linea."
            ),
            "esperado": 'Comilla doble de cierre `"` para completar el literal de cadena.',
            "simbolo_probable": '"',
            "sugerencia_deterministica": (
                f'Probablemente falta `"` justo despues de `{contenido}`. '
                f'La cadena deberia quedar como `"{contenido}"`.'
            ),
        }
    if error.lexema.startswith("/*"):
        return {
            "mensaje": (
                f"Comentario de bloque sin cerrar en fila {error.fila}, col {error.columna}: "
                "se esperaba el cierre del comentario."
            ),
            "esperado": "Cierre de comentario de bloque `*/`.",
            "simbolo_probable": "*/",
            "sugerencia_deterministica": "Probablemente falta `*/` antes del fin del archivo.",
        }
    return {
        "mensaje": f"Caracter no reconocido '{error.lexema}' en fila {error.fila}, col {error.columna}",
        "esperado": "Un token valido del lenguaje Claudio.",
        "simbolo_probable": "",
        "sugerencia_deterministica": (
            "Elimina el caracter o reemplazalo por un simbolo, operador, literal, "
            "identificador o palabra reservada valida."
        ),
    }


def _serializar_diagnosticos(diagnosticos) -> list[ErrorSintacticoResponse]:
    return [ErrorSintacticoResponse(**d.to_dict()) for d in diagnosticos]


def _errores_lexicos_legacy(errores_lex) -> list[str]:
    return [
        f"Error lexico: {e.lexema} en fila {e.fila}, col {e.columna}"
        for e in errores_lex
    ]


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

    parser = ParserDescendenteRecursivo(tokens)
    arbol, aceptado = parser.analizar_con_recuperacion()
    diagnosticos = _serializar_diagnosticos(parser.obtener_errores_sintacticos())
    errores = _errores_lexicos_legacy(errores_lex) + [
        d.mensaje_legacy() for d in parser.obtener_errores_sintacticos()
    ]
    valido = aceptado and not errores_lex

    return AnalisisRecursivoResponse(
        valido=valido,
        arbol=arbol.to_dict() if valido else None,
        arbol_parcial=arbol.to_dict(),
        total_nodos=contar_nodos(arbol) if valido else 0,
        profundidad=profundidad_arbol(arbol) if valido else 0,
        errores=errores,
        errores_sintacticos=diagnosticos,
        total_errores_sintacticos=len(diagnosticos),
        lexico=lexico,
    )


@app.post("/api/ll1", response_model=AnalisisLL1Response)
def analizar_ll1(req: CodigoRequest):
    """Ejecuta analisis lexico + sintactico predictivo LL(1)."""
    tokens, errores_lex, lexico = _analizar_lexico(req.codigo)

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
    diagnosticos = _serializar_diagnosticos(parser.obtener_errores_sintacticos())
    valido = aceptado and not errores_lex
    pasos = [PasoTraza(
        paso=p['paso'],
        pila=p['pila'],
        entrada=p['entrada'],
        accion=p['accion'],
    ) for p in pasos_raw]

    arbol_dict = arbol.to_dict() if arbol and valido else None
    arbol_parcial = arbol.to_dict() if arbol else None
    n = contar_nodos(arbol) if arbol and valido else 0
    p = profundidad_arbol(arbol) if arbol and valido else 0

    return AnalisisLL1Response(
        valido=valido,
        arbol=arbol_dict,
        arbol_parcial=arbol_parcial,
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
        errores=_errores_lexicos_legacy(errores_lex) + [
            d.mensaje_legacy() for d in parser.obtener_errores_sintacticos()
        ],
        errores_sintacticos=diagnosticos,
        total_errores_sintacticos=len(diagnosticos),
        lexico=lexico,
    )


@app.post("/api/sugerencias-ia", response_model=SugerenciasIAResponse)
def sugerencias_ia(req: SugerenciasIARequest):
    """Genera sugerencias IA en lote para errores sintacticos ya detectados."""
    estado, sugerencias_raw = generar_sugerencias_ia(req.codigo, req.diagnosticos)
    sugerencias = [SugerenciaIAResponse(**s) for s in sugerencias_raw]
    return SugerenciasIAResponse(estado=estado, sugerencias=sugerencias)


@app.post("/api/traducir", response_model=TraduccionResponse)
def traducir(req: CodigoRequest):
    """Traduce codigo Claudio a Swift."""
    swift = traducir_claudio_a_swift(req.codigo)
    mapeo_raw = obtener_mapeo_linea_a_linea(req.codigo)
    mapeo = [{"claudio": cl, "swift": sw} for cl, sw in mapeo_raw]
    return TraduccionResponse(swift=swift, mapeo=mapeo)
