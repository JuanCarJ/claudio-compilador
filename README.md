# Claudio Compiler IDE

Compilador fuente-a-fuente **Claudio** (espanol) → **Swift** con interfaz web interactiva.

Incluye Entrega 3 / Quiz 3: recuperacion de errores sintacticos con reporte detallado, sugerencias deterministicas y sugerencias complementarias con OpenAI.

## Estructura

```
new_version/
├── backend/          # FastAPI — lexer, parsers, traductor
│   ├── main.py       # API (5 endpoints)
│   ├── lexer.py      # Analizador lexico
│   ├── parser_rd.py  # Parser descendente recursivo
│   ├── parser_ll1.py # Parser predictivo LL(1)
│   ├── diagnostics.py # Errores sintacticos estructurados + modo panico
│   ├── ai_suggestions.py # Sugerencias IA con OpenAI
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
| POST | `/api/traducir` | Traduccion Claudio → Swift |
| POST | `/api/sugerencias-ia` | Sugerencias IA en lote para errores sintacticos |

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

## Pruebas

```bash
cd backend
python3 -m py_compile diagnostics.py ai_suggestions.py lexer.py parser_rd.py parser_ll1.py main.py
python3 -m unittest test_quiz3.py test_quiz3_diagnostic_cases.py

cd ../frontend
npm run lint
npm run build
```
