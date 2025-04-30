from core.domain.inventory import LoteSII, MovimientoInventario
from core.infrastructure.security.security_manager import SecurityManager
from typing import List, Dict
from datetime import datetime


class FIFOInventoryManager:
    def __init__(self):
        self.security = SecurityManager()
        self.lotes: List[LoteSII] = []
        self.historial: List[MovimientoInventario] = []

    def registrar_lote(self, lote_data: Dict) -> LoteSII:
        """Registra nuevo Lote con validación completa"""
        lote = LoteSII(**lote_data)
        self.lotes.append(lote)
        self._registrar_movimiento('ENTRADA', lote.cantidad,
                                   lote.costo_unitario * lote.cantidad,
                                   lote.documento_relacionado)
        return lote

    def consumir_stock(self, cantidad: int, usuario: str, documento: str) -> float:
        """Ejecuta consumo FIFO con trazabilidad"""
        if cantidad <= 0:
            raise ValueError("Cantidad debe ser positiva")

        costo_total = 0.0
        cantidad_restante = cantidad

        # Ordenar por fecha más antigua primero
        sorted_lotes = sorted(self.lotes, key=lambda x: x.fecha_ingreso)

        for lote in sorted_lotes:
            if cantidad_restante <= 0:
                break

            disponible = lote.cantidad
            if disponible <= 0:
                continue

            consumir = min(disponible, cantidad_restante)
            costo_total += consumir * lote.costo_unitario
            lote.cantidad -= consumir
            cantidad_restante = consumir

            # Registrar movimiento parcial
            self._registrar_movimiento(
                tipo='SALIDA',
                cantidad=consumir,
                costo_total=consumir * lote.costo_unitario,
                referencia=documento,
                usuario=usuario
            )

            if cantidad_restante > 0:
                raise ValueError(f"Stock insuficiente. Faltan {cantidad_restante} unidades")

            # Eliminar lotes vacíos
            self.lotes = [l for l in self.lotes if l.cantidad > 0]

            return costo_total

        def _registrar_movimiento(self, tipo: str, cantidad: int,
                                  costo_total: float, referencia: str, usuario: str):
            """Registro de auditoría ISO 9001"""
            movimiento = MovimientoInventario(
                tipo=tipo,
                cantidad=cantidad,
                costo_total=costo_total,
                referencia=referencia,
                usuario=usuario
            )
            self.historial.append(movimiento)

        def generar_reporte_sii(self) -> Dict:
            """Genera reporte en formato compatible con SII"""
            reporte = {
                "lotes": [l.dict() for l in self.lotes],
                "movimientos": [m.dict() for m in self.historial],
                "fecha_reporte": datetime.now().isoformat(),
                "sello_digital": self._generar_sello_digital()
            }
            reporte["sello_digital"] = self.security.generar_sello_digital(reporte)
            return reporte
        def _generar_sello_digital(self) -> str:
            """Generar sello para validación integridad (ISO 27001)"""
