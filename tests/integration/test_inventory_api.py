import os
import pytest
from fastapi.testclient import TestClient

# Forzamos la DB de testing
os.environ["DB_NAME"] = "erp8102_test"
os.environ["DB_USER"] = "postgres"
os.environ["DB_PASSWORD"] = "admin123"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"

from inventory_api.main import app
from inventory_api.database import engine, Base, SessionLocal

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    # Creamos tablas en la DB de testing
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

def test_create_batch_endpoint(client):
    payload = {"sku": "ENDPT1", "quantity": 7, "unit_cost": 3.14}
    resp = client.post("/inventory/batches/", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["sku"] == "ENDPT1"
    assert data["quantity"] == 7
    assert resp.json()["id"] is not None

def test_read_stock_and_value(client):
    # Ya existe ENDPT1 con 7 uds a 3.14
    r1 = client.get("/inventory/stock/ENDPT1")
    assert r1.status_code == 200 and r1.json()["stock"] == 7

    r2 = client.get("/inventory/stock_value/ENDPT1")
    assert r2.status_code == 200
    assert pytest.approx(r2.json()["stock_value"], rel=1e-6) == 7 * 3.14

def test_consume_endpoint_success(client):
    # Consumimos 5 unidades
    resp = client.post("/inventory/consume/ENDPT1", params={"quantity": 5})
    assert resp.status_code == 200
    body = resp.json()
    assert body["sku"] == "ENDPT1"
    assert body["quantity"] == 5
    assert pytest.approx(body["total_cost"], rel=1e-6) == 5 * 3.14

    # Ahora stock remanente = 2
    r = client.get("/inventory/stock/ENDPT1")
    assert r.json()["stock"] == 2

def test_consume_endpoint_insufficient(client):
    # Intentamos consumir más de lo que queda
    resp = client.post("/inventory/consume/ENDPT1", params={"quantity": 10})
    assert resp.status_code == 400
    assert "No hay suficiente stock" in resp.json()["detail"]
