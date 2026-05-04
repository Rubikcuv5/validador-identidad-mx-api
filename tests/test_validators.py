import os
import tempfile

# Usar DB temporal antes de importar la app
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ.setdefault("DB_PATH", _tmp.name)
_tmp.close()

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.validators import validate_curp, validate_rfc  # noqa: E402

client = TestClient(app)

VALID_CURP = "BADD110313HCMLNS06"


# --- Endpoints ---


def test_endpoint_curp():
    r = client.post("/validate", json={"document": VALID_CURP, "doc_type": "CURP"})
    assert r.status_code == 200
    assert r.json()["valid"] is True


def test_endpoint_rfc():
    r = client.post("/validate", json={"document": "GODE561231GR8", "doc_type": "RFC"})
    assert r.status_code == 200
    assert r.json()["valid"] is True


# --- CURP ---


def test_curp_valido():
    result = validate_curp(VALID_CURP)
    assert result["valid"] is True
    assert result["type"] == "CURP"


def test_curp_real_valido_emmanuel_cruz():
    result = validate_curp("CULE011101HOCRPMA3")
    assert result["valid"] is True


def test_curp_formato_invalido():
    result = validate_curp("INVALIDO123")
    assert result["valid"] is False
    assert "Formato" in result["reason"]


def test_curp_digito_verificador_incorrecto():
    # BADD110313HCMLNS06 es válido; cambiamos el último dígito
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
    result = validate_rfc("XAXX991332XXX")
    assert result["valid"] is False
    assert "imposible" in result["reason"]
