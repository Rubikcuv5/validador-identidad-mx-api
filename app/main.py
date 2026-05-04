from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from app import cache, models
from app.validators import validate_curp, validate_rfc

app = FastAPI(title="Validador Identidad MX")


class ValidationRequest(BaseModel):
    document: str
    doc_type: Literal["CURP", "RFC"]


class ValidationResponse(BaseModel):
    valid: bool
    type: str
    value: str
    reason: str | None
    cached: bool


class AuditEntry(BaseModel):
    id: int
    doc_type: str
    doc_value: str
    is_valid: bool
    reason: str | None
    created_at: str


@app.post("/validate", response_model=ValidationResponse)
def validate(req: ValidationRequest):
    key = f"{req.doc_type}:{req.document.upper()}"
    cached = cache.get(key)
    if cached:
        return ValidationResponse(**cached, cached=True)

    result = validate_curp(req.document) if req.doc_type == "CURP" else validate_rfc(req.document)
    cache.set(key, result)
    models.save_audit(result["type"], result["value"], result["valid"], result["reason"])
    return ValidationResponse(**result, cached=False)


@app.get("/history", response_model=list[AuditEntry])
def history():
    return models.get_audit_log()
