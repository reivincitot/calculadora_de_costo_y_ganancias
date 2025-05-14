from core.infrastructure.repositories import InventoryRepository
from core.domain.inventory import InventoryMovement, InventoryBatch
from core.infrastructure.security.security_manager import check_permission


class inventoryService:
    def __init__(self, user: str, repo: InventoryRepository):
        self.user = user
        self.repo = repo

    def add_batch(self, sku: str, quantity: int, unit_cost: float):
        check_permission(self.user, "add_batch")
        batch = InventoryBatch(product_sku=sku, quantity=quantity, unit_cost=unit_cost)
        self.repo.insert_batch(batch)
        self.repo.insert_movement(InventoryMovement(
            product_sku=sku,
            quantity=quantity,
            movement_type='IN',
            unit_cost=unit_cost
        ))

    def consume(self, sku: str, quantity: int):
        check_permission(self.user, "consume_stock")
        batches = self.repo.get_batches_fifo(sku)
        remaining= quantity
        for batch in batches:
            if batch.quantity >= remaining:
                self.repo.update_batch_quantity(batch.id, batch.quantity - remaining)
                self.repo.insert_movement(InventoryMovement(
                    product_sku=sku,
                    quantity=remaining,
                    movement_type='OUT',
                    unit_cost=batch.unit_cost,
                    related_batch_id=batch.id
                ))
                return
            else:
                self.repo.update_batch_quantity(batch.id, 0)
                self.repo.insert_movement(InventoryMovement(
                    product_sku=sku,
                    quantity=batch.quantity,
                    movement_type='OUT',
                    unit_cost=batch.unit_cost,
                    related_batch_id=batch.id
                ))
                remaining -= batch.quantity

            if remaining > 0:
                raise ValueError(f"No hay suficiente stock para consumir {quantity} unidades de {sku}")

    def get_stock(self, sku: str) -> int:
        return self.repo.get_total_stock(sku)

    def stock_value(self, sku: str) -> float:
        return self.repo.get_total_stock_value(sku)
