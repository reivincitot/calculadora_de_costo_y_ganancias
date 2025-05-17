import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from inventory_api import database, models, crud, schemas

# Configuramos SQLite en memoria para unit tests
SQLITE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="module")
def db_engine():
    engine = create_engine(SQLITE_URL)
    database.Base.metadata.create_all(bind=engine)
    yield engine
    database.Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()

def test_create_and_read_batch_and_movement(db_session):
    # Preparamos la entrada
    batch_in = schemas.BatchCreate(sku="ABC123", quantity=5, unit_cost=10.0)
    # Creamos lote
    created = crud.create_batch(db_session, batch_in)
    assert created.id is not None
    assert created.sku == "ABC123"
    assert created.quantity == 5

    # Debe existir también un movimiento IN
    mv = db_session.query(models.Movement).filter_by(batch_id=created.id).one()
    assert mv.movement_type == "IN"
    assert mv.quantity == 5

def test_consume_exact_and_partial(db_session):
    # Creamos un lote de 10 unidades a $2.5
    b = crud.create_batch(db_session, schemas.BatchCreate(sku="SKU1", quantity=10, unit_cost=2.5))
    # Consumimos 4 => costo 4*2.5 = 10.0
    cost = crud.consume_stock(db_session, "SKU1", 4)
    assert cost == pytest.approx(10.0)
    # Stock remanente
    remaining = db_session.query(models.Batch).get(b.id).quantity
    assert remaining == 6

    # Consumimos luego 6 => vacía lote
    cost2 = crud.consume_stock(db_session, "SKU1", 6)
    assert cost2 == pytest.approx(6 * 2.5)
    assert db_session.query(models.Batch).get(b.id).quantity == 0

def test_consume_insufficient_raises(db_session):
    # Intentar consumir más de lo disponible
    with pytest.raises(ValueError) as ei:
        crud.consume_stock(db_session, "NO_EXISTE", 1)
    assert "No hay suficiente stock" in str(ei.value)

def test_get_stock_and_value(db_session):
    # Insertamos dos lotes distintos
    crud.create_batch(db_session, schemas.BatchCreate(sku="X", quantity=3, unit_cost=5.0))
    crud.create_batch(db_session, schemas.BatchCreate(sku="X", quantity=2, unit_cost=7.0))
    # Stock total = 5
    assert crud.get_stock(db_session, "X") == 5
    # Valor total = 3*5 + 2*7 = 29.0
    assert crud.get_stock_value(db_session, "X") == pytest.approx(29.0)
