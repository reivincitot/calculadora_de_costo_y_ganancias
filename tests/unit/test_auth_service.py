import pytest
from unittest.mock import MagicMock
from core.application.auth import AuthService
from core.domain.entities import Usuario
from bcrypt import hashpw, gensalt

@pytest.fixture
def fake_repo():
    return MagicMock()

@pytest.fixture
def auth_service(fake_repo):
    return AuthService(fake_repo)

def test_autenticar_con_repo_nulo(auth_service, fake_repo):
    fake_repo.obtener_por_rut.return_value = None
    with pytest.raises(ValueError):
        auth_service.autenticar("00.000.000-0", "pwd")

def test_autenticar_success(auth_service, fake_repo):
    pwd = "Test123!"
    hashed = hashpw(pwd.encode(), gensalt()).decode()
    fake_user = Usuario(id=1, rut="55.555.555-5", nombre="Mock", rol="operador", hashed_password=hashed, activo=True)
    fake_repo.obtener_por_rut.return_value = fake_user

    u = auth_service.autenticar(fake_user.rut, pwd)
    assert u is fake_user

def test_autenticar_inactivo(auth_service, fake_repo):
    pwd = "Test999!"
    hashed = hashpw(pwd.encode(), gensalt()).decode()
    fake_user = Usuario(
        id=2,
        rut="66.666.666-6",
        nombre="MockOff",
        rol="operador",
        hashed_password=hashed,
        activo=False
    )
    fake_repo.obtener_por_rut.return_value = fake_user

    with pytest.raises(ValueError) as exc:
        auth_service.autenticar(fake_user.rut, pwd)
    assert "inactivo" in str(exc.value)
