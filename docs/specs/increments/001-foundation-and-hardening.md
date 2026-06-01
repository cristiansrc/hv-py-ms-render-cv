# Delta Spec - Incremento 001: foundation-and-hardening

**Parent**: Master Spec (`docs/specs/master-spec.md`)
**Lifecycle Status**: `awaiting-human-plan-approval`
**Created**: 2026-05-31
**Author**: planner

---

## 1. Contexto

Este es el primer incremento del proyecto `hv-py-ms-render-cv`. El servicio tiene una implementación base funcional pero carece de:
- Contrato OpenAPI formal
- Error responses alineados al estándar del workspace
- Health check
- Validación estricta del schema de entrada
- Tests automatizados
- Trazabilidad de requests (trace_id)

## 2. Impacto en Master Spec

| Sección Master Spec | Cambio |
|---|---|
| Sección 3 (Contratos API) | Se formaliza con OpenAPI |
| Secciones 5 (Reglas de Negocio) y 7 (Seguridad) | Se reemplaza formato actual por `ApiErrorResponse` |
| Sección 8 (Operación) | Se agrega health check y trace_id |
| Sección 9 (Tests) | Se configura pytest + httpx + cobertura |
| Sección 12 (Deuda Técnica) | Se resuelven 4 deudas listadas |

## 3. Requisitos

### 3.1 R-001: OpenAPI Contract
**Descripción**: El servicio debe exponer un contrato OpenAPI 3.1.0 formal que documente todos los endpoints, schemas y respuestas de error.

**Acceptance Criteria**:
- [ ] Archivo `docs/api/openapi.yaml` existe con `openapi: "3.1.0"` y es válido
- [ ] Documenta `POST /render` con request body, response 200, 400, 500
- [ ] Documenta `GET /health` con response 200, 503
- [ ] Respuestas de error 400 y 500 referenciadas via `$ref` a `components.responses` (`BadRequest`, `InternalError`)
- [ ] La respuesta 503 de `GET /health` usa `HealthResponse` con `status: "unhealthy"` (NO usa `ApiErrorResponse`, es estado operativo, no error de validación)
- [ ] `ApiErrorResponse` y `ApiErrorDetail` definidos en `components.schemas` y reutilizados
- [ ] Schemas con `additionalProperties: false` para evitar campos accidentales
- [ ] Constraints declarados: `minLength`, `maxLength`, `minProperties`, `maxItems`, `format: email`, `format: uri`, `format: uuid` para `trace_id`
- [ ] FastAPI genera `/docs` y `/redoc` que reflejan el contrato

### 3.2 R-002: Error Response Alignment
**Descripción**: Todas las respuestas de error deben seguir el formato `ApiErrorResponse` definido en el integration-map del workspace.

**Acceptance Criteria**:
- [ ] Modelo Pydantic `ApiErrorResponse` con campos: `timestamp`, `status`, `error`, `code`, `message`, `path`, `trace_id`, `details`
- [ ] Modelo Pydantic `ApiErrorDetail` con campos: `field`, `code`, `message`, `rejected_value`
- [ ] `extra="forbid"` en ambos modelos
- [ ] Handler para `RequestValidationError` retorna `400 VALIDATION_ERROR`
- [ ] Handler para `RenderCVUserValidationError` retorna `400 VALIDATION_ERROR` con detalles mapeados
- [ ] Handler para `RenderCVUserError` retorna `400` con código `RENDERCV_USER_ERROR`
- [ ] Handler para `RenderCVInternalError` retorna `500 INTERNAL_ERROR`
- [ ] Handler fallback para `Exception` retorna `500 INTERNAL_ERROR` sin exponer `str(exc)`
- [ ] Ningún endpoint retorna `{"detail": "..."}` (formato default de FastAPI)
- [ ] `timestamp` es UTC ISO 8601
- [ ] `trace_id` se obtiene del middleware de contexto

### 3.3 R-003: Health Check
**Descripción**: Endpoint `GET /health` para verificación de liveness y readiness. Incluye validación de que Typst está disponible en el PATH.

**Acceptance Criteria**:
- [ ] `GET /health` retorna `200` con `{"status": "healthy", "timestamp": "...", "version": "1.0.0"}` cuando Typst está disponible
- [ ] `GET /health` retorna `503` con `{"status": "unhealthy", "timestamp": "...", "version": "1.0.0"}` cuando Typst NO está en el PATH
- [ ] La verificación de Typst se hace ejecutando `typst --version` o equivalente (subprocess no bloqueante)
- [ ] La versión se lee de una constante o variable de entorno `APP_VERSION`
- [ ] El timestamp es UTC ISO 8601
- [ ] El resultado de la verificación de Typst se cachea por 30 segundos para no impactar performance

### 3.4 R-004: Trace ID Middleware
**Descripción**: Middleware que genera/propaga un `trace_id` por request para correlación de logs.

**Acceptance Criteria**:
- [ ] Si el header `X-Trace-Id` viene en la request, se usa ese valor
- [ ] Si no viene, se genera un UUID4
- [ ] El `trace_id` está disponible en `request.state.trace_id`
- [ ] El `trace_id` se incluye en todas las respuestas de error
- [ ] El `trace_id` se loggea en cada request

### 3.5 R-005: Schema Validation Estricto
**Descripción**: Reemplazar `RenderRequest` (actualmente `RootModel[dict[str, Any]]`) por un schema Pydantic estricto que valide la estructura mínima del CV.

**Acceptance Criteria**:
- [ ] `RenderRequest` tiene campo `cv` de tipo `CvData` (requerido)
- [ ] `CvData` requiere `name` (str), `email` (str, formato email), `sections` (dict)
- [ ] `CvData` tiene campos opcionales: `phone`, `location`, `headline`, `photo`, `website`, `social_networks`, `locale`, `design`
- [ ] `email` valida formato email (Pydantic `EmailStr`)
- [ ] `website` valida formato URL si se proporciona
- [ ] `social_networks` valida estructura `[{network: str, username: str}]`
- [ ] `locale.language` valida contra enum de idiomas soportados
- [ ] `design.theme` valida contra enum de temas disponibles
- [ ] Request con payload inválido retorna `400 VALIDATION_ERROR` con detalles por campo

### 3.6 R-006: Configuración de Tests
**Descripción**: Configurar pytest, httpx y pytest-cov con umbrales de cobertura.

**Acceptance Criteria**:
- [ ] `pytest` instalado como dev dependency
- [ ] `httpx` instalado como dev dependency (para TestClient async)
- [ ] `pytest-cov` instalado como dev dependency
- [ ] `pyproject.toml` o `pytest.ini` configurado con:
  - `--cov=api`
  - `--cov-fail-under=85`
  - Exclusiones: `api/schemas.py`, `rendercv/`, `__init__.py`
- [ ] Directorio `tests/` con estructura:
  - `tests/conftest.py` (fixtures: client, app)
  - `tests/test_health.py`
  - `tests/test_render.py`
  - `tests/test_error_handlers.py`

### 3.7 R-007: Tests Funcionales
**Descripción**: Tests que validen el comportamiento de los endpoints.

**Acceptance Criteria**:
- [ ] Test `GET /health` → 200, body correcto
- [ ] Test `POST /render` con payload válido → 200, `pdf_base64` presente
- [ ] Test `POST /render` con payload sin `cv` → 400
- [ ] Test `POST /render` con `cv.email` inválido → 400 con detalle de campo
- [ ] Test `POST /render` con payload vacío → 400
- [ ] Test error handler fallback → 500 sin stack trace
- [ ] Test que verifica `trace_id` en respuesta de error
- [ ] Cobertura ≥ 85% en archivos testables de `api/`

## 4. Modelo de Datos

No hay cambios en persistencia (el servicio es stateless).

### 4.1 DTOs Nuevos

| DTO | Ubicación | Campos |
|---|---|---|
| `ApiErrorResponse` | `api/schemas.py` | timestamp, status, error, code, message, path, trace_id, details |
| `ApiErrorDetail` | `api/schemas.py` | field, code, message, rejected_value |
| `RenderRequest` (nuevo) | `api/schemas.py` | cv: CvData |
| `CvData` | `api/schemas.py` | name, email, phone?, location?, headline?, photo?, website?, social_networks?, sections, locale?, design? |
| `HealthResponse` | `api/schemas.py` | status, timestamp, version |

### 4.2 Enums

| Enum | Valores |
|---|---|
| `SupportedLanguage` | english, spanish, french, german, italian, portuguese, dutch, danish, russian, turkish, hindi, indonesian, japanese, korean, mandarin_chinese |
| `SupportedTheme` | engineeringclassic, engineeringresumes, moderncv, sb2nov |

## 5. Integraciones

Sin cambios en integraciones externas. Este incremento es interno al servicio.

## 6. Seguridad

- Los error handlers NO deben exponer `str(exc)` ni stack traces.
- El `trace_id` no debe ser predecible (UUID4).
- No se agregan credenciales ni autenticación en este incremento.

## 7. Operación

### 7.1 Nuevas Variables de Entorno

| Variable | Default | Descripción |
|---|---|---|
| `APP_VERSION` | `1.0.0` | Versión del servicio |
| `LOG_LEVEL` | `INFO` | Nivel de logging |

### 7.2 Logging

- Cada request debe loggear: method, path, status_code, trace_id, duration_ms
- Formato: JSON estructurado

## 8. Estrategia de Tests

| Tipo | Herramienta | Umbral |
|---|---|---|
| Unit | pytest | 85% |
| Integration | pytest + httpx | N/A |

**Comando de ejecución**:
```bash
pytest tests/ -v --cov=api --cov-fail-under=85 --cov-report=term-missing
```

## 9. Archivos a Crear/Modificar

### Crear
| Archivo | Descripción |
|---|---|
| `docs/api/openapi.yaml` | Contrato OpenAPI 3.1.0 formal |
| `api/core/trace.py` | Middleware de trace_id |
| `api/core/logging.py` | Configuración de logging estructurado |
| `api/core/typst_check.py` | Verificación de Typst en PATH con cache |
| `tests/__init__.py` | Package marker |
| `tests/conftest.py` | Fixtures de test |
| `tests/test_health.py` | Tests de health check |
| `tests/test_render.py` | Tests de endpoint render |
| `tests/test_error_handlers.py` | Tests de error handlers |
| `pyproject.toml` | Configuración de pytest y cov |
| `api/routers/health.py` | Nuevo endpoint GET /health con verificación Typst |

### Modificar
| Archivo | Cambio |
|---|---|
| `api/schemas.py` | Reemplazar schemas actuales por nuevos DTOs estrictos |
| `api/core/errors.py` | Reemplazar handlers por `ApiErrorResponse` |
| `api/main.py` | Agregar middleware trace, health router, registrar handlers |
| `api/routers/render.py` | Usar nuevo `RenderRequest` estricto |
| `requirements.txt` | Agregar dev dependencies |
| `Dockerfile` | Agregar HEALTHCHECK |

## 10. Orden de Ejecución Permitido

1. Crear `pyproject.toml` y actualizar `requirements.txt`
2. Crear `api/schemas.py` con nuevos DTOs
3. Crear `api/core/trace.py` middleware
4. Crear `api/core/logging.py`
5. Crear `api/core/typst_check.py` (verificación Typst con cache 30s)
6. Modificar `api/core/errors.py` con nuevos handlers
7. Crear `api/routers/health.py` con endpoint GET /health + verificación Typst
8. Modificar `api/main.py` para integrar todo (middleware trace, routers, handlers)
9. Modificar `api/routers/render.py` para usar nuevo schema
10. Crear `tests/` con todos los tests
11. Crear `docs/api/openapi.yaml`
12. Modificar `Dockerfile` con HEALTHCHECK

## 11. Términos Prohibidos (Stale Terms Guard)

Los siguientes términos NO deben aparecer en código nuevo:
- `RenderCVUserValidationError` como response directo (debe mapearse a `ApiErrorResponse`)
- `RenderCVUserError` como response directo (debe mapearse a `ApiErrorResponse`)
- `RenderCVInternalError` como response directo (debe mapearse a `ApiErrorResponse`)
- `{"detail": ...}` como formato de error
- `RootModel[dict[str, Any]]` para `RenderRequest`
- `type: "validation_error"`, `type: "user_error"`, `type: "internal_error"` (formato viejo)

## 12. Criterios de Cierre

- [ ] OpenAPI 3.1.0 válido y alineado con runtime (respuestas de error via `$ref` a `components.responses`)
- [ ] Todos los tests pasan con cobertura ≥ 85%
- [ ] Error responses siguen `ApiErrorResponse` con `extra="forbid"`
- [ ] Health check funcional: retorna 200 si Typst está en PATH, 503 si no
- [ ] Verificación de Typst cacheada por 30 segundos
- [ ] Trace_id en todas las responses de error (NO en responses exitosas)
- [ ] Dockerfile con HEALTHCHECK
- [ ] Spec Validator verdict: `ready`
- [ ] Human plan approval: `approved_by_user`
