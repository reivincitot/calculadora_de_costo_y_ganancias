import re
from unidecode import unidecode
from core.infrastructure.database.postgres_manager import DatabaseManager


class SKUGenerator:
    def __init__(self):
        self.db = DatabaseManager()

    def _generar_codigo(self, texto: str, tipo: str) -> str:
        """
        Genera código automático según tipo (material/color)
        siguiendo reglas del SII:
        - Material: 3 primeras letras (sin espacios/acentos)
        - Color: 3 primeras consonantes significativas
        """
        texto_limpio = unidecode(texto).upper().replace(" ", "")  # Corregido unidecode

        if tipo == "material":
            return texto_limpio[:3].ljust(3, 'X')  # Rellena con X si es necesario

        elif tipo == "color":
            # Tomar primeras 3 consonantes omitiendo vocales
            consonantes = re.sub(r'[AEIOU]', '', texto_limpio)
            return (consonantes[:3] if len(consonantes) >= 3
                    else texto_limpio[:3].ljust(3, 'X'))

        return "GEN"

    def generar_base_sku(self, material: str, grosor_mm: float, color: str) -> str:
        """Genera base SKU dinámica sin hardcoding"""
        material_code = self._generar_codigo(material, "material")
        color_code = self._generar_codigo(color, "color")
        grosor_code = f"{int(round(grosor_mm)):02d}MM"  # 2 dígitos siempre

        return f"{material_code}-{grosor_code}-{color_code}"

    def generar_sku_completo(self, base: str) -> str:
        """Genera SKU final con secuencia numérica"""
        with self.db.get_cursor() as cur:
            # Busca el último SKU con el formato correcto
            cur.execute("""
                SELECT sku FROM lotes 
                WHERE sku ~ %s
                ORDER BY sku DESC
                LIMIT 1
            """, (f"^{re.escape(base)}-\\d{{4}}$",))  # Regex mejorada

            ultimo_sku = cur.fetchone()
            secuencia = 1

            if ultimo_sku:
                try:
                    # Extrae solo la parte numérica final
                    ultimo_numero = int(ultimo_sku['sku'].split('-')[-1])
                    secuencia = ultimo_numero + 1
                except (IndexError, ValueError):
                    pass  # Mantiene secuencia=1 si hay formato inválido

        return f"{base}-{secuencia:04d}"
