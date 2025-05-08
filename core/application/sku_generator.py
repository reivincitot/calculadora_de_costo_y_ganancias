import re
from core.infrastructure.database.postgres_manager import DatabaseManager


class SKUGenerator:
    def __init__(self):
        self.db = DatabaseManager()

    def generar_sku(self, base: str) -> str:
        """
        Genera un SKU con prefijo base y número correlativo basado en SKUS ya existentes.
        Ejemeplo: base = "MAT-ALU02" -> resultado = "MAT-ALU02.0001"
        """
        with self.db.get_cursor() as cur:
            cur.execute("""
                    SELECT sku FROM lotes WHERE sku LIKE %s
            """, (f"{base}-%",))
            existentes = [row['sku'] for row in cur.fetchall()]

        secuencias = [int(re.search(rf"{base}-(\d+)", sku).group(1))
                      for sku in existentes if re.search(rf"{base}-(\d+)", sku)]

        next_number = max(secuencias, default=0) + 1
        return f"{base}-{next_number:04d}"
