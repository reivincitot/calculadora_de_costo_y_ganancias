from cryptography.fernet import Fernet
from datetime import datetime


class AuditLogger:
    def __init__(self):
        self.key = Fernet.generate_key()

    def registrar(self, accion:str, usuario: str):
        log_entr = f"{datetime.now()} | {usuario} | {accion}"
        encrypted = Fernet(self.key).encrypt(log_entr.encode())
        with open("audit_log", "ab") as f:
            f.write(encrypted + b"\n")