from core.domain.entities import Usuario
from core.infrastructure.database.database import Database
from core.domain.inventory import InventoryMovement, InventoryBatch


class UsuarioPGRepository:
    def __init__(self, pool=None):
        self.pool = pool or Database.get_pool()

    def obtener_por_rut(self, rut: str) -> Usuario:
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
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
            with conn.cursor() as cur:
                # Nuevo usuario si id es None o 0
                if usuario.id is None or usuario.id == 0:
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
        """Elimina un usuario de la base de datos por su ID."""
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM usuarios WHERE id = %s",
                    (user_id,)
                )


class InventoryRepository:
    def __init__(self, db: Database):
        self.db = db

    def insert_batch(self, batch: InventoryBatch):
        query = """"
            INSERT INTO batches (product_sku, quantity, unit_cost)
            VALUES (%s, %s, %s)
        """
        self.db.execute(query, (batch.product_sku, batch.quantity, batch.unit_cost))

    def insert_movement(self, movement: InventoryMovement):
        query = """
            INSERT INTO movements (product_sku, quantity, movement_type, unit_cost, related_batch_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        self.db.execute(query,(
            movement.product_sku,
            movement.quantity,
            movement.unit_cost,
            movement.related_batch_id
        ))

    def get_batches_fifo(self, sku: str):
        query = """
            SELECT id, product_sku, quantity, unit_cost
            FROM batches
            WHERE product_sku = %s AND quantity > 0
            ORDER BY id ASC
        """
        rows = self.db.fetch_all(query, (sku,))
        return [InventoryBatch(id=row[0], product_sku=row[1], quantity=row[2], unit_cost=row[3]) for row in rows]

    def update_batch_quantity(self, batch_id: int, new_quantity: int):
        query = "UPDATE batches SET quantity = %s WHERE id = %s"
        self.db.execute(query, (new_quantity, batch_id))

    def get_total_stock(self, sku: str) -> int:
        query = "SELECT SUM(quantity) FROM batches WHERE product_sku = %s"
        result = self.db.fetch_one(query, (sku,))
        return result[0] if result[0] is not None else 0

    def get_total_stock_value(self, sku: str) -> float:
        query = "SELECT SUM(quantity * unit_cost) FROM batches WHERE product_sku = %s"
        result = self.db.fetch_one(query, (sku,))
        return result[0] if result[0] is not None else 0.0
