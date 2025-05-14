import pytest
from core.application.auth import AuthService
from core.infrastructure.repositories import UsuarioPGRepository


@pytest.fixture
def auth_service():
    repo = UsuarioPGRepository()
    return AuthService(repo)


def test_autenticacion_exitosa(auth_service):
    # Setup
    test_user = {
        'rut': '12.345.678-9',
        'nombre': 'Test Admin',
        'password': 'SecurePass123!',
        'rol': 'admin'
    }

    nuevo_usuario = auth_service.registrar_usuario(test_user)

    # Test
    usuario = auth_service.autenticar(test_user['rut'], test_user['password'])

    # Verify
    assert usuario is not None
    assert usuario.rut == test_user['rut']
    assert usuario.rol == test_user['rol']
    assert usuario.nombre == test_user['nombre']

    # Cleanup
    auth_service.user_repo.eliminar(usuario.id)
