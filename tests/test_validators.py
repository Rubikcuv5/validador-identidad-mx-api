from fastapi.testclient import TestClient
from app.main import app
from app.validators import validate_curp, validate_rfc

client = TestClient(app)


# --- Endpoints ---


def test_endpoint_curp():
    r = client.get("/validate/curp/BADD110313HCMLNS09")
    assert r.status_code == 200
    assert r.json()["valid"] is True


def test_endpoint_rfc():
    r = client.get("/validate/rfc/GODE561231GR8")
    assert r.status_code == 200
    assert r.json()["valid"] is True


# --- CURP ---


def test_curp_valido():
    # CURP real con dígito verificador correcto
    result = validate_curp("BADD110313HCMLNS09")
    assert result["valid"] is True
    assert result["type"] == "CURP"


def test_curp_formato_invalido():
    result = validate_curp("INVALIDO123")
    assert result["valid"] is False
    assert "Formato" in result["reason"]


def test_curp_digito_verificador_incorrecto():
    # BADD110313HCMLNS09 es válido; cambiamos el último dígito
    result = validate_curp("BADD110313HCMLNS07")
    assert result["valid"] is False
    assert "verificador" in result["reason"]


# --- RFC ---


def test_rfc_valido():
    result = validate_rfc("GODE561231GR8")
    assert result["valid"] is True
    assert result["type"] == "RFC"


def test_rfc_formato_invalido():
    result = validate_rfc("123INVALIDO")
    assert result["valid"] is False
    assert "Formato" in result["reason"]


def test_rfc_fecha_imposible():
    # Mes 13, día 32 → fecha imposible
    result = validate_rfc("XAXX991332XXX")
    assert result["valid"] is False
    assert "imposible" in result["reason"]
