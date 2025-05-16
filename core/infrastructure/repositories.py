from core.domain.entities import Usuario
from core.domain.inventory import InventoryBatch, InventoryMovement
from core.infrastructure.database.database import Database


class UsuarioPGRepository:
    def __init__(self, pool=None):
        self.pool = pool or Database.get_pool()

    def obtener_por_rut(self, rut: str) -> Usuario:
        with self.pool.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, rut, nombre, rol, hashed_password, activo
                FROM usuarios
                WHERE rut = %s
                """,
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
            cur = conn.cursor()
            # Insertar o actualizar según id
            if not usuario.id:
                cur.execute(
                    """
                    INSERT INTO usuarios
                        (rut, nombre, rol, hashed_password, activo)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        usuario.rut,
                        usuario.nombre,
                        usuario.rol,
                        usuario.hashed_password,
                        usuario.activo,
                    )
                )
                usuario.id = cur.fetchone()[0]
            else:
                cur.execute(
                    """
                    UPDATE usuarios SET
                        rut = %s,
                        nombre = %s,
                        rol = %s,
                        hashed_password = %s,
                        activo = %s
                    WHERE id = %s
                    """,
                    (
                        usuario.rut,
                        usuario.nombre,
                        usuario.rol,
                        usuario.hashed_password,
                        usuario.activo,
                        usuario.id,
                    )
                )
        return usuario

    def eliminar(self, user_id: int) -> None:
        with self.pool.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM usuarios WHERE id = %s",
                (user_id,)
            )


class InventoryRepository:
    """
    Implementación de repositorio para gestión de inventario.
    Usa tablas 'batches' y 'movements' en PostgreSQL.
    """
    def __init__(self, pool=None):
        self.pool = pool or Database.get_pool()

    def insert_batch(self, batch: InventoryBatch) -> None:
        with self.pool.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO batches (sku, quantity, unit_cost)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (batch.product_sku, batch.quantity, batch.unit_cost)
            )
            batch.id = cur.fetchone()[0]

    def insert_movement(self, mov: InventoryMovement) -> None:
        with self.pool.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO movements
                  (batch_id, movement_type, quantity, unit_cost, created_at)
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (mov.related_batch_id, mov.movement_type, mov.quantity, mov.unit_cost)
            )

    def get_batches_fifo(self, sku: str) -> list[InventoryBatch]:
        with self.pool.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, sku, quantity, unit_cost
                FROM batches
                WHERE sku = %s AND quantity > 0
                ORDER BY created_at
                """,
                (sku,)
            )
            rows = cur.fetchall()
            return [InventoryBatch(product_sku=row[1], quantity=row[2], unit_cost=row[3], id=row[0]) for row in rows]

    def update_batch_quantity(self, batch_id: int, new_qty: int) -> None:
        with self.pool.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE batches SET quantity = %s WHERE id = %s",
                (new_qty, batch_id)
            )

    def get_total_stock(self, sku: str) -> int:
        with self.pool.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT COALESCE(SUM(quantity), 0) FROM batches WHERE sku = %s",
                (sku,)
            )
            return cur.fetchone()[0]

    def get_total_stock_value(self, sku: str) -> float:
        with self.pool.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT COALESCE(SUM(quantity * unit_cost), 0.0) FROM batches WHERE sku = %s",
                (sku,)
            )
            return float(cur.fetchone()[0])
