from __future__ import annotations

from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
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
OUT_REPO = ROOT / "docs" / "final" / "entrega_final_claudio_swift.pdf"
OUT_DOWNLOADS = Path("/Users/juancarj/Downloads/Entrega Final Claudio.pdf")
EVIDENCE_DIR = ROOT / "docs" / "final" / "evidencias_ui"

PAGE_W, PAGE_H = letter
MARGIN_X = 0.68 * inch
MARGIN_TOP = 0.72 * inch
MARGIN_BOTTOM = 0.58 * inch
CONTENT_W = PAGE_W - (MARGIN_X * 2)

RED = colors.HexColor("#B42318")
RED_BG = colors.HexColor("#FFF4F2")
AMBER = colors.HexColor("#FFF3CD")
AMBER_LINE = colors.HexColor("#D59E00")
BLUE = colors.HexColor("#0F4C81")
BLUE_BG = colors.HexColor("#EEF6FF")
DARK = colors.HexColor("#172033")
MUTED = colors.HexColor("#5B6472")
GREEN = colors.HexColor("#146C43")
LIGHT = colors.HexColor("#F3F6FA")
LINE = colors.HexColor("#CBD5E1")
CODE_BG = colors.HexColor("#F7F7F7")


def make_styles():
    base = getSampleStyleSheet()
    base.add(ParagraphStyle(
        name="CoverTitle",
        parent=base["Title"],
        fontName="Helvetica-Bold",
        fontSize=25,
        leading=30,
        alignment=TA_CENTER,
        textColor=DARK,
        spaceAfter=14,
    ))
    base.add(ParagraphStyle(
        name="CoverSub",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        alignment=TA_CENTER,
        textColor=MUTED,
        spaceAfter=7,
    ))
    base.add(ParagraphStyle(
        name="H1x",
        parent=base["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15.2,
        leading=19,
        textColor=DARK,
        spaceBefore=10,
        spaceAfter=7,
    ))
    base.add(ParagraphStyle(
        name="H2x",
        parent=base["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12.2,
        leading=15,
        textColor=BLUE,
        spaceBefore=8,
        spaceAfter=5,
    ))
    base.add(ParagraphStyle(
        name="Bodyx",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=8.9,
        leading=11.7,
        textColor=colors.HexColor("#202631"),
        spaceAfter=4,
    ))
    base.add(ParagraphStyle(
        name="Smallx",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=7.7,
        leading=9.8,
        textColor=MUTED,
        spaceAfter=3,
    ))
    base.add(ParagraphStyle(
        name="Prod",
        parent=base["BodyText"],
        fontName="Courier-Bold",
        fontSize=7.7,
        leading=9.5,
        textColor=RED,
        spaceAfter=2,
    ))
    base.add(ParagraphStyle(
        name="BoxTitle",
        parent=base["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=8.8,
        leading=11,
        textColor=colors.black,
        spaceAfter=3,
    ))
    base.add(ParagraphStyle(
        name="BoxBody",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=7.75,
        leading=9.6,
        textColor=colors.black,
        spaceAfter=2,
    ))
    base.add(ParagraphStyle(
        name="CodeSmall",
        parent=base["Code"],
        fontName="Courier",
        fontSize=7.35,
        leading=8.7,
        textColor=colors.HexColor("#111827"),
    ))
    return base


S = make_styles()


def xml(text: str) -> str:
    return escape(text, quote=False)


def p(text: str, style: str = "Bodyx") -> Paragraph:
    return Paragraph(text, S[style])


def bullet(items: list[str]) -> ListFlowable:
    return ListFlowable(
        [ListItem(p(item, "Bodyx"), leftIndent=12) for item in items],
        bulletType="bullet",
        leftIndent=14,
        bulletFontSize=6,
        bulletOffsetY=1,
    )


def prod(text: str) -> Table:
    rows = [[p("<br/>".join(xml(line) for line in text.splitlines()), "Prod")]]
    t = Table(rows, colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), RED_BG),
        ("BOX", (0, 0), (-1, -1), 0.45, colors.HexColor("#F1B3B3")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def semantic_box(title: str, attrs: str, domain: str, action: str) -> Table:
    return colored_box(title, [
        f"<b>Atributos:</b> {xml(attrs)}",
        f"<b>Dominio / restriccion:</b> {xml(domain)}",
        f"<b>Accion:</b> {xml(action)}",
    ], AMBER, AMBER_LINE)


def sdt_box(title: str, actions: list[str]) -> Table:
    return colored_box(title, [xml(action) for action in actions], BLUE_BG, BLUE)


def colored_box(title: str, lines: list[str], bg, border) -> Table:
    content = [p(title, "BoxTitle")]
    content.extend(p(line, "BoxBody") for line in lines)
    t = Table([[content]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.62, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def code(text: str) -> Table:
    t = Table([[Preformatted(text, S["CodeSmall"])]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
        ("BOX", (0, 0), (-1, -1), 0.45, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def screenshot(path: Path, caption: str) -> Table:
    img = Image(str(path))
    max_w = CONTENT_W
    max_h = 3.95 * inch
    scale = min(max_w / img.imageWidth, max_h / img.imageHeight)
    img.drawWidth = img.imageWidth * scale
    img.drawHeight = img.imageHeight * scale
    table = Table([[img], [p(caption, "Smallx")]], colWidths=[CONTENT_W])
    table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOX", (0, 0), (0, 0), 0.45, LINE),
        ("BACKGROUND", (0, 1), (0, 1), LIGHT),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def simple_table(rows: list[list[str]], widths: list[float] | None = None) -> Table:
    table_rows = [[p(xml(cell), "Smallx") for cell in row] for row in rows]
    col_widths = widths or [CONTENT_W / len(rows[0])] * len(rows[0])
    t = Table(table_rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN_X, 0.36 * inch, "Entrega Final - Compilador Claudio a Swift")
    canvas.drawRightString(PAGE_W - MARGIN_X, 0.36 * inch, f"Pagina {doc.page}")
    canvas.restoreState()


def story() -> list:
    flow = []
    flow.append(Spacer(1, 0.45 * inch))
    flow.append(p("Entrega Final: Compilador Claudio a Swift", "CoverTitle"))
    flow.append(p("Gramatica ampliada, reglas semanticas, SDT de traduccion, implementacion y pruebas", "CoverSub"))
    flow.append(p("Curso: Teoria de Compiladores", "CoverSub"))
    flow.append(p("Autores: Juan David Cardenas Jimenez, Maria Jose Restrepo Ramirez, Jose Zuluaga", "CoverSub"))
    flow.append(p("Junio de 2026", "CoverSub"))
    flow.append(Spacer(1, 0.25 * inch))
    flow.append(colored_box("Convencion visual exigida por el enunciado", [
        "Rojo: producciones originales de la gramatica.",
        "Amarillo: reglas semanticas del Quiz 4 con atributos, dominios y acciones.",
        "Azul: acciones SDT que sintetizan codigo Swift.",
    ], LIGHT, LINE))
    flow.append(PageBreak())

    flow.append(p("1. Alcance Del Compilador Final", "H1x"))
    flow.append(p("Este documento presenta el compilador Claudio como resultado final: un lenguaje fuente en espanol que se analiza en cuatro fases y produce codigo Swift como lenguaje destino. El punto central no es solo listar componentes, sino mostrar que la traduccion se obtiene despues de validar correctamente el programa fuente.", "Bodyx"))
    flow.append(p("La propiedad mas importante para la evaluacion es la siguiente: Claudio solo muestra codigo Swift cuando el programa pasa analisis lexico, sintactico y semantico. Si alguna fase falla, la interfaz explica el error y bloquea la salida destino.", "Bodyx"))
    flow.append(simple_table([
        ["Requisito del enunciado", "Evidencia en Claudio"],
        ["Lexico -> sintactico -> semantico -> SDT", "Endpoint /api/compilar encadena las fases y bloquea Swift si alguna falla."],
        ["Errores unificados", "Cada diagnostico final trae fase, fila, columna, lexema y mensaje."],
        ["Tabla de simbolos disponible durante SDT", "AnalizadorSemantico construye tabla de simbolos y /api/compilar la retorna junto con la salida."],
        ["Tres casos de prueba", "Disponibles y seleccionables desde la galeria de programas de la interfaz grafica."],
        ["Bonus IA", "OpenAI revisa la salida Swift generada y aporta una lectura complementaria sin reemplazar al compilador."],
    ], [2.2 * inch, CONTENT_W - 2.2 * inch]))
    flow.append(Spacer(1, 6))
    flow.append(p("Cadena de fases:", "H2x"))
    flow.append(code("Fuente Claudio\n  -> Lexer: tokens + errores lexicos\n  -> Parser RD: arbol + errores sintacticos\n  -> Analizador semantico: tabla de simbolos + SEM-1..SEM-7\n  -> SDT Swift: codigo destino + mapeo linea a linea\n  -> IA opcional: revision del Swift generado"))

    flow.append(p("2. Gramatica Base y SDT", "H1x"))
    flow.append(p("Las producciones estan escritas en forma BNF compacta. Los no terminales con repeticion usan recursividad derecha o epsilon; sus acciones SDT concatenan fragmentos Swift en orden de aparicion.", "Bodyx"))

    flow.append(p("2.1 Programa y declaraciones", "H2x"))
    flow.append(prod("""programa -> declaracion programa | ε
declaracion -> importacion | decl_variable | def_funcion | def_clase | sentencia
importacion -> importar ID"""))
    flow.append(sdt_box("SDT-PROG", [
        "programa.swift = declaracion.swift + \"\\n\" + programa1.swift.",
        "programa -> ε sintetiza cadena vacia; no altera la salida.",
        "importacion.swift = \"import \" + ID.lexema.",
    ]))

    flow.append(p("2.2 Variables y tipos", "H2x"))
    flow.append(prod("""decl_variable -> (var | sea) tipo ID = expresion
tipo -> entero | real | cadena | booleano | ID
tipo_basico -> entero | real | cadena | booleano"""))
    flow.append(semantic_box(
        "SEM-1 y SEM-4: declaracion de variable",
        "ID.nombre, tipo.declarado, expresion.tipo, ambito.actual, tabla_simbolos",
        "ID no debe existir en el ambito actual; expresion.tipo debe ser compatible con tipo.declarado. entero puede promoverse a real.",
        "Reportar duplicado o incompatibilidad; si no hay duplicado, registrar simbolo con tipo e inmutabilidad.",
    ))
    flow.append(sdt_box("SDT-VAR", [
        "Si el declarador es var: decl_variable.swift = \"var ID: TipoSwift = expr.swift\".",
        "Si el declarador es sea: decl_variable.swift = \"let ID: TipoSwift = expr.swift\".",
        "TipoSwift(entero, real, cadena, booleano) = Int, Double, String, Bool.",
    ]))

    flow.append(p("2.3 Funciones y parametros", "H2x"))
    flow.append(prod("""def_funcion -> funcion tipo_ret ID ( parametros ) hacer bloque fin_funcion
tipo_ret -> tipo_basico | ε
parametros -> param_lista | ε
param_lista -> tipo ID param_resto
param_resto -> , tipo ID param_resto | ε
sent_retornar -> retornar expresion"""))
    flow.append(semantic_box(
        "SEM-FUNC: ambito y parametros",
        "funcion.nombre, tipo_ret, parametros.lista, ambito.funcion",
        "El nombre de funcion no debe duplicarse en el ambito actual; cada parametro se declara en el ambito de la funcion.",
        "Registrar la funcion como simbolo, abrir ambito, registrar parametros, analizar bloque y cerrar ambito.",
    ))
    flow.append(sdt_box("SDT-FUNC", [
        "def_funcion.swift = \"func ID(params.swift) -> TipoRet {\\n\" + bloque.swift + \"\\n}\".",
        "Si tipo_ret es ε, se omite \"-> TipoRet\".",
        "param_lista.swift = \"_ ID: TipoSwift\" + param_resto.swift; param_resto epsilon sintetiza cadena vacia.",
        "sent_retornar.swift = \"return \" + expresion.swift.",
    ]))

    flow.append(p("2.4 Clases, atributos y metodos", "H2x"))
    flow.append(prod("""def_clase -> clase ID herencia_opt hacer cuerpo_clase fin_clase
herencia_opt -> hereda ID | ε
cuerpo_clase -> miembro_clase cuerpo_clase | ε
miembro_clase -> def_atributo | def_metodo
def_atributo -> atributo tipo ID
def_metodo -> metodo ID ( parametros ) hacer bloque fin_funcion"""))
    flow.append(semantic_box(
        "SEM-CLASE: nombres de clase, atributos y metodos",
        "clase.nombre, atributo.nombre, metodo.nombre, ambito.clase",
        "Cada nombre declarado dentro de la clase debe ser unico en el ambito de clase.",
        "Registrar clase, abrir ambito de clase, registrar atributos/metodos y analizar cuerpos de metodo.",
    ))
    flow.append(sdt_box("SDT-CLASS", [
        "def_clase.swift = \"class ID[: Super] {\\n\" + cuerpo.swift + \"\\n}\".",
        "def_atributo.swift = \"var ID: TipoSwift = default(TipoSwift)\" para evitar propiedades almacenadas sin valor inicial.",
        "default(Int, Double, String, Bool) = 0, 0.0, \"\", false.",
        "def_metodo.swift = \"func ID(params.swift) {\\n\" + bloque.swift + \"\\n}\".",
    ]))

    flow.append(PageBreak())
    flow.append(p("2.5 Bloques y sentencias", "H2x"))
    flow.append(prod("""bloque -> sentencia bloque'       bloque' -> sentencia bloque' | ε
sentencia -> sent_id | sent_si | sent_para | sent_mientras
           | sent_retornar | sent_imprimir | sent_romper | sent_continuar | decl_variable
sent_id -> (ID | este) resto_id
resto_id -> = expresion | . ID resto_id | ( argumentos ) | ε
argumentos -> arg_lista | ε
arg_lista -> expresion arg_resto
arg_resto -> , expresion arg_resto | ε"""))
    flow.append(semantic_box(
        "SEM-2, SEM-3 y SEM-5: uso y asignacion",
        "ID.nombre, ID.tipo, ID.inmutable, expresion.tipo, tabla_simbolos",
        "El identificador debe existir; una constante declarada con sea no puede reasignarse; el tipo asignado debe ser compatible.",
        "Reportar identificador no declarado, reasignacion de constante o incompatibilidad de tipo.",
    ))
    flow.append(sdt_box("SDT-STMT", [
        "sent_id asignacion: \"lhs.swift = expresion.swift\"; este.campo se traduce a self.campo.",
        "sent_id llamada: \"ID(args.swift)\"; acceso por punto conserva el receptor y traduce este a self.",
        "argumentos y restos con epsilon sintetizan cadena vacia; las repeticiones agregan coma y expresion.swift.",
        "sent_imprimir.swift = \"print(\" + expresion.swift + \")\"; romper/continuar -> break/continue.",
    ]))

    flow.append(p("2.6 Condicionales y ciclos", "H2x"))
    flow.append(prod("""sent_si -> si expresion entonces bloque rama_sino fin_si
rama_sino -> sino bloque | ε
sent_para -> para ID desde expresion hasta expresion paso_opt hacer bloque fin_para
paso_opt -> paso expresion | ε
sent_mientras -> mientras expresion hacer bloque fin_mientras"""))
    flow.append(semantic_box(
        "SEM-6 y SEM-7: condiciones y limites",
        "condicion.tipo, desde.tipo, hasta.tipo, paso.tipo",
        "La condicion de si/mientras debe ser booleana; desde, hasta y paso de para deben ser enteros o reales.",
        "Reportar condicion no booleana o limites/paso no numericos. La variable de para se declara como entero en su ambito.",
    ))
    flow.append(sdt_box("SDT-CONTROL", [
        "sent_si.swift = \"if cond.swift {\\n\" + bloque.swift + \"\\n}\" + rama_sino.swift.",
        "rama_sino epsilon sintetiza cadena vacia; rama_sino con sino sintetiza \" else {\\n bloque.swift \\n}\".",
        "sent_para.swift = \"for ID in stride(from: desde.swift, through: hasta.swift, by: paso.swift) {\\n bloque.swift \\n}\".",
        "paso_opt epsilon sintetiza 1; sent_mientras.swift = \"while cond.swift {\\n bloque.swift \\n}\".",
    ]))

    flow.append(p("2.7 Expresiones", "H2x"))
    flow.append(prod("""expresion -> expr_or
expr_or -> expr_and expr_or'             expr_or' -> o expr_and expr_or' | ε
expr_and -> expr_rel expr_and'           expr_and' -> y expr_rel expr_and' | ε
expr_rel -> expr_add expr_rel'           expr_rel' -> op_rel expr_add | ε
expr_add -> expr_mul expr_add'           expr_add' -> + expr_mul expr_add' | - expr_mul expr_add' | ε
expr_mul -> expr_pot expr_mul'           expr_mul' -> * expr_pot expr_mul' | / expr_pot expr_mul' | % expr_pot expr_mul' | ε
expr_pot -> expr_unaria expr_pot'        expr_pot' -> ** expr_unaria expr_pot' | ε
expr_unaria -> no expr_unaria | - expr_unaria | expr_primaria
expr_primaria -> literal | verdadero | falso | nulo | nuevo ID(argumentos) | este sufijo_id | ID sufijo_id | ( expresion )
sufijo_id -> ( argumentos ) | . ID sufijo_id | ε"""))
    flow.append(sdt_box("SDT-EXPR", [
        "Operadores aritmeticos y relacionales conservan su simbolo Swift: +, -, *, /, %, ==, !=, <, >, <=, >=.",
        "y -> &&, o -> ||, no -> !. verdadero/falso/nulo -> true/false/nil.",
        "nuevo ID(args) -> ID(args). este.sufijo -> self.sufijo.",
        "a ** b -> pow(Double(a), Double(b)); los nodos epsilon de expresion sintetizan cadena vacia.",
    ]))

    flow.append(PageBreak())
    flow.append(p("3. Reglas Semanticas Implementadas", "H1x"))
    flow.append(simple_table([
        ["Regla", "Logica tecnica", "Como se aplica"],
        ["SEM-1", "Evita nombres repetidos dentro del mismo ambito.", "Antes de registrar una variable, funcion, clase, atributo o parametro, se consulta el ambito actual de la tabla de simbolos."],
        ["SEM-2", "Impide usar identificadores inexistentes.", "Cada aparicion de un identificador en expresiones, llamadas o asignaciones se resuelve contra la pila de ambitos."],
        ["SEM-3", "Protege constantes declaradas con sea.", "La tabla conserva si el simbolo es inmutable; una asignacion posterior a ese nombre se reporta como error."],
        ["SEM-4", "Valida que el valor inicial coincida con el tipo declarado.", "Se infiere el tipo de la expresion y se compara con el tipo de la declaracion, permitiendo entero hacia real."],
        ["SEM-5", "Valida asignaciones posteriores.", "El tipo almacenado en la tabla se contrasta con el tipo inferido de la nueva expresion asignada."],
        ["SEM-6", "Exige condiciones booleanas.", "Las expresiones de si y mientras deben inferirse como booleano; un entero, cadena o real no sirve como condicion."],
        ["SEM-7", "Exige limites numericos en para.", "desde, hasta y paso se infieren y deben pertenecer al dominio numerico: entero o real."],
    ], [0.75 * inch, 3.1 * inch, CONTENT_W - 3.85 * inch]))
    flow.append(Spacer(1, 6))
    flow.append(p("La tabla de simbolos almacena nombre, tipo, inmutabilidad, estado de inicializacion, ambito, fila y columna. La inferencia de tipos es conservadora: si una expresion no se puede determinar con certeza, se evita un falso positivo semantico.", "Bodyx"))

    flow.append(p("4. Como Se Materializa En Claudio", "H1x"))
    flow.append(p("La solucion se implemento como una cadena de fases conectadas. Cada fase recibe el resultado de la anterior, agrega informacion propia y decide si el proceso puede continuar. Por eso la salida Swift no aparece como una conversion directa de texto, sino como el ultimo paso de una validacion completa del programa fuente.", "Bodyx"))
    flow.append(p("En la interfaz, esta logica se observa de forma progresiva: primero se reconocen tokens, luego se construye el arbol sintactico, despues se valida la tabla de simbolos y finalmente se muestra el codigo Swift solo si no existen errores pendientes.", "Bodyx"))
    flow.append(simple_table([
        ["Fase", "Entrada", "Proceso tecnico", "Salida"],
        ["Lexica", "Texto Claudio", "Recorre caracteres, clasifica lexemas y conserva fila/columna.", "Tokens, errores lexicos y simbolos lexicos."],
        ["Sintactica", "Tokens validos", "Aplica la gramatica descendente recursiva, construye AST y recupera errores cuando es posible.", "Arbol de derivacion, diagnosticos sintacticos y estado valido/invalido."],
        ["Semantica", "AST", "Recorre el arbol con tabla de simbolos por ambitos e inferencia conservadora de tipos.", "Errores SEM-1..SEM-7 y tabla de simbolos."],
        ["SDT Swift", "Programa semanticamente valido", "Aplica acciones de traduccion asociadas a producciones: tipos, bloques, condiciones, ciclos, funciones y expresiones.", "Codigo Swift y mapeo Claudio->Swift."],
        ["IA opcional", "Swift generado", "OpenAI revisa la salida destino sin reemplazar las decisiones deterministicas del compilador.", "Resumen de validacion y sugerencias si aplica."],
    ], [0.95 * inch, 1.15 * inch, 3.05 * inch, CONTENT_W - 5.15 * inch]))
    flow.append(Spacer(1, 6))
    flow.append(p("Compuerta de generacion Swift", "H2x"))
    flow.append(simple_table([
        ["Situacion", "Comportamiento implementado"],
        ["Hay error lexico", "Se reporta la fase lexica con posicion y lexema; no se ejecuta la traduccion a Swift."],
        ["Hay error sintactico", "Se reporta el token encontrado y el fragmento esperado por la gramatica; no se genera codigo destino."],
        ["Hay error semantico", "Se reporta la regla SEM correspondiente y la tabla de simbolos parcial; Swift queda bloqueado."],
        ["No hay errores", "Se sintetiza Swift, se muestra el mapeo fuente-destino y se activa la validacion IA opcional."],
    ], [2.0 * inch, CONTENT_W - 2.0 * inch]))

    flow.append(p("5. Pruebas Desde La Interfaz Grafica", "H1x"))
    flow.append(p("Los tres casos exigidos se demuestran desde la UI de Claudio, usando el selector de programas de ejemplo y el metodo Semantico. Esto permite al evaluador observar el comportamiento real del compilador sin ejecutar comandos.", "Bodyx"))
    flow.append(simple_table([
        ["Caso en la UI", "Que demuestra", "Observacion esperada"],
        ["Final. Valido con Swift", "Programa correcto con funcion, constante, ciclo para, acumulador, imprimir y condicional.", "La pestaña Swift muestra codigo destino, mapeo Claudio->Swift y validacion IA."],
        ["Final. Error semantico sin Swift", "Sintaxis correcta con SEM-3, SEM-4 y SEM-6.", "La pestaña Swift muestra bloqueo; los errores aparecen como semanticos."],
        ["Final. Error lexico/sintactico sin Swift", "Falta entonces, parentesis sin cerrar y caracter @.", "La pestaña Swift muestra bloqueo; los errores aparecen como lexicos y sintacticos."],
    ], [2.15 * inch, 3.0 * inch, CONTENT_W - 5.15 * inch]))
    flow.append(Spacer(1, 6))
    flow.append(p("Las capturas siguientes fueron tomadas desde la aplicacion desplegada en claudio.dautia.com. En cada una se observa el estado de la cadena de fases y el comportamiento de la pestaña Swift.", "Bodyx"))
    flow.append(PageBreak())
    flow.append(p("5.1 Caso Valido: Swift Generado", "H2x"))
    flow.append(screenshot(
        EVIDENCE_DIR / "01_ui_caso_valido_swift.png",
        "Caso Final. Valido con Swift: la interfaz confirma fases validas y muestra codigo Swift, mapeo y validacion IA.",
    ))
    flow.append(PageBreak())
    flow.append(p("5.2 Caso Semantico: Swift Bloqueado", "H2x"))
    flow.append(screenshot(
        EVIDENCE_DIR / "02_ui_caso_semantico_bloqueado.png",
        "Caso Final. Error semantico sin Swift: la sintaxis es aceptada, pero los errores SEM-3, SEM-4 y SEM-6 bloquean la salida destino.",
    ))
    flow.append(Spacer(1, 8))
    flow.append(p("5.3 Caso Lexico/Sintactico: Swift Bloqueado", "H2x"))
    flow.append(screenshot(
        EVIDENCE_DIR / "03_ui_caso_lexico_sintactico_bloqueado.png",
        "Caso Final. Error lexico/sintactico sin Swift: el compilador detecta errores tempranos y no permite generar codigo destino.",
    ))

    flow.append(PageBreak())
    flow.append(p("5.4 Respaldo Tecnico De Las Pruebas", "H2x"))
    flow.append(p("Los mismos programas usados en la UI tambien quedan guardados como archivos fuente para reproducibilidad y regresion automatizada.", "Bodyx"))
    flow.append(simple_table([
        ["Archivo fuente", "Caso UI equivalente"],
        ["tests/final/caso_valido.claudio", "Final. Valido con Swift"],
        ["tests/final/caso_semantico.claudio", "Final. Error semantico sin Swift"],
        ["tests/final/caso_lexico_sintactico.claudio", "Final. Error lexico/sintactico sin Swift"],
    ], [3.0 * inch, CONTENT_W - 3.0 * inch]))
    flow.append(Spacer(1, 6))
    flow.append(p("Verificacion automatizada complementaria:", "H2x"))
    flow.append(code("""cd backend
python3 -m unittest test_quiz3.py test_quiz3_diagnostic_cases.py test_quiz4_semantico.py test_entrega_final.py

cd ../frontend
npm run lint
npm run build"""))

    flow.append(p("6. Bonus IA Con OpenAI", "H1x"))
    flow.append(p("La integracion con OpenAI se usa como una revision posterior del lenguaje destino. Primero Claudio decide, con sus reglas propias, si el programa fuente es valido. Solo cuando esa validacion termina sin errores se envia el Swift generado a revision complementaria.", "Bodyx"))
    flow.append(p("Esto evita que la IA sustituya al compilador: OpenAI no acepta ni rechaza programas Claudio. Su papel es revisar la calidad de la traduccion generada y explicar si el Swift conserva la intencion del programa fuente.", "Bodyx"))
    flow.append(simple_table([
        ["Aspecto", "Descripcion para la entrega"],
        ["Momento de uso", "Despues de lexico, sintactico, semantico y SDT. Si hay errores, no se consulta IA porque no existe salida destino valida."],
        ["Informacion revisada", "Codigo Claudio original y codigo Swift generado por las acciones de traduccion."],
        ["Criterios enviados", "Sintaxis Swift razonable, llaves y bloques balanceados, operadores y literales traducidos, y conservacion de la intencion del programa."],
        ["Resultado mostrado", "Resumen breve en la interfaz, junto con posibles problemas y sugerencias sobre el Swift."],
        ["Comportamiento si no esta disponible", "La compilacion deterministica se conserva; simplemente no se muestra la revision complementaria."],
    ], [1.7 * inch, CONTENT_W - 1.7 * inch]))
    flow.append(Spacer(1, 6))
    flow.append(p("En la prueba valida de la interfaz se observa esta integracion: la pestaña Swift muestra el codigo destino y, debajo, un resumen de validacion IA que indica si la traduccion conserva la estructura e intencion del programa Claudio.", "Bodyx"))

    flow.append(p("7. Conclusiones", "H1x"))
    flow.append(bullet([
        "La entrega final queda cerrada como un flujo de compilacion completo: las fases no son pantallas aisladas, sino una cadena con compuertas claras.",
        "La gramatica, las reglas semanticas y las acciones SDT se mantienen alineadas con la implementacion real: tipos, bloques, ciclos, funciones, clases y expresiones tienen traduccion definida.",
        "La visualizacion Swift facilita defender el resultado: muestra salida destino, mapeo fuente-destino, estado de validacion y bloqueo explicito cuando hay errores.",
        "OpenAI se conserva como bonus educativo y no como dependencia critica: el compilador sigue funcionando aunque la IA no este disponible.",
    ]))
    return flow


def build_pdf(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
    )
    frame = Frame(
        MARGIN_X,
        MARGIN_BOTTOM,
        PAGE_W - 2 * MARGIN_X,
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
