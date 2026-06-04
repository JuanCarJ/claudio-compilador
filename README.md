# Claudio Compiler IDE

Compilador fuente-a-fuente **Claudio** (espanol) → **Swift** con interfaz web interactiva.

Incluye Entrega 3 / Quiz 3: recuperacion de errores sintacticos con reporte detallado, sugerencias deterministicas y sugerencias complementarias con OpenAI.

Incluye Entrega 4 / Quiz 4: analisis semantico con tabla de simbolos, 7 reglas semanticas clasicas y sugerencias complementarias con OpenAI.

Incluye Entrega Final: pipeline completo `lexico -> sintactico -> semantico -> SDT Swift`, visualizacion mejorada del lenguaje destino, errores unificados y validacion IA opcional sobre el Swift generado.

## Estructura

```
new_version/
├── backend/          # FastAPI — lexer, parsers, traductor
│   ├── main.py       # API de fases + compilacion final
│   ├── lexer.py      # Analizador lexico
│   ├── parser_rd.py  # Parser descendente recursivo
│   ├── parser_ll1.py # Parser predictivo LL(1)
│   ├── diagnostics.py # Errores sintacticos estructurados + modo panico
│   ├── ai_suggestions.py # Sugerencias IA con OpenAI
│   ├── semantico.py  # Analizador semantico + tabla de simbolos
│   ├── arbol.py      # Nodo del arbol + serializacion
│   ├── traductor.py  # Traduccion Claudio → Swift
│   ├── programas.py  # 15 programas de ejemplo
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/         # Next.js — IDE interactivo
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── tests/final/      # 3 casos obligatorios de la entrega final
└── README.md
```

## Desarrollo local

```bash
# Terminal 1 — Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --port 8000

# Terminal 2 — Frontend
cd frontend
npm install
npm run dev
```

Abrir http://localhost:3000

## Despliegue con Docker

```bash
docker compose up --build
```

Backend en `:8000`, frontend en `:3000`.

## Despliegue en servidor (sin Docker)

### Backend (cualquier VPS con Python 3.9+)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
NEXT_PUBLIC_API_URL=https://tu-backend.com npm run build
npm start
```

## Variables de entorno

| Variable | Donde | Default | Descripcion |
|----------|-------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | frontend | `http://localhost:8000` | URL del backend API |

## API Endpoints

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/programas` | 15 programas de ejemplo |
| POST | `/api/lexico` | Analisis lexico |
| POST | `/api/recursivo` | Parser descendente recursivo |
| POST | `/api/ll1` | Parser predictivo LL(1) |
| POST | `/api/semantico` | Analisis semantico con tabla de simbolos |
| POST | `/api/traducir` | Traduccion Claudio → Swift |
| POST | `/api/compilar` | Entrega final: lexico → sintactico → semantico → Swift + IA opcional |
| POST | `/api/sugerencias-ia` | Sugerencias IA en lote para errores sintacticos |
| POST | `/api/sugerencias-ia-semantico` | Sugerencias IA para errores semanticos |

Todos los POST reciben `{ "codigo": "..." }`.

## Entrega 3 / Quiz 3 — Recuperacion de errores

Los endpoints `/api/recursivo` y `/api/ll1` conservan sus campos anteriores y agregan:

| Campo | Descripcion |
|-------|-------------|
| `errores_sintacticos` | Lista estructurada de errores detectados en una sola pasada |
| `total_errores_sintacticos` | Total de errores sintacticos |
| `arbol_parcial` | Arbol construido hasta donde fue posible, incluso con errores |

Cada error contiene:

- `fila`, `columna`
- `lexema_encontrado`, `tipo_encontrado`
- `esperados`
- `contexto`
- `sugerencia_deterministica`: siempre empieza indicando el siguiente token o fragmento esperado por la gramatica.
- `sugerencia_ia`
- `estado_ia`
- `recuperacion`

### Estrategia de recuperacion

La recuperacion usa modo panico. Cuando se detecta un error, el analizador avanza o desapila hasta encontrar un punto seguro:

- inicio de sentencia/declaracion: `si`, `para`, `mientras`, `retornar`, `imprimir`, `var`, `sea`, `funcion`, `clase`, `importar`
- cierres de bloque: `sino`, `fin_si`, `fin_para`, `fin_mientras`, `fin_funcion`, `fin_clase`
- delimitadores de sincronizacion: `)`, `,`, `;`
- fin de archivo: `EOF` / `$`

### Sugerencias IA

La sugerencia IA es complementaria. La sugerencia deterministica siempre se genera primero con base en la gramatica y el estado del parser, indicando que sigue segun FIRST/FOLLOW o la produccion activa; luego el frontend llama `/api/sugerencias-ia` para explicar ese siguiente paso con lenguaje natural.

Variables:

| Variable | Default | Uso |
|----------|---------|-----|
| `OPENAI_API_KEY` | sin default | Habilita el bonus IA |
| `OPENAI_MODEL` | `gpt-5.4-mini` | Modelo usado por Responses API |
| `OPENAI_TIMEOUT_SECONDS` | `8` | Timeout de la llamada |
| `OPENAI_MAX_ERRORS` | `8` | Maximo de errores enviados por lote |

Si no hay `OPENAI_API_KEY`, el endpoint responde `estado=no_disponible` y la UI sigue funcionando.

Para desarrollo local, crea `backend/.env` (ignorado por Git):

```env
OPENAI_API_KEY=tu_api_key
OPENAI_MODEL=gpt-5.4-mini
OPENAI_TIMEOUT_SECONDS=8
OPENAI_MAX_ERRORS=8
```

## Entrega 4 / Quiz 4 — Analisis semantico

El endpoint `/api/semantico` ejecuta:

```text
Lexico -> Parser descendente recursivo -> Analizador semantico
```

La fase semantica esta separada en `backend/semantico.py` y recorre el AST con una pasada tipo visitor.

Reglas implementadas:

| Regla | Validacion |
|-------|------------|
| `SEM-1` | Declaracion duplicada en el mismo ambito |
| `SEM-2` | Uso de identificador no declarado |
| `SEM-3` | Reasignacion de constante declarada con `sea` |
| `SEM-4` | Tipo incompatible en declaracion |
| `SEM-5` | Tipo incompatible en asignacion |
| `SEM-6` | Condicion de `si`/`mientras` no booleana |
| `SEM-7` | Limites o `paso` no numericos en ciclo `para` |

Cada error semantico incluye `fila`, `columna`, `lexema`, `regla`, `mensaje`, `sugerencia` y estado de IA. La tabla de simbolos almacena `nombre`, `tipo`, `inmutable`, `inicializado`, `ambito`, `fila` y `columna`.

Documento entregable:

- `docs/quiz4/gramatica_semantica_quiz4.html`
- `docs/quiz4/gramatica_semantica_quiz4.pdf` si fue generado localmente con Chrome headless.

## Entrega Final — SDT Claudio → Swift

El endpoint `/api/compilar` ejecuta el flujo completo:

```text
Lexico -> Sintactico RD -> Semantico -> SDT Swift -> Validacion IA opcional
```

Reglas de salida:

- si hay errores lexicos, no se genera Swift
- si hay errores sintacticos, no se genera Swift
- si hay errores semanticos, no se genera Swift
- si el programa es valido, la respuesta incluye `swift`, `mapeo`, `tabla_simbolos` y `validacion_ia`

Cada error final queda normalizado como:

```json
{
  "fase": "lexico | sintactico | semantico",
  "fila": 1,
  "columna": 1,
  "lexema": "...",
  "mensaje": "...",
  "regla": "SEM-1"
}
```

Archivos de prueba de la entrega final:

- `tests/final/caso_valido.claudio`
- `tests/final/caso_semantico.claudio`
- `tests/final/caso_lexico_sintactico.claudio`

Documento PDF generado:

- `docs/final/entrega_final_claudio_swift.pdf`
- copia local de entrega: `/Users/juancarj/Downloads/Entrega Final Claudio.pdf`

## Pruebas

```bash
cd backend
python3 -m py_compile diagnostics.py ai_suggestions.py lexer.py parser_rd.py parser_ll1.py semantico.py main.py
python3 -m unittest test_quiz3.py test_quiz3_diagnostic_cases.py test_quiz4_semantico.py test_entrega_final.py

cd ../frontend
npm run lint
npm run build
```
