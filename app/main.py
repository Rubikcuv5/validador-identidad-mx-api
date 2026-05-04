from fastapi import FastAPI
from app.validators import validate_curp, validate_rfc

app = FastAPI(title="Validador Identidad MX")


@app.get("/validate/curp/{curp}")
def curp(curp: str):
    return validate_curp(curp)


@app.get("/validate/rfc/{rfc}")
def rfc(rfc: str):
    return validate_rfc(rfc)
