# Shared Context - Incremento 001: foundation-and-hardening

**Increment**: `001-foundation-and-hardening`
**Spec**: `docs/specs/increments/001-foundation-and-hardening.md`
**Master Spec**: `docs/specs/master-spec.md`
**OpenAPI**: `docs/api/openapi.yaml`
**Current Status**: `awaiting-human-plan-approval`
**Created**: 2026-05-31
**Last Updated**: 2026-05-31

---

## Current status

`awaiting-human-plan-approval` - Especificación validada por Spec Validator con veredicto `ready`. Pendiente de aprobación humana del plan para proceder a descomposición de tareas.

## Canonical artifacts

| Artefacto | Ruta | Estado |
|---|---|---|
| Master Spec | `docs/specs/master-spec.md` | ✅ Creado |
| Delta Spec 001 | `docs/specs/increments/001-foundation-and-hardening.md` | ✅ Creado |
| Delta Spec 002 | `docs/specs/increments/002-production-readiness.md` | ✅ Creado |
| OpenAPI Contract | `docs/api/openapi.yaml` | ✅ Creado (v3.1.0) |
| Shared Context | `docs/specs/.working/001-foundation-and-hardening-sdd-context.md` | ✅ Este archivo |

## Artifact evidence

| Campo | Artefacto | Evidencia | Estado |
|---|---|---|---|
| OpenAPI version | `docs/api/openapi.yaml` | `openapi: "3.1.0"` | ✅ pass |
| POST /render contract | `docs/api/openapi.yaml` | Path `/render` con POST, request `RenderRequest`, response 200/400/500 | ✅ pass |
| GET /health contract | `docs/api/openapi.yaml` | Path `/health` con GET, response 200/503 | ✅ pass |
| Error responses reutilizables | `docs/api/openapi.yaml` | `components.responses.BadRequest` y `InternalError` referenciados via `$ref` | ✅ pass |
| ApiErrorResponse schema | `docs/api/openapi.yaml` | Schema con timestamp, status, error, code, message, path, trace_id (format:uuid), details | ✅ pass |
| ApiErrorDetail schema | `docs/api/openapi.yaml` | Schema con field, code, message, rejected_value | ✅ pass |
| CvData schema | `docs/api/openapi.yaml` | Schema con name (minLength:1, maxLength:200), email (format:email, maxLength:254), sections (minProperties:1) required + opcionales | ✅ pass |
| Constraints declarados | `docs/api/openapi.yaml` | minLength, maxLength, minProperties, maxItems, format:email, format:uri, format:uuid | ✅ pass |
| additionalProperties | `docs/api/openapi.yaml` | `false` en RenderRequest, CvData, SocialNetwork, Locale, Design, RenderResponse, HealthResponse, ApiErrorResponse, ApiErrorDetail | ✅ pass |
| Error codes | `docs/api/openapi.yaml` | VALIDATION_ERROR, RENDERCV_USER_ERROR, INTERNAL_ERROR | ✅ pass |
| Supported languages enum | `docs/api/openapi.yaml` | 15 idiomas listados | ✅ pass |
| Supported themes enum | `docs/api/openapi.yaml` | 4 temas listados | ✅ pass |
| trace_id solo en errores | `docs/api/openapi.yaml` | trace_id presente en ApiErrorResponse, NO en RenderResponse ni HealthResponse | ✅ pass |
| Requisitos R-001 a R-007 | `docs/specs/increments/001-foundation-and-hardening.md` | 7 requisitos con acceptance criteria actualizados | ✅ pass |
| Health check con Typst | `docs/specs/increments/001-foundation-and-hardening.md` | R-003: verifica Typst en PATH, cache 30s, retorna 200/503 | ✅ pass |
| Stale terms guard | `docs/specs/increments/001-foundation-and-hardening.md` | Sección 11 con términos prohibidos | ✅ pass |
| Execution order | `docs/specs/increments/001-foundation-and-hardening.md` | Sección 10 con orden de 12 pasos | ✅ pass |

## Spec Validator Approval

**verdict**: `ready`
**reviewed_at**: 2026-05-31
**validator_agent**: spec-validator
**artifact_set_reviewed**:
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/docs/specs/master-spec.md`
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/docs/specs/increments/001-foundation-and-hardening.md`
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/docs/specs/increments/002-production-readiness.md`
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/docs/api/openapi.yaml`
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/docs/specs/.working/001-foundation-and-hardening-sdd-context.md`
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/api/schemas.py`
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/api/main.py`
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/api/core/errors.py`
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/api/routers/render.py`
- `/home/cristiansrc/Documentos/Proyectos/hv-workspace/projects/hv-py-ms-render-cv/api/services/rendercv_service.py`
**summary**: |
  Re-validación completa post-remediación. Las 8 correcciones de Spec Remediator verificadas en disco.
  2 hallazgos no resueltos (#3 code drift, #5 technical_debt.md) con razón documentada y no bloqueantes.
  3 nuevos hallazgos detectados (#12 workspace error naming medium, #13 Graphify stale low, #14 code baseline info).
  OpenAPI 3.1.0 consistente con Delta Specs. Error contract alineado a fastapi-rest-error-response-standards.
  Lifecycle unificado. Especificación suficientemente completa para implementación segura.
**invalidated_by_changes_since**: none

## Decisions locked

1. **Error contract**: Se usa `ApiErrorResponse` con `extra="forbid"`, no se permite formato legacy.
2. **Schema validation**: `RenderRequest` debe ser Pydantic estricto, no `RootModel[dict[str, Any]]`.
3. **Trace ID**: UUID4 generado por middleware, propagado via `X-Trace-Id` header. **Solo en respuestas de error**, NO en responses exitosas (200).
4. **Health check**: Verifica que Typst está en el PATH ejecutando `typst --version`. Resultado cacheado por 30 segundos. Retorna 200 si healthy, 503 si Typst no disponible.
5. **OpenAPI version**: 3.1.0 (soportado por FastAPI). Respuestas de error reutilizables via `components.responses`.
6. **Tests**: pytest + httpx + pytest-cov, umbral 85%, exclusiones: schemas, rendercv/, __init__.py.
7. **No se modifica rendercv/**: La librería vendor no se toca en este incremento.
8. **additionalProperties: false** en todos los schemas del OpenAPI para evitar campos accidentales.

## Validator findings

1. **Finding #1 (Blocker - Mechanical)**: `rejected_value: true` en `ApiErrorDetail` del OpenAPI. Schema booleano ambiguo.
   - **Estado**: CORREGIDO en IT-1. Reemplazado por schema explícito con description y example.
2. **Finding #2 (High - Doc Bug)**: Delta Spec 001 referencia "Sección 6 (Error handling)" que no existe en Master Spec.
   - **Estado**: CORREGIDO en IT-2. Corregida referencia a "Secciones 5 (Reglas de Negocio) y 7 (Seguridad)".
3. **Finding #3 (High - Contract Drift)**: `api/core/errors.py` expone `exc.message` en 500. Es drift de código baseline.
   - **Estado**: ⏭️ `superseded-finding`. No es artefacto SDD corregible por Spec Remediator. Se resolverá en implementación del incremento.
4. **Finding #4 (Medium - Mechanical)**: `api/routers/health.py` listado en tabla "Modificar" cuando debería estar en "Crear".
   - **Estado**: CORREGIDO en IT-3. Movido de tabla "Modificar" a "Crear".
5. **Finding #5 (Medium - Missing Artifact)**: Falta `docs/specs/technical_debt.md`.
   - **Estado**: 🚫 `blocked-planner-decision`. Requiere decisión de Planner sobre si crear archivo separado o mantener deuda técnica inline en Master Spec.
6. **Finding #6 (Medium - Mechanical)**: OpenAPI no declara `security: []` explícitamente.
   - **Estado**: CORREGIDO en IT-4. Agregado `security: []` a POST /render y GET /health.
7. **Finding #7 (Medium - Consistency)**: Lifecycle status inconsistentes entre artefactos (planning vs draft).
   - **Estado**: CORREGIDO en IT-5. Unificados a `draft` en Master Spec, Delta Specs y Shared Context.
8. **Finding #8 (Medium - Mechanical)**: Shared context evidencia no refleja issue de `rejected_value`.
   - **Estado**: CORREGIDO. Resuelto vía este registro de hallazgos.
9. **Finding #9 (Low - Spec Prose)**: Ambigüedad sobre formato 503 de health check.
   - **Estado**: CORREGIDO en IT-6. Agregado AC explícito indicando que HealthResponse se usa para 503.
10. **Finding #10 (Low - Expected)**: Archivos faltantes pre-implementación.
    - **Estado**: ✅ Esperado, no requiere acción. Son archivos a crear en implementación.
11. **Finding #11 (Low - Mechanical)**: Mejora de documentación en ApiErrorDetail.
    - **Estado**: CORREGIDO en IT-6. Agregada descripción con nota sobre campo `field` opcional.
12. **Finding #12 (Medium - Workspace Alignment)**: El contrato de error del proyecto (`details: [{field, code, message, rejected_value}]`, con `code` y `trace_id`) difiere en nomenclatura del workspace `integration-map.md` (`validationErrors: [{field, message}]`, sin `code` ni `trace_id`).
    - **Estado**: 🟡 Documentado. El formato del proyecto es superset compatible. ms-resume actúa como ACL. No bloquea implementación. Recomendación: documentar como decisión consciente en Master Spec ADR.
13. **Finding #13 (Low - Observability)**: Reporte Graphify del workspace (`graphify-out/GRAPH_REPORT.md`) no refleja los nuevos artefactos SDD. `Canonical artifacts` del shared context no incluye el reporte.
    - **Estado**: 🟡 Documentado. Sugerir `graphify update` en el workspace tras el incremento.
14. **Finding #14 (Info - Code Baseline)**: `api/main.py` no tiene handler fallback para `Exception` ni `RequestValidationError`. Será corregido durante la implementación del incremento (R-002).
    - **Estado**: ℹ️ Informativo. Capturado en Delta Spec R-002.

## Resolved findings

| # | Hallazgo | Iteración | Archivo Modificado | Resultado |
|---|---|---|---|---|---|
| 1 | `rejected_value: true` ambiguo en OpenAPI | IT-1 | `docs/api/openapi.yaml` | ✅ validated (spec-validator 2026-05-31) |
| 2 | Referencia a sección inexistente "Sección 6 (Error handling)" en Delta Spec 001 | IT-2 | `docs/specs/increments/001-foundation-and-hardening.md` | ✅ validated (spec-validator 2026-05-31) |
| 4 | `api/routers/health.py` en tabla "Modificar" en vez de "Crear" | IT-3 | `docs/specs/increments/001-foundation-and-hardening.md` | ✅ validated (spec-validator 2026-05-31) |
| 6 | OpenAPI sin `security: []` explícito en operaciones | IT-4 | `docs/api/openapi.yaml` | ✅ validated (spec-validator 2026-05-31) |
| 7 | Lifecycle status inconsistentes (planning vs draft) | IT-5 | `docs/specs/master-spec.md`, shared context | ✅ validated (spec-validator 2026-05-31) |
| 8 | Shared context evidencia no reflejaba issue de rejected_value | IT-1..6 | shared context | ✅ validated (spec-validator 2026-05-31) |
| 9 | Ambigüedad 503 health check (HealthResponse vs ApiErrorResponse) | IT-6 | `docs/specs/increments/001-foundation-and-hardening.md` | ✅ validated (spec-validator 2026-05-31) |
| 11 | ApiErrorDetail sin descripción del campo `field` opcional | IT-6 | `docs/api/openapi.yaml` | ✅ validated (spec-validator 2026-05-31) |

## Open questions

> Ninguna. Las decisiones fueron confirmadas por el usuario.

## Stale terms guard

Los siguientes términos NO deben usarse en código nuevo:
- `{"detail": ...}` como formato de error
- `RootModel[dict[str, Any]]` para RenderRequest
- `type: "validation_error"`, `type: "user_error"`, `type: "internal_error"`
- `RenderCVUserValidationError` como response directo sin mapear
- `nullable: true` en OpenAPI 3.1.0 (usar union types con `null` en su lugar)

## Human Plan Approval: approved_by_user

Aprobado por el usuario (cristiansrc) el 2026-05-31. Se autoriza la descomposición de tareas e implementación.

## Next action

1. ✅ **Human Plan Approval granted** — El usuario ha aprobado el plan.
2. Enrutar a **Task Decomposer** para crear `docs/specs/tasks/001-foundation-and-hardening-task-board.md`.
3. Tras task board, enrutar a **Executor** para implementación.
4. **Hallazgos pendientes que no bloquean implementación**:
   - **Finding #3** (code drift en `api/core/errors.py`): Se resuelve durante la implementación del incremento (R-002)
   - **Finding #5** (`technical_debt.md`): Planner debe decidir — crear archivo separado o mantener deuda inline en Master Spec
   - **Finding #12** (workspace error naming): Documentar como ADR si la divergencia es intencional
   - **Finding #13** (Graphify stale): Ejecutar `graphify update` post-incremento
5. **Gate obligatorio**: Spec Validator verificó el bloque `## Human Plan Approval: approved_by_user` — NO existe aún. No autorizar Task Decomposer ni Executor hasta que el usuario apruebe.
