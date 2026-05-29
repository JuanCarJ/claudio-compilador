from __future__ import annotations

from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
OUT_REPO = ROOT / "docs" / "quiz4" / "entrega_quiz4_claudio_semantico.pdf"
OUT_DOWNLOADS = Path("/Users/juancarj/Downloads/quiz4_comp/04_pdf_entrega_quiz4_claudio_semantico.pdf")
OUT_DOWNLOADS_MAIN = Path("/Users/juancarj/Downloads/Quiz 4 Claudio.pdf")


PAGE_W, PAGE_H = letter
MARGIN_X = 0.72 * inch
MARGIN_TOP = 0.78 * inch
MARGIN_BOTTOM = 0.64 * inch

RED = colors.HexColor("#B42318")
AMBER = colors.HexColor("#FFF3CD")
AMBER_LINE = colors.HexColor("#D59E00")
DARK = colors.HexColor("#18212F")
BLUE = colors.HexColor("#0F4C81")
GREEN = colors.HexColor("#146C43")
MUTED = colors.HexColor("#5B6472")
LIGHT = colors.HexColor("#F3F6FA")
LINE = colors.HexColor("#CBD5E1")
CODE_BG = colors.HexColor("#F7F7F7")


def make_styles():
    base = getSampleStyleSheet()
    base.add(ParagraphStyle(
        name="CoverTitle",
        parent=base["Title"],
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=31,
        alignment=TA_CENTER,
        textColor=DARK,
        spaceAfter=16,
    ))
    base.add(ParagraphStyle(
        name="CoverSub",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        textColor=MUTED,
        spaceAfter=8,
    ))
    base.add(ParagraphStyle(
        name="H1x",
        parent=base["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=DARK,
        spaceBefore=12,
        spaceAfter=8,
    ))
    base.add(ParagraphStyle(
        name="H2x",
        parent=base["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12.8,
        leading=16,
        textColor=BLUE,
        spaceBefore=10,
        spaceAfter=5,
    ))
    base.add(ParagraphStyle(
        name="Bodyx",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=9.2,
        leading=12.4,
        textColor=colors.HexColor("#202631"),
        spaceAfter=5,
    ))
    base.add(ParagraphStyle(
        name="Smallx",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=MUTED,
        spaceAfter=4,
    ))
    base.add(ParagraphStyle(
        name="Prod",
        parent=base["BodyText"],
        fontName="Courier-Bold",
        fontSize=8.6,
        leading=11,
        textColor=RED,
        leftIndent=4,
        rightIndent=4,
        spaceAfter=4,
    ))
    base.add(ParagraphStyle(
        name="SemTitle",
        parent=base["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=12,
        textColor=colors.black,
        spaceAfter=4,
    ))
    base.add(ParagraphStyle(
        name="SemBody",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=8.4,
        leading=10.5,
        textColor=colors.black,
        leftIndent=0,
        spaceAfter=2,
    ))
    base.add(ParagraphStyle(
        name="CodexBlock",
        parent=base["Code"],
        fontName="Courier",
        fontSize=7.8,
        leading=9.6,
        textColor=colors.HexColor("#111827"),
    ))
    return base


S = make_styles()


def p(text: str, style: str = "Bodyx") -> Paragraph:
    return Paragraph(text, S[style])


def xml(text: str) -> str:
    return escape(text, quote=False)


def bullet(items: list[str]) -> ListFlowable:
    return ListFlowable(
        [ListItem(p(item, "Bodyx"), leftIndent=12) for item in items],
        bulletType="bullet",
        start="circle",
        leftIndent=16,
        bulletFontSize=7,
        bulletOffsetY=1,
    )


def code(text: str) -> Table:
    block = Preformatted(text, S["CodexBlock"])
    t = Table([[block]], colWidths=[6.72 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
        ("BOX", (0, 0), (-1, -1), 0.45, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def sem_box(title: str, attrs: str, domain: str, action: str) -> Table:
    content = [
        p(title, "SemTitle"),
        p(f"<b>Atributos:</b> {xml(attrs)}", "SemBody"),
        p(f"<b>Dominio / restriccion:</b> {xml(domain)}", "SemBody"),
        p(f"<b>Accion de validacion:</b> {xml(action)}", "SemBody"),
    ]
    t = Table([[content]], colWidths=[6.72 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), AMBER),
        ("BOX", (0, 0), (-1, -1), 0.65, AMBER_LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


def prod(text: str) -> Table:
    production = "<br/>".join(xml(line) for line in text.splitlines())
    t = Table([[p(production, "Prod")]], colWidths=[6.72 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF8F8")),
        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#F1B3B3")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(DARK)
    canvas.setFont("Helvetica-Bold", 8.5)
    canvas.drawString(MARGIN_X, PAGE_H - 0.42 * inch, "Compiladores - Quiz 4 / Entrega 4")
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 0.42 * inch, "Claudio - Analisis semantico")
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN_X, PAGE_H - 0.50 * inch, PAGE_W - MARGIN_X, PAGE_H - 0.50 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawCentredString(PAGE_W / 2, 0.34 * inch, str(doc.page))
    canvas.restoreState()


def cover_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(DARK)
    canvas.rect(0, PAGE_H - 0.42 * inch, PAGE_W, 0.42 * inch, stroke=0, fill=1)
    canvas.setFillColor(RED)
    canvas.rect(0, PAGE_H - 0.48 * inch, PAGE_W, 0.06 * inch, stroke=0, fill=1)
    canvas.restoreState()


def summary_table() -> Table:
    data = [[
        p("<b>ID</b>", "Smallx"),
        p("<b>Regla</b>", "Smallx"),
        p("<b>Nodo gramatical</b>", "Smallx"),
        p("<b>Atributos principales</b>", "Smallx"),
        p("<b>Dominio</b>", "Smallx"),
    ]]
    rows = [
        ("SEM-1", "Declaracion duplicada", "decl_variable, def_funcion, parametros, clases",
         "ID.nombre sintetizado; ambitoActual heredado", "nombre no existe en el ambito actual"),
        ("SEM-2", "Identificador no declarado", "sent_id, expresiones, imprimir, llamadas",
         "ID.nombre sintetizado; ID.tipo sintetizado desde tabla", "nombre existe en algun ambito activo"),
        ("SEM-3", "Constante reasignada", "sent_id -> ID = expresion",
         "ID.inmutable heredado desde tabla", "inmutable == false para poder asignar"),
        ("SEM-4", "Tipo en declaracion", "decl_variable",
         "decl.tipo sintetizado; expr.tipo sintetizado", "tipos iguales o entero -> real"),
        ("SEM-5", "Tipo en asignacion", "sent_id -> ID = expresion",
         "ID.tipo heredado; expr.tipo sintetizado", "valor compatible con tipo declarado"),
        ("SEM-6", "Condicion booleana", "sent_si, sent_mientras",
         "cond.tipo sintetizado", "cond.tipo == booleano"),
        ("SEM-7", "Limites numericos", "sent_para, paso_opt",
         "desde.tipo, hasta.tipo, paso.tipo sintetizados", "cada tipo en {entero, real}"),
    ]
    for row in rows:
        data.append([p(cell, "Smallx") for cell in row])

    t = Table(data, colWidths=[0.55 * inch, 1.14 * inch, 1.40 * inch, 1.78 * inch, 1.85 * inch], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def implementation_table() -> Table:
    rows = [
        ("backend/semantico.py", "AnalizadorSemantico, TablaSimbolos, SemanticDiagnostic y reglas SEM-1 a SEM-7."),
        ("backend/main.py", "Endpoint POST /api/semantico y endpoint POST /api/sugerencias-ia-semantico."),
        ("backend/ai_suggestions.py", "Integracion OpenAI para explicar diagnosticos semanticos ya detectados."),
        ("frontend/src/app/page.tsx", "Modo semantico, ejecucion del endpoint y conexion con sugerencias IA."),
        ("frontend/src/components/errors-view.tsx", "Vista de errores semanticos con regla, fila, columna, lexema y sugerencia."),
        ("frontend/src/components/symbol-table-view.tsx", "Tabla de simbolos visible: nombre, tipo, inmutable, ambito, fila y columna."),
        ("backend/test_quiz4_semantico.py", "Pruebas unitarias del caso integral, caso valido, endpoint y fallback OpenAI."),
    ]
    data = [[p("<b>Archivo</b>", "Smallx"), p("<b>Responsabilidad</b>", "Smallx")]]
    for r in rows:
        data.append([p(r[0], "Smallx"), p(r[1], "Smallx")])
    t = Table(data, colWidths=[2.35 * inch, 4.37 * inch], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def compliance_table() -> Table:
    rows = [
        ("PDF con gramatica ampliada", "Se presentan producciones originales en rojo y reglas semanticas agregadas en fondo ambar."),
        ("Minimo cinco reglas semanticas", "Se especifican siete reglas: SEM-1 a SEM-7."),
        ("Atributos y dominios", "Cada regla identifica atributos sintetizados/heredados y la restriccion que debe satisfacerse."),
        ("Acciones de validacion", "Cada regla describe consulta a tabla, comparacion de tipos, reporte de error y continuacion del analisis."),
        ("Implementacion en compilador", "Se documentan los archivos donde se implementan analizador, tabla, diagnosticos, endpoints y UI."),
        ("Bonus IA", "Se describe OpenAI como capa adicional de explicacion sin reemplazar las reglas clasicas."),
    ]
    data = [[p("<b>Requisito del enunciado</b>", "Smallx"), p("<b>Cumplimiento en Claudio</b>", "Smallx")]]
    for row in rows:
        data.append([p(row[0], "Smallx"), p(row[1], "Smallx")])
    t = Table(data, colWidths=[2.10 * inch, 4.62 * inch], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def build_story():
    story = []
    story.extend([
        Spacer(1, 0.70 * inch),
        p("UNIVERSIDAD CATOLICA DE ORIENTE", "CoverSub"),
        p("Facultad de Ingenieria - Compiladores", "CoverSub"),
        Spacer(1, 0.42 * inch),
        p("Claudio - Gramatica ampliada con reglas semanticas", "CoverTitle"),
        p("Quiz 4 / Entrega 4", "CoverSub"),
        Spacer(1, 0.16 * inch),
        p("Lenguaje fuente: Claudio (palabras clave en espanol) &nbsp;&nbsp;|&nbsp;&nbsp; Lenguaje destino: Swift", "CoverSub"),
        Spacer(1, 0.46 * inch),
        Table([[p("<b>Entregable PDF:</b> producciones sintacticas originales en rojo y reglas semanticas en fondo ambar, segun el enunciado.", "Bodyx")]], colWidths=[5.9 * inch], style=[
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
            ("BOX", (0, 0), (-1, -1), 0.6, LINE),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]),
        Spacer(1, 1.00 * inch),
        p("Presentado por: Juan David Cardenas Jimenez, Maria Jose Restrepo Ramirez, Jose Manuel Zuluaga F.", "CoverSub"),
        p("Semestre 1-2026", "CoverSub"),
        PageBreak(),
    ])

    story.extend([
        p("1. Alcance del entregable", "H1x"),
        p("Este documento presenta la version ampliada de la gramatica usada por Claudio para el Quiz 4. La ampliacion conserva las producciones sintacticas del lenguaje, pero incorpora reglas semanticas que verifican propiedades que la gramatica por si sola no puede garantizar: declaracion de identificadores, compatibilidad de tipos, manejo de constantes, validez de condiciones y dominios numericos en ciclos.", "Bodyx"),
        p("La fase semantica se ejecuta despues del parser. Por tanto, el analizador no decide si la cadena tiene forma valida; esa responsabilidad sigue siendo sintactica. Su tarea es recorrer el AST y comprobar si el programa construido tiene significado correcto dentro del lenguaje Claudio.", "Bodyx"),
        p("Convencion visual exigida", "H2x"),
        bullet([
            "<font color='#B42318'><b>Rojo:</b></font> produccion sintactica original de la gramatica.",
            "<b>Fondo ambar:</b> regla semantica agregada con atributos, dominio y accion.",
            "Las reglas se implementaron como fase independiente sobre el AST: el parser construye el arbol y el analizador semantico lo recorre.",
        ]),
        p("Cumplimiento del enunciado", "H2x"),
        compliance_table(),
        p("2. Resumen de reglas semanticas", "H1x"),
        summary_table(),
        p("Todas las reglas reportan diagnosticos con fila, columna, lexema, regla SEM-N, mensaje descriptivo y sugerencia. El analisis continua tras cada error para acumular diagnosticos restantes y entregar una retroalimentacion completa al usuario.", "Bodyx"),
    ])

    grammar_sections = [
        (
            "3.1 Declaracion de variables",
            "<decl_variable> -> (var | sea) <tipo> ID = <expresion>",
            [
                sem_box(
                    "SEM-1 - Declaracion duplicada en el mismo ambito",
                    "ID.nombre es sintetizado desde el token ID; ambitoActual es heredado desde la pila de ambitos.",
                    "ID.nombre no debe existir en tablaSimbolos[ambitoActual].",
                    "Consultar la tabla del ambito actual. Si el nombre ya existe, reportar error con fila, columna, lexema y ubicacion de la primera declaracion. El analizador no se detiene."
                ),
                sem_box(
                    "SEM-4 - Tipo compatible en la inicializacion",
                    "decl.tipo es sintetizado desde <tipo>; expr.tipo es sintetizado por inferencia sobre <expresion>.",
                    "decl.tipo == expr.tipo, o decl.tipo == real y expr.tipo == entero como conversion de ampliacion.",
                    "Inferir el tipo de la expresion, comparar contra el tipo declarado, reportar tipo esperado y tipo encontrado si no son compatibles, y registrar el simbolo para permitir recuperacion."
                ),
            ],
        ),
        (
            "3.2 Sentencia iniciada por identificador",
            "<sent_id> -> ID = <expresion> | ID ( <argumentos> ) | ID . ID <sufijo_id>",
            [
                sem_box(
                    "SEM-2 - Uso de identificador previamente declarado",
                    "ID.nombre es sintetizado desde el token; ID.tipo se sintetiza desde la entrada encontrada en tabla.",
                    "ID.nombre debe existir en algun ambito activo.",
                    "Buscar desde el ambito mas interno hacia el global. Si no existe, reportar fila, columna, lexema y sugerir declaracion previa."
                ),
                sem_box(
                    "SEM-3 - Las constantes declaradas con sea no se reasignan",
                    "ID.inmutable es heredado desde la entrada de tabla; ID.nombre es sintetizado.",
                    "Si la produccion es asignacion, ID.inmutable debe ser false.",
                    "Leer el atributo inmutable. Si fue declarado con sea, reportar error y continuar analizando la expresion asignada."
                ),
                sem_box(
                    "SEM-5 - Tipo compatible en asignacion posterior",
                    "ID.tipo es heredado desde la tabla de simbolos; expr.tipo es sintetizado por inferencia.",
                    "El tipo de la expresion debe ser compatible con el tipo declarado del identificador.",
                    "Inferir expr.tipo, comparar con ID.tipo, reportar tipo esperado y tipo encontrado si falla."
                ),
            ],
        ),
        (
            "3.3 Condicional y ciclo mientras",
            "<sent_si> -> si <expresion> entonces <bloque> <rama_sino> fin_si\n<sent_mientras> -> mientras <expresion> hacer <bloque> fin_mientras",
            [
                sem_box(
                    "SEM-6 - La condicion debe ser booleana",
                    "cond.tipo es sintetizado por inferencia sobre la expresion de condicion.",
                    "cond.tipo debe pertenecer al conjunto {booleano}.",
                    "Si la condicion se infiere como entero, real o cadena, reportar error en el token si o mientras y visitar el bloque para conservar recuperacion."
                ),
            ],
        ),
        (
            "3.4 Ciclo para",
            "<sent_para> -> para ID desde <expresion> hasta <expresion> <paso_opt> hacer <bloque> fin_para\n<paso_opt> -> paso <expresion> | epsilon",
            [
                sem_box(
                    "SEM-7 - Limites y paso numericos",
                    "desde.tipo, hasta.tipo y paso.tipo son atributos sintetizados desde sus expresiones.",
                    "Cada tipo debe pertenecer a {entero, real}. Si paso_opt es epsilon no se valida paso.",
                    "Declarar la variable de ciclo como entero en un ambito local, validar desde/hasta/paso y reportar cada violacion sin detener el recorrido."
                ),
            ],
        ),
        (
            "3.5 Funciones, parametros y ambitos",
            "<def_funcion> -> funcion <tipo_retorno> ID ( <parametros> ) hacer <bloque> fin_funcion\n<parametro> -> <tipo> ID",
            [
                sem_box(
                    "SEM-1 aplicada a funciones y parametros",
                    "ID.nombre es sintetizado; ambitoActual es heredado. En parametros tambien se sintetiza parametro.tipo.",
                    "Una funcion no debe duplicarse en el ambito donde se declara; un parametro no debe duplicarse dentro de la misma firma/ambito.",
                    "Registrar la funcion como simbolo de tipo funcion; entrar a un nuevo ambito para parametros y cuerpo; reportar duplicados con SEM-1."
                ),
            ],
        ),
    ]

    story.append(p("3. Gramatica ampliada", "H1x"))
    for heading, production, boxes in grammar_sections:
        story.append(p(heading, "H2x"))
        story.append(prod(production))
        for b in boxes:
            story.append(b)
            story.append(Spacer(1, 4))

    story.extend([
        p("4. Tabla de simbolos", "H1x"),
        p("La tabla de simbolos almacena los atributos requeridos por las reglas semanticas y se implementa con una pila de ambitos. Cada ambito es un diccionario de nombres a entradas de simbolo.", "Bodyx"),
        Table([
            [p("<b>Atributo</b>", "Smallx"), p("<b>Uso semantico</b>", "Smallx")],
            [p("nombre", "Smallx"), p("Deteccion de duplicados y busqueda de identificadores.", "Smallx")],
            [p("tipo", "Smallx"), p("Comparacion de tipos en declaracion, asignacion, condicion y ciclos.", "Smallx")],
            [p("inmutable", "Smallx"), p("Validacion de constantes declaradas con sea.", "Smallx")],
            [p("inicializado", "Smallx"), p("Estado disponible para reglas futuras y trazabilidad.", "Smallx")],
            [p("ambito", "Smallx"), p("Resolucion de nombres desde el ambito interno al global.", "Smallx")],
            [p("fila, columna", "Smallx"), p("Reporte exacto del diagnostico al usuario.", "Smallx")],
        ], colWidths=[1.30 * inch, 5.42 * inch], style=[
            ("BACKGROUND", (0, 0), (-1, 0), DARK),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.35, LINE),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]),
        p("5. Implementacion en el compilador", "H1x"),
        p("La implementacion separa fases: el parser descendente recursivo construye el AST y el analizador semantico realiza una pasada posterior. Esta arquitectura cumple el requisito de separacion entre analisis sintactico y semantico.", "Bodyx"),
        implementation_table(),
        p("Flujo de ejecucion", "H2x"),
        bullet([
            "El usuario envia codigo a POST /api/semantico.",
            "El backend ejecuta analisis lexico y sintactico. Si existe AST, invoca AnalizadorSemantico.",
            "El analizador recorre nodos de declaracion, asignacion, condiciones, ciclos, funciones y expresiones.",
            "Cada error se agrega como SemanticDiagnostic; no se lanza una excepcion que detenga el analisis.",
            "La respuesta incluye valido, errores_semanticos, total_errores_semanticos y tabla_simbolos.",
        ]),
        p("6. Bonus opcional: integracion OpenAI", "H1x"),
        p("Se implementa la modalidad A del enunciado: IA como capa adicional de explicacion. Las reglas clasicas SEM-1 a SEM-7 siguen siendo la fuente de verdad; OpenAI no reemplaza el analisis por atributos.", "Bodyx"),
        bullet([
            "Entrada al modelo: codigo fuente y diagnosticos semanticos ya detectados.",
            "Salida esperada: explicacion para el usuario, causa probable, correccion sugerida, mini ejemplo y nivel de confianza.",
            "Endpoint: POST /api/sugerencias-ia-semantico.",
            "Configuracion: OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TIMEOUT_SECONDS y OPENAI_MAX_ERRORS.",
            "Fallback: si no hay clave, el compilador sigue funcionando y retorna estado no_disponible junto con la sugerencia deterministica.",
        ]),
        p("Ejemplo de error enriquecido por IA", "H2x"),
        code('var entero x = "hola"'),
        p("Diagnostico clasico: SEM-4, tipo incompatible en declaracion: x fue declarado como entero pero el valor asignado es cadena. La capa OpenAI puede explicar que debe cambiarse el literal a un entero o ajustar el tipo declarado a cadena.", "Bodyx"),
        p("7. Casos de validacion", "H1x"),
        p("Caso integral con recuperacion", "H2x"),
        code('''var entero x = "hola"
var entero x = 2
x = "texto"
sea entero c = 1
c = 2
imprimir(fantasma)
si x entonces
    imprimir(x)
fin_si
para i desde "a" hasta 10 paso falso hacer
    imprimir(i)
fin_para'''),
        bullet([
            "SEM-1: x duplicado en el mismo ambito.",
            "SEM-2: fantasma no declarado.",
            "SEM-3: c fue declarado con sea y se reasigna.",
            "SEM-4: x declarado entero con valor cadena.",
            "SEM-5: x recibe cadena en asignacion posterior.",
            "SEM-6: condicion si x no es booleana.",
            "SEM-7: desde/paso no numericos en para.",
        ]),
        p("Caso valido", "H2x"),
        code('''funcion entero suma(entero a, entero b) hacer
    var entero resultado = a + b
    retornar resultado
fin_funcion

var entero total = 10
total = 20
si total > 0 entonces
    imprimir(total)
fin_si'''),
        p("Resultado esperado: sin errores semanticos y tabla con suma, a, b, resultado y total.", "Bodyx"),
        p("8. Evidencia de validacion", "H1x"),
        p("La validacion se planteo sobre tres frentes: comportamiento del analizador, respuesta de la interfaz y consistencia entre la gramatica documentada y las reglas implementadas.", "Bodyx"),
        bullet([
            "Caso integral: un mismo programa activa SEM-1 a SEM-7 y demuestra recuperacion semantica.",
            "Caso valido: un programa con funcion, parametros, asignacion compatible y condicion booleana no produce errores semanticos.",
            "Tabla de simbolos: la UI muestra nombre, tipo, inmutabilidad, ambito, fila y columna de cada entrada registrada.",
            "API semantica: el backend retorna bandera de validez, lista de diagnosticos y tabla de simbolos estructurada.",
            "IA: cuando OpenAI esta configurado, los diagnosticos clasicos se enriquecen con una explicacion pedagogica y una correccion sugerida.",
        ]),
        p("La prueba puntual de <b>var entero x = \"hola\"</b> debe producir SEM-4, porque el tipo declarado es entero y el literal asignado es cadena. Este caso evidencia que el analizador compara tipos, no solo tokens o estructura sintactica.", "Bodyx"),
        p("9. Conclusiones", "H1x"),
        p("La ampliacion semantica convierte a Claudio en un compilador mas completo: ya no se limita a aceptar programas bien formados, sino que tambien valida que los nombres, tipos, constantes, condiciones y ciclos tengan coherencia dentro del lenguaje. Esta diferencia es central en teoria de compiladores, porque separa claramente la forma del programa de su significado.", "Bodyx"),
        p("La tabla de simbolos es el componente que conecta la gramatica con el comportamiento real del compilador. Al almacenar tipo, ambito, inmutabilidad y ubicacion fuente, permite detectar errores que no son visibles desde la sintaxis, como usar una variable no declarada, duplicar nombres en el mismo ambito o reasignar una constante.", "Bodyx"),
        p("El modo de recuperacion mejora la experiencia de uso del compilador: en lugar de detenerse ante el primer fallo, Claudio acumula diagnosticos y entrega una vision mas completa de los problemas del programa. Esto hace que el analizador sea mas util para depuracion, demostracion en clase y validacion automatizada.", "Bodyx"),
        p("La integracion con OpenAI se mantiene como complemento, no como reemplazo de las reglas formales. Las reglas SEM-1 a SEM-7 siguen siendo deterministas y verificables; la IA agrega una capa de explicacion en lenguaje natural que ayuda al usuario a entender la causa del error y una posible correccion.", "Bodyx"),
        bullet([
            "Se documentan siete reglas semanticas, superando el minimo solicitado.",
            "Cada regla incluye atributos, dominio y accion de validacion.",
            "La implementacion respeta la separacion de fases: parser primero, analizador semantico despues.",
            "Los diagnosticos incluyen regla, fila, columna, lexema, mensaje y sugerencia.",
            "El bonus de OpenAI queda integrado como asistencia explicativa sobre errores ya detectados.",
        ]),
    ])
    return story


def build_pdf(output: Path):
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(output),
        pagesize=letter,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title="Claudio - Quiz 4 - Gramatica ampliada con reglas semanticas",
        author="Juan David Cardenas Jimenez, Maria Jose Restrepo Ramirez, Jose Manuel Zuluaga F.",
    )
    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        id="normal",
        leftPadding=0,
        bottomPadding=0,
        rightPadding=0,
        topPadding=0,
    )
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[frame], onPage=cover_footer),
        PageTemplate(id="body", frames=[frame], onPage=header_footer),
    ])
    story = build_story()
    doc.build(story)


if __name__ == "__main__":
    build_pdf(OUT_REPO)
    build_pdf(OUT_DOWNLOADS)
    build_pdf(OUT_DOWNLOADS_MAIN)
    print(OUT_REPO)
    print(OUT_DOWNLOADS)
    print(OUT_DOWNLOADS_MAIN)
