# tests/integration/test_auth_db.py
import pytest
from core.application.auth import AuthService
from core.infrastructure.repositories import UsuarioPGRepository
from core.infrastructure.database import Database


@pytest.fixture(scope="module")
def db_pool():
    return Database.get_pool()


@pytest.fixture
def auth_service(db_pool):
    repo = UsuarioPGRepository(db_pool)
    return AuthService(repo)


def test_flujo_completo_autenticacion(auth_service):
    # 1. Registrar nuevo usuario
    test_rut = "99.888.777-6"
    test_password = "Ch$ll3ng3P@ss"

    user_id = auth_service.registrar_usuario({
        "rut": test_rut,
        "nombre": "Usuario Test",
        "rol": "operador",
        "password": test_password
    }).id

    # 2. Autenticar con credenciales válidas
    usuario_autenticado = auth_service.autenticar(test_rut, test_password)

    assert usuario_autenticado is not None
    assert usuario_autenticado.rol == "operador"
    assert usuario_autenticado.activo is True

    # 3. Autenticar con password incorrecto (ISO 27001 - Control de accesos)
    with pytest.raises(ValueError) as e:
        auth_service.autenticar(test_rut, "password_incorrecto")
    assert "Credenciales inválidas" in str(e.value)

    # 4. Limpieza (ISO 9001 - Mantener ambiente de pruebas)
    with db_pool.connection() as conn:
        conn.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
    conn.commit()
        