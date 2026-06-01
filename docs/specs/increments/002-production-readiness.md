# Delta Spec - Incremento 002: production-readiness

**Parent**: Master Spec (`docs/specs/master-spec.md`)
**Depends on**: Incremento 001 (`foundation-and-hardening`)
**Lifecycle Status**: `awaiting-human-plan-approval`
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
- [ ] Endpoint `GET /metrics` expone métricas en formato Prometheus
- [ ] Métrica `render_requests_total` (counter) con labels: `status` (success/error)
- [ ] Métrica `render_duration_seconds` (histogram) con buckets apropiados
- [ ] Métrica `render_errors_total` (counter) con labels: `error_type`
- [ ] Dependencia `prometheus-client` agregada
- [ ] Las métricas no incluyen datos sensibles del payload

### 3.2 R-009: Graceful Shutdown
**Descripción**: El servicio debe manejar señales de shutdown de forma ordenada.

**Acceptance Criteria**:
- [ ] Uvicorn configurado con `--timeout-graceful-shutdown` (default 30s)
- [ ] Requests en curso se completan antes de shutdown
- [ ] Nuevas requests durante shutdown reciben `503 SERVICE_UNAVAILABLE`
- [ ] Log de inicio y fin de shutdown

### 3.3 R-010: Docker Hardening
**Descripción**: Endurecer la imagen Docker para producción.

**Acceptance Criteria**:
- [ ] Container corre como non-root user (`rendercv`)
- [ ] HEALTHCHECK en Dockerfile apunta a `GET /health`
- [ ] Multi-stage build si reduce el tamaño de la imagen final
- [ ] `.dockerignore` excluye `__pycache__`, `.git`, `tests/`, `docs/`
- [ ] Imagen final no incluye dev dependencies

### 3.4 R-011: Documentación
**Descripción**: README completo para desarrolladores y operadores.

**Acceptance Criteria**:
- [ ] `README.md` con:
  - Descripción del servicio
  - Arquitectura y posicionamiento en el ecosistema
  - Requisitos previos (Docker, Python 3.12)
  - Desarrollo local (instalación, ejecución, tests)
  - Variables de entorno
  - Endpoints con ejemplos
  - Deploy con Docker
- [ ] Diagrama de arquitectura (Mermaid o ASCII)
- [ ] Link a documentación de RenderCV

### 3.5 R-012: Consolidación de Specs
**Descripción**: Consolidar cambios de incrementos en la Master Spec.

**Acceptance Criteria**:
- [ ] Master Spec actualizada con decisiones del Incremento 001
- [ ] Deuda técnica resuelta removida del registro
- [ ] Incremento 001 marcado como `closed`
- [ ] Incremento 002 marcado como `closed`

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
| `api/core/metrics.py` | Configuración de métricas Prometheus |
| `api/routers/metrics.py` | Endpoint `/metrics` |
| `.dockerignore` | Exclusiones de build Docker |
| `README.md` | Documentación del proyecto |

### Modificar
| Archivo | Cambio |
|---|---|
| `api/main.py` | Agregar router de métricas, configuración de graceful shutdown |
| `Dockerfile` | Non-root user, HEALTHCHECK, multi-stage |
| `requirements.txt` | Agregar `prometheus-client` |
| `docs/specs/master-spec.md` | Consolidar cambios |

## 8. Orden de Ejecución Permitido

1. Crear `api/core/metrics.py` y `api/routers/metrics.py`
2. Modificar `api/main.py` para integrar métricas
3. Modificar `Dockerfile` con hardening
4. Crear `.dockerignore`
5. Crear `README.md`
6. Consolidar specs

## 9. Criterios de Cierre

- [ ] Métricas Prometheus funcionales
- [ ] Graceful shutdown configurado
- [ ] Docker hardening completado
- [ ] README completo
- [ ] Specs consolidadas
- [ ] Spec Validator verdict: `ready`
- [ ] Human plan approval: `approved_by_user`
