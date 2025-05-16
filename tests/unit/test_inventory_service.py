import pytest
from unittest.mock import MagicMock, call

from core.application.Inventory_service import InventoryService
from core.domain.inventory import InventoryBatch, InventoryMovement


def make_user(username: str, name: str):
    # Simple object with username and name attributes
    class User:
        def __init__(self, username, name):
            self.username = username
            self.name = name
    return User(username, name)

@pytest.fixture
def user_admin():
    return make_user('admin', 'Administrador')

@pytest.fixture
def repo_mock():
    repo = MagicMock()
    # prepare FIFO batches for consume tests
    def get_batches_fifo(sku):
        # two batches: batch1 id=1 qty=5 cost=10, batch2 id=2 qty=3 cost=20
        if sku == 'SKU1':
            b1 = InventoryBatch(product_sku='SKU1', quantity=5, unit_cost=10.0, id=1)
            b2 = InventoryBatch(product_sku='SKU1', quantity=3, unit_cost=20.0, id=2)
            return [b1, b2]
        return []
    repo.get_batches_fifo.side_effect = get_batches_fifo
    repo.get_total_stock.return_value = 8
    repo.get_total_stock_value.return_value = 5*10.0 + 3*20.0
    return repo

class TestInventoryService:
    def test_add_batch_calls_repo_and_movement(self, user_admin, repo_mock):
        service = InventoryService(user_admin, repo_mock)
        batch = service.add_batch('SKU1', 10, 15.5)

        # should insert batch then movement
        assert isinstance(batch, InventoryBatch)
        repo_mock.insert_batch.assert_called_once()
        repo_mock.insert_movement.assert_called_once()
        mov_arg = repo_mock.insert_movement.call_args[0][0]
        assert isinstance(mov_arg, InventoryMovement)
        assert mov_arg.product_sku == 'SKU1'
        assert mov_arg.quantity == 10
        assert mov_arg.unit_cost == 15.5
        assert mov_arg.movement_type == 'IN'

    def test_consume_partial_and_full_batches(self, user_admin, repo_mock):
        service = InventoryService(user_admin, repo_mock)
        # consume 6: should consume 5 from batch1 then 1 from batch2
        service.consume('SKU1', 6)

        # update and movement calls: first batch1, then batch2
        assert repo_mock.update_batch_quantity.call_count == 2
        assert repo_mock.update_batch_quantity.call_args_list[0] == call(1, 0)
        assert repo_mock.update_batch_quantity.call_args_list[1] == call(2, 2)

        # check movements: two calls
        assert repo_mock.insert_movement.call_count == 2
        m1, m2 = repo_mock.insert_movement.call_args_list
        mv1 = m1[0][0]
        mv2 = m2[0][0]
        assert mv1.quantity == 5 and mv1.movement_type == 'OUT'
        assert mv2.quantity == 1 and mv2.related_batch_id == 2

    def test_consume_insufficient_stock_raises(self, user_admin, repo_mock):
        service = InventoryService(user_admin, repo_mock)
        with pytest.raises(ValueError) as exc:
            service.consume('SKU1', 20)
        assert 'No hay suficiente stock' in str(exc.value)

    def test_get_stock_and_stock_value(self, user_admin, repo_mock):
        service = InventoryService(user_admin, repo_mock)
        stock = service.get_stock('SKU1')
        value = service.stock_value('SKU1')
        assert stock == 8
        assert value == 5*10.0 + 3*20.0

    def test_permission_denied_for_non_admin(self, repo_mock):
        user = make_user('usuario', 'Usuario Normal')
        service = InventoryService(user, repo_mock)
        with pytest.raises(PermissionError) as exc:
            service.add_batch('SKU1', 1, 1.0)
        assert "no tiene permiso" in str(exc.value)
