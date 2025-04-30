from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
import base64
import json


class SecurityManager:
    def __init__(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )

    def generar_sello_digital(self, data: dict) -> str:
        """
        Implementación base para sellos digitales genéricos.
        Usa RSA-SHA256 y formato JSON canónico.
        """
        # 1. Serialización canónica
        serialized = json.dumps(data, sort_keys=True).encode()

        # 2. Generar hash SHA-256
        digest = hashes.Hash(hashes.SHA256())
        digest.update(serialized)
        hashed = digest.finalize()

        # 3. Firma con clave privada
        signature = self.private_key.sign(
            hashed,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # 4. Codificación Base64
        return base64.b64encode(signature).decode()
