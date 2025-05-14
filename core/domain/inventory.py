from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class InventoryBatch:
    product_sku: str
    quantity: int
    unit_cost: float
    id: Optional[int] = None
    created_at: datetime = datetime.now()


@dataclass
class InventoryMovement:
    product_sku: str
    quantity: int
    movement_type: str  # 'IN' or 'OUT'
    unit_cost: float
    timestamp: datetime = datetime.now()
    related_batch_id: Optional[int] = None
    id: Optional[int] = None
