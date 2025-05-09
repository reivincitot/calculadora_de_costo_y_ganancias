import logging
import os


def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)

    # Crea directorio de logs si no existe
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Configurar handler para archivo
    file_handler = logging.FileHandler(f"{log_dir}/app_errors.log")
    file_formater = logging.Formatter(
        '%(asctime)s -%(name)s -%(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formater)

    # Configurar handler para consola
    console_handler = logging.StreamHandler
    console_formatter = logging.Formatter('%(levelname)s -(message)s')
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()