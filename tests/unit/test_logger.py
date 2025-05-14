import logging
from unittest.mock import patch, MagicMock
from utils.logger import AuditLogger



def test_logger_configuration():
    logger = AuditLogger().logger
    assert logger.name == "ERP_Audit"
    assert logger.level == logging.INFO
    assert len(logger.handlers) >= 1
    handler = logger.handlers[0]
    from logging.handlers import RotatingFileHandler
    assert isinstance(handler, RotatingFileHandler)


@patch("utils.logger.logging.getLogger")
def test_log_event(mock_get_logger):
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    logger = AuditLogger()
    test_details = "Intento de acceso"

    logger.log_event("INFO", "12.345.678-9", "AUTH_ATTEMPT", test_details)

    mock_logger.log.assert_called_once_with(
        logging.INFO,
        "USER:12.345.678-9|EVENT:AUTH_ATTEMPT|DETAILS:Intento de acceso"
    )