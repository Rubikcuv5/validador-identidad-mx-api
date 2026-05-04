# Arquitectura técnica

## Esquema de base de datos

```sql
CREATE TABLE audit_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_type   TEXT NOT NULL,          -- "CURP" | "RFC"
    doc_value  TEXT NOT NULL,          -- valor normalizado (uppercase)
    is_valid   INTEGER NOT NULL,       -- 0 | 1
    reason     TEXT,                   -- "OK" o descripción del error
    created_at TEXT NOT NULL           -- ISO 8601 UTC
);
```

El registro es **inmutable**: no hay UPDATE ni DELETE. Cada llamada a `POST /validate` que no sea cache hit genera una fila nueva.

## Cache

**Estructura interna** (`app/cache.py`):

```python
_store = {
    "CURP:BADD110313HCMLNS09": {
        "value": {"valid": True, "reason": "OK", ...},
        "expires_at": 1714812345.0   # time.time() + ttl
    }
}
```

**Cache key**: `"{doc_type}:{document.upper()}"` — normalización en mayúsculas garantiza que `badd110313hcmlns09` y `BADD110313HCMLNS09` sean el mismo hit.

**TTL por defecto**: 3600 segundos. Configurable por llamada en `cache.set(key, value, ttl_seconds)`.

**Invalidación**: pasiva (lazy expiry). La entrada permanece en memoria hasta que se intenta leer y se detecta que `time.time() > expires_at`.

## Algoritmo de validación CURP

El CURP tiene 18 caracteres con la siguiente estructura:

```
AAAA YYMMDD S EE CCC H D
│    │      │ │  │   │ └─ dígito verificador
│    │      │ │  │   └─── homoclave alfanumérica
│    │      │ │  └─────── 3 consonantes internas del apellido/nombre
│    │      │ └────────── clave de estado (2 letras)
│    │      └──────────── sexo (H/M)
│    └─────────────────── fecha de nacimiento (YYMMDD)
└──────────────────────── 4 letras iniciales
```

**Dígito verificador** (posición 18):

1. Mapear cada carácter a su índice en `"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"`.
2. Multiplicar cada valor por su peso `(18 - posición)` para las primeras 17 posiciones.
3. Sumar todos los productos.
4. `resto = suma % 10`
5. `dígito = 0 if resto == 0 else 10 - resto`

## Algoritmo de validación RFC

El RFC tiene 12 caracteres (persona moral) o 13 (persona física):

```
AAAA YYMMDD HHH
│    │      └─── homoclave (3 chars alfanuméricos)
│    └────────── fecha de nacimiento/constitución (YYMMDD)
└─────────────── 3-4 letras iniciales
```

La validación de fecha construye un objeto `datetime.date(year, month, day)` real. Si el constructor lanza `ValueError`, la fecha es imposible (ej. mes 13, día 32).

**Año**: `2000 + yy` si `yy <= 30`, sino `1900 + yy`. Cubre el rango 1931–2030.

## Flujo de request completo

```
Cliente
  │
  │  POST /validate {"document": "BADD110313HCMLNS09", "doc_type": "CURP"}
  ▼
FastAPI (Pydantic valida schema)
  │
  ├─ doc_type inválido ──► HTTP 422 (automático)
  │
  ▼
cache.get("CURP:BADD110313HCMLNS09")
  │
  ├─ HIT  ──► ValidationResponse(cached=True)
  │
  └─ MISS
       │
       ▼
  validate_curp(document)
       │
       ▼
  cache.set(key, result, ttl=3600)
  models.save_audit(...)
       │
       ▼
  ValidationResponse(cached=False)
```
