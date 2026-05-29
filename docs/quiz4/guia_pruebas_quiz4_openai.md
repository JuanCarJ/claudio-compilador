# Guia de pruebas - Quiz 4 Claudio con OpenAI

Esta guia usa la sintaxis y los endpoints reales de nuestro repo/despliegue. La capa IA usa OpenAI.

## Produccion

URL:

```text
https://claudio.dautia.com/?metodo=semantico
```

Endpoint principal:

```bash
curl -s https://claudio.dautia.com/api/semantico \
  -H 'content-type: application/json' \
  -d '{"codigo":"var entero x = \"hola\""}'
```

Resultado esperado:

- `valido: false`
- `total_errores_semanticos >= 1`
- primer error con regla `SEM-4`
- `tabla_simbolos` contiene `x`

## Local

Backend:

```bash
cd /Users/juancarj/UCO/S8/Compiladores/Claudio/new_version/backend
python -m uvicorn main:app --reload --port 8000
```

Frontend:

```bash
cd /Users/juancarj/UCO/S8/Compiladores/Claudio/new_version/frontend
npm run dev
```

Abrir:

```text
http://localhost:3000/?metodo=semantico
```

## Caso integral: SEM-1 a SEM-7

```claudio
var entero x = "hola"
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
fin_para
```

Resultado esperado:

- SEM-1: `x` duplicado en el mismo ambito
- SEM-2: `fantasma` no declarado
- SEM-3: `c` fue declarado con `sea` y se reasigna
- SEM-4: `x` declarado entero con valor cadena
- SEM-5: `x` recibe cadena en asignacion posterior
- SEM-6: condicion `si x` no es booleana
- SEM-7: limite/paso no numerico en `para`

## Caso valido

```claudio
funcion entero suma(entero a, entero b) hacer
    var entero resultado = a + b
    retornar resultado
fin_funcion

var entero total = 10
total = 20
si total > 0 entonces
    imprimir(total)
fin_si
```

Resultado esperado:

- sin errores sintacticos
- sin errores semanticos
- tabla con `suma`, `a`, `b`, `resultado`, `total`

## Pruebas por regla

### SEM-1 duplicado

```claudio
var entero contador = 0
var entero contador = 10
```

Esperado: SEM-1 en la segunda declaracion.

### SEM-2 no declarado

```claudio
var entero x = 10
imprimir(fantasma)
```

Esperado: SEM-2 sobre `fantasma`.

### SEM-3 constante reasignada

```claudio
sea real pi = 3.14
pi = 2.71
```

Esperado: SEM-3 sobre `pi`.

### SEM-4 tipo incompatible en declaracion

```claudio
var booleano activo = 42
var cadena nombre = verdadero
```

Esperado: SEM-4 para ambas declaraciones.

### SEM-5 tipo incompatible en asignacion

```claudio
var entero numero = 5
numero = "hola"
var cadena texto = "mundo"
texto = 99
```

Esperado: SEM-5 en ambas asignaciones.

### SEM-6 condicion no booleana

```claudio
var entero x = 10
si x entonces
    imprimir(x)
fin_si
```

Esperado: SEM-6.

### SEM-7 limites no numericos en para

```claudio
para i desde "a" hasta 10 paso falso hacer
    imprimir(i)
fin_para
```

Esperado: SEM-7.

## OpenAI

Endpoint:

```bash
curl -s https://claudio.dautia.com/api/sugerencias-ia-semantico \
  -H 'content-type: application/json' \
  -d '{"codigo":"var entero x = \"hola\"","diagnosticos":[{"indice":1,"regla":"SEM-4","mensaje":"Tipo incompatible","fila":1,"columna":12,"lexema":"x"}]}'
```

Resultado esperado cuando `OPENAI_API_KEY` esta configurada:

- `estado: lista`
- sugerencia con explicacion
- correccion sugerida
- mini ejemplo
- confianza

Resultado esperado sin clave:

- `estado: no_disponible`
- el compilador sigue funcionando
- la sugerencia deterministica se conserva

## Checklist de defensa

- Mostrar que el modo semantico existe.
- Mostrar la tabla de simbolos.
- Mostrar errores con badge SEM-N.
- Mostrar que un solo programa puede reportar varias reglas.
- Mostrar un programa valido sin errores.
- Decir explicitamente que OpenAI no detecta errores; solo los explica.
