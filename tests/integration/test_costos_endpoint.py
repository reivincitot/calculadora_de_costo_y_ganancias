import pytest
from fastapi.testclient import TestClient
from costos_api.main import app
from costos_api.database import init_db, engine, SessionLocal
from costos_api.models import Costos


client = TestClient(app)

def test_precio_sugerido_endpoint_existente(tmp_path, monkeypatch):
    # Preparamos un registro en la tabla costos
    from inventory_api.database import get_db, Base, engine
    from inventory_api.models import Costos

    Base.metadata.create_all(engine)
    db = next(get_db())
    db.add(Costos(sku="TEST01", concepto="C1", monto=20.0))
    db.commit()

    resp = client.get("/costos/precio-sugerido/TEST01")
    assert resp.status_code == 200
    data = resp.json()
    assert data["sku"] == "TEST01"
    assert data["precio_sugerido"] == pytest.approx(20.0 * 1.3)  # si tu lógica aplica, p.ej. +30%

def test_precio_sugerido_no_existente():
    resp = client.get("/costos/precio-sugerido/NOEXISTE")
    assert resp.status_code == 404

@pytest.fixture(autouse=True)
def prepare_db():
    init_db()
    # limpiar
    with SessionLocal() as db:
        db.query(Costos).delete()
        db.commit()
    yield
def test_precio_sugerido_flow():
    # Creo un costo
    client.post("/costos/", json={"sku":"XYZ","concepto":"C1","monto":50.0})
    # Consulto precio sugerido
    resp = client.get("/costos/precio-sugerido/XYZ")
    assert resp.status_code == 200
    data = resp.json()
    assert data["sku"] == "XYZ"
    assert data["precio_sugerido"] == pytest.approx(65.0)