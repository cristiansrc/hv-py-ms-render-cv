# Shared Context - Incremento 002: production-readiness

**Increment**: `002-production-readiness`
**Spec**: `docs/specs/increments/002-production-readiness.md`
**Master Spec**: `docs/specs/master-spec.md`
**OpenAPI**: `docs/api/openapi.yaml`
**Current Status**: `implemented`
**Created**: 2026-06-01
**Last Updated**: 2026-06-01

---

## Current status

`implemented` - Incremento 002 implementado por Executor el 2026-06-01.

## Canonical artifacts

| Artefacto | Ruta | Estado |
|---|---|---|
| Master Spec | `docs/specs/master-spec.md` | ✅ `implemented` |
| Delta Spec 001 | `docs/specs/increments/001-foundation-and-hardening.md` | ✅ `implemented` |
| Delta Spec 002 | `docs/specs/increments/002-production-readiness.md` | ✅ `validated-not-executed` |
| OpenAPI Contract | `docs/api/openapi.yaml` | ✅ Creado (v3.1.0) |
| Shared Context 001 | `docs/specs/.working/001-foundation-and-hardening-sdd-context.md` | ✅ Cerrado |
| Shared Context 002 | `docs/specs/.working/002-production-readiness-sdd-context.md` | ✅ Este archivo |
| Task Board 001 | `docs/specs/tasks/001-foundation-and-hardening-task-board.md` | ✅ 15/15 done |
| Task Board 002 | `docs/specs/tasks/002-production-readiness-task-board.md` | ✅ Creado (9 tareas, status: todo) |

## Artifact evidence

### Baseline (código existente del Incremento 001)

| Campo | Artefacto | Evidencia | Estado |
|---|---|---|---|
| api/main.py | `api/main.py` | 65 líneas, create_app() con middleware, routers, handlers | ✅ Implementado |
| api/schemas.py | `api/schemas.py` | 113 líneas, Pydantic estricto, extra="forbid" | ✅ Implementado |
| api/core/errors.py | `api/core/errors.py` | 160 líneas, 5 handlers ApiErrorResponse | ✅ Implementado |
| api/core/trace.py | `api/core/trace.py` | TraceMiddleware con UUID4 | ✅ Implementado |
| api/core/logging.py | `api/core/logging.py` | setup_logging() JSON estructurado | ✅ Implementado |
| api/core/typst_check.py | `api/core/typst_check.py` | is_typst_available() con cache 30s | ✅ Implementado |
| api/routers/health.py | `api/routers/health.py` | GET /health con 200/503 | ✅ Implementado |
| api/routers/render.py | `api/routers/render.py` | POST /render con RenderRequest estricto | ✅ Implementado |
| Dockerfile | `Dockerfile` | 19 líneas, HEALTHCHECK incluido, corre como root | ⚠️ Requiere hardening (R-010) |
| requirements.txt | `requirements.txt` | 16 líneas, sin prometheus-client | ⚠️ Requiere prometheus-client (R-008) |
| tests/ | `tests/` | conftest.py, test_health.py, test_render.py, test_error_handlers.py | ✅ Implementado |
| pyproject.toml | `pyproject.toml` | pytest + cov configurado | ✅ Implementado |
| .gitignore | `.gitignore` | 59 líneas, excludes .env, *.log, logs/, /tmp/rendercv_output/ | ✅ Mejorado en Incremento 002 |

### Artefactos faltantes (a crear en Incremento 002)

| Campo | Artefacto esperado | Estado |
|---|---|---|
| api/core/metrics.py | Configuración de métricas Prometheus | ❌ No existe |
| api/routers/metrics.py | Endpoint GET /metrics | ❌ No existe |
| .dockerignore | Exclusiones de build Docker | ❌ No existe |
| README.md | Documentación del proyecto | ❌ No existe |
| tests/test_metrics.py | Tests de métricas | ❌ No existe (a crear en Incremento 002) |

### Delta Spec 002 verification

| Campo | Artefacto | Evidencia | Estado |
|---|---|---|---|
| R-008 Métricas Prometheus | `docs/specs/increments/002-production-readiness.md` Sección 3.1 | 10 AC, counter + histogram (buckets explícitos) + error counter + tests | ✅ Corregido |
| R-009 Graceful Shutdown | Sección 3.2 | 4 AC, uvicorn timeout, 503 durante shutdown | ✅ pass |
| R-010 Docker Hardening | Sección 3.3 | 6 AC, non-root UID/GID, HEALTHCHECK mantenido, .dockerignore explícito, prod/dev separados | ✅ Corregido |
| R-011 Documentación | Sección 3.4 | 3 AC, README completo, diagrama, link RenderCV | ✅ pass |
| R-012 Consolidación | Sección 3.5 | 5 AC, master spec update, deuda resuelta, incremento implemented | ✅ Corregido |
| Variables de entorno | Sección 6.1 | METRICS_ENABLED default true | ✅ pass |
| Archivos a crear | Sección 7 | 5 archivos nuevos (incluye tests), 4 a modificar | ✅ Corregido |
| Stale terms guard | Sección 8 | 7 términos prohibidos explícitos | ✅ Corregido |
| Orden de ejecución | Sección 9 | 9 pasos ordenados | ✅ Corregido |
| Criterios de cierre | Sección 10 | 9 criterios explícitos | ✅ Corregido |

## Spec Validator Approval

**verdict**: `ready`
**reviewed_at**: 2026-06-01T12:00:00Z
**validator_agent**: spec-validator
**artifact_set_reviewed**:
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/docs/specs/master-spec.md`
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/docs/specs/increments/002-production-readiness.md`
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/docs/api/openapi.yaml`
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/docs/specs/.working/002-production-readiness-sdd-context.md`
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/docs/specs/.working/001-foundation-and-hardening-sdd-context.md`
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/docs/specs/technical_debt.md`
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/.gitignore`
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/Dockerfile`
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/requirements.txt`
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/api/main.py`
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/api/schemas.py`
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/api/core/errors.py`
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/api/routers/render.py`
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/api/routers/health.py`
**summary**: |
  Re-validación completa post-remediación (2026-06-01).
  Los 12 hallazgos originales verificados como corregidos en disco.
  2 inconsistencias de metadata en shared context corregidas durante re-validación (stale status en Canonical artifacts table, stale decision en Decisions locked).
  OpenAPI 3.1.0 consistente con Delta Spec 002. Error contract alineado a fastapi-rest-error-response-standards.
  Lifecycle unificado a awaiting-human-plan-approval. Especificación suficientemente completa para implementación segura.
**invalidated_by_changes_since**: none

## Decisions locked

1. **Métricas**: Se usa `prometheus-client` como librería oficial. No se usa `starlette-exporter` ni terceros.
2. **Métricas custom**: 3 métricas: `render_requests_total` (counter), `render_duration_seconds` (histogram), `render_errors_total` (counter).
3. **Graceful shutdown**: Se configura via flag de uvicorn `--timeout-graceful-shutdown 30`. No se requiere middleware custom.
4. **Docker non-root**: Usuario `rendercv` con UID 1000, grupo `rendercv` con GID 1000.
5. **HEALTHCHECK**: Ya existe del Incremento 001. Se mantiene sin cambios.
6. **Multi-stage build**: No se usa. `python:3.12-slim` ya es suficientemente pequeña; el beneficio de reducir tamaño no justifica la complejidad adicional. (Decisión del usuario, 2026-06-01)
7. **No se modifica rendercv/**: La librería vendor no se toca en este incremento.
8. **No se modifica api/schemas.py**: Los DTOs del Incremento 001 no cambian.

## Validator findings

Reporte completo de spec-validator (2026-06-01): 12 hallazgos detectados (2 HIGH, 7 MEDIUM, 3 LOW).

Ver sección `## Resolved findings` para el detalle de correcciones aplicadas.

## Resolved findings

| # | Hallazgo | Severidad | Tipo | Iteración | Archivo Modificado | Resultado |
|---|---|---|---|---|---|---|
| 3 | Lifecycle status inconsistente (awaiting-human-plan-approval vs draft) | MEDIUM | mechanical | IT-1 | `docs/specs/increments/002-production-readiness.md` L5, `docs/specs/master-spec.md` L247 | ✅ Corregido a `draft` |
| 5 | Falta `## Resolved findings` en Shared Context 002 | MEDIUM | mechanical | IT-2 | `docs/specs/.working/002-production-readiness-sdd-context.md` | ✅ Agregada sección |
| 7 | Nota stale "no listado en spec" en tabla evidencia | MEDIUM | mechanical | IT-3 | `docs/specs/.working/002-production-readiness-sdd-context.md` L56 | ✅ Corregido a "a crear en Incremento 002" |
| 1 | OpenAPI no documenta GET /metrics | HIGH | contract-drift | IT-4 | `docs/api/openapi.yaml` | ✅ Agregado path /metrics con responses 200/503 |
| 2 | OpenAPI no documenta 503 en POST /render | HIGH | contract-drift | IT-5 | `docs/api/openapi.yaml` | ✅ Agregada response 503 + componente ServiceUnavailable |
| 4 | Graceful shutdown flag no listado en tabla "Modificar" | MEDIUM | spec-gap | IT-6 | `docs/specs/increments/002-production-readiness.md` | ✅ Agregado en tabla Dockerfile |
| 8 | Ambigüedad 503 en R-009 AC#3 (connection refused vs HTTP 503) | MEDIUM | spec-prose | IT-7 | `docs/specs/increments/002-production-readiness.md` L46 | ✅ Clarificado: uvicorn rechaza conexiones TCP, aceptable para red interna |
| 10 | R-011 AC "Desarrollo local" vago sobre tooling | LOW | spec-prose | IT-8 | `docs/specs/increments/002-production-readiness.md` | ✅ Especificado venv + pip |
| 11 | rejected_value sin tipo explícito en OpenAPI | LOW | consistency | IT-9 | `docs/api/openapi.yaml` | ✅ oneOf con tipos explícitos |
| 12 | .gitignore no verificado como artefacto canónico | LOW | mechanical | IT-10 | `docs/specs/.working/002-production-readiness-sdd-context.md` | ✅ Agregado a tabla de evidencia |
| 6 | Falta `docs/specs/technical_debt.md` | MEDIUM | missing-artifact | Decisión usuario | `docs/specs/technical_debt.md` | ✅ Creado — contenido: "Active Technical Debt: none" |
| 9 | Multi-stage build delegado al Executor (R-010 AC#5) | MEDIUM | design-decision | Decisión usuario | `docs/specs/increments/002-production-readiness.md` R-010 AC#5 | ✅ Actualizado: sin multi-stage build. python:3.12-slim suficiente. |

### Hallazgos pendientes de decisión

Ninguno. Ambos hallazgos bloqueados fueron resueltos por decisión del usuario (2026-06-01).

## Open questions

> Resueltas durante la corrección de la Delta Spec:
> 1. **Tests para métricas**: ✅ Resuelto — R-008 ahora incluye 2 AC de tests y `tests/test_metrics.py` en tabla de archivos a crear.
> 2. **Multi-stage build**: ✅ Resuelto — no se usa. `python:3.12-slim` es suficientemente pequeña para un proyecto personal monousuario (decisión del usuario, 2026-06-01).
> 3. **Protección /metrics**: ✅ Resuelto — Sección 5 confirma aislamiento de red es suficiente.

## Stale terms guard

Los siguientes términos NO deben usarse en código nuevo del Incremento 002:
- `print()` para logging (usar el módulo `api.core.logging`)
- `{"detail": ...}` como formato de error
- Métricas con datos sensibles (cv.name, cv.email, etc.)
- `root` como usuario del container
- Dev dependencies en imagen de producción

## Human Plan Approval

Aprobado por el usuario (cristiansrc) el 2026-06-01. Se autoriza la descomposición de tareas e implementación.

## Next action

1. ✅ **Delta Spec 002 corregida** — 10 hallazgos resueltos por Spec Remediator.
2. ✅ **Finding #6**: `docs/specs/technical_debt.md` creado con contenido mínimo.
3. ✅ **Finding #9**: R-010 AC#5 actualizado — sin multi-stage build por decisión del usuario.
4. ✅ **Shared context actualizado** — Todos los hallazgos resueltos, metadata corregida.
5. ✅ **Re-validación completada** — Spec Validator verdict: `ready`.
6. ✅ **Human Plan Approval** — Aprobado por el usuario (cristiansrc) el 2026-06-01.
7. ✅ **Task Board creado** — 9 tareas atómicas descompuestas por Task Decomposer.
8. ⏳ **Pendiente**: Executor → implementar tareas T-001 a T-009.
