# Task Board - Incremento 001: foundation-and-hardening

**Increment**: `001-foundation-and-hardening`
**Spec**: `docs/specs/increments/001-foundation-and-hardening.md`
**OpenAPI**: `docs/api/openapi.yaml`
**Created**: 2026-06-01
**Status**: `done`

---

## Tareas

### T-001: Configurar pyproject.toml y actualizar requirements.txt

**agent**: executor
**spec_refs**: R-006
**goal**: Configurar el entorno de testing con pytest, httpx y pytest-cov.
**scope**: Crear `pyproject.toml` con configuración de pytest y cov. Actualizar `requirements.txt` con dev dependencies.
**out_of_scope**: Instalar paquetes (solo declarar dependencias).
**inputs**:
- `requirements.txt` existente (11 líneas, solo prod dependencies).
- Spec R-006: pytest, httpx, pytest-cov como dev dependencies.
- Umbral de cobertura: 85%.
- Exclusiones: `api/schemas.py`, `rendercv/`, `__init__.py`.

**implementation_notes**:
- Crear `pyproject.toml` con sección `[tool.pytest.ini_options]` configurando `--cov=api`, `--cov-fail-under=85`, `--cov-report=term-missing`.
- Configurar `[tool.coverage.run]` con `omit` para `api/schemas.py`, `rendercv/*`, `**/__init__.py`.
- En `requirements.txt`, agregar al final las dev dependencies: `pytest`, `httpx`, `pytest-cov`.
- Seguir convenciones de `python-stack` skill.

**edge_cases**:
- `requirements.txt` no tiene separador entre prod y dev dependencies; agregar comentario `# Dev dependencies` antes de las nuevas.

**done_criteria**:
- [ ] `pyproject.toml` existe con configuración de pytest y coverage.
- [ ] `requirements.txt` incluye pytest, httpx, pytest-cov.
- [ ] `pytest --collect-only` funciona (aunque no haya tests aún).

**verification**: `cat pyproject.toml && cat requirements.txt && pytest --collect-only`
**dependencies**: Ninguna
**handoff_context**: Ninguna
**source_of_truth**: R-006, python-stack skill
**stale_terms_guard**: No usar `setup.py`, `setup.cfg`, `tox.ini`.
**status**: `done`
**executor_notes**: ""
**verification_result**: ""
**blocker**: `none`

---

### T-002: Crear schemas Pydantic estrictos (ApiErrorResponse, ApiErrorDetail, RenderRequest, CvData, HealthResponse)

**agent**: executor
**spec_refs**: R-002, R-005, Sección 4 (Modelo de Datos)
**goal**: Reemplazar `api/schemas.py` con DTOs estrictos siguiendo el OpenAPI.
**scope**: Reescribir `api/schemas.py` con todos los nuevos modelos Pydantic.
**out_of_scope**: Modificar error handlers, routers o middleware.
**inputs**:
- `api/schemas.py` actual (11 líneas, con `RootModel[dict[str, Any]]`).
- OpenAPI `docs/api/openapi.yaml` schemas: RenderRequest, CvData, SocialNetwork, Locale, Design, RenderResponse, HealthResponse, ApiErrorResponse, ApiErrorDetail.
- Enums: SupportedLanguage (15 idiomas), SupportedTheme (4 temas).
- Decisiones locked: `extra="forbid"` en todos los modelos.

**implementation_notes**:
- Crear enums `SupportedLanguage` y `SupportedTheme` con los valores exactos del OpenAPI.
- `ApiErrorDetail`: campos `field` (Optional[str]), `code` (str), `message` (str), `rejected_value` (Optional[Any]). `extra="forbid"`.
- `ApiErrorResponse`: campos `timestamp` (datetime), `status` (int), `error` (str), `code` (str), `message` (str), `path` (str), `trace_id` (UUID), `details` (list[ApiErrorDetail]). `extra="forbid"`.
- `RenderRequest`: campo `cv: CvData` (requerido). `extra="forbid"`.
- `CvData`: campos requeridos `name` (str, min_length=1, max_length=200), `email` (EmailStr, max_length=254), `sections` (dict[str, Any], min_length=1). Opcionales: `phone`, `location`, `headline`, `photo`, `website` (HttpUrl), `social_networks` (list[SocialNetwork]), `locale` (Locale), `design` (Design). `extra="forbid"`.
- `SocialNetwork`: `network` (str), `username` (str). `extra="forbid"`.
- `Locale`: `language` (SupportedLanguage). `extra="forbid"`.
- `Design`: `theme` (SupportedTheme). `extra="forbid"`.
- `HealthResponse`: `status` (Literal["healthy", "unhealthy"]), `timestamp` (datetime), `version` (str). `extra="forbid"`.
- `RenderResponse`: mantener existente `pdf_base64: str`. Agregar `extra="forbid"`.
- Usar `pydantic.Field` para constraints.
- Seguir `fastapi-stack` y `fastapi-rest-error-response-standards` skills.

**edge_cases**:
- `sections` debe permitir cualquier clave (secciones custom) pero requerir al menos una.
- `rejected_value` en `ApiErrorDetail` puede ser cualquier tipo (Any).
- `email` debe usar `EmailStr` de pydantic.
- `website` debe usar `HttpUrl` de pydantic.

**done_criteria**:
- [ ] `api/schemas.py` contiene todos los modelos listados.
- [ ] Todos los modelos tienen `model_config = ConfigDict(extra="forbid")`.
- [ ] `RenderRequest` NO es `RootModel`.
- [ ] Enums tienen los valores exactos del OpenAPI.
- [ ] Constraints (minLength, maxLength, format) aplicados via Pydantic Field.

**verification**: `python -c "from api.schemas import *; print('OK')"`
**dependencies**: Ninguna
**handoff_context**: T-003, T-006, T-009 necesitan estos schemas.
**source_of_truth**: OpenAPI `docs/api/openapi.yaml`, R-002, R-005
**stale_terms_guard**: No usar `RootModel[dict[str, Any]]`, no usar `{"detail": ...}`.
**status**: `done`
**executor_notes**: ""
**verification_result**: ""
**blocker**: `none`

---

### T-003: Crear middleware de trace_id

**agent**: executor
**spec_refs**: R-004
**goal**: Middleware que genera/propaga trace_id por request.
**scope**: Crear `api/core/trace.py` con middleware de Starlette.
**out_of_scope**: Logging, error handlers, health check.
**inputs**:
- Spec R-004: Si header `X-Trace-Id` viene, usarlo; si no, generar UUID4.
- `trace_id` disponible en `request.state.trace_id`.
- `trace_id` se loggea en cada request.
- Decision locked: UUID4, no predecible.

**implementation_notes**:
- Crear middleware `TraceMiddleware` que envuelve requests.
- Leer header `X-Trace-Id`; si ausente, generar `uuid.uuid4()`.
- Setear `request.state.trace_id`.
- Agregar header `X-Trace-Id` a la response para propagación.
- Loggear: method, path, trace_id al inicio del request.
- Seguir `fastapi-stack` skill para middleware.

**edge_cases**:
- Header `X-Trace-Id` viene vacío: generar UUID4.
- Header `X-Trace-Id` viene con formato inválido: usarlo igual (el cliente es responsable).

**done_criteria**:
- [ ] `api/core/trace.py` existe con `TraceMiddleware`.
- [ ] Middleware lee `X-Trace-Id` o genera UUID4.
- [ ] `request.state.trace_id` está disponible.
- [ ] Header `X-Trace-Id` se agrega a la response.
- [ ] Log de method, path, trace_id por request.

**verification**: Test manual con curl enviando y no enviando X-Trace-Id.
**dependencies**: Ninguna
**handoff_context**: T-008 (main.py) integrará este middleware.
**source_of_truth**: R-004
**stale_terms_guard**: No usar `request_id`, `correlation_id` como nombre de variable.
**status**: `done`
**executor_notes**: ""
**verification_result**: ""
**blocker**: `none`

---

### T-004: Crear módulo de logging estructurado

**agent**: executor
**spec_refs**: R-004, Sección 7.2 (Logging)
**goal**: Configurar logging estructurado en formato JSON.
**scope**: Crear `api/core/logging.py` con configuración de logging.
**out_of_scope**: Middleware de trace (T-003), error handlers.
**inputs**:
- Sección 7.2: Cada request loggea method, path, status_code, trace_id, duration_ms.
- Formato: JSON estructurado.
- Variable de entorno `LOG_LEVEL` con default `INFO`.

**implementation_notes**:
- Crear función `setup_logging()` que configura el logger root.
- Usar `logging` estándar de Python o `structlog` si disponible (preferir estándar).
- Configurar handler con formato JSON (usar `json.dumps` para el record).
- Leer `LOG_LEVEL` de env con default `INFO`.
- Crear helper `get_logger(name)` que retorna logger configurado.

**edge_cases**:
- `LOG_LEVEL` inválido: fallback a `INFO`.
- Logs en stderr para compatibilidad con Docker.

**done_criteria**:
- [ ] `api/core/logging.py` existe con `setup_logging()`.
- [ ] Logs en formato JSON.
- [ ] `LOG_LEVEL` configurable via env.
- [ ] Logs van a stderr.

**verification**: `LOG_LEVEL=DEBUG python -c "from api.core.logging import setup_logging; setup_logging(); import logging; logging.getLogger().info('test')"`
**dependencies**: Ninguna
**handoff_context**: T-008 (main.py) llamará `setup_logging()`.
**source_of_truth**: Sección 7.2
**stale_terms_guard**: No usar `print()` para logging.
**status**: `done`
**executor_notes**: ""
**verification_result**: ""
**blocker**: `none`

---

### T-005: Crear módulo de verificación de Typst con cache

**agent**: executor
**spec_refs**: R-003
**goal**: Verificar que Typst está en el PATH con resultado cacheado 30s.
**scope**: Crear `api/core/typst_check.py` con función de verificación.
**out_of_scope**: Endpoint /health (T-007), Dockerfile HEALTHCHECK.
**inputs**:
- R-003: Ejecutar `typst --version` o equivalente.
- Cache de 30 segundos.
- Retorna booleano (True si Typst disponible).

**implementation_notes**:
- Usar `subprocess.run` con timeout razonable (5s).
- Implementar cache con `functools.lru_cache` no sirve (no tiene TTL); usar clase con timestamp o `cachetools.TTLCache` si disponible. Preferir implementación simple con timestamp.
- Función `is_typst_available() -> bool`.
- Capturar `FileNotFoundError` si typst no está en PATH.
- Seguir `python-stack` skill.

**edge_cases**:
- `typst --version` tarda más de 5s: considerar no disponible.
- Typst se instala/desinstala en runtime: el cache de 30s cubre la transición.
- subprocess retorna código de salida != 0: considerar no disponible.

**done_criteria**:
- [ ] `api/core/typst_check.py` existe con `is_typst_available()`.
- [ ] Ejecuta `typst --version` via subprocess.
- [ ] Resultado cacheado por 30 segundos.
- [ ] Retorna True/False correctamente.

**verification**: `python -c "from api.core.typst_check import is_typst_available; print(is_typst_available())"`
**dependencies**: Ninguna
**handoff_context**: T-007 (health router) usará esta función.
**source_of_truth**: R-003
**stale_terms_guard**: No usar `os.system()`, no usar `lru_cache` sin TTL.
**status**: `done`
**executor_notes**: ""
**verification_result**: ""
**blocker**: `none`

---

### T-006: Reescribir error handlers con ApiErrorResponse

**agent**: executor
**spec_refs**: R-002, Sección 6 (Seguridad)
**goal**: Reemplazar `api/core/errors.py` con handlers que retornan `ApiErrorResponse`.
**scope**: Reescribir `api/core/errors.py` con todos los handlers de error.
**out_of_scope**: Middleware de trace (solo usa `request.state.trace_id`), schemas (T-002 los crea).
**inputs**:
- `api/core/errors.py` actual (51 líneas, formato legacy con `type: "validation_error"`).
- T-002: `ApiErrorResponse`, `ApiErrorDetail` ya existen en `api/schemas.py`.
- R-002: Handlers para RequestValidationError, RenderCVUserValidationError, RenderCVUserError, RenderCVInternalError, Exception fallback.
- Decision locked: NO exponer `str(exc)` en 500.
- `trace_id` se obtiene de `request.state.trace_id`.
- `timestamp` es UTC ISO 8601.

**implementation_notes**:
- Crear helper `_get_trace_id(request)` que lee `request.state.trace_id` o genera UUID4 como fallback.
- Crear helper `_make_error_response(status, code, error, message, request, details=[])` que construye `ApiErrorResponse`.
- Handler `RequestValidationError` (de FastAPI): mapear errores de Pydantic a `ApiErrorDetail` con `field`, `code="FIELD_INVALID"`, `message`, `rejected_value`.
- Handler `RenderCVUserValidationError`: mapear `_format_validation_errors` existente a `ApiErrorDetail`.
- Handler `RenderCVUserError`: retornar 400 con `code="RENDERCV_USER_ERROR"`, `details=[]`.
- Handler `RenderCVInternalError`: retornar 500 con `code="INTERNAL_ERROR"`, `details=[]`, message genérico.
- Handler fallback `Exception`: retornar 500 con `code="INTERNAL_ERROR"`, message genérico, NO `str(exc)`.
- Seguir `fastapi-rest-error-response-standards` skill.

**edge_cases**:
- `request.state.trace_id` no existe (middleware no registrado aún): generar UUID4 como fallback.
- `RenderCVUserValidationError` tiene errores sin campo específico: usar `field=None`.
- `rejected_value` puede ser cualquier tipo; convertir a string si no es serializable.

**done_criteria**:
- [ ] `api/core/errors.py` tiene los 5 handlers.
- [ ] Todos retornan `ApiErrorResponse` (JSONResponse con body correcto).
- [ ] Ningún handler expone `str(exc)` ni stack traces.
- [ ] `trace_id` incluido en todas las responses.
- [ ] `timestamp` es UTC ISO 8601.
- [ ] No se usa formato legacy `{"type": "...", ...}`.

**verification**: `python -c "from api.core.errors import *; print('OK')"`
**dependencies**: T-002 (schemas)
**handoff_context**: T-008 (main.py) registrará estos handlers.
**source_of_truth**: R-002, OpenAPI ApiErrorResponse schema
**stale_terms_guard**: No usar `{"detail": ...}`, no usar `type: "validation_error"`, no usar `exc.message` en 500.
**status**: `done`
**executor_notes**: ""
**verification_result**: ""
**blocker**: `none`

---

### T-007: Crear endpoint GET /health con verificación Typst

**agent**: executor
**spec_refs**: R-003
**goal**: Crear `api/routers/health.py` con endpoint GET /health.
**scope**: Crear router con endpoint /health que usa `is_typst_available()`.
**out_of_scope**: Middleware, logging, Dockerfile HEALTHCHECK.
**inputs**:
- T-005: `is_typst_available()` en `api/core/typst_check.py`.
- T-002: `HealthResponse` en `api/schemas.py`.
- R-003: 200 si healthy, 503 si unhealthy.
- `APP_VERSION` env var con default `1.0.0`.
- Timestamp UTC ISO 8601.

**implementation_notes**:
- Crear `APIRouter` con prefijo vacío.
- Endpoint `GET /health` retorna `HealthResponse`.
- Si `is_typst_available()` → 200 con `status="healthy"`.
- Si no → 503 con `status="unhealthy"`.
- Leer `APP_VERSION` de env con default `1.0.0`.
- Usar `datetime.now(timezone.utc)` para timestamp.
- Seguir `fastapi-stack` skill.

**edge_cases**:
- `APP_VERSION` no seteada: usar default `1.0.0`.
- Typst check falla por timeout: retornar 503.

**done_criteria**:
- [ ] `api/routers/health.py` existe con router y endpoint GET /health.
- [ ] Retorna 200 con HealthResponse healthy si Typst disponible.
- [ ] Retorna 503 con HealthResponse unhealthy si Typst no disponible.
- [ ] Version leída de APP_VERSION env var.
- [ ] Timestamp UTC ISO 8601.

**verification**: `python -c "from api.routers.health import router; print('OK')"`
**dependencies**: T-002 (schemas), T-005 (typst_check)
**handoff_context**: T-008 (main.py) incluirá este router.
**source_of_truth**: R-003, OpenAPI GET /health
**stale_terms_guard**: No usar `{"status": "ok"}`, no retornar ApiErrorResponse en 503.
**status**: `done`
**executor_notes**: ""
**verification_result**: ""
**blocker**: `none`

---

### T-008: Integrar todo en api/main.py

**agent**: executor
**spec_refs**: R-002, R-003, R-004, Sección 7.1, Sección 7.2
**goal**: Modificar `api/main.py` para integrar middleware, routers, handlers y logging.
**scope**: Reescribir `api/main.py` con toda la integración.
**out_of_scope**: Modificar routers o handlers (solo integrarlos).
**inputs**:
- `api/main.py` actual (29 líneas, solo render router y 3 handlers legacy).
- T-003: `TraceMiddleware` en `api/core/trace.py`.
- T-004: `setup_logging()` en `api/core/logging.py`.
- T-006: Nuevos handlers en `api/core/errors.py`.
- T-007: Health router en `api/routers/health.py`.
- T-002: Schemas existentes.
- Sección 7.1: Variables de entorno `APP_VERSION`, `LOG_LEVEL`.

**implementation_notes**:
- Llamar `setup_logging()` al inicio.
- Crear FastAPI app con title y version.
- Agregar `TraceMiddleware` con `app.add_middleware()`.
- Incluir routers: render y health.
- Registrar exception handlers: RequestValidationError, RenderCVUserValidationError, RenderCVUserError, RenderCVInternalError, Exception.
- Mantener compatibilidad con `rendercv.exception` imports.
- Seguir `fastapi-stack` skill.

**edge_cases**:
- Orden de registration de handlers: el más específico primero (RequestValidationError antes que Exception).
- Middleware debe estar antes de los routers.

**done_criteria**:
- [ ] `api/main.py` integra logging, middleware, routers y handlers.
- [ ] `app` es exportada correctamente.
- [ ] `create_app()` funciona sin errores.
- [ ] Todos los handlers registrados.
- [ ] Health router incluido.

**verification**: `python -c "from api.main import app; print(app.title, len(app.routes))"`
**dependencies**: T-002, T-003, T-004, T-006, T-007
**handoff_context**: T-009 (render router) y T-010 (tests) dependen de main.py funcional.
**source_of_truth**: R-002, R-003, R-004
**stale_terms_guard**: No mantener handlers legacy registrados.
**status**: `done`
**executor_notes**: ""
**verification_result**: ""
**blocker**: `none`

---

### T-009: Actualizar api/routers/render.py para usar nuevo schema

**agent**: executor
**spec_refs**: R-005, R-002
**goal**: Modificar `api/routers/render.py` para usar `RenderRequest` estricto.
**scope**: Actualizar el endpoint POST /render.
**out_of_scope**: Error handlers, service layer (rendercv_service.py no se modifica).
**inputs**:
- `api/routers/render.py` actual (14 líneas, usa `request.root`).
- T-002: `RenderRequest` con campo `cv: CvData`.
- T-008: main.py ya registra handlers de error.
- `rendercv_service.render_pdf_base64` espera `dict[str, Any]`.

**implementation_notes**:
- Cambiar `request: RenderRequest` → el nuevo schema tiene `cv: CvData`.
- Convertir `RenderRequest` a dict para pasar a `render_pdf_base64`: usar `request.model_dump()`.
- El endpoint debe seguir retornando `RenderResponse(pdf_base64=...)`.
- Mantener `run_in_threadpool` para no bloquear el event loop.
- Seguir `fastapi-stack` skill.

**edge_cases**:
- `model_dump()` debe producir un dict compatible con el servicio existente.
- El servicio espera la clave `cv` en el payload.

**done_criteria**:
- [ ] `api/routers/render.py` usa nuevo `RenderRequest`.
- [ ] Convierte a dict correctamente para el servicio.
- [ ] Retorna `RenderResponse` correctamente.
- [ ] No usa `request.root`.

**verification**: `python -c "from api.routers.render import router; print('OK')"`
**dependencies**: T-002 (schemas), T-008 (main.py con handlers)
**handoff_context**: T-010 (tests) testeará este endpoint.
**source_of_truth**: R-005, OpenAPI POST /render
**stale_terms_guard**: No usar `request.root`, no usar `RootModel`.
**status**: `done`
**executor_notes**: ""
**verification_result**: ""
**blocker**: `none`

---

### T-010: Crear tests de health check

**agent**: executor
**spec_refs**: R-003, R-006, R-007
**goal**: Crear `tests/` con `conftest.py` y `test_health.py`.
**scope**: Tests para GET /health.
**out_of_scope**: Tests de render, error handlers.
**inputs**:
- T-001: pyproject.toml con pytest configurado.
- T-008: `api/main.py` con app funcional.
- T-007: GET /health endpoint.
- R-007: Test GET /health → 200, body correcto.
- R-006: httpx para TestClient async.

**implementation_notes**:
- Crear `tests/__init__.py`.
- Crear `tests/conftest.py` con fixtures `app` y `client` (AsyncClient de httpx).
- `test_health.py`:
  - `test_health_healthy`: GET /health → 200, status="healthy", version presente, timestamp presente.
  - `test_health_unhealthy`: Mockear `is_typst_available` para retornar False → 503, status="unhealthy".
  - Verificar formato de timestamp (ISO 8601).
- Usar `unittest.mock.patch` para mockear typst check.
- Seguir `testing-strategy` skill.

**edge_cases**:
- El test de unhealthy necesita mockear el cache de typst_check.
- Asegurar que el mock limpia el cache entre tests.

**done_criteria**:
- [ ] `tests/__init__.py` existe.
- [ ] `tests/conftest.py` con fixtures app y client.
- [ ] `tests/test_health.py` con tests de healthy y unhealthy.
- [ ] Tests pasan con `pytest tests/test_health.py -v`.

**verification**: `pytest tests/test_health.py -v`
**dependencies**: T-001, T-007, T-008
**handoff_context**: Ninguna
**source_of_truth**: R-003, R-006, R-007
**stale_terms_guard**: No usar `TestClient` de starlette (usar httpx AsyncClient).
**status**: `done`
**executor_notes**: ""
**verification_result**: ""
**blocker**: `none`

---

### T-011: Crear tests de endpoint render

**agent**: executor
**spec_refs**: R-005, R-006, R-007
**goal**: Crear `tests/test_render.py` con tests de POST /render.
**scope**: Tests para POST /render con payloads válidos e inválidos.
**out_of_scope**: Tests de health, error handlers específicos.
**inputs**:
- T-001: pyproject.toml configurado.
- T-008: main.py funcional.
- T-009: render.py con nuevo schema.
- R-007: Tests de payload válido, sin cv, email inválido, payload vacío.

**implementation_notes**:
- `test_render.py`:
  - `test_render_valid`: POST /render con payload válido → 200, `pdf_base64` presente. Mockear `render_pdf_base64` para evitar Typst real.
  - `test_render_missing_cv`: POST /render sin campo `cv` → 400.
  - `test_render_invalid_email`: POST /render con email inválido → 400 con detalle de campo.
  - `test_render_empty_payload`: POST /render con `{}` → 400.
  - Verificar que las responses de error tienen formato `ApiErrorResponse`.
- Usar `unittest.mock.patch` para mockear `render_pdf_base64`.
- Seguir `testing-strategy` skill.

**edge_cases**:
- Mockear el servicio para no depender de Typst real en tests.
- Validar que los detalles de error incluyen `field`, `code`, `message`.

**done_criteria**:
- [ ] `tests/test_render.py` existe con al menos 4 tests.
- [ ] Tests pasan con `pytest tests/test_render.py -v`.
- [ ] Payload válido retorna 200 con pdf_base64.
- [ ] Payloads inválidos retornan 400 con ApiErrorResponse.

**verification**: `pytest tests/test_render.py -v`
**dependencies**: T-001, T-009, T-008
**handoff_context**: Ninguna
**source_of_truth**: R-005, R-007
**stale_terms_guard**: No usar `{"detail": ...}` en assertions.
**status**: `done`
**executor_notes**: ""
**verification_result**: ""
**blocker**: `none`

---

### T-012: Crear tests de error handlers

**agent**: executor
**spec_refs**: R-002, R-006, R-007
**goal**: Crear `tests/test_error_handlers.py` con tests de error handlers.
**scope**: Tests para todos los handlers de error.
**out_of_scope**: Tests de health, render.
**inputs**:
- T-001: pyproject.toml configurado.
- T-008: main.py con handlers registrados.
- T-006: Error handlers con ApiErrorResponse.
- R-007: Test fallback → 500 sin stack trace, test trace_id en error.

**implementation_notes**:
- `test_error_handlers.py`:
  - `test_fallback_exception`: Provocar excepción no manejada → 500 con `code="INTERNAL_ERROR"`, sin stack trace en body.
  - `test_trace_id_in_error_response`: Verificar que response de error incluye `trace_id` (formato UUID).
  - `test_trace_id_propagation`: Enviar request con `X-Trace-Id` header → error response incluye ese trace_id.
  - `test_validation_error_format`: Payload con campo inválido → 400 con `details` array.
  - Verificar que NO se expone `str(exc)` ni stack traces.
  - Verificar formato de timestamp (ISO 8601).
- Seguir `testing-strategy` skill.

**edge_cases**:
- Para provocar excepción fallback, se puede mockear el servicio para lanzar `RuntimeError`.
- El trace_id generado debe ser un UUID válido.

**done_criteria**:
- [ ] `tests/test_error_handlers.py` existe con al menos 4 tests.
- [ ] Tests pasan con `pytest tests/test_error_handlers.py -v`.
- [ ] Fallback retorna 500 sin stack trace.
- [ ] trace_id presente en responses de error.
- [ ] trace_id propagado desde header.

**verification**: `pytest tests/test_error_handlers.py -v`
**dependencies**: T-001, T-006, T-008
**handoff_context**: Ninguna
**source_of_truth**: R-002, R-007
**stale_terms_guard**: No usar `{"detail": ...}` en assertions.
**status**: `done`
**executor_notes**: ""
**verification_result**: ""
**blocker**: `none`

---

### T-013: Ejecutar tests con cobertura y verificar umbral 85%

**agent**: executor
**spec_refs**: R-006, R-007
**goal**: Ejecutar todos los tests con cobertura y verificar umbral.
**scope**: Ejecutar pytest con cobertura sobre todo el proyecto.
**out_of_scope**: Escribir tests nuevos (ya creados en T-010, T-011, T-012).
**inputs**:
- T-001: pyproject.toml con configuración de cobertura.
- T-010, T-011, T-012: Tests creados.
- R-006: Umbral 85%, exclusiones: schemas, rendercv/, __init__.py.

**implementation_notes**:
- Ejecutar `pytest tests/ -v --cov=api --cov-fail-under=85 --cov-report=term-missing`.
- Si cobertura < 85%, identificar archivos con baja cobertura y agregar tests.
- Verificar que exclusiones están aplicadas correctamente.
- Seguir `testing-strategy` skill.

**edge_cases**:
- Si algún archivo no tiene tests, puede bajar la cobertura general.
- `api/schemas.py` está excluido, no cuenta para cobertura.

**done_criteria**:
- [ ] Todos los tests pasan.
- [ ] Cobertura ≥ 85%.
- [ ] Reporte de cobertura muestra archivos testables.

**verification**: `pytest tests/ -v --cov=api --cov-fail-under=85 --cov-report=term-missing`
**dependencies**: T-010, T-011, T-012
**handoff_context**: T-014 (OpenAPI validation)
**source_of_truth**: R-006, R-007
**stale_terms_guard**: Ninguno
**status**: `done`
**executor_notes**: ""
**verification_result**: ""
**blocker**: `none`

---

### T-014: Validar OpenAPI contra runtime

**agent**: executor
**spec_refs**: R-001
**goal**: Verificar que FastAPI genera `/docs` y `/redoc` que reflejan el contrato OpenAPI.
**scope**: Validación manual/automática de que el runtime coincide con el OpenAPI.
**out_of_scope**: Modificar OpenAPI (ya existe y está validado).
**inputs**:
- `docs/api/openapi.yaml` existente (414 líneas).
- R-001: FastAPI genera `/docs` y `/redoc`.
- T-008: main.py funcional con todos los endpoints.

**implementation_notes**:
- Levantar la app con `uvicorn api.main:app`.
- Verificar que `/docs` y `/redoc` están accesibles.
- Verificar que el OpenAPI generado por FastAPI (`/openapi.json`) es consistente con `docs/api/openapi.yaml`.
- Opcional: usar script para comparar schemas clave.
- El OpenAPI ya existe y fue validado por Spec Validator; esta tarea es verificar que el runtime lo refleja.

**edge_cases**:
- Diferencias menores entre OpenAPI estático y generado por FastAPI son esperadas (ej: server URLs).
- Los schemas y paths deben coincidir.

**done_criteria**:
- [ ] `/docs` accesible y muestra endpoints.
- [ ] `/redoc` accesible y muestra endpoints.
- [ ] `/openapi.json` generado contiene POST /render y GET /health.
- [ ] Schemas en runtime coinciden con OpenAPI estático.

**verification**: `curl -s http://localhost:8000/openapi.json | python -m json.tool | head -50`
**dependencies**: T-008, T-009
**handoff_context**: T-015 (Dockerfile)
**source_of_truth**: R-001
**stale_terms_guard**: Ninguno
**status**: `done`
**executor_notes**: ""
**verification_result**: ""
**blocker**: `none`

---

### T-015: Agregar HEALTHCHECK al Dockerfile

**agent**: executor
**spec_refs**: R-003, Sección 12 (Criterios de Cierre)
**goal**: Modificar `Dockerfile` para incluir HEALTHCHECK.
**scope**: Agregar instrucción HEALTHCHECK al Dockerfile existente.
**out_of_scope**: Modificar otros archivos de infraestructura.
**inputs**:
- `Dockerfile` actual (14 líneas, sin HEALTHCHECK).
- R-003: GET /health endpoint existe.
- Criterios de cierre: Dockerfile con HEALTHCHECK.

**implementation_notes**:
- Agregar `HEALTHCHECK` después de `COPY` y antes de `CMD`.
- Usar `curl` o `python` para hacer GET /health.
- Como la imagen es `python:3.12-slim`, curl no está disponible; usar python o instalar curl.
- Opción preferida: `HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"` o instalar curl.
- Seguir buenas prácticas de Docker.

**edge_cases**:
- `python:3.12-slim` no tiene curl; usar python o agregar `RUN apt-get update && apt-get install -y curl`.
- El healthcheck debe usar el puerto correcto (8000).

**done_criteria**:
- [ ] `Dockerfile` tiene instrucción HEALTHCHECK.
- [ ] HEALTHCHECK hace GET /health en puerto 8000.
- [ ] Intervalo, timeout y retries configurados razonablemente.

**verification**: `docker build -t test-render-cv . && docker run -d --name test-container test-render-cv && sleep 15 && docker inspect --format='{{.State.Health.Status}}' test-container`
**dependencies**: T-007 (health endpoint), T-008 (main.py)
**handoff_context**: Ninguna
**source_of_truth**: R-003, Criterios de Cierre
**stale_terms_guard**: Ninguno
**status**: `done`
**executor_notes**: ""
**verification_result**: ""
**blocker**: `none`

---

## Resumen de dependencias

```
T-001 (pyproject + requirements) → T-010, T-011, T-012, T-013
T-002 (schemas) → T-006, T-007, T-008, T-009
T-003 (trace middleware) → T-008
T-004 (logging) → T-008
T-005 (typst_check) → T-007
T-006 (error handlers) → T-008, T-012
T-007 (health router) → T-008, T-010
T-008 (main.py integration) → T-009, T-010, T-011, T-012, T-014
T-009 (render router) → T-011, T-014
T-010 (health tests) → T-013
T-011 (render tests) → T-013
T-012 (error handler tests) → T-013
T-013 (coverage check) → (final verification)
T-014 (OpenAPI validation) → (final verification)
T-015 (Dockerfile HEALTHCHECK) → (final verification)
```

## Orden de ejecución recomendado

1. T-001 (pyproject + requirements)
2. T-002 (schemas)
3. T-003 (trace middleware)
4. T-004 (logging)
5. T-005 (typst_check)
6. T-006 (error handlers) - depende de T-002
7. T-007 (health router) - depende de T-002, T-005
8. T-008 (main.py integration) - depende de T-002, T-003, T-004, T-006, T-007
9. T-009 (render router) - depende de T-002, T-008
10. T-010 (health tests) - depende de T-001, T-007, T-008
11. T-011 (render tests) - depende de T-001, T-009, T-008
12. T-012 (error handler tests) - depende de T-001, T-006, T-008
13. T-013 (coverage check) - depende de T-010, T-011, T-012
14. T-014 (OpenAPI validation) - depende de T-008, T-009
15. T-015 (Dockerfile HEALTHCHECK) - depende de T-007, T-008
