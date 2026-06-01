# Master Spec - hv-py-ms-render-cv

**Bounded Context**: CV Rendering
**Owner**: cristiansrc
**Lifecycle Status**: `implemented`
**Created**: 2026-05-31
**Last Updated**: 2026-06-01

---

## 1. Objetivo del Servicio

Microservicio responsable de generar PDFs ATS-friendly a partir de datos de CV estructurados, utilizando la librería RenderCV (Python) como motor de renderizado. El servicio es consumido exclusivamente por `hv-go-ms-resume` vía HTTP interno en red Docker.

## 2. Arquitectura

### 2.1 Stack Tecnológico

| Componente | Tecnología | Versión |
|---|---|---|
| Lenguaje | Python | 3.12 |
| Framework HTTP | FastAPI | 0.115+ |
| Motor de renderizado | RenderCV (librería embebida) | Latest |
| Motor de PDF | Typst | 0.14+ |
| Validación | Pydantic | v2 |
| Servidor ASGI | Uvicorn | 0.30+ |
| Containerización | Docker | python:3.12-slim |

### 2.2 Estructura del Proyecto

```
hv-py-ms-render-cv/
├── api/                          # Capa de adaptación HTTP (FastAPI)
│   ├── main.py                   # Bootstrap de la aplicación
│   ├── schemas.py                # Pydantic DTOs (request/response)
│   ├── core/                     # Cross-cutting concerns
│   │   └── errors.py             # Exception handlers globales
│   ├── routers/                  # Endpoints FastAPI
│   │   └── render.py             # POST /render
│   └── services/                 # Lógica de aplicación
│       └── rendercv_service.py   # Orquestación de RenderCV
├── rendercv/                     # Librería RenderCV embebida (vendor)
│   ├── schema/                   # Schema y validación Pydantic
│   ├── renderer/                 # Generación Typst + PDF
│   └── exception.py              # Excepciones propias
├── Dockerfile
├── requirements.txt
└── main.py                       # Entry point (vacío, usar api.main)
```

### 2.3 Posicionamiento en el Ecosistema

```
Frontends (Vercel)
       │ HTTPS
       ▼
   Nginx (servidor)
       │
       ├── /api/resume/*     → hv-go-ms-resume (Go, puerto 8080)
       └── /api/render/*     → hv-py-ms-render-cv (Python, puerto 8000, solo red interna)
```

**Relación**: Customer-Supplier con `hv-go-ms-resume`. ms-resume actúa como Anti-Corruption Layer, transformando sus entidades de dominio al schema de RenderCV.

## 3. Contratos API

### 3.1 POST /render

Genera un PDF a partir de datos de CV en formato RenderCV.

**Request**:
```json
{
  "cv": {
    "name": "string",
    "email": "string",
    "phone": "string | null",
    "location": "string | null",
    "headline": "string | null",
    "photo": "string | null",
    "website": "string | null",
    "social_networks": [{"network": "string", "username": "string"}],
    "sections": {
      "education": [{"institution": "string", "area": "string", ...}],
      "experience": [{"company": "string", "position": "string", ...}],
      "skills": [{"label": "string", "details": "string"}],
      "...": "cualquier sección válida de RenderCV"
    },
    "locale": {"language": "spanish"} | null,
    "design": {"theme": "engineeringclassic"} | null
  }
}
```

**Response (200)**:
```json
{
  "pdf_base64": "<base64-encoded-pdf-bytes>"
}
```

**Error Responses**: Ver `docs/api/openapi.yaml` para el contrato completo de errores.

### 3.2 GET /health

Health check para orquestador Docker y monitoreo.

**Response (200)**:
```json
{
  "status": "healthy",
  "timestamp": "2026-05-31T12:00:00Z",
  "version": "1.0.0"
}
```

## 4. Modelo de Datos

### 4.1 No hay persistencia

Este servicio es **stateless**. No utiliza base de datos. Los PDFs se generan de forma efímera en un directorio temporal y se eliminan inmediatamente después de la respuesta.

### 4.2 Schema de Entrada (RenderCV)

El payload de entrada sigue el schema de RenderCV. Los campos principales son:

| Campo | Tipo | Required | Descripción |
|---|---|---|---|
| `cv.name` | string | Sí | Nombre completo |
| `cv.email` | string (email) | Sí | Email de contacto |
| `cv.phone` | string | No | Teléfono |
| `cv.location` | string | No | Ubicación |
| `cv.headline` | string | No | Título profesional |
| `cv.photo` | string (URL/path) | No | Ruta de foto |
| `cv.website` | string (URL) | No | Sitio web |
| `cv.social_networks` | array | No | Redes sociales |
| `cv.sections` | object | Sí | Secciones del CV |
| `cv.locale` | object | No | Configuración de idioma |
| `cv.design` | object | No | Configuración de diseño/tema |

### 4.3 Secciones Válidas

RenderCV soporta las siguientes secciones predefinidas:
- `education` → EducationEntry
- `experience` → ExperienceEntry
- `skills` → SkillEntry (label + details)
- `publications` → PublicationEntry
- `projects` → ProjectEntry
- `selected_honors` → BulletEntry
- `patents` → BulletEntry
- `invited_talks` → ReversedNumberedEntry
- Secciones custom con cualquier título → TextEntry, NumberedEntry, etc.

## 5. Reglas de Negocio

### 5.1 Validación
- El payload debe ser un objeto con clave `cv` que contenga al menos `name`, `email` y `sections`.
- Los emails deben ser válidos según RFC 5322.
- Los teléfonos deben ser parseables por la librería `phonenumbers`.
- Las URLs deben ser válidas.
- Las fechas deben estar en formato `YYYY-MM` o `YYYY`.

### 5.2 Renderizado
- El PDF se genera en un directorio temporal que se elimina tras la respuesta.
- No se cachean PDFs generados.
- El timeout máximo de generación es 30 segundos.
- Si la generación falla, se retorna error 500 con mensaje genérico.

### 5.3 Internacionalización
- Soporte para múltiples idiomas vía `cv.locale.language`.
- Idiomas soportados: spanish, english, french, german, italian, portuguese, dutch, danish, russian, turkish, hindi, indonesian, japanese, korean, mandarin_chinese.

### 5.4 Temas de Diseño
- Temas disponibles: engineeringclassic, engineeringresumes, moderncv, sb2nov.
- Tema por defecto: definido por RenderCV si no se especifica.

## 6. Integraciones

### 6.1 Upstream: hv-go-ms-resume

| Propiedad | Valor |
|---|---|
| **Tipo** | Sync HTTP |
| **Protocolo** | HTTP (red interna Docker) |
| **Direction** | hv-go-ms-resume → hv-py-ms-render-cv |
| **Auth** | Ninguna (red interna) |
| **Timeout** | 30s |
| **Retry** | 1 reintento desde ms-resume |
| **Idempotency** | No aplica (generación PDF es determinista para mismo input) |

### 6.2 Dependencia Externa: RenderCV Library

| Propiedad | Valor |
|---|---|
| **Tipo** | Librería Python embebida (vendor) |
| **Responsabilidad** | Validación Pydantic + generación Typst + PDF |
| **Actualización** | Manual, vía actualización del directorio `rendercv/` |
| **Fallback** | Si RenderCV falla, el servicio retorna 500 |

## 7. Seguridad

- **No expuesto públicamente**: Solo accesible desde red interna Docker.
- **Sin autenticación**: Confiar en aislamiento de red.
- **Sin datos sensibles persistentes**: Los datos de CV son efímeros.
- **Input sanitization**: RenderCV valida y sanitiza el input vía Pydantic.
- **No se exponen stack traces**: Los errores internos retornan mensajes genéricos.

## 8. Operación

### 8.1 Deploy
- **Runtime**: Docker container con python:3.12-slim
- **Puerto**: 8000
- **Health check**: `GET /health`
- **Restart policy**: always

### 8.2 Observabilidad
- **Logs**: stdout/stderr (estructurados JSON)
- **Health**: `GET /health`
- **Métricas**: `GET /metrics` expone métricas Prometheus:
  - `render_requests_total` (counter) con labels `status` (success/error)
  - `render_duration_seconds` (histogram) con buckets `[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]` y labels `status`
  - `render_errors_total` (counter) con labels `error_type` (validation_error, user_error, internal_error)
- **Graceful Shutdown**: Uvicorn configurado con `--timeout-graceful-shutdown 30`

### 8.3 Configuración
| Variable | Default | Descripción |
|---|---|---|
| `PORT` | 8000 | Puerto de escucha |
| `RENDER_TIMEOUT` | 30 | Timeout en segundos para generación PDF |
| `LOG_LEVEL` | INFO | Nivel de logging |
| `METRICS_ENABLED` | true | Habilitar endpoint de métricas Prometheus |

## 9. Estrategia de Tests

| Tipo | Herramienta | Umbral | Cobertura |
|---|---|---|---|
| Unit | pytest | 85% | Services, core |
| Integration | pytest + httpx | N/A | Endpoints completos |
| Schema | pytest | N/A | Validación de payloads |

**Exclusiones de cobertura**:
- `api/schemas.py` (DTOs puros)
- `rendercv/` (librería vendor, no testeamos código externo)
- `__init__.py` files

## 10. Incrementos Planificados

| # | Nombre | Estado | Descripción |
|---|---|---|---|
| 001 | `foundation-and-hardening` | `implemented` | Contratos, error alignment, health, tests, schema validation |
| 002 | `production-readiness` | `implemented` | Métricas, graceful shutdown, Docker hardening, docs |

## 11. Decisiones Arquitectónicas

| Decisión | Razonamiento | ADR |
|---|---|---|
| Mantener Python + RenderCV | No hay equivalente Go maduro para generación ATS-friendly PDFs | ADR-001 (workspace) |
| RenderCV embebido como vendor | Evitar dependencia de pip package inestable; control total de versión | Esta spec |
| Sin persistencia | Los PDFs son efímeros; ms-resume maneja almacenamiento si necesita cache | Esta spec |
| Sin autenticación HTTP | Servicio solo en red interna Docker; aislamiento de red es suficiente | Esta spec |
| Error contract alineado al workspace | Los frontends consumen formato de error estandarizado vía ms-resume | Integration Map |

## 12. Deuda Técnica

| Deuda | Impacto | Plan de Mitigación | Incremento | Estado |
|---|---|---|---|---|
| `RenderRequest` es `dict[str, Any]` sin validación | OpenAPI inútil, errores tardíos | Schema Pydantic estricto en Incremento 1 | 001 | ✅ Resuelta |
| Error response no alineado al workspace | Inconsistencia en manejo de errores | Migrar a `ApiErrorResponse` en Incremento 1 | 001 | ✅ Resuelta |
| Sin tests | Regresiones silenciosas | pytest + httpx en Incremento 1 | 001 | ✅ Resuelta |
| Sin health check | No hay forma de verificar readiness | `GET /health` en Incremento 1 | 001 | ✅ Resuelta |
| Sin métricas | No hay visibilidad de performance | Prometheus metrics en Incremento 2 | 002 | ✅ Resuelta |
