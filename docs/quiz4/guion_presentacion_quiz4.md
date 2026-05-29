# Guia de exposicion - Quiz 4 Claudio

Duracion sugerida: 12 a 15 minutos.

Tesis: Claudio pasa de reconocer programas bien formados a validar si esos programas tienen sentido. La exposicion debe enseñar primero los conceptos de analisis semantico y despues demostrar como quedaron implementados.

## Preparacion antes de exponer

- Abrir la PPT: `docs/quiz4/claudio_quiz4_semantico_openai.pptx`.
- Abrir la app desplegada: `https://claudio.dautia.com/?metodo=semantico`.
- Tener listo el caso con errores de `guia_pruebas_quiz4_openai.md`.
- Tener listo el caso valido de `guia_pruebas_quiz4_openai.md`.
- Recordar el punto de proveedor IA: en nuestro caso es OpenAI.

## Slide 1 - Portada

Decir:

> Esta entrega implementa analisis semantico para Claudio. No se trata solo de una pantalla nueva: la fase semantica valida significado sobre el AST, genera una tabla de simbolos, detecta siete reglas de error y usa OpenAI para explicar diagnosticos reales.

## Slide 2 - Agenda

Decir:

> La exposicion tiene cuatro partes: primero el contexto de Claudio, luego los conceptos de semantica, despues las reglas SEM-1 a SEM-7, y finalmente la implementacion con demo.

## Slide 3 - Que es Claudio

Decir:

> Claudio es un compilador fuente-a-fuente: recibe codigo en espanol y lo traduce hacia Swift. Ya teniamos lexer y parser; el Quiz 4 agrega una fase posterior: el analisis semantico.

Rematar:

> El pipeline queda: lexico, sintactico, semantico y traduccion.

## Slide 4 - Sintaxis vs semantica

Decir:

> La sintaxis valida forma. Por ejemplo, que una asignacion tenga `ID = expresion`. La semantica valida significado: si ese ID existe, si su tipo permite esa expresion, si no es una constante, etc.

Ejemplo:

> `x = "texto"` puede tener forma correcta, pero si `x` fue declarado como entero, semanticamente es incorrecto.

## Slide 5 - Atributos semanticos

Decir:

> Una regla semantica se expresa con atributos. Un atributo sintetizado se calcula desde el nodo o sus hijos, como `expr.tipo`. Un atributo heredado viene del contexto, como `ambitoActual`.

Luego:

> Cada regla tambien tiene un dominio y una accion. El dominio dice que debe cumplirse; la accion dice que hace el compilador cuando no se cumple.

## Slide 6 - Tabla de simbolos

Decir:

> La tabla de simbolos es la memoria del programa. Guarda nombre, tipo, si es inmutable, si fue inicializado, ambito, fila y columna.

Punto clave:

> Cuando aparece un identificador, se busca desde el ambito mas interno hacia el global. Eso permite detectar duplicados, no declarados y constantes reasignadas.

## Slide 7 - Tipos y dominios

Decir:

> Las expresiones sintetizan un tipo. Luego ese tipo se compara con un dominio esperado. Por ejemplo, una condicion de `si` debe ser booleana; los limites de `para` deben ser numericos.

Mencionar:

> Claudio permite `entero -> real` como widening, pero no permite asignar cadena a entero ni booleano a cadena.

## Slide 8 - Recuperacion semantica

Decir:

> El analizador no se detiene en el primer error. Reporta el error, conserva informacion suficiente y sigue recorriendo el AST para entregar una lista completa de diagnosticos.

## Slide 9 - Mapa de reglas

Decir:

> Estas son las siete reglas que hay que defender. Para cada una se debe explicar: nodo gramatical, atributos usados, dominio validado y diagnostico emitido.

Resumen rapido:

> SEM-1 duplicado, SEM-2 no declarado, SEM-3 constante, SEM-4 tipo en declaracion, SEM-5 tipo en asignacion, SEM-6 condicion no booleana y SEM-7 limites no numericos.

## Slide 10 - SEM-1 a SEM-4

Decir:

> Las primeras reglas cubren identidad y declaracion. SEM-1 revisa duplicados en el mismo ambito. SEM-2 busca nombres en la tabla. SEM-3 usa el atributo heredado `inmutable`. SEM-4 compara tipo declarado contra tipo inferido al inicializar.

## Slide 11 - SEM-5 a SEM-7

Decir:

> SEM-5 aplica el mismo criterio de tipos, pero en asignaciones posteriores. SEM-6 exige que `si` y `mientras` reciban booleanos. SEM-7 valida que `desde`, `hasta` y `paso` sean numericos.

## Slide 12 - Backend

Decir:

> En backend, `AnalizadorSemantico` implementa una pasada independiente sobre el AST. `TablaSimbolos` maneja ambitos. `SemanticDiagnostic` estructura los errores. `/api/semantico` expone la tabla y los diagnosticos.

Punto fuerte:

> El parser no se mezcla con la semantica; produce el AST y la nueva fase lo recorre.

## Slide 13 - Arquitectura

Decir:

> La arquitectura es determinista primero. Lexer y parser producen tokens y AST. El semantico detecta errores. OpenAI entra despues para explicar errores ya detectados.

Rematar:

> La IA no inventa reglas semanticas. Solo traduce diagnosticos reales a lenguaje mas entendible.

## Slide 14 - UI y OpenAI

Decir:

> En frontend se agrego el modo semantico, la tabla de simbolos y la vista de errores semanticos. En OpenAI se envia el diagnostico y el codigo para obtener explicacion, correccion sugerida, mini ejemplo y confianza.

## Slide 15 - Validacion

Decir:

> La validacion cubre caso integral con SEM-1 a SEM-7, caso valido sin errores, endpoint `/api/semantico`, fallback cuando no hay `OPENAI_API_KEY`, y ejecucion en produccion.

## Slide 16 - Cierre

Decir:

> Lo importante es que la semantica valida significado sobre un AST ya construido. El mecanismo son atributos, tabla de simbolos y dominios por regla. En Claudio eso quedo implementado como backend independiente, UI visible y OpenAI explicativo.

Frase final:

> Claudio no solo reconoce programas bien formados; ahora explica por que un programa tiene o no tiene sentido.

## Demo en vivo

1. Abrir `https://claudio.dautia.com/?metodo=semantico`.
2. Pegar el caso integral con errores.
3. Ejecutar.
4. Mostrar la tabla de simbolos.
5. Mostrar errores SEM-1 a SEM-7.
6. Mostrar sugerencias OpenAI si estan disponibles.
7. Pegar el caso valido y mostrar cero errores.

## Preguntas esperables

**¿Por que separar parser y semantica?**

Porque el parser valida estructura y la semantica valida significado. Mezclarlos vuelve el compilador mas dificil de mantener y explicar.

**¿OpenAI detecta los errores?**

No. Los errores son deterministas. OpenAI solo explica diagnosticos que Claudio ya encontro.

**¿Por que tabla de simbolos?**

Porque sin memoria de nombres, tipos, constantes y ambitos no se pueden detectar duplicados, no declarados ni reasignaciones.

**¿Que pasa con tipos desconocidos?**

El analizador evita falsos positivos. Si no puede inferir con seguridad, no inventa un error.
