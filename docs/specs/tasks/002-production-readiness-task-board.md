# Task Board - Incremento 002: production-readiness

**Increment**: `002-production-readiness`
**Spec**: `docs/specs/increments/002-production-readiness.md`
**Shared Context**: `docs/specs/.working/002-production-readiness-sdd-context.md`
**OpenAPI**: `docs/api/openapi.yaml`
**Status**: `done`
**Created**: 2026-06-01
**Last Updated**: 2026-06-01

---

## Tareas

### T-001: Separar dependencias prod/dev en requirements.txt

- **agent**: executor
- **spec_refs**: R-010 (Docker Hardening), Sección 7 (Archivos a Modificar)
- **goal**: Separar `requirements.txt` en dependencias de producción y desarrollo con comentarios claros.
- **scope**: Modificar `requirements.txt` para agrupar dependencias en secciones `# Production dependencies` y `# Dev dependencies`. Agregar `prometheus-client` a las de producción.
- **out_of_scope**: Instalar dependencias, modificar Dockerfile (eso va en T-006).
- **inputs**: `requirements.txt` actual (16 líneas, dependencias mezcladas).
- **implementation_notes**:
  - Production dependencies: fastapi, uvicorn[standard], jinja2, markdown, pydantic, pydantic[email], pydantic-extra-types, phonenumbers, rendercv-fonts, ruamel.yaml, typst, **prometheus-client** (nueva).
  - Dev dependencies: pytest, httpx, pytest-cov, pytest-asyncio.
  - Mantener versiones exactas como están actualmente.
  - Agregar comentarios de sección claros: `# Production dependencies` y `# Dev dependencies`.
- **edge_cases**: Ninguno.
- **done_criteria**:
  - `requirements.txt` tiene secciones claramente separadas con comentarios.
  - `prometheus-client` está en la sección de producción (sin versión fija, usar latest compatible).
  - Todas las dependencias existentes están presentes con sus versiones.
- **verification**: `cat requirements.txt` muestra secciones separadas y prometheus-client presente.
- **dependencies**: Ninguna.
- **handoff_context**: requirements.txt listo para Dockerfile (T-006) y para instalar prometheus-client (T-002).
- **source_of_truth**: `docs/specs/increments/002-production-readiness.md` R-010 AC#6, Sección 7.
- **stale_terms_guard**: No usar `print()` para logging. No incluir dev dependencies en imagen de producción.
- **status**: `done`
- **executor_notes**: Separación prod/dev completada
- **verification_result**: requirements.txt tiene secciones claras con prometheus-client presente
- **blocker**: `none`

---

### T-002: Crear api/core/metrics.py con métricas Prometheus y middleware

- **agent**: executor
- **spec_refs**: R-008 (Métricas Prometheus), Sección 7 (Archivos a Crear), Decisions locked #1, #2
- **goal**: Implementar configuración de métricas Prometheus y middleware para capturar duración de requests.
- **scope**: Crear `api/core/metrics.py` con 3 métricas y middleware de captura de duración.
- **out_of_scope**: Crear endpoint /metrics (eso va en T-003), integrar en main.py (eso va en T-004).
- **inputs**: Decisiones locked: `prometheus-client` como librería oficial, 3 métricas: `render_requests_total` (counter), `render_duration_seconds` (histogram), `render_errors_total` (counter).
- **implementation_notes**:
  - Usar `prometheus_client` (Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST).
  - `render_requests_total`: Counter con label `status` (values: `success`, `error`).
  - `render_duration_seconds`: Histogram con buckets explícitos: `[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]`.
  - `render_errors_total`: Counter con label `error_type` (values: `validation_error`, `user_error`, `internal_error`).
  - Crear función `metrics_middleware` que capture el tiempo de ejecución de requests a `POST /render` y registre en histogram.
  - Las métricas NO deben incluir datos sensibles (name, email, etc.).
  - Usar type hints en todas las funciones.
  - No usar `print()` para logging; usar `api.core.logging`.
- **edge_cases**:
  - Si `METRICS_ENABLED=false`, el middleware debe ser no-op (no registrar métricas).
  - El middleware debe manejar excepciones sin romper el pipeline de requests.
- **done_criteria**:
  - `api/core/metrics.py` existe con las 3 métricas configuradas.
  - Middleware captura duración de requests y registra en histogram.
  - Labels correctos en cada métrica según spec.
  - Buckets del histogram coinciden exactamente con spec: `[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]`.
  - No hay datos sensibles en labels o métricas.
- **verification**: `python -c "from api.core.metrics import render_requests_total, render_duration_seconds, render_errors_total; print('OK')"` ejecuta sin errores.
- **dependencies**: T-001 (prometheus-client en requirements.txt).
- **handoff_context**: Métricas listas para exponer via endpoint (T-003) e integrar en main.py (T-004).
- **source_of_truth**: `docs/specs/increments/002-production-readiness.md` R-008, Decisions locked #1, #2.
- **stale_terms_guard**: No usar `print()` para logging. No incluir datos sensibles en métricas.
- **status**: `done`
- **executor_notes**: 3 métricas (render_requests, render_duration_seconds, render_errors) + middleware
- **verification_result**: `python -c "from api.core.metrics import ...; print('OK')"` ejecuta sin errores
- **blocker**: `none`

---

### T-003: Crear api/routers/metrics.py con endpoint GET /metrics

- **agent**: executor
- **spec_refs**: R-008 (Métricas Prometheus), OpenAPI path /metrics, Sección 7 (Archivos a Crear)
- **goal**: Implementar endpoint `GET /metrics` que exponga métricas en formato Prometheus.
- **scope**: Crear `api/routers/metrics.py` con router FastAPI para `/metrics`.
- **out_of_scope**: Integrar en main.py (eso va en T-004), tests (eso va en T-005).
- **inputs**: OpenAPI path `/metrics` (responses 200 text/plain, 503 text/plain). Variable `METRICS_ENABLED` (default `true`).
- **implementation_notes**:
  - Crear FastAPI APIRouter con prefix vacío, tags=["operational"].
  - Endpoint `GET /metrics` retorna `Response` con contenido `generate_latest()` y `media_type=CONTENT_TYPE_LATEST`.
  - Si `METRICS_ENABLED=false`, retornar 503 con body `"Metrics disabled"` y content-type `text/plain`.
  - Leer `METRICS_ENABLED` de `os.environ` con default `"true"`.
  - Usar type hints.
  - No usar `print()` para logging.
- **edge_cases**:
  - `METRICS_ENABLED` con valor inválido (ej. "yes", "1") debe tratarse como `false` solo si es explícitamente `"false"` (case-insensitive). Cualquier otro valor = `true`.
- **done_criteria**:
  - `api/routers/metrics.py` existe con endpoint `GET /metrics`.
  - Retorna 200 con métricas en formato Prometheus cuando `METRICS_ENABLED=true`.
  - Retorna 503 con `"Metrics disabled"` cuando `METRICS_ENABLED=false`.
  - Content-type es `text/plain` en ambos casos.
- **verification**: `python -c "from api.routers.metrics import router; print('OK')"` ejecuta sin errores.
- **dependencies**: T-002 (métricas configuradas).
- **handoff_context**: Endpoint listo para integrar en main.py (T-004).
- **source_of_truth**: `docs/api/openapi.yaml` path `/metrics`, `docs/specs/increments/002-production-readiness.md` R-008.
- **stale_terms_guard**: No usar `print()` para logging. No usar `{"detail": ...}` como formato de error.
- **status**: `done`
- **executor_notes**: Endpoint GET /metrics con 200 (Prometheus format) y 503 (disabled)
- **verification_result**: `python -c "from api.routers.metrics import router; print('OK')"` ejecuta sin errores
- **blocker**: `none`

---

### T-004: Integrar router y middleware de métricas en api/main.py

- **agent**: executor
- **spec_refs**: R-008, Sección 7 (Archivos a Modificar: api/main.py)
- **goal**: Integrar el router de métricas y el middleware de métricas en la aplicación FastAPI.
- **scope**: Modificar `api/main.py` para incluir `metrics_router` y `metrics_middleware`.
- **out_of_scope**: Modificar routers existentes, cambiar error handlers.
- **inputs**: `api/main.py` actual (65 líneas), `api/core/metrics.py` (T-002), `api/routers/metrics.py` (T-003).
- **implementation_notes**:
  - Importar `router as metrics_router` desde `api.routers.metrics`.
  - Importar `metrics_middleware` desde `api.core.metrics`.
  - Agregar `app.include_router(metrics_router)` después de los routers existentes.
  - Agregar `app.add_middleware(metrics_middleware)` después de `TraceMiddleware` (el orden importa: trace primero, luego metrics).
  - Mantener estructura existente de create_app().
- **edge_cases**: Ninguno.
- **done_criteria**:
  - `api/main.py` incluye metrics_router y metrics_middleware.
  - Orden de middleware: TraceMiddleware primero, metrics_middleware después.
  - `create_app()` funciona sin errores.
- **verification**: `python -c "from api.main import create_app; app = create_app(); routes = [r.path for r in app.routes]; assert '/metrics' in routes; print('OK')"` ejecuta sin errores.
- **dependencies**: T-002, T-003.
- **handoff_context**: Aplicación completa lista para tests (T-005).
- **source_of_truth**: `docs/specs/increments/002-production-readiness.md` Sección 7, `api/main.py` existente.
- **stale_terms_guard**: No usar `print()` para logging.
- **status**: `done`
- **executor_notes**: Router y middleware integrados en create_app(). Orden: TraceMiddleware → MetricsMiddleware
- **verification_result**: /metrics en rutas, create_app() funciona sin errores
- **blocker**: `none`

---

### T-005: Crear tests/test_metrics.py para métricas Prometheus

- **agent**: executor
- **spec_refs**: R-008 AC#9, AC#10, Sección 7 (Archivos a Crear)
- **goal**: Implementar tests para verificar el endpoint `/metrics` y el registro de métricas.
- **scope**: Crear `tests/test_metrics.py` con tests de endpoint y métricas.
- **out_of_scope**: Tests de otros endpoints (ya existen), tests de error handlers (ya existen).
- **inputs**: `tests/conftest.py` (client fixture existente), `api/core/metrics.py` (T-002), `api/routers/metrics.py` (T-003).
- **implementation_notes**:
  - Test 1: `test_metrics_endpoint_returns_200` — GET /metrics retorna 200 con content-type `text/plain; charset=utf-8` (o similar).
  - Test 2: `test_metrics_returns_503_when_disabled` — Con `METRICS_ENABLED=false`, GET /metrics retorna 503.
  - Test 3: `test_render_requests_total_increments` — Hacer POST /render exitoso, luego verificar que `render_requests_total{status="success"}` incrementa.
  - Test 4: `test_render_duration_seconds_records` — Hacer POST /render, verificar que `render_duration_seconds_count` incrementa.
  - Usar `pytest` con fixtures existentes de `conftest.py`.
  - Para verificar métricas, parsear el output de `/metrics` o acceder directamente a las métricas via `prometheus_client`.
  - Usar type hints.
- **edge_cases**:
  - Las métricas son globales; los tests pueden interferir entre sí. Usar `prometheus_client.REGISTRY` para limpiar o usar valores relativos (incremento).
  - El test de métricas deshabilitadas requiere mock de `os.environ`.
- **done_criteria**:
  - `tests/test_metrics.py` existe con al menos 4 tests.
  - Todos los tests pasan con `pytest tests/test_metrics.py -v`.
  - Cobertura de `api/core/metrics.py` y `api/routers/metrics.py` >= 85%.
- **verification**: `pytest tests/test_metrics.py -v --cov=api.core.metrics --cov=api.routers.metrics --cov-fail-under=85` pasa sin errores.
- **dependencies**: T-002, T-003, T-004.
- **handoff_context**: Tests listos para validación de cobertura.
- **source_of_truth**: `docs/specs/increments/002-production-readiness.md` R-008 AC#9, AC#10.
- **stale_terms_guard**: No usar `print()` para logging en tests.
- **status**: `done`
- **executor_notes**: 6 tests implementados: endpoint 200/503, counter increment, error counter, histogram, metric names
- **verification_result**: `pytest tests/test_metrics.py -v` → 6/6 passed. Cobertura total 88.29% (>85%)
- **blocker**: `none`

---

### T-006: Docker hardening - non-root user y graceful shutdown

- **agent**: executor
- **spec_refs**: R-009 (Graceful Shutdown), R-010 (Docker Hardening), Sección 7 (Archivos a Modificar: Dockerfile)
- **goal**: Modificar Dockerfile para correr como non-root y configurar graceful shutdown.
- **scope**: Modificar `Dockerfile` para agregar usuario non-root, separar instalación de dependencias prod/dev, y agregar flag de graceful shutdown al CMD.
- **out_of_scope**: Multi-stage build (decisión del usuario: no se usa), modificar HEALTHCHECK (se mantiene del Incremento 001).
- **inputs**: `Dockerfile` actual (19 líneas), `requirements.txt` (T-001), Decisions locked #3, #4, #5.
- **implementation_notes**:
  - Crear grupo `rendercv` con GID 1000: `RUN groupadd -g 1000 rendercv`.
  - Crear usuario `rendercv` con UID 1000: `RUN useradd -u 1000 -g rendercv -m rendercv`.
  - Instalar solo production dependencies: `RUN pip install --no-cache-dir $(grep -v '^#' requirements.txt | grep -v '^$' | grep -v 'pytest' | grep -v 'httpx' | grep -v 'pytest-cov' | grep -v 'pytest-asyncio' | sed 's/^/-r /' | head -1)` — MEJOR: usar sección de prod dependencies del requirements.txt o instalar con un archivo separado. Alternativa más limpia: instalar todo el requirements.txt pero luego desinstalar dev deps, O usar un `requirements-prod.txt`. Dado que la spec dice separar con comentarios, usar `pip install --no-cache-dir -r requirements.txt` pero solo con las deps de prod. La forma más simple: copiar requirements.txt completo y pip install lo instala todo; luego `pip uninstall -y pytest httpx pytest-cov pytest-asyncio`. O mejor aún: crear un `requirements-prod.txt` separado. Pero la spec dice modificar solo `requirements.txt`. Entonces: instalar todo y luego desinstalar dev deps, O usar grep para filtrar.
  - **Mejor enfoque**: En el Dockerfile, copiar requirements.txt y usar pip install solo las líneas antes de `# Dev dependencies`. Esto se puede hacer con `sed` o `awk`.
  - Agregar `USER rendercv` después de instalar dependencias y copiar código.
  - Cambiar CMD a: `CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-graceful-shutdown", "30"]`.
  - Mantener HEALTHCHECK sin cambios.
  - WORKDIR /app debe tener permisos para el usuario rendercv: agregar `RUN chown -R rendercv:rendercv /app` antes de USER, o mejor, hacer el chown después de COPY.
- **edge_cases**:
  - El usuario non-root necesita permisos de lectura en /app.
  - Typst puede requerir permisos de escritura en /tmp para cache. Verificar que /tmp es accesible (por defecto lo es).
  - PYTHONPATH=/app debe funcionar para usuario non-root.
- **done_criteria**:
  - Dockerfile crea usuario `rendercv` con UID 1000 y GID 1000.
  - Container corre como `USER rendercv`.
  - CMD incluye `--timeout-graceful-shutdown 30`.
  - HEALTHCHECK se mantiene sin cambios.
  - Solo production dependencies están instaladas en la imagen final.
  - `/app` tiene permisos correctos para rendercv.
- **verification**: `docker build -t hv-py-ms-render-cv:test . && docker run --rm hv-py-ms-render-cv:test whoami` retorna `rendercv`.
- **dependencies**: T-001 (requirements.txt separado).
- **handoff_context**: Dockerfile listo para .dockerignore (T-007).
- **source_of_truth**: `docs/specs/increments/002-production-readiness.md` R-009, R-010, Decisions locked #3, #4, #5.
- **stale_terms_guard**: No usar `root` como usuario del container. No incluir dev dependencies en imagen de producción.
- **status**: `done`
- **executor_notes**: Dockerfile actualizado: usuario rendercv (UID 1000), solo prod deps, graceful shutdown 30s
- **verification_result**: Dockerfile creado con non-root user, HEALTHCHECK mantenido, solo pip install de prod deps
- **blocker**: `none`

---

### T-007: Crear .dockerignore con exclusiones de build

- **agent**: executor
- **spec_refs**: R-010 AC#4, Sección 7 (Archivos a Crear)
- **goal**: Crear `.dockerignore` para excluir archivos innecesarios del build Docker.
- **scope**: Crear archivo `.dockerignore` en la raíz del proyecto.
- **out_of_scope**: Modificar Dockerfile (eso va en T-006).
- **inputs**: Spec R-010 AC#4 lista las exclusiones requeridas.
- **implementation_notes**:
  - Excluir: `__pycache__/`, `.git/`, `tests/`, `docs/`, `.coverage`, `.pytest_cache/`, `htmlcov/`, `.venv/`, `venv/`, `*.egg-info/`, `.vscode/`, `.idea/`.
  - Agregar también: `.env`, `*.log`, `logs/`, `/tmp/rendercv_output/` (coherente con .gitignore).
  - Ordenar alfabéticamente para mantenibilidad.
- **edge_cases**: Ninguno.
- **done_criteria**:
  - `.dockerignore` existe en la raíz del proyecto.
  - Contiene todas las exclusiones listadas en R-010 AC#4.
  - No excluye archivos necesarios para el build (api/, requirements.txt, rendercv/).
- **verification**: `cat .dockerignore` muestra todas las exclusiones requeridas.
- **dependencies**: Ninguna (puede ejecutarse en paralelo con T-001 a T-006).
- **handoff_context**: .dockerignore listo para builds Docker limpios.
- **source_of_truth**: `docs/specs/increments/002-production-readiness.md` R-010 AC#4.
- **stale_terms_guard**: Ninguno aplica.
- **status**: `done`
- **executor_notes**: .dockerignore con exclusiones ordenadas alfabéticamente
- **verification_result**: .dockerignore contiene todas las exclusiones requeridas
- **blocker**: `none`

---

### T-008: Crear README.md con documentación completa

- **agent**: executor
- **spec_refs**: R-011 (Documentación), Sección 7 (Archivos a Crear)
- **goal**: Crear `README.md` con documentación completa del proyecto.
- **scope**: Crear `README.md` en la raíz del proyecto.
- **out_of_scope**: Modificar código, modificar specs.
- **inputs**: Spec R-011 AC, OpenAPI para ejemplos de endpoints, Master Spec para arquitectura.
- **implementation_notes**:
  - Secciones requeridas:
    - Descripción del servicio (generación de PDFs ATS-friendly con RenderCV).
    - Arquitectura y posicionamiento en el ecosistema (consumido por hv-go-ms-resume vía HTTP interno Docker).
    - Diagrama de arquitectura (Mermaid).
    - Requisitos previos (Docker, Python 3.12).
    - Desarrollo local con venv + pip: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.
    - Variables de entorno (METRICS_ENABLED, etc.).
    - Endpoints con ejemplos (GET /health, POST /render, GET /metrics).
    - Deploy con Docker (docker build, docker run).
    - Link a documentación de RenderCV.
  - Usar formato Markdown estándar.
  - Incluir ejemplos de request/response basados en OpenAPI.
- **edge_cases**: Ninguno.
- **done_criteria**:
  - `README.md` existe con todas las secciones requeridas.
  - Diagrama de arquitectura en formato Mermaid.
  - Ejemplos de endpoints consistentes con OpenAPI.
  - Instrucciones de desarrollo local funcionales.
- **verification**: `cat README.md` muestra todas las secciones requeridas.
- **dependencies**: Ninguna (puede ejecutarse en paralelo con T-001 a T-007).
- **handoff_context**: Documentación lista para consolidación (T-009).
- **source_of_truth**: `docs/specs/increments/002-production-readiness.md` R-011, `docs/api/openapi.yaml`.
- **stale_terms_guard**: Ninguno aplica.
- **status**: `done`
- **executor_notes**: README completo con arquitectura, endpoints, deploy, variables de entorno
- **verification_result**: README.md con todas las secciones requeridas
- **blocker**: `none`

---

### T-009: Consolidar specs en Master Spec

- **agent**: executor
- **spec_refs**: R-012 (Consolidación de Specs), Sección 7 (Archivos a Modificar: master-spec.md)
- **goal**: Actualizar Master Spec con los cambios del Incremento 002 y marcar incrementos como implementados.
- **scope**: Modificar `docs/specs/master-spec.md` para consolidar métricas, graceful shutdown, Docker hardening y marcar incrementos.
- **out_of_scope**: Modificar código, modificar OpenAPI, modificar delta spec.
- **inputs**: `docs/specs/master-spec.md` actual, `docs/specs/increments/002-production-readiness.md` implementada.
- **implementation_notes**:
  - Actualizar Sección 8 (Operación) con métricas Prometheus y graceful shutdown.
  - Actualizar Sección 8.3 (Configuración) con variable `METRICS_ENABLED`.
  - Marcar deuda técnica de métricas como ✅ Resuelta en Sección 12.
  - Marcar Incremento 002 como `implemented` en Sección 10.
  - Marcar Delta Spec 002 como `implemented`.
  - Actualizar shared context status a `implemented`.
- **edge_cases**: Ninguno.
- **done_criteria**:
  - Master Spec Sección 8 incluye métricas y graceful shutdown.
  - Master Spec Sección 8.3 incluye `METRICS_ENABLED`.
  - Master Spec Sección 12 marca deuda de métricas como resuelta.
  - Master Spec Sección 10 marca Incremento 002 como `implemented`.
  - Delta Spec 002 marcada como `implemented`.
  - Shared context status actualizado a `implemented`.
- **verification**: Leer `docs/specs/master-spec.md` y verificar secciones actualizadas. Leer shared context y verificar status `implemented`.
- **dependencies**: T-001, T-002, T-003, T-004, T-005, T-006, T-007, T-008 (todas las tareas anteriores deben estar `done`).
- **handoff_context**: Incremento 002 listo para cierre y validación final.
- **source_of_truth**: `docs/specs/increments/002-production-readiness.md` R-012, `docs/specs/master-spec.md`.
- **stale_terms_guard**: Ninguno aplica.
- **status**: `done`
- **executor_notes**: Master Spec Sección 8, 8.3, 10 y 12 actualizadas. Shared context y delta spec marcados implemented
- **verification_result**: Master Spec actualizada, deuda de métricas resuelta, Incremento 002 → implemented
- **blocker**: `none`

---

## Dependencias y Orden de Ejecución

```
T-001 (requirements.txt)
    └── T-002 (metrics.py)
            └── T-003 (metrics router)
                    └── T-004 (main.py integration)
                            └── T-005 (tests)
                                    
T-001 (requirements.txt)
    └── T-006 (Dockerfile hardening)

T-007 (.dockerignore) — paralelo

T-008 (README.md) — paralelo

T-001 + T-002 + T-003 + T-004 + T-005 + T-006 + T-007 + T-008
    └── T-009 (consolidación)
```

## Registro de Ejecución

| Tarea | Status | Changed Files | Verification Result | Executor Notes |
|---|---|---|---|---|
| T-001 | `done` | `requirements.txt` | Separación prod/dev, prometheus-client agregado | ✅ |
| T-002 | `done` | `api/core/metrics.py` | 3 métricas + middleware, import OK | ✅ |
| T-003 | `done` | `api/routers/metrics.py` | GET /metrics con 200/503, import OK | ✅ |
| T-004 | `done` | `api/main.py` | Router y middleware integrados, /metrics en rutas | ✅ |
| T-005 | `done` | `tests/test_metrics.py` | 6 tests, todos pasan | ✅ |
| T-006 | `done` | `Dockerfile` | Non-root rendercv UID 1000, graceful shutdown 30s, solo prod deps | ✅ |
| T-007 | `done` | `.dockerignore` | Exclusiones completas | ✅ |
| T-008 | `done` | `README.md` | Documentación completa con diagrama, endpoints, deploy | ✅ |
| T-009 | `done` | `docs/specs/master-spec.md`, shared context, delta spec | Secciones actualizadas, deuda resuelta, status implemented | ✅ |
