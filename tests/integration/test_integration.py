from core.application.inventory_service import InventoryService
def test_full_flow():
    # Configurar
    service = InventoryService()

    # Testear registro
    service.add_batch("TEST-001", 100, 1500)
    assert service.get_stock("TEST-001") == 100

    # Testear consumo
    cost = service.consume("TEST-001", 50, "test_user", "DOC-001")
    assert cost == 75000.0
    assert service.get_stock("TEST-001") == 50

    # Testear reporte
    report = service.generar_reporte_sii("TEST-001")
    assert len(report["lotes"]) == 1
    assert report["lotes"][0]["sku"] == "TEST-001"