"""
Programas de ejemplo predefinidos del lenguaje Claudio.
"""

PROGRAMAS = {
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
var booleano tieneMullas = falso

// Conjuncion: ambas condiciones deben cumplirse
var booleano puedeConducir = (edad >= 18) y tieneCarnet

// Disyuncion: al menos una condicion
var booleano requiereRevision = tieneMullas o (edad < 21)

// Negacion
var booleano sinMultas = no tieneMullas

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

    "8. Ciclo para (for)": """// Tabla de multiplicar del 7
var entero numero = 7

para i desde 1 hasta 10 paso 1 hacer
    var entero resultado = numero * i
    imprimir(resultado)
fin_para

// Sumatoria con paso de 2 (solo impares)
var entero sumaImpares = 0
para j desde 1 hasta 9 paso 2 hacer
    sumaImpares = sumaImpares + j
fin_para
imprimir(sumaImpares)""",

    "9. Ciclo mientras (while)": """// Cuenta regresiva de lanzamiento
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

    "13. Clases y objetos": """// Clase Cuenta Bancaria
clase CuentaBancaria hacer
    atributo cadena titular
    atributo real saldo

    metodo depositar(real monto) hacer
        este.saldo = este.saldo + monto
    fin_funcion

    metodo retirar(real monto) hacer
        si monto <= este.saldo entonces
            este.saldo = este.saldo - monto
            imprimir("Retiro exitoso")
        sino
            imprimir("Fondos insuficientes")
        fin_si
    fin_funcion

    metodo consultarSaldo() hacer
        imprimir(este.titular)
        imprimir(este.saldo)
    fin_funcion
fin_clase

// Crear objeto e interactuar
var CuentaBancaria miCuenta = nuevo CuentaBancaria()
miCuenta.titular = "Juan Cardenas"
miCuenta.saldo = 500000.0
miCuenta.depositar(150000.0)
miCuenta.retirar(80000.0)
miCuenta.consultarSaldo()""",

    "14. Herencia": """// Jerarquia de clases con herencia
clase Animal hacer
    atributo cadena nombre
    atributo entero edad

    metodo presentarse() hacer
        imprimir(este.nombre)
        imprimir(este.edad)
    fin_funcion
fin_clase

clase Perro hereda Animal hacer
    atributo cadena raza

    metodo ladrar() hacer
        imprimir("Guau!")
    fin_funcion
fin_clase

clase Gato hereda Animal hacer
    atributo booleano domestico

    metodo maullar() hacer
        imprimir("Miau!")
    fin_funcion
fin_clase

// Instanciacion y uso
var Perro miPerro = nuevo Perro()
miPerro.nombre = "Rex"
miPerro.edad = 3
miPerro.raza = "Pastor Aleman"
miPerro.presentarse()
miPerro.ladrar()

var Gato miGato = nuevo Gato()
miGato.nombre = "Luna"
miGato.edad = 2
miGato.domestico = verdadero
miGato.presentarse()
miGato.maullar()""",

    "15. Programa completo": """/* Sistema de notas — usa TODAS las capacidades */

// 1. Palabras en espanol + 9. Tipos basicos
sea entero NOTA_MINIMA = 60
sea real PESO_PARCIAL = 0.3
sea real PESO_FINAL = 0.7

// 10. Asignacion
var cadena alumno = "Ana Garcia"
var entero parcial = 78
var entero examenFinal = 92
var booleano asistencia = verdadero

// 2. Operaciones aritmeticas
var real notaPonderada = (parcial * PESO_PARCIAL) + (examenFinal * PESO_FINAL)
var real notaRedondeada = notaPonderada ** 1

// 8. Funcion con retorno
funcion cadena clasificar(real nota) hacer
    // 5. Condicional si...entonces...sino
    si nota >= 90.0 entonces
        retornar "Sobresaliente"
    sino
        si nota >= 80.0 entonces
            retornar "Notable"
        sino
            si nota >= 60.0 entonces
                retornar "Aprobado"
            sino
                retornar "Reprobado"
            fin_si
        fin_si
    fin_si
fin_funcion

// 8. Funcion recursiva
funcion entero sumatoria(entero n) hacer
    si n <= 0 entonces
        retornar 0
    fin_si
    retornar n + sumatoria(n - 1)
fin_funcion

// 8. Clase con atributos y metodos
clase Estudiante hacer
    atributo cadena nombre
    atributo real promedio

    metodo mostrar() hacer
        imprimir(este.nombre)
        imprimir(este.promedio)
    fin_funcion
fin_clase

// 3. Operadores logicos (y, o, no)
si (notaPonderada >= 60.0) y asistencia entonces
    imprimir("Aprobado con asistencia completa")
fin_si

si no (parcial < NOTA_MINIMA) o (examenFinal >= 90) entonces
    imprimir("Buen desempeno")
fin_si

// 4. Operadores relacionales
si parcial == examenFinal entonces
    imprimir("Notas iguales")
fin_si
si parcial != examenFinal entonces
    imprimir("Notas diferentes")
fin_si

// 6. Ciclo para
para i desde 1 hasta 5 paso 1 hacer
    var entero nota = 60 + i * 5
    imprimir(nota)
fin_para

// 7. Ciclo mientras
var entero contador = 3
mientras contador > 0 hacer
    imprimir(contador)
    contador = contador - 1
fin_mientras

// Crear objeto y mostrar resultado
var Estudiante est = nuevo Estudiante()
est.nombre = alumno
est.promedio = notaPonderada
est.mostrar()

var cadena clasificacion = clasificar(notaPonderada)
imprimir(clasificacion)""",

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
