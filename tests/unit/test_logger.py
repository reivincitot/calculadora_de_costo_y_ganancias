# tests/unit/test_logger.py
import logging
from unittest.mock import patch
from utils.logger import AuditLogger



def test_logger_configuration():
    logger = AuditLogger().logger

    assert logger.name == "ERP_Audit"
    assert logger.level == logging.INFO
    assert len(logger.handlers) >= 1  # Depende del ambiente

    handler = logger.handlers[0]
    assert isinstance(handler, logging.handlers.RotatingFileHandler)


@patch("calculadora_de_costo_y_ganancias.utils.logger.AuditLogger.logger")
def test_log_event(mock_log):
    logger = AuditLogger()
    test_details = "Intento de acceso"

    logger.log_event("INFO", "12.345.678-9", "AUTH_ATTEMPT", test_details)

    mock_log.assert_called_once()
    args, kwargs = mock_log.call_args
    assert args[0] == logging.INFO
    assert test_details in args[1]
