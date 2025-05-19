import requests
from requests.exceptions import HTTPError


INVENTORY_API_URL = "http://localhost:8000/inventory"
COSTOS_API_URL = "http://localhost:8001/costos"

def calcular_precio_sugerido(sku: str):
    """
    Llama al endpoint /costos/precio-sugerido/{sku} y devuelve un dict:
    {"sku": "...", "precio_sugerido": ...}
    """
    try:
        response = requests.get(
            f"{COSTOS_API_URL}/costos/precio-sugerido/{sku.strip()}"
        )
        response.raise_for_status()
        return response.json()
    except HTTPError as e:
        raise ValueError(f"Error API: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        raise ConnectionError(f"No se pudo conectar a la API: {str(e)}")
    