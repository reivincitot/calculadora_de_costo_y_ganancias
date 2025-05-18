import pytest
import requests
from unittest.mock import patch
from desktop_app.api_client import COSTOS_API_URL, calcular_precio_sugerido


class DummyResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json = json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Error")

    def json(self):
        return self._json


@patch("desktop_app.api_client.requests.get")
def test_calcular_precio_sugerido_success(mock_get):
    # Simulamos una respuesta 200 correcta
    mock_get.return_value = DummyResponse(200, {"sku": "ABC", "precio_sugerido": 123.45})
    result = calcular_precio_sugerido("ABC")
    expected_url = f"{COSTOS_API_URL}/costos/precio-sugerido/ABC"
    mock_get.assert_called_once_with(expected_url)
    assert result["precio_sugerido"] == 123.45


@patch("desktop_app.api_client.requests.get")
def test_calcular_precio_sugerido_http_error(mock_get):
    # Simulamos un 500 para probar el raise_for_status
    mock_get.return_value = DummyResponse(500, {})
    with pytest.raises(requests.HTTPError):
        calcular_precio_sugerido("XZY")
