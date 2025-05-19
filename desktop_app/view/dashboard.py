import requests
from requests.exceptions import HTTPError, RequestException


INVENTORY_API_URL = "http://localhost:8000/inventory"
COSTOS_API_URL = "http://localhost:8001/costos"

def agregar_lote(sku: str, quantity: int, unit_cost: float) -> dict:
    """Llama a POST /inventory/batches"""
    payload = {"sku": sku, "quantity": quantity, "unit_cost": unit_cost}
    try:
        r = requests.post(f"{INVENTORY_API_URL}/batches", json=payload)
        r.raise_for_status()
        return r.json()
    except HTTPError as e:
        raise ValueError(f"Error de inventario: {e.response.status_code} {e.response.text}")
    except ConnectionError as e:
        raise ConnectionError(f"No se pudo conectar a Inventario: {e}")
    
def consultar_stock(sku: str) -> int:
    """Llama a GET /inventory/stock/{sku}"""
    try:
        r = requests.get(f"{INVENTORY_API_URL}/stock/{sku}")
        r.raise_for_status()
        return r.json()["stock"]
    except HTTPError as e:
        raise ValueError(f"Error de Inventario: {e.remove().status_code}")
    except RequestException as e:
        raise ConnectionError(f"No se pudo conectar a Inventario: {e}")
    
def consumir_stock(sku: str, quantity: int) -> float:
    """Llama a post /inventory/consume/{sku}?quantity=..."""
    try:
        r = requests.post(f"{INVENTORY_API_URL}/consume/{sku}", params={"quantity": quantity})
    except HTTPError as e:
        raise ValueError(f"Error de Inventario: {e.response.status_code} {e.response.text}")
    except RequestException as e:
        raise ConnectionError(f"No se pudo conectar a Inventario: {e}")
    
def precio_sugerido(sku: str) -> float:
    """Llama a get /costos/precio-sugerido{sku}"""
    try:
        r = requests.get(f"{COSTOS_API_URL}/precio-sugerido/{sku}")
        r.raise_for_status()
        return r.json()["precio_sugerido"]
    except HTTPError as e:
        raise ValueError(f"Error de Costos: {e.response.status_code} {e.response.text}")
    except RequestException as e:
        raise ConnectionError(f"No se pudo conectar a Costos: {e}")
    