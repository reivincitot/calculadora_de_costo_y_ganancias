import requests


COSTOS_API_URL = "http://localhost:8001"

def calcular_precio_sugerido(sku: str):
    """
    Llama al endpoint /costos/precio-sugerido/{sku} y devuelve un dict:
    {"sku": "...", "precio_sugerido": ...}
    """
    resp = requests.get(f"{COSTOS_API_URL}/costos/precio-sugerido/{sku}")
    resp.raise_for_status()
    return resp.json()
