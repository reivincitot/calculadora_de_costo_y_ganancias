import sys
from pathlib import Path

# Inserta el directorio raíz del proyecto para que 'import inventory_api' funcione
ROOT = Path(__file__).resolve().parents[1]  # ../.. desde tests/
sys.path.insert(0, str(ROOT))
