from typing import Dict
from datetime import datetime
from functools import lru_cache
from core.application.sku_generator import SKUGenerator
from core.domain.inventory import LoteSII, MovimientoInventario
from core.infrastructure.security.security_manager import SecurityManager
from core.infrastructure.database.postgres_manager import DatabaseManager


class InventoryService:
    def __init__(self):
        self.db = DatabaseManager()
        self.security = SecurityManager()
        self.sku_generator = SKUGenerator()

    # OPERACIONES PRINCIPALES
    def add_batch(self, sku: str, quantity: int, unit_cost: float, doc: str = None) -> LoteSII:
        """Registra nuevo lote con costo unitario"""
        with self.db.get_cursor() as cur:
            cur.execute("""
                INSERT INTO lotes (sku, cantidad, costo_unitario, documento_asociado)
                VALUES (%s, %s, %s, %s)
                RETURNING id, fecha_ingreso
            """, (sku, quantity, unit_cost, doc))

            lote_data = cur.fetchone()
            lote = LoteSII(
                id=lote_data['id'],
                sku=sku,
                cantidad=quantity,
                costo_unitario=unit_cost,
                fecha_ingreso=lote_data['fecha_ingreso'],
                documento_relacionado=doc
            )

            self._registrar_movimiento_db(cur, lote.id, 'ENTRADA', quantity)
            self.get_stock.cache_clear()
            return lote

    def consume(self, sku: str, quantity: int, user: str = "system", doc: str = None) -> float:
        """Consume stock usando FIFO y retorna costo total"""
        if self.get_stock(sku) < quantity:
            raise ValueError(f"Stock insuficiente para {sku}. Stock actual: {self.get_stock(sku)}")

        total_cost = 0.0
        remaining = quantity

        with self.db.get_cursor() as cur:
            cur.execute("""
                SELECT id, cantidad, costo_unitario 
                FROM lotes 
                WHERE sku = %s AND cantidad > 0 
                ORDER BY fecha_ingreso
                FOR UPDATE
            """, (sku,))

            for lote in cur.fetchall():
                if remaining <= 0:
                    break

                disponible = lote['cantidad']
                usar = min(disponible, remaining)

                # Actualizar lote
                cur.execute("""
                    UPDATE lotes 
                    SET cantidad = cantidad - %s 
                    WHERE id = %s
                """, (usar, lote['id']))

                new_quantity = cur.fetchone()['cantidad']
                if new_quantity == 0:
                    cur.execute("DELETE FROM lotes WHERE id = %s", (lote['id'],))

                # Registrar movimiento y acumular costo
                self._registrar_movimiento_db(cur, lote['id'], 'SALIDA', usar, user, doc)
                total_cost += usar * lote['costo_unitario']
                remaining -= usar

            self.get_stock.cache_clear()
            return total_cost

    # CONSULTAS
    @lru_cache(maxsize=100)
    def get_stock(self, sku: str) -> int:
        """Stock disponible por SKU (con cache)"""
        with self.db.get_cursor() as cur:
            cur.execute("""
                SELECT COALESCE(SUM(cantidad), 0) AS stock
                FROM lotes
                WHERE sku = %s AND cantidad > 0
            """, (sku,))
            return int(cur.fetchone()['stock'])

    def stock_value(self) -> float:
        """Valor total del inventario (costo)"""
        with self.db.get_cursor() as cur:
            cur.execute("""
                SELECT COALESCE(SUM(cantidad * costo_unitario), 0.0)
                FROM lotes
                WHERE cantidad > 0
            """)
            return cur.fetchone()[0]

    # HELPERS
    def _registrar_movimiento_db(self, cursor, lote_id: int, tipo: str,
                                 cantidad: int, user: str = None, doc: str = None):
        cursor.execute("""
            INSERT INTO movimientos (lote_id, tipo_movimiento, cantidad, usuario, documento)
            VALUES (%s, %s, %s, %s, %s)
        """, (lote_id, tipo, cantidad, user, doc))

    # REPORTES
    def generar_reporte_sii(self, sku: str) -> Dict:
        """Genera reporte con sello digital válido"""
        with self.db.get_cursor() as cur:
            cur.execute("""
                SELECT id, sku, cantidad, costo_unitario, fecha_ingreso, documento_asociado
                FROM lotes
                WHERE sku = %s
            """, (sku,))
            lotes = [LoteSII(**row) for row in cur.fetchall()]

            cur.execute("""
                SELECT tipo_movimiento, cantidad, usuario, documento, fecha
                FROM movimientos
                WHERE lote_id IN %s
            """, (tuple(l.id for l in lotes),))

            reporte = {
                "lotes": [l.model_dump() for l in lotes],
                "movimientos": [MovimientoInventario.model_validate(row).model_dump() for row in cur.fetchall()],
                "fecha_reporte": datetime.now().isoformat()
            }

            reporte["sello_digital"] = self.security.generar_sello_digital(reporte)
            return reporte

    def get_average_cost(self, sku: str) -> float:
        with self.db.get_cursor() as cur:
            cur.execute("""
                SELECT AVG(costo_unitario) as avg_cost
                FROM lotes
                WHERE sku = %s AND cantidad > 0
            """, (sku,))
            return cur.fetchone()['avg_cost'] or 0.0

    def registrar_lote_con_sku_auto(self, base_sku: str, quantity: int, unit_cost: float, doc: str = None) -> LoteSII:
        """
        Registra un nuevo lote generando automáticamente el SKU basado en una base (por ejemplo, 'MAT-ALU02').
        """
        with self.db.get_cursor() as cur:
            # Obtener ID del producto base (corregido typo en SELECT)
            cur.execute("SELECT id FROM productos WHERE codigo_base = %s", (base_sku,))
            producto = cur.fetchone()
            if not producto:
                raise ValueError(f"Producto base {base_sku} no existe")

            nuevo_sku = self.sku_generator.generar_sku(base_sku)

            # Insertar con referencia al producto (corregido nombre de tabla)
            cur.execute("""
                INSERT INTO lotes (sku, cantidad, costo_unitario, documento_asociado, producto_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, sku, cantidad, costo_unitario, fecha_ingreso, documento_asociado
            """, (nuevo_sku, quantity, unit_cost, doc, producto['id']))

            lote_data = cur.fetchone()
            lote = LoteSII(
                id=lote_data['id'],
                sku=lote_data['sku'],
                cantidad=lote_data['cantidad'],
                costo_unitario=lote_data['costo_unitario'],
                fecha_ingreso=lote_data['fecha_ingreso'],
                documento_relacionado=lote_data['documento_asociado']
            )

            self._registrar_movimiento_db(cur, lote.id, 'ENTRADA', quantity)
            return lote  # <-- ¡Faltaba este retorno!

    def list_inventory(self):
        """Obtiene inventario agrupado por SKU con costo promedio"""
        with self.db.get_cursor() as cur:
            cur.execute("""
                SELECT
                    sku,
                    SUM(cantidad) as stock,
                    ROUND(AVG(costo_unitario), 2) as average_cost
                FROM lotes
                GROUP BY sku
                ORDER BY sku
            """)
            return cur.fetchall()
