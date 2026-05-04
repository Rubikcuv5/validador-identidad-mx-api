import os
import tempfile

import pytest
from fastapi.testclient import TestClient

# Usar DB temporal antes de importar la app
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DB_PATH"] = _tmp.name
_tmp.close()

from app import cache  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app)

VALID_CURP = "BADD110313HCMLNS09"


@pytest.fixture(autouse=True)
def clear_state():
    cache._store.clear()
    yield


def test_validate_curp_valido():
    r = client.post("/validate", json={"document": VALID_CURP, "doc_type": "CURP"})
    assert r.status_code == 200
    data = r.json()
    assert data["valid"] is True
    assert data["cached"] is False


def test_validate_curp_cached():
    client.post("/validate", json={"document": VALID_CURP, "doc_type": "CURP"})
    r = client.post("/validate", json={"document": VALID_CURP, "doc_type": "CURP"})
    assert r.status_code == 200
    assert r.json()["cached"] is True


def test_validate_curp_invalido():
    r = client.post("/validate", json={"document": "INVALIDO123", "doc_type": "CURP"})
    assert r.status_code == 200
    assert r.json()["valid"] is False


def test_validate_tipo_incorrecto():
    r = client.post("/validate", json={"document": "X", "doc_type": "DNI"})
    assert r.status_code == 422


def test_history_no_vacio():
    client.post("/validate", json={"document": VALID_CURP, "doc_type": "CURP"})
    r = client.get("/history")
    assert r.status_code == 200
    assert len(r.json()) > 0
