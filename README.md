# validador-identidad-mx-api

![CI](https://github.com/tu-usuario/validador-identidad-mx-api/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)

API REST para validar CURP y RFC con reglas oficiales de México, cache en memoria con TTL y registro de auditoría inmutable en SQLite.

---

## Problema

En México, el onboarding digital de usuarios requiere validar su identidad mediante CURP y RFC. Sin validación en el backend:

- Se aceptan documentos con formato inválido o dígitos verificadores incorrectos.
- El fraude de identidad aumenta en flujos de registro no supervisados.
- Los equipos de soporte reciben tickets por datos mal capturados que pudieron rechazarse en origen.

## Solución

Una API ligera que valida CURP y RFC contra las reglas oficiales (regex + dígito verificador + fecha real), con dos capas adicionales:

- **Cache en memoria con TTL**: evita re-validar el mismo documento en ventanas de tiempo cortas, reduciendo latencia a <1ms en hits.
- **Auditoría inmutable en SQLite**: cada validación queda registrada con timestamp UTC, permitiendo trazabilidad sin infraestructura externa.

## Arquitectura

```
POST /validate
      │
      ▼
 Cache check ──── HIT ────► Response (cached: true)
      │
     MISS
      │
      ▼
  Validator (regex + dígito verificador + fecha)
      │
      ▼
 Cache set + Audit log (SQLite)
      │
      ▼
 Response (cached: false)
```

## Instalación y uso

**Requisitos**: Python 3.11+

```bash
# Setup completo (venv + dependencias + pre-commit + tests)
bash scripts/setup.sh

# Levantar servidor
source .venv/bin/activate
uvicorn app.main:app --reload
```

Demo automático (levanta servidor, ejecuta requests y muestra respuestas):

```bash
bash scripts/demo.sh
```

## Endpoints

| Método | Path        | Descripción                        |
|--------|-------------|------------------------------------|
| POST   | `/validate` | Valida un CURP o RFC               |
| GET    | `/history`  | Retorna las últimas 50 validaciones|

### POST /validate

**Request:**
```json
{
  "document": "BADD110313HCMLNS09",
  "doc_type": "CURP"
}
```

**Response (primera vez):**
```json
{
  "valid": true,
  "type": "CURP",
  "value": "BADD110313HCMLNS09",
  "reason": "OK",
  "cached": false
}
```

**Response (segunda vez, mismo documento):**
```json
{
  "valid": true,
  "type": "CURP",
  "value": "BADD110313HCMLNS09",
  "reason": "OK",
  "cached": true
}
```

**Validación fallida:**
```json
{
  "valid": false,
  "type": "CURP",
  "value": "INVALIDO123",
  "reason": "Formato inválido",
  "cached": false
}
```

### GET /history

**Response:**
```json
[
  {
    "id": 1,
    "doc_type": "CURP",
    "doc_value": "BADD110313HCMLNS09",
    "is_valid": true,
    "reason": "OK",
    "created_at": "2026-05-04T07:00:00+00:00"
  }
]
```

### Ejemplos curl

```bash
# Validar CURP
curl -s -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"document": "BADD110313HCMLNS09", "doc_type": "CURP"}' | python3 -m json.tool

# Validar RFC
curl -s -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"document": "GODE561231GR8", "doc_type": "RFC"}' | python3 -m json.tool

# Historial
curl -s http://localhost:8000/history | python3 -m json.tool
```

## Decisiones técnicas

**SQLite sobre Postgres/MySQL**: Para un MVP de validación sin usuarios concurrentes masivos, SQLite elimina la necesidad de un servidor de base de datos. El archivo `audit.db` es portable y suficiente para volúmenes de auditoría moderados. Advertencia: SQLite no escala bien con escrituras concurrentes altas; migrar a Postgres es el paso natural en producción.

**Cache en memoria sobre Redis**: Un `dict` con TTL cubre el caso de uso (evitar re-validar el mismo documento en segundos/minutos) sin añadir dependencias de infraestructura. El tradeoff es que el cache no persiste entre reinicios del servidor ni se comparte entre instancias.

**Pydantic v2 + `Literal`**: La validación de `doc_type` con `Literal["CURP", "RFC"]` delega el rechazo de tipos inválidos a Pydantic, retornando HTTP 422 automáticamente sin código adicional.

## Testing y calidad

```bash
pytest -v --cov=app --cov-fail-under=80
```

- **13 tests** cubriendo validadores unitarios, endpoints de integración y comportamiento de cache.
- **100% de cobertura** en todos los módulos de `app/`.
- **Pre-commit hooks**: `ruff check`, `ruff format` y `pytest` bloquean commits con estilo inválido o tests fallidos.
- **GitHub Actions CI**: corre en cada push y PR, falla si coverage < 80%.

## Próximos pasos

- **Autenticación**: API Keys o JWT para entornos multi-tenant.
- **Redis**: Reemplazar cache en memoria para soportar múltiples instancias y persistencia entre reinicios.
- **Validación contra fuentes oficiales**: Integración con RENAPO (CURP) y SAT (RFC) cuando las APIs estén disponibles.
- **Rate limiting**: Protección contra abuso por IP.
- **Postgres**: Migración de SQLite para escrituras concurrentes en producción.
