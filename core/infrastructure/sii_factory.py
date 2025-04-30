import os
from .security import SIISecurityManager
from ..application.sii_integration import SIIProduccion, SIIDesarrollo


def get_sii_adapter():
    ambiente = os.getenv("AMBIENTE", "desarrollo")

    if ambiente == "produccion":
        return SIIProduccion(SIISecurityManager())
    return SIIDesarrollo()