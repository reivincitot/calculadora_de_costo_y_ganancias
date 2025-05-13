from bcrypt import hashpw, gensalt, checkpw
from core.domain.entities import Usuario


class AuthService:
    def __init__(self, user_repository):
        self.user_repo = user_repository

    def autenticar(self, rut: str, password: str) -> Usuario:
        usuario = self.user_repo.obtener_por_rut(rut)
        if not usuario or not checkpw(password.encode(), usuario.hashed_password.encode()):
            raise ValueError("Credenciales inválidas")
        return usuario

    def registrar_usuario(self, usuario_data: dict) -> Usuario:
        hashed = hashpw(usuario_data['password'].enconde(), gensalt()).decode()
        nuevo_usuario = Usuario(
            rut=usuario_data['rut'],
            nombre=usuario_data['nombre'],
            rol=usuario_data['rol'],
            hashed_password=hashed
        )
        return self.user_repo.guardar(nuevo_usuario)
    