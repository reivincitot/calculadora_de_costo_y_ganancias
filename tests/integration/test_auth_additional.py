# tests/integration/test_auth_additional.py

import pytest
from core.application.auth import AuthService
from core.infrastructure.repositories import UsuarioPGRepository

@pytest.fixture
def auth_service():
    repo = UsuarioPGRepository()
    return AuthService(repo)

def test_autenticacion_fallida_usuario_inexistente(auth_service):
    with pytest.raises(ValueError) as exc:
        auth_service.autenticar("99.999.999-9", "cualquier")
    assert "Credenciales inválidas" in str(exc.value)

def test_autenticacion_fallida_password_incorrecta(auth_service):
    # Primero registro un usuario válido
    usuario_data = {
        'rut': '11.111.111-1',
        'nombre': 'User Test',
        'password': 'ClaveCorrecta!',
        'rol': 'operador'
    }
    auth_service.registrar_usuario(usuario_data)

    # Intento autenticar con contraseña errónea
    with pytest.raises(ValueError) as exc:
        auth_service.autenticar(usuario_data['rut'], "ClaveIncorrecta")
    assert "Credenciales inválidas" in str(exc.value)

def test_registro_usuario_duplicado(auth_service):
    usuario_data = {
        'rut': '22.222.222-2',
        'nombre': 'Duplicado',
        'password': 'Pwd123!',
        'rol': 'operador'
    }
    # primer registro OK
    auth_service.registrar_usuario(usuario_data)
    # segundo registro debe fallar
    with pytest.raises(Exception):
        auth_service.registrar_usuario(usuario_data)

def test_usuario_activo_por_defecto(auth_service):
    usuario_data = {
        'rut': '33.333.333-3',
        'nombre': 'ActivoTest',
        'password': 'PwdActivo!',
        'rol': 'operador'
    }
    nuevo = auth_service.registrar_usuario(usuario_data)
    # acceder directamente al repo para comprobar campo activo
    repo = auth_service.user_repo
    u = repo.obtener_por_rut(usuario_data['rut'])
    assert u.activo is True

def test_eliminacion_usuario(auth_service):
    usuario_data = {
        'rut': '44.444.444-4',
        'nombre': 'EliminarTest',
        'password': 'PwdElim!',
        'rol': 'admin'
    }
    nuevo = auth_service.registrar_usuario(usuario_data)
    # ahora elimino
    auth_service.user_repo.eliminar(nuevo.id)
    # debe fallar al autenticar
    with pytest.raises(ValueError):
        auth_service.autenticar(usuario_data['rut'], usuario_data['password'])
