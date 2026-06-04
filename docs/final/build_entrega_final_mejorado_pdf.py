from __future__ import annotations

from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
OUT_REPO = ROOT / "docs" / "final" / "entrega_final_claudio_mejorado.pdf"
OUT_DOWNLOADS = Path("/Users/juancarj/Downloads/Entrega Final Claudio Mejorado.pdf")
EVIDENCE_DIR = ROOT / "docs" / "final" / "evidencias_ui"

PAGE_W, PAGE_H = A4
MARGIN_X = 0.58 * inch
MARGIN_TOP = 0.55 * inch
MARGIN_BOTTOM = 0.5 * inch
CONTENT_W = PAGE_W - (MARGIN_X * 2)

DARK = colors.HexColor("#151A25")
MUTED = colors.HexColor("#687083")
LINE = colors.HexColor("#CBD5E1")
LIGHT = colors.HexColor("#F4F7FB")
PANEL = colors.HexColor("#EFF4FF")
RED = colors.HexColor("#B42318")
RED_BG = colors.HexColor("#FFF2F2")
AMBER = colors.HexColor("#8A5A00")
AMBER_BG = colors.HexColor("#FFF4D6")
BLUE = colors.HexColor("#1D4ED8")
BLUE_BG = colors.HexColor("#EEF5FF")
GREEN = colors.HexColor("#146C43")
GREEN_BG = colors.HexColor("#EAF7EF")
PURPLE = colors.HexColor("#6D4AFF")


def make_styles():
    base = getSampleStyleSheet()
    base.add(
        ParagraphStyle(
            name="CoverMark",
            parent=base["Title"],
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            fontSize=38,
            leading=42,
            textColor=colors.white,
        )
    )
    base.add(
        ParagraphStyle(
            name="CoverKicker",
            parent=base["BodyText"],
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=PURPLE,
            spaceAfter=8,
        )
    )
    base.add(
        ParagraphStyle(
            name="CoverTitle",
            parent=base["Title"],
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=29,
            textColor=DARK,
            spaceAfter=8,
        )
    )
    base.add(
        ParagraphStyle(
            name="CoverSub",
            parent=base["BodyText"],
            alignment=TA_CENTER,
            fontName="Helvetica",
            fontSize=9.7,
            leading=13,
            textColor=MUTED,
            spaceAfter=5,
        )
    )
    base.add(
        ParagraphStyle(
            name="H1x",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=14.2,
            leading=17,
            textColor=DARK,
            spaceBefore=8,
            spaceAfter=6,
        )
    )
    base.add(
        ParagraphStyle(
            name="H2x",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11.2,
            leading=14,
            textColor=BLUE,
            spaceBefore=7,
            spaceAfter=4,
        )
    )
    base.add(
        ParagraphStyle(
            name="Bodyx",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.55,
            leading=11.1,
            textColor=colors.HexColor("#222938"),
            spaceAfter=4,
        )
    )
    base.add(
        ParagraphStyle(
            name="Smallx",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.25,
            leading=9.3,
            textColor=MUTED,
            spaceAfter=2,
        )
    )
    base.add(
        ParagraphStyle(
            name="TableHead",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.45,
            leading=9.2,
            textColor=colors.white,
        )
    )
    base.add(
        ParagraphStyle(
            name="TableCell",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.15,
            leading=9.1,
            textColor=colors.HexColor("#222938"),
        )
    )
    base.add(
        ParagraphStyle(
            name="BoxTitle",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8.2,
            leading=10.2,
            textColor=DARK,
            spaceAfter=2,
        )
    )
    base.add(
        ParagraphStyle(
            name="BoxBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.35,
            leading=9.1,
            textColor=colors.HexColor("#202631"),
            spaceAfter=2,
        )
    )
    base.add(
        ParagraphStyle(
            name="CodeSmall",
            parent=base["Code"],
            fontName="Courier",
            fontSize=6.85,
            leading=8.25,
            textColor=colors.HexColor("#111827"),
        )
    )
    return base


S = make_styles()


def x(text: str) -> str:
    return escape(text, quote=False)


def p(text: str, style: str = "Bodyx") -> Paragraph:
    return Paragraph(text, S[style])


def section_title(number: str, title: str) -> Table:
    num_w = 0.46 * inch
    table = Table(
        [[p(number, "H1x"), p(title, "H1x")]],
        colWidths=[num_w, CONTENT_W - num_w],
    )
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return table


def simple_table(rows: list[list[str]], widths: list[float] | None = None) -> Table:
    table_rows = []
    for row_i, row in enumerate(rows):
        style = "TableHead" if row_i == 0 else "TableCell"
        table_rows.append([p(x(cell), style) for cell in row])
    col_widths = widths or [CONTENT_W / len(rows[0])] * len(rows[0])
    table = Table(table_rows, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), DARK),
                ("GRID", (0, 0), (-1, -1), 0.35, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ]
        )
    )
    return table


def callout(title: str, body: list[str], bg=LIGHT, border=LINE, title_color=DARK) -> Table:
    title_style = ParagraphStyle(
        name=f"BoxTitle{abs(hash((title, title_color))) % 100000}",
        parent=S["BoxTitle"],
        textColor=title_color,
    )
    content = [Paragraph(title, title_style)]
    content.extend(p(line, "BoxBody") for line in body)
    table = Table([[content]], colWidths=[CONTENT_W])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), bg),
                ("BOX", (0, 0), (-1, -1), 0.65, border),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def prod(text: str) -> Table:
    table = Table([[Preformatted(text, S["CodeSmall"])]], colWidths=[CONTENT_W])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), RED_BG),
                ("BOX", (0, 0), (-1, -1), 0.55, colors.HexColor("#F1A6A6")),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def semantic_box(title: str, attrs: str, domain: str, action: str) -> Table:
    return callout(
        title,
        [
            f"<b>Atributos:</b> {x(attrs)}",
            f"<b>Dominio:</b> {x(domain)}",
            f"<b>Acción:</b> {x(action)}",
        ],
        bg=AMBER_BG,
        border=colors.HexColor("#E0A800"),
        title_color=AMBER,
    )


def sdt_box(title: str, actions: list[str]) -> Table:
    return callout(
        title,
        [x(action) for action in actions],
        bg=BLUE_BG,
        border=BLUE,
        title_color=BLUE,
    )


def screenshot(path: Path, caption: str, max_h: float = 4.25 * inch) -> Table:
    if not path.exists():
        raise FileNotFoundError(path)
    img = Image(str(path))
    scale = min(CONTENT_W / img.imageWidth, max_h / img.imageHeight)
    img.drawWidth = img.imageWidth * scale
    img.drawHeight = img.imageHeight * scale
    table = Table([[img], [p(caption, "Smallx")]], colWidths=[CONTENT_W])
    table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("BOX", (0, 0), (0, 0), 0.45, LINE),
                ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#F8FAFC")),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def code_snippet(text: str) -> Table:
    table = Table([[Preformatted(text, S["CodeSmall"])]], colWidths=[CONTENT_W])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("BOX", (0, 0), (-1, -1), 0.45, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def cover_badge() -> Table:
    size = 0.72 * inch
    table = Table([[p("C", "CoverMark")]], colWidths=[size], rowHeights=[size])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), DARK),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOX", (0, 0), (-1, -1), 0.8, PURPLE),
            ]
        )
    )
    return table


def bullets(items: list[str]) -> Table:
    rows = [[p(f"• {x(item)}", "Bodyx")] for item in items]
    table = Table(rows, colWidths=[CONTENT_W])
    table.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )
    return table


def story() -> list:
    flow: list = []

    flow.append(Spacer(1, 0.42 * inch))
    flow.append(Table([[cover_badge()]], colWidths=[CONTENT_W], style=[("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    flow.append(Spacer(1, 0.18 * inch))
    flow.append(p("Entrega Final", "CoverKicker"))
    flow.append(p("Compilador Claudio → Swift", "CoverTitle"))
    flow.append(
        p(
            "Gramática ampliada · Reglas semánticas · SDT de traducción · Implementación · Pruebas",
            "CoverSub",
        )
    )
    flow.append(Spacer(1, 0.22 * inch))
    flow.append(
        simple_table(
            [
                ["Convención visual", "Uso en el informe"],
                ["Rojo", "Producciones de la gramática base."],
                ["Ámbar", "Reglas semánticas: atributos, dominio y acción."],
                ["Azul", "Acciones SDT que sintetizan lenguaje destino Swift."],
            ],
            [1.75 * inch, CONTENT_W - 1.75 * inch],
        )
    )
    flow.append(Spacer(1, 0.28 * inch))
    flow.append(
        callout(
            "Prueba directa del compilador",
            [
                "La aplicación desplegada está disponible en <b>https://claudio.dautia.com</b>. Los casos finales se pueden seleccionar desde la galería de programas y ejecutar en modo Semántico.",
            ],
            bg=GREEN_BG,
            border=GREEN,
            title_color=GREEN,
        )
    )
    flow.append(Spacer(1, 0.28 * inch))
    flow.append(
        p(
            "Autores: Juan David Cárdenas Jiménez · María José Restrepo Ramírez · José Manuel Zuluaga",
            "CoverSub",
        )
    )
    flow.append(p("Teoría de Compiladores · Facultad de Ingeniería · Semestre 1-2026", "CoverSub"))
    flow.append(PageBreak())

    flow.append(p("Tabla de Contenidos", "H1x"))
    flow.append(
        simple_table(
            [
                ["Sección", "Título", "Pág."],
                ["1", "Alcance del Compilador Final", "3"],
                ["2", "Gramática Base y SDT", "4"],
                ["2.1–2.7", "Producciones, semántica y acciones SDT", "4–8"],
                ["3", "Reglas Semánticas Implementadas (SEM-1 … SEM-7)", "8"],
                ["4", "Cómo se Materializa en Claudio", "9"],
                ["5", "Pruebas desde la Interfaz Gráfica", "10"],
                ["6", "Bonus IA con OpenAI", "13"],
                ["7", "Conclusiones", "13"],
            ],
            [0.9 * inch, CONTENT_W - 1.6 * inch, 0.7 * inch],
        )
    )
    flow.append(PageBreak())

    flow.append(section_title("1", "Alcance del Compilador Final"))
    flow.append(
        p(
            "Claudio es un compilador fuente-a-fuente para un lenguaje en español que produce Swift como lenguaje destino. La entrega final integra análisis léxico, análisis sintáctico, análisis semántico y una SDT de traducción. La salida Swift se habilita únicamente cuando el programa supera las fases previas.",
        )
    )
    flow.append(
        simple_table(
            [
                ["Requisito del enunciado", "Evidencia en Claudio"],
                ["Léxico → sintáctico → semántico → SDT", "La compilación encadena fases y detiene la traducción cuando una fase queda inválida."],
                ["Errores unificados", "Cada diagnóstico informa fase, ubicación, lexema asociado y mensaje comprensible."],
                ["Tabla de símbolos en semántica", "El análisis conserva nombre, tipo, ámbito, mutabilidad, fila y columna para validar reglas SEM."],
                ["Casos de prueba desde UI", "La galería incluye casos válidos primero y casos con fallas al final."],
                ["Swift como lenguaje destino", "El panel Swift muestra contraste Claudio/Swift y estado de validación."],
                ["Bonus IA", "OpenAI revisa la salida Swift generada sin reemplazar las reglas determinísticas del compilador."],
            ],
            [2.05 * inch, CONTENT_W - 2.05 * inch],
        )
    )
    flow.append(Spacer(1, 6))
    flow.append(p("Cadena de fases", "H2x"))
    flow.append(
        simple_table(
            [
                ["Fase", "Entrada", "Proceso técnico", "Salida"],
                ["Léxica", "Texto Claudio", "Clasifica lexemas y conserva posición.", "Tokens y errores léxicos."],
                ["Sintáctica", "Tokens válidos", "Aplica la gramática descendente recursiva y construye AST.", "AST y diagnósticos sintácticos."],
                ["Semántica", "AST", "Valida tipos, ámbitos, constantes y condiciones.", "Tabla de símbolos y reglas SEM."],
                ["SDT Swift", "Programa válido", "Ejecuta acciones de traducción asociadas a producciones.", "Código Swift destino."],
                ["IA opcional", "Swift generado", "Revisa legibilidad y coherencia del destino.", "Resumen complementario."],
            ],
            [0.88 * inch, 1.1 * inch, 3.0 * inch, CONTENT_W - 4.98 * inch],
        )
    )

    flow.append(PageBreak())
    flow.append(section_title("2", "Gramática Base y SDT"))
    flow.append(
        p(
            "Las producciones se presentan en BNF compacta. Para cada bloque se indican reglas semánticas cuando aplican y acciones SDT que sintetizan Swift. La idea central es que el árbol no solo se reconoce: también transporta información suficiente para validar y traducir.",
        )
    )

    flow.append(p("2.1 Programa y Declaraciones", "H2x"))
    flow.append(
        prod(
            """programa        -> declaracion programa | ε
declaracion     -> importacion | decl_variable | def_funcion | def_clase | sentencia
importacion     -> importar ID"""
        )
    )
    flow.append(
        sdt_box(
            "Acciones SDT",
            [
                "programa.swift = declaracion.swift + salto de línea + programa1.swift.",
                "programa -> ε sintetiza cadena vacía.",
                "importacion.swift = 'import ' + ID.lexema.",
            ],
        )
    )

    flow.append(p("2.2 Variables y Tipos", "H2x"))
    flow.append(
        prod(
            """decl_variable  -> (var | sea) tipo ID = expresion
tipo           -> entero | real | cadena | booleano | ID
tipo_basico    -> entero | real | cadena | booleano"""
        )
    )
    flow.append(
        semantic_box(
            "SEM-1 y SEM-4: declaración de variable",
            "ID.nombre, tipo.declarado, expresion.tipo, ambito.actual, tabla_simbolos",
            "El identificador no debe existir en el ámbito actual; el tipo de la expresión debe ser compatible con el tipo declarado. entero puede promoverse a real.",
            "Registrar el símbolo si no hay conflicto; si existe duplicado o incompatibilidad, reportar diagnóstico y bloquear Swift.",
        )
    )
    flow.append(
        sdt_box(
            "Acciones SDT",
            [
                "var ID => var ID: TipoSwift = expr.swift.",
                "sea ID => let ID: TipoSwift = expr.swift.",
                "Mapeo de tipos: entero→Int, real→Double, cadena→String, booleano→Bool.",
            ],
        )
    )

    flow.append(PageBreak())
    flow.append(p("2.3 Funciones y Parámetros", "H2x"))
    flow.append(
        prod(
            """def_funcion    -> funcion tipo_ret ID ( parametros ) hacer bloque fin_funcion
tipo_ret       -> tipo_basico | ε
parametros     -> param_lista | ε
param_lista    -> tipo ID param_resto
param_resto    -> , tipo ID param_resto | ε
sent_retornar  -> retornar expresion"""
        )
    )
    flow.append(
        semantic_box(
            "SEM-FUNC: ámbito y parámetros",
            "funcion.nombre, tipo_ret, parametros.lista, ambito.funcion",
            "El nombre de función no debe duplicarse; cada parámetro se declara en el ámbito propio de la función.",
            "Registrar la función, abrir ámbito local, registrar parámetros, analizar el bloque y cerrar el ámbito.",
        )
    )
    flow.append(
        sdt_box(
            "Acciones SDT",
            [
                "def_funcion.swift = func ID(params.swift) -> TipoRet { bloque.swift }.",
                "Si tipo_ret = ε, se omite la flecha de retorno.",
                "param_lista.swift usa la forma _ ID: TipoSwift para facilitar llamadas estilo Claudio.",
                "sent_retornar.swift = return + expresion.swift.",
            ],
        )
    )

    flow.append(p("2.4 Clases, Atributos y Métodos", "H2x"))
    flow.append(
        prod(
            """def_clase      -> clase ID herencia_opt hacer cuerpo_clase fin_clase
herencia_opt   -> hereda ID | ε
cuerpo_clase   -> miembro_clase cuerpo_clase | ε
miembro_clase  -> def_atributo | def_metodo
def_atributo   -> atributo tipo ID
def_metodo     -> metodo ID ( parametros ) hacer bloque fin_funcion"""
        )
    )
    flow.append(
        semantic_box(
            "SEM-CLASE: nombres dentro de clase",
            "clase.nombre, atributo.nombre, metodo.nombre, ambito.clase",
            "Los nombres declarados dentro del ámbito de clase deben ser únicos.",
            "Registrar clase, abrir ámbito de clase, registrar miembros y traducir métodos como funciones Swift internas.",
        )
    )
    flow.append(
        sdt_box(
            "Acciones SDT",
            [
                "def_clase.swift = class ID[: Super] { cuerpo.swift }.",
                "def_atributo.swift declara una propiedad Swift con valor por defecto.",
                "default(Int, Double, String, Bool) = 0, 0.0, \"\", false.",
                "def_metodo.swift = func ID(params.swift) { bloque.swift }.",
            ],
        )
    )

    flow.append(PageBreak())
    flow.append(p("2.5 Bloques y Sentencias", "H2x"))
    flow.append(
        prod(
            """bloque         -> sentencia bloque'
bloque'        -> sentencia bloque' | ε
sentencia      -> sent_id | sent_si | sent_para | sent_mientras
               | sent_retornar | sent_imprimir | sent_romper | sent_continuar | decl_variable
sent_id        -> (ID | este) resto_id
resto_id       -> = expresion | . ID resto_id | ( argumentos ) | ε
argumentos     -> arg_lista | ε
arg_lista      -> expresion arg_resto
arg_resto      -> , expresion arg_resto | ε"""
        )
    )
    flow.append(
        semantic_box(
            "SEM-2, SEM-3 y SEM-5: uso y asignación",
            "ID.nombre, ID.tipo, ID.inmutable, expresion.tipo, tabla_simbolos",
            "Un identificador usado debe existir; una constante declarada con sea no puede reasignarse; el tipo asignado debe ser compatible.",
            "Resolver el símbolo contra la pila de ámbitos y reportar no declarado, reasignación de constante o incompatibilidad.",
        )
    )
    flow.append(
        sdt_box(
            "Acciones SDT",
            [
                "Asignación: lhs.swift = expresion.swift.",
                "este.campo se traduce a self.campo.",
                "Llamada: ID(args.swift); los argumentos concatenan expresiones con coma.",
                "imprimir(expr) -> print(expr); romper/continuar -> break/continue.",
            ],
        )
    )

    flow.append(p("2.6 Condicionales y Ciclos", "H2x"))
    flow.append(
        prod(
            """sent_si        -> si expresion entonces bloque rama_sino fin_si
rama_sino      -> sino bloque | ε
sent_para      -> para ID desde expresion hasta expresion paso_opt hacer bloque fin_para
paso_opt       -> paso expresion | ε
sent_mientras  -> mientras expresion hacer bloque fin_mientras"""
        )
    )
    flow.append(
        semantic_box(
            "SEM-6 y SEM-7: condiciones y límites",
            "condicion.tipo, desde.tipo, hasta.tipo, paso.tipo",
            "La condición de si/mientras debe ser booleana; desde, hasta y paso de para deben ser numéricos.",
            "Reportar condición no booleana o límites no numéricos. La variable del ciclo se registra en el ámbito del bloque.",
        )
    )
    flow.append(
        sdt_box(
            "Acciones SDT",
            [
                "si -> if cond.swift { bloque.swift } y sino -> else { bloque.swift }.",
                "para -> for ID in stride(from: desde.swift, through: hasta.swift, by: paso.swift) { bloque.swift }.",
                "paso_opt -> ε sintetiza 1.",
                "mientras -> while cond.swift { bloque.swift }.",
            ],
        )
    )

    flow.append(PageBreak())
    flow.append(p("2.7 Expresiones", "H2x"))
    flow.append(
        prod(
            """expresion      -> expr_or
expr_or        -> expr_and expr_or'
expr_or'       -> o expr_and expr_or' | ε
expr_and       -> expr_rel expr_and'
expr_and'      -> y expr_rel expr_and' | ε
expr_rel       -> expr_add expr_rel'
expr_rel'      -> op_rel expr_add | ε
expr_add       -> expr_mul expr_add'
expr_add'      -> + expr_mul expr_add' | - expr_mul expr_add' | ε
expr_mul       -> expr_pot expr_mul'
expr_mul'      -> * expr_pot expr_mul' | / expr_pot expr_mul' | % expr_pot expr_mul' | ε
expr_pot       -> expr_unaria expr_pot'
expr_pot'      -> ** expr_unaria expr_pot' | ε
expr_unaria    -> no expr_unaria | - expr_unaria | expr_primaria
expr_primaria  -> literal | verdadero | falso | nulo | nuevo ID(argumentos)
               | este sufijo_id | ID sufijo_id | ( expresion )
sufijo_id      -> ( argumentos ) | . ID sufijo_id | ε"""
        )
    )
    flow.append(
        sdt_box(
            "Acciones SDT",
            [
                "Los operadores aritméticos y relacionales conservan su forma Swift cuando son equivalentes.",
                "y -> &&, o -> ||, no -> !; verdadero/falso/nulo -> true/false/nil.",
                "nuevo ID(args) -> ID(args); este -> self.",
                "a ** b se traduce como pow(Double(a), Double(b)).",
            ],
        )
    )

    flow.append(PageBreak())
    flow.append(section_title("3", "Reglas Semánticas Implementadas"))
    flow.append(
        simple_table(
            [
                ["Regla", "Concepto validado", "Aplicación en Claudio"],
                ["SEM-1", "Declaración única.", "Antes de registrar variables, funciones, clases, atributos o parámetros se revisa el ámbito actual."],
                ["SEM-2", "Uso de identificadores existentes.", "Cada identificador en expresiones, llamadas y asignaciones se resuelve contra la pila de ámbitos."],
                ["SEM-3", "Inmutabilidad de constantes.", "Un símbolo creado con sea queda marcado como inmutable y una asignación posterior se reporta."],
                ["SEM-4", "Compatibilidad en inicialización.", "El tipo declarado se compara con el tipo inferido del valor inicial."],
                ["SEM-5", "Compatibilidad en asignación.", "El tipo almacenado en la tabla se contrasta con la expresión asignada."],
                ["SEM-6", "Condiciones booleanas.", "Las expresiones de si y mientras deben inferirse como booleano."],
                ["SEM-7", "Límites numéricos en para.", "desde, hasta y paso deben inferirse como entero o real."],
            ],
            [0.7 * inch, 2.0 * inch, CONTENT_W - 2.7 * inch],
        )
    )
    flow.append(Spacer(1, 6))
    flow.append(
        p(
            "La tabla de símbolos es el soporte técnico de estas reglas: permite saber dónde fue declarado un nombre, con qué tipo, si es constante y en qué ámbito vive. La inferencia de tipos es conservadora para evitar rechazos incorrectos cuando el compilador no tiene información suficiente.",
        )
    )
    flow.append(
        callout(
            "Relación con la SDT",
            [
                "La traducción no se ejecuta como reemplazo de texto. Primero se valida el AST; después, cada nodo sintetiza un fragmento Swift. Por eso un error SEM bloquea el lenguaje destino aunque la sintaxis sea correcta.",
            ],
            bg=BLUE_BG,
            border=BLUE,
            title_color=BLUE,
        )
    )

    flow.append(PageBreak())
    flow.append(section_title("4", "Cómo se Materializa en Claudio"))
    flow.append(
        p(
            "La implementación se organiza como una cadena observable de fases. Cada fase agrega evidencia: tokens, árbol/diagnósticos, tabla de símbolos, errores semánticos y salida Swift. La interfaz refleja esta lógica para que el comportamiento del compilador se pueda defender desde el producto desplegado.",
        )
    )
    flow.append(
        simple_table(
            [
                ["Fase", "Responsabilidad", "Criterio de continuación"],
                ["Código", "Entrada fuente escrita en Claudio.", "El texto se envía al análisis elegido."],
                ["Léxico", "Reconocer tokens y errores de caracteres.", "Debe quedar sin errores léxicos para confiar en el parser."],
                ["Sintáctico", "Validar la forma del programa con la gramática.", "Debe producir AST válido para análisis semántico."],
                ["Semántico", "Validar tipos, ámbitos y reglas SEM.", "Debe quedar sin errores para habilitar la SDT."],
                ["Swift", "Sintetizar el lenguaje destino.", "Solo se muestra si las fases previas son válidas."],
            ],
            [1.0 * inch, 3.25 * inch, CONTENT_W - 4.25 * inch],
        )
    )
    flow.append(Spacer(1, 6))
    flow.append(p("Compuerta de generación Swift", "H2x"))
    flow.append(
        simple_table(
            [
                ["Situación", "Comportamiento esperado"],
                ["Error léxico", "Se reporta el carácter/lexema inválido y se bloquea Swift."],
                ["Error sintáctico", "Se reporta token encontrado y elemento esperado por la gramática; Swift no se genera."],
                ["Error semántico", "Se informa la regla SEM involucrada y se bloquea el lenguaje destino."],
                ["Sin errores", "Se muestra el código Swift y la validación IA opcional."],
            ],
            [1.7 * inch, CONTENT_W - 1.7 * inch],
        )
    )
    flow.append(Spacer(1, 7))
    flow.append(
        screenshot(
            EVIDENCE_DIR / "01_claudio_swift_generado.png",
            "Evidencia desde https://claudio.dautia.com: caso válido con panel Swift generado, contraste Claudio/Swift y validación IA Swift.",
            max_h=3.95 * inch,
        )
    )

    flow.append(PageBreak())
    flow.append(section_title("5", "Pruebas desde la Interfaz Gráfica"))
    flow.append(
        p(
            "Las pruebas se ejecutan directamente en la interfaz pública: <b>https://claudio.dautia.com</b>. Para reproducirlas, se abre la galería de programas, se selecciona el caso indicado y se ejecuta el análisis en modo Semántico.",
        )
    )
    flow.append(
        simple_table(
            [
                ["Caso en la UI", "Qué demuestra", "Resultado visible"],
                ["Final. Valido con Swift", "Programa correcto con función, constante, ciclo para, acumulador, imprimir y condicional.", "La pestaña Swift queda disponible y muestra validación IA."],
                ["Final. Error semantico sin Swift", "Sintaxis correcta, pero fallas SEM-3, SEM-4 y SEM-6.", "La pestaña Errores lista diagnósticos semánticos y Swift queda bloqueado."],
                ["Final. Error lexico/sintactico sin Swift", "Caracter inválido, condicional incompleto y llamada imprimir mal formada.", "La pestaña Swift informa bloqueo por errores previos."],
            ],
            [2.05 * inch, 3.05 * inch, CONTENT_W - 5.1 * inch],
        )
    )
    flow.append(Spacer(1, 7))
    flow.append(p("5.1 Caso Válido — Swift Generado", "H2x"))
    flow.append(
        p(
            "El caso válido demuestra la ruta completa: el compilador acepta léxico, sintaxis y semántica; luego aplica la SDT para producir Swift y habilita la revisión complementaria con OpenAI.",
        )
    )
    flow.append(
        simple_table(
            [
                ["Observación", "Interpretación"],
                ["Fases marcadas como válidas.", "La compuerta de generación se abre porque no hay errores acumulados."],
                ["Panel Claudio origen / Swift destino.", "La traducción conserva la intención del programa fuente."],
                ["Validación IA Swift visible.", "OpenAI revisa la salida destino después de que Claudio la genera."],
            ],
            [2.25 * inch, CONTENT_W - 2.25 * inch],
        )
    )

    flow.append(PageBreak())
    flow.append(p("5.2 Caso Semántico — Errores y Swift Bloqueado", "H2x"))
    flow.append(
        p(
            "Este caso tiene forma sintáctica aceptable, pero viola reglas semánticas. La evidencia importante es que Claudio no deja pasar la SDT: muestra diagnósticos SEM y conserva la salida Swift bloqueada.",
        )
    )
    flow.append(
        screenshot(
            EVIDENCE_DIR / "02_claudio_errores_semanticos.png",
            "Caso Final. Error semantico sin Swift: Errores muestra SEM-3, SEM-4 y SEM-6 con sugerencias determinísticas e IA.",
            max_h=4.25 * inch,
        )
    )

    flow.append(PageBreak())
    flow.append(p("5.3 Caso Léxico/Sintáctico — Swift Bloqueado", "H2x"))
    flow.append(
        p(
            "Este caso falla antes de la fase semántica por un carácter no reconocido y por construcciones incompletas. La pestaña Swift no presenta código destino; en su lugar resume los errores que impiden la traducción.",
        )
    )
    flow.append(
        screenshot(
            EVIDENCE_DIR / "03_claudio_swift_bloqueado.png",
            "Caso Final. Error lexico/sintactico sin Swift: el panel Swift queda bloqueado y resume errores léxicos/sintácticos.",
            max_h=4.25 * inch,
        )
    )

    flow.append(PageBreak())
    flow.append(section_title("6", "Bonus IA con OpenAI"))
    flow.append(
        p(
            "La integración con OpenAI funciona como revisión posterior del lenguaje destino. Claudio decide de forma determinística si el programa fuente es válido; solo cuando esa decisión es positiva se revisa el Swift generado.",
        )
    )
    flow.append(
        simple_table(
            [
                ["Aspecto", "Descripción"],
                ["Momento de uso", "Después de léxico, sintáctico, semántico y SDT. Si hay errores, no se consulta la revisión de destino."],
                ["Información revisada", "Código Claudio original y Swift sintetizado por las acciones de traducción."],
                ["Criterios", "Sintaxis Swift razonable, bloques balanceados, operadores/literales traducidos y conservación de intención."],
                ["Resultado en UI", "Resumen breve bajo el panel Swift, con estado visible de revisión."],
                ["Límite conceptual", "La IA no reemplaza la gramática, la tabla de símbolos ni las reglas SEM."],
            ],
            [1.55 * inch, CONTENT_W - 1.55 * inch],
        )
    )
    flow.append(Spacer(1, 7))
    flow.append(
        callout(
            "Lectura correcta del bonus",
            [
                "El bonus no convierte a Claudio en un validador probabilístico. La IA se usa para explicar y revisar el Swift ya generado; la aceptación del programa sigue dependiendo de las fases del compilador.",
            ],
            bg=GREEN_BG,
            border=GREEN,
            title_color=GREEN,
        )
    )

    flow.append(section_title("7", "Conclusiones"))
    flow.append(
        bullets(
            [
                "La entrega final implementa una cadena de compilación completa y observable: código fuente, tokens, análisis sintáctico, tabla de símbolos, errores y Swift.",
                "La gramática ampliada y las acciones SDT cubren variables, funciones, clases, bloques, condicionales, ciclos y expresiones.",
                "Las reglas semánticas SEM-1 a SEM-7 se explican desde su concepto y desde su efecto real sobre la generación del lenguaje destino.",
                "La interfaz pública permite reproducir los casos de prueba desde la galería visual de Claudio, sin depender de pasos técnicos externos.",
                "OpenAI aporta una revisión complementaria del Swift, pero la validez del programa depende de las reglas determinísticas del compilador.",
            ]
        )
    )
    return flow


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.3)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN_X, 0.32 * inch, "Entrega Final - Compilador Claudio a Swift")
    canvas.drawRightString(PAGE_W - MARGIN_X, 0.32 * inch, f"Página {doc.page}")
    canvas.restoreState()


def build_pdf(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title="Entrega Final – Compilador Claudio a Swift",
        author="Juan David Cárdenas, María José Restrepo, José Zuluaga",
    )
    frame = Frame(
        MARGIN_X,
        MARGIN_BOTTOM,
        CONTENT_W,
        PAGE_H - MARGIN_TOP - MARGIN_BOTTOM,
        id="normal",
    )
    doc.addPageTemplates([PageTemplate(id="all", frames=[frame], onPage=header_footer)])
    doc.build(story())


def main():
    build_pdf(OUT_REPO)
    build_pdf(OUT_DOWNLOADS)
    print(f"PDF repo: {OUT_REPO}")
    print(f"PDF downloads: {OUT_DOWNLOADS}")


if __name__ == "__main__":
    main()
