# hv-py-ms-render-cv

Microservicio de generación de PDFs ATS-friendly para CVs, utilizando [RenderCV](https://rendercv.com/) como motor de renderizado.

## Arquitectura

```
Frontends (Vercel)
       │ HTTPS
       ▼
   Nginx (servidor)
       │
       ├── /api/resume/*     → hv-go-ms-resume (Go, puerto 8080)
       └── /api/render/*     → hv-py-ms-render-cv (Python, puerto 8000, solo red interna)
```

**Relación**: Customer-Supplier con `hv-go-ms-resume`. `ms-resume` actúa como Anti-Corruption Layer, transformando sus entidades de dominio al schema de RenderCV.

### Stack Tecnológico

| Componente | Tecnología | Versión |
|---|---|---|
| Lenguaje | Python | 3.12 |
| Framework HTTP | FastAPI | 0.115+ |
| Motor de renderizado | RenderCV (embebido) | Latest |
| Motor de PDF | Typst | 0.14+ |
| Validación | Pydantic | v2 |
| Servidor ASGI | Uvicorn | 0.30+ |
| Containerización | Docker | python:3.12-slim |

## Requisitos Previos

- Docker (para ejecución en contenedor)
- Python 3.12+ (para desarrollo local)
- Typst instalado localmente (para desarrollo local)

## Desarrollo Local

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor de desarrollo
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

El servicio estará disponible en `http://localhost:8000`.

## Variables de Entorno

| Variable | Default | Descripción |
|---|---|---|
| `PORT` | 8000 | Puerto de escucha |
| `RENDER_TIMEOUT` | 30 | Timeout en segundos para generación PDF |
| `LOG_LEVEL` | INFO | Nivel de logging |
| `METRICS_ENABLED` | true | Habilitar endpoint de métricas Prometheus |
| `APP_VERSION` | 1.0.0 | Versión de la aplicación |

## Endpoints

### `GET /health`

Health check para verificar disponibilidad del servicio.

**Response 200**:
```json
{
  "status": "healthy",
  "timestamp": "2026-06-01T12:00:00Z",
  "version": "1.0.0"
}
```

**Response 503** (Typst no disponible):
```json
{
  "status": "unhealthy",
  "timestamp": "2026-06-01T12:00:00Z",
  "version": "1.0.0"
}
```

### `POST /render`

Genera un PDF ATS-friendly a partir de datos de CV estructurados.

**Request**:
```json
{
  "cv": {
    "name": "John Doe",
    "email": "john.doe@email.com",
    "sections": {
      "experience": [
        {
          "company": "Acme Corp",
          "position": "Senior Engineer",
          "start_date": "2023-01",
          "end_date": "present"
        }
      ]
    },
    "locale": {"language": "english"},
    "design": {"theme": "engineeringclassic"}
  }
}
```

**Response 200**:
```json
{
  "pdf_base64": "<base64-encoded-pdf-bytes>"
}
```

### `GET /metrics`

Expone métricas en formato Prometheus (solo red interna).

**Response 200** (cuando `METRICS_ENABLED=true`):
```
Content-Type: text/plain; charset=utf-8

# HELP render_requests_total Total number of render requests
# TYPE render_requests_total counter
render_requests_total{status="success"} 42
```

**Response 503** (cuando `METRICS_ENABLED=false`):
```
Metrics disabled
```

## Deploy con Docker

```bash
# Construir imagen
docker build -t hv-py-ms-render-cv .

# Ejecutar contenedor
docker run -d \
  --name hv-py-ms-render-cv \
  -p 8000:8000 \
  -e LOG_LEVEL=INFO \
  -e METRICS_ENABLED=true \
  hv-py-ms-render-cv
```

El contenedor corre como usuario no-root (`rendercv`, UID 1000) por seguridad.

### Health Check

El contenedor incluye un HEALTHCHECK que verifica el endpoint `GET /health` cada 30 segundos.

## Licencia

RenderCV es un proyecto open source. Ver documentación oficial en [rendercv.com](https://rendercv.com/).
