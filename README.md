# Claudio Compiler IDE

Compilador fuente-a-fuente **Claudio** (espanol) → **Swift** con interfaz web interactiva.

## Estructura

```
new_version/
├── backend/          # FastAPI — lexer, parsers, traductor
│   ├── main.py       # API (5 endpoints)
│   ├── lexer.py      # Analizador lexico
│   ├── parser_rd.py  # Parser descendente recursivo
│   ├── parser_ll1.py # Parser predictivo LL(1)
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

Todos los POST reciben `{ "codigo": "..." }`.
