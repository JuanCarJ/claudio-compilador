"""
Programas de ejemplo predefinidos del lenguaje Claudio.

La galeria publica debe ser limpia: primero programas que compilan y generan
Swift; al final solo dos fallas de demostracion.
"""

PROGRAMAS_VALIDOS = {
    "1. Hola Mundo": """// El programa mas simple en Claudio
imprimir("Hola Mundo desde Claudio")""",

    "2. Tipos y variables": """// Los 4 tipos basicos del lenguaje
var entero edad = 21
var real estatura = 1.75
var cadena nombre = "Maria"
var booleano estudiante = verdadero

// Constante inmutable (equivale a let en Swift)
sea real PI = 3.14159
sea cadena universidad = "UCO"

// Reasignacion de variable mutable
edad = 22
imprimir(nombre)
imprimir(edad)""",

    "3. Calculadora aritmetica": """// Todas las operaciones aritmeticas del lenguaje
var real precio = 45000.0
var entero cantidad = 3
var real descuento = 10.5
var real estatura = 1.75

// Suma, resta, multiplicacion, division
var real subtotal = precio * cantidad
var real ahorro = subtotal * descuento / 100.0
var real total = subtotal - ahorro

// Modulo y potencia
var entero resto = 17 % 5
var real cuadrado = estatura ** 2

imprimir(total)
imprimir(resto)
imprimir(cuadrado)""",

    "4. Comparaciones": """// Los 6 operadores relacionales
var entero edad = 18

var booleano esMayor = edad >= 18
var booleano esMenor = edad < 18
var booleano exacto = edad == 18
var booleano diferente = edad != 21
var booleano superaLimite = edad > 65
var booleano bajoMinimo = edad <= 14

imprimir(esMayor)
imprimir(diferente)""",

    "5. Logica booleana": """// Operadores logicos: y (&&), o (||), no (!)
var entero edad = 20
var booleano tieneCarnet = verdadero
var booleano tieneMultas = falso

// Conjuncion: ambas condiciones deben cumplirse
var booleano puedeConducir = (edad >= 18) y tieneCarnet

// Disyuncion: al menos una condicion
var booleano requiereRevision = tieneMultas o (edad < 21)

// Negacion
var booleano sinMultas = no tieneMultas

imprimir(puedeConducir)
imprimir(requiereRevision)
imprimir(sinMultas)""",

    "6. Condicional simple": """// Condicional si...entonces...sino...fin_si
var entero nota = 75

si nota >= 60 entonces
    imprimir("Aprobado")
sino
    imprimir("Reprobado")
fin_si""",

    "7. Condicional anidado": """// Clasificacion de notas con condicionales anidados
var entero nota = 85

si nota >= 90 entonces
    imprimir("Sobresaliente")
sino
    si nota >= 80 entonces
        imprimir("Notable")
    sino
        si nota >= 60 entonces
            imprimir("Aprobado")
        sino
            imprimir("Reprobado")
        fin_si
    fin_si
fin_si""",

    "8. Ciclo para": """// Tabla de multiplicar del 7
var entero numero = 7

para i desde 1 hasta 10 paso 1 hacer
    var entero resultado = numero * i
    imprimir(resultado)
fin_para

// Sumatoria con paso de 2
var entero sumaImpares = 0
para j desde 1 hasta 9 paso 2 hacer
    sumaImpares = sumaImpares + j
fin_para
imprimir(sumaImpares)""",

    "9. Ciclo mientras": """// Cuenta regresiva de lanzamiento
var entero segundos = 10

mientras segundos > 0 hacer
    imprimir(segundos)
    segundos = segundos - 1
fin_mientras

imprimir("Despegue!")

// Buscar potencia de 2 mayor a 1000
var entero potencia = 1
mientras potencia <= 1000 hacer
    potencia = potencia * 2
fin_mientras
imprimir(potencia)""",

    "10. Romper y continuar": """// Buscar el primer numero primo mayor a 50
var entero numero = 51
var booleano encontrado = falso

mientras no encontrado hacer
    var booleano esPrimo = verdadero
    var entero divisor = 2

    mientras divisor * divisor <= numero hacer
        si numero % divisor == 0 entonces
            esPrimo = falso
            romper
        fin_si
        divisor = divisor + 1
    fin_mientras

    si esPrimo entonces
        imprimir(numero)
        encontrado = verdadero
    fin_si
    numero = numero + 1
fin_mientras""",

    "11. Funciones": """// Funcion: calcular area de un circulo
funcion real areaCirculo(real radio) hacer
    sea real PI = 3.14159
    retornar PI * radio ** 2
fin_funcion

// Funcion: calcular perimetro
funcion real perimetroCirculo(real radio) hacer
    sea real PI = 3.14159
    retornar 2.0 * PI * radio
fin_funcion

// Usar las funciones
var real radio = 5.0
var real area = areaCirculo(radio)
var real perimetro = perimetroCirculo(radio)

imprimir(area)
imprimir(perimetro)""",

    "12. Factorial recursivo": """// Factorial: algoritmo recursivo clasico
funcion entero factorial(entero n) hacer
    si n <= 1 entonces
        retornar 1
    sino
        retornar n * factorial(n - 1)
    fin_si
fin_funcion

// Calcular factoriales de 1 a 8
para i desde 1 hasta 8 paso 1 hacer
    var entero resultado = factorial(i)
    imprimir(resultado)
fin_para""",

    "Quiz 4. Caso semantico valido": """// Programa valido para comparar contra los errores semanticos
funcion entero suma(entero a, entero b) hacer
    var entero resultado = a + b
    retornar resultado
fin_funcion

var entero total = 10
total = 20

si total > 0 entonces
    imprimir(total)
fin_si""",

    "Final. Valido con Swift": """// Entrega final: debe pasar lexico, sintactico y semantico, y generar Swift
funcion entero doble(entero n) hacer
    retornar n * 2
fin_funcion

sea entero LIMITE = 4
var entero acumulado = 0

para i desde 1 hasta LIMITE paso 1 hacer
    var entero valor = doble(i)
    acumulado = acumulado + valor
    imprimir(valor)
fin_para

si acumulado > 0 entonces
    imprimir(acumulado)
fin_si""",
}


PROGRAMAS_CON_ERROR = {
    "Final. Error semantico sin Swift": """// Error semantico: la sintaxis es correcta, pero la semantica bloquea Swift
sea entero limite = 3
limite = 7

var entero total = "mucho"

si total entonces
    imprimir(total)
fin_si""",

    "Final. Error lexico/sintactico sin Swift": """// Error lexico/sintactico: no debe generarse Swift
var entero x = 10

si x > 5
    imprimir("Mayor"
fin_si

imprimir(@)""",
}


PROGRAMAS = {
    **PROGRAMAS_VALIDOS,
    **PROGRAMAS_CON_ERROR,
}


PROGRAMAS_DIAGNOSTICO = {
    "Quiz 3. Error: falta entonces": """// Caso invalido: falta la palabra reservada entonces
var entero x = 10

si x > 5
    imprimir("Mayor")
fin_si""",

    "Quiz 3. Error: parentesis sin cerrar": """// Caso invalido: llamada incompleta
var cadena nombre = "Claudio"
imprimir(nombre
imprimir("continua")""",

    "Quiz 3. Error: multiples fallos": """// Caso invalido: varios errores para demostrar recuperacion
var x = 10

si x > entonces
    imprimir(x
fin_si

mientras hacer
    imprimir("loop")
fin_mientras

imprimir(@)""",
}
