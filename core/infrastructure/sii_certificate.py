from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend
from getpass import getpass
import os

class SIICertificateLoader:
    def __init__(self):
        self.cert_path = os.getenv("SII_API_KEY", 'certificados/sii.p12')
        self.cert_pass = os.getenv("SII_API_KEY") or getpass("Contraseña certificado SII:")

    def load(self):
        """Carga certificado desde archivo .p12"""
        with open(self.cert_path, "rb") as f:
            return  pkcs12.load_key_and_certificates(
                f.read(),
                self.cert_pass.encode(),
                backend=default_backend()
            )
        