from core.domain.entities import Usuario
from core.infrastructure.database import Database


class UsuarioPGRepository:
    def __init__(self, pool=None):
        self.pool = pool or Database.get_pool()

    def obtener_por_rut(self, rut: str) -> Usuario:
        with self.pool.connection() as conn:
            with conn.cursor() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id, rut, nombre, rol, hashed_password, activo FROM usuarios WHERE rut = %s",
                        (rut,)
                    )
                    result = cur.fetchone()
                    if result:
                        return Usuario(
                            id=result[0],
                            rut=result[1],
                            nombre=result[2],
                            rol=result[3],
                            hashed_password=result[4],
                            activo=result[5]
                        )
                    return None

    def guardar(self, usuario: Usuario) -> Usuario:
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                if usuario.id is None:
                    cur.execute(
                        """INSERT INTO usuarios
                        (rut, nombre, rol, hashed_password, activo)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id""",
                        (usuario.rut, usuario.nombre, usuario.rol, usuario.hashed_password, usuario.activo)
                    )
                    usuario.id = cur.fetchone()[0]
                else:
                    cur.execute(
                        """UPDATE usuarios SET
                        rut = %s, nombre = %s, rol = %s,
                        hashed_password = %s, activo = %s
                        WHERE id = %s""",
                        (usuario.rut, usuario.nombre, usuario.rol, usuario.hashed_password, usuario.activo, usuario.id)
                    )
                return usuario
