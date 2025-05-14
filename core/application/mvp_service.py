from dataclasses import dataclass
from core.infrastructure.database.database import Database


@dataclass
class MVPItem:
    nombre: str
    test_asociado: str
    completado: bool = False


class MVPStatusService:
    def __init__(self):
        self.pool = Database.get_pool()
        self.items = [
            MVPItem(nombre="Login", test_asociado="test_login"),
            MVPItem(nombre="Gestión de productos", test_asociado="test_gestion_productos"),
            MVPItem(nombre="Panel de ventas", test_asociado="test_panel_ventas"),
            MVPItem(nombre="Dashboard de análisis", test_asociado="test_dashboard_analisis")
        ]

    def obtener_items(self):
        return self.items

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
        total = len(self.items)
        completados = sum(1 for item in self.items if item.completado)
        return completados / total if total else 0.0
