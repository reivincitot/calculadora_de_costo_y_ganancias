# utils/logger.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()


class AuditLogger:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._configure_logger()
        return cls._instance

    def _configure_logger(self):
        self.logger = logging.getLogger("ERP_Audit")
        self.logger.setLevel(logging.INFO)

        # Formato ISO 8601 + información crítica
        formatter = logging.Formatter(
            fmt='%(asctime)s.%(msecs)03d|%(levelname)s|%(module)s|%(funcName)s|%(message)s',
            datefmt='%d-%m-%YT%H:%M:%S'
        )

        # Handler para archivo rotativo (ISO 27001 - Conservación)
        logs_dir = Path(__file__).parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True, parents=True)

        file_handler = RotatingFileHandler(
            filename=logs_dir / "audit_erp.log",
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)

        # Handler para consola solo en desarrollo
        if os.getenv("AMBIENTE") == "desarrollo":
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        self.logger.addHandler(file_handler)

    def log_event(self, level: str, user: str, event_type: str, details: str):
        log_message = f"USER:{user}|EVENT:{event_type}|DETAILS:{details}"
        getattr(self.logger, level.lower())(log_message)
