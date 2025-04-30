from abc import ABC, abstractmethod
from typing import Optional


class SIIAdapter(ABC):
    @abstractmethod
    def enviar_documento(self, xml_data: str) -> dict:
        pass

class SIIDesarrollo(SIIAdapter):
    """Mock del SII para ambiente de desarrollo"""
    def enviar_documento(self, xml_data: str) -> dict:
        return {
            "status": "success",
            "ambiente": "desrrollo",
            "track_id": "MOCK-123",
            "fecha": "2024-01-01",
            "sello": "SIMULADO"
        }

class SIIProduccion(SIIAdapter):
    """Implementeción real para producción"""
    def __init__(self, security_manager):
        self.security = security_manager

    def enviar_documento(self, xml_data:str ) -> dict:
        # Lógica real usando request a la API del SII
        pass

class SIIIntegration:
    def __init__(self, adapter: Optional[SIIAdapter] = None):
        self.adapter = adapter or SIIDesarrollo()

    def enviar_documento(self, xml_data: str) -> dict:
        return self.adapter.enviar_documento(xml_data)