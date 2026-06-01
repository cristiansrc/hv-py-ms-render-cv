# Delta Spec - Incremento 002: production-readiness

**Parent**: Master Spec (`docs/specs/master-spec.md`)
**Depends on**: Incremento 001 (`foundation-and-hardening`)
**Lifecycle Status**: `implemented`
**Created**: 2026-05-31
**Author**: planner

---

## 1. Contexto

Una vez que el Incremento 001 establece los contratos, validación, tests y error handling, este incremento se enfoca en la operabilidad del servicio en producción: métricas, graceful shutdown, hardening de Docker y documentación.

## 2. Impacto en Master Spec

| Sección Master Spec | Cambio |
|---|---|
| Sección 8 (Operación) | Se agregan métricas Prometheus y graceful shutdown |
| Sección 8.3 (Configuración) | Se agregan variables de métricas |
| Sección 12 (Deuda Técnica) | Se resuelve deuda de métricas |

## 3. Requisitos

### 3.1 R-008: Métricas Prometheus
**Descripción**: Exponer métricas de rendimiento del servicio para monitoreo.

**Acceptance Criteria**:
- [ ] Endpoint `GET /metrics` expone métricas en formato Prometheus (text/plain)
- [ ] Métrica `render_requests_total` (counter) con labels: `status` (success/error)
- [ ] Métrica `render_duration_seconds` (histogram) con buckets: 0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0
- [ ] Métrica `render_errors_total` (counter) con labels: `error_type` (validation_error, user_error, internal_error)
- [ ] Dependencia `prometheus-client` agregada a `requirements.txt`
- [ ] Las métricas no incluyen datos sensibles del payload (name, email, etc.)
- [ ] Middleware de métricas captura duración de requests a `POST /render`
- [ ] Variable de entorno `METRICS_ENABLED` controla si el endpoint responde (default `true`)
- [ ] Tests: `tests/test_metrics.py` verifica que `/metrics` retorna 200 con contenido `text/plain`
- [ ] Tests: verifica que `render_requests_total` incrementa tras request exitoso

### 3.2 R-009: Graceful Shutdown
**Descripción**: El servicio debe manejar señales de shutdown de forma ordenada.

**Acceptance Criteria**:
- [ ] Uvicorn configurado con `--timeout-graceful-shutdown` (default 30s)
- [ ] Requests en curso se completan antes de shutdown
- [ ] Uvicorn con `--timeout-graceful-shutdown` rechaza nuevas conexiones TCP durante shutdown (aceptable para red interna Docker; el upstream hv-go-ms-resume recibe connection refused y debe reintentar)
- [ ] Log de inicio y fin de shutdown

### 3.3 R-010: Docker Hardening
**Descripción**: Endurecer la imagen Docker para producción.

**Acceptance Criteria**:
- [ ] Container corre como non-root user (`rendercv`, UID 1000, GID 1000)
- [ ] HEALTHCHECK se mantiene del Incremento 001 (no modificar)
- [ ] No se usa multi-stage build. `python:3.12-slim` ya es suficientemente pequeña para un proyecto personal monousuario; el beneficio de reducir tamaño no justifica la complejidad adicional
- [ ] `.dockerignore` excluye `__pycache__/`, `.git/`, `tests/`, `docs/`, `.coverage`, `.pytest_cache/`, `htmlcov/`, `.venv/`, `venv/`, `*.egg-info/`, `.vscode/`, `.idea/`
- [ ] Imagen final no incluye dev dependencies (pytest, httpx, pytest-cov, pytest-asyncio)
- [ ] `requirements.txt` separado en prod y dev dependencies (comentarios claros)

### 3.4 R-011: Documentación
**Descripción**: README completo para desarrolladores y operadores.

**Acceptance Criteria**:
- [ ] `README.md` con:
  - Descripción del servicio
  - Arquitectura y posicionamiento en el ecosistema
  - Requisitos previos (Docker, Python 3.12)
  - Desarrollo local con `venv` + `pip`: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
  - Variables de entorno
  - Endpoints con ejemplos
  - Deploy con Docker
- [ ] Diagrama de arquitectura (Mermaid o ASCII)
- [ ] Link a documentación de RenderCV

### 3.5 R-012: Consolidación de Specs
**Descripción**: Consolidar cambios de incrementos en la Master Spec.

**Acceptance Criteria**:
- [ ] Master Spec actualizada con métricas, graceful shutdown y Docker hardening (Sección 8)
- [ ] Master Spec sección 8.3 actualizada con variable `METRICS_ENABLED`
- [ ] Deuda técnica de métricas marcada como ✅ Resuelta en Master Spec sección 12
- [ ] Incremento 002 marcado como `implemented` en Master Spec sección 10
- [ ] Delta Spec 002 marcada como `implemented`

## 4. Integraciones

Sin cambios en integraciones externas.

## 5. Seguridad

- El endpoint `/metrics` debe estar protegido o solo accesible desde red interna (ya lo está por diseño).
- Las métricas no deben exponer datos de CV ni PII.

## 6. Operación

### 6.1 Nuevas Variables de Entorno

| Variable | Default | Descripción |
|---|---|---|
| `METRICS_ENABLED` | `true` | Habilitar endpoint de métricas |

### 6.2 Healthcheck Docker

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
```

## 7. Archivos a Crear/Modificar

### Crear
| Archivo | Descripción |
|---|---|
| `api/core/metrics.py` | Configuración de métricas Prometheus + middleware de duración |
| `api/routers/metrics.py` | Endpoint `GET /metrics` |
| `tests/test_metrics.py` | Tests de métricas (endpoint 200, counter incrementa, histogram registra) |
| `.dockerignore` | Exclusiones de build Docker |
| `README.md` | Documentación del proyecto |

### Modificar
| Archivo | Cambio |
|---|---|
| `api/main.py` | Agregar router de métricas, middleware de métricas |
| `Dockerfile` | Non-root user (USER rendercv), separar prod/dev dependencies, agregar `--timeout-graceful-shutdown 30` al CMD de uvicorn |
| `requirements.txt` | Agregar `prometheus-client`, separar prod y dev dependencies |
| `docs/specs/master-spec.md` | Consolidar cambios de métricas, graceful shutdown, Docker hardening |

## 8. Términos Prohibidos (Stale Terms Guard)

Los siguientes términos NO deben aparecer en código nuevo del Incremento 002:
- `print()` para logging (usar `api.core.logging`)
- Métricas con datos sensibles: `cv.name`, `cv.email`, `cv.phone`, etc.
- `root` como usuario del container Docker
- Dev dependencies (`pytest`, `httpx`, `pytest-cov`, `pytest-asyncio`) en imagen de producción
- `{"detail": ...}` como formato de error (ya resuelto en Incremento 001)
- Modificar `api/schemas.py` (DTOs del Incremento 001 no cambian)
- Modificar `rendercv/` (librería vendor no se toca)

## 9. Orden de Ejecución Permitido

1. Agregar `prometheus-client` a `requirements.txt` y separar prod/dev dependencies
2. Crear `api/core/metrics.py` con métricas y middleware
3. Crear `api/routers/metrics.py` con endpoint `GET /metrics`
4. Modificar `api/main.py` para integrar router y middleware de métricas
5. Crear `tests/test_metrics.py`
6. Modificar `Dockerfile` con non-root user
7. Crear `.dockerignore`
8. Crear `README.md`
9. Consolidar specs en Master Spec

## 10. Criterios de Cierre

- [ ] Métricas Prometheus funcionales (`GET /metrics` retorna 200 con formato Prometheus)
- [ ] 3 métricas registradas: `render_requests_total`, `render_duration_seconds`, `render_errors_total`
- [ ] Middleware de métricas captura duración de `POST /render`
- [ ] Graceful shutdown configurado (`--timeout-graceful-shutdown 30`)
- [ ] Docker hardening: non-root user, `.dockerignore`, sin dev dependencies en imagen
- [ ] Tests de métricas pasan (`tests/test_metrics.py`)
- [ ] README completo con arquitectura, endpoints, deploy, variables de entorno
- [ ] Specs consolidadas en Master Spec
- [ ] Spec Validator verdict: `ready`
- [ ] Human plan approval: `approved_by_user`
