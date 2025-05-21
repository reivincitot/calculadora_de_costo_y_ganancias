import pytest
from fastapi.testclient import TestClient
from auth_api.main import app as auth_app
from inventory_api.main import app as inv_app
from costos_api.main import app as cos_app

auth = TestClient(auth_app)
inv = TestClient(inv_app)
cos = TestClient(cos_app)


@pytest.fixture(scope="module")
def tokens():
    # 1) Register y login de admin
    auth.post("/auth/register", json={"username": "admin", "password": "secret", "role": "admin"})
    r1 = auth.post("/auth/login", data={"username": "admin", "password": "secret"})
    admin_token = r1.json()["access_token"]

    # 2) Register y login de operador
    auth.post("/auth/register", json={"username": "user1", "password": "secret", "role": "operador"})
    r2 = auth.post("/auth/login", data={"username": "user1", "password": "secret"})
    user_token = r2.json()["access_token"]

    return {"admin": admin_token, "user": user_token}


def test_admin_can_create_batch(tokens):
    resp = inv.post(
        "/inventory/batches/",
        json={"sku": "X", "quantity": 5, "unit_cost": 1.0},
        headers={"Authorization": f"Bearer {tokens['admin']}"}
    )
    assert resp.status_code == 201


def test_user_cannot_create_batch(tokens):
    resp = inv.post(
        "/inventory/batches/",
        json={"sku": "Y", "quantity": 1, "unit_cost": 1.0},
        headers={"Authorization": f"Bearer {tokens['user']}"}
    )
    assert resp.status_code == 403


def test_user_can_consume_and_read(tokens):
    # Admin crea primero
    r = inv.post(
        "/inventory/batches/",
        json={"sku": "Z", "quantity": 10, "unit_cost": 2.0},
        headers={"Authorization": f"Bearer {tokens['admin']}"}
    )
    batch_id = r.json()["id"]

    # Operador consume
    r2 = inv.post(
        f"/inventory/consume/Z?quantity=3",
        headers={"Authorization": f"Bearer {tokens['user']}"}
    )
    assert r2.status_code == 200
    assert r2.json()["total_cost"] == pytest.approx(3 * 2.0)

    # Y lee stock
    r3 = inv.get(
        "/inventory/stock/Z",
        headers={"Authorization": f"Bearer {tokens['user']}"}
    )
    assert r3.status_code == 200
    assert r3.json()["stock"] == 7


def test_costos_requires_auth(tokens):
    # Sin token
    r_no = cos.get("/costos/precio-sugerido/X")
    assert r_no.status_code in (401, 403)

    # Con token válido de operador/admin funciona igual:
    r = cos.get(
       "/costos/precio-sugerido/X",
       headers={"Authorization": f"Bearer {tokens['user']}"}
    )
    assert r.status_code in (200, 404)  # 404 si no existe el SKU
