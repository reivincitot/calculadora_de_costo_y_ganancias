from dataclasses import dataclass
from core.infrastructure.database import Database


@dataclass
class MVPItem:
    nombre: str
    completado: bool
    test_asociado: str

class MVPStatusService:
    def __init__(self):
        self.pool = Database.get_pool()
        self.items = [
            MVPItem("Login funcional", False, "test_autentication"),
            MVPItem("Registro de producto", False, "test_inventario"),
        ]

    def actualizar_estado(self):
        """Actualiza estado desde resultados de test en la base de datos"""
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                for item in self.items:
                    cur.execute(
                        "SELECT passed FROM test_results WHERE test_name = %s",
                        (item.test_asociado,)
                    )
                    result = cur.fetchone()
                    item.completado = result[0] if result else False

    def obtener_progreso(self) -> float:
        return sum(1 for item in self.items if item.completado) / len(self.items)