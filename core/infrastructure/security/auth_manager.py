from hashlib import pbkdf2_hmac
import secrets
from core.infrastructure.database.postgres_manager import DatabaseManager


class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()
        self._create_users_table()
        self._create_access_log_table()

    def _create_users_table(self):
        with self.db.get_cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    username VARCHAR(50) PRIMARY KEY,
                    password_hash VARCHAR(64) NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    salt VARCHAR(32) NOT NULL
                )
            """)

    def _create_access_log_table(self):
        with self.db.get_cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS access_log (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) NOT NULL,
                    success BOOLEAN NOT NULL,
                    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
                    FOREIGN KEY (username) REFERENCES usuarios(username)
                )
            """)

    def _hash_password(self, password: str, salt: str) -> str:
        iterations = 100000
        return pbkdf2_hmac('sha256', password.encode(), salt.encode(), iterations).hex()

    def create_user(self, username: str, password: str, role: str) -> bool:
        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)

        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    INSERT INTO usuarios (username, password_hash, role, salt)
                    VALUES (%s, %s, %s, %s)
                """, (username, password_hash, role, salt))
            return True
        except Exception:
            return False

    def authenticate(self, username: str, password: str) -> bool:
        success = False
        try:
            with self.db.get_cursor() as cur:
                cur.execute(
                    """
                    SELECT password_hash, salt
                    FROM usuarios
                    WHERE username = %s
                    """, (username,)
                )
                result = cur.fetchone()
                if not result:
                    return False

                stored_hash = result['password_hash']
                salt = result['salt']
                success = self._hash_password(password, salt) == stored_hash
                return success
        finally:
            self._log_access_attempt(username, success)

    def get_user_role(self, username: str) -> str:
        with self.db.get_cursor() as cur:
            cur.execute("SELECT role FROM usuarios WHERE username = %s", (username,))
            result = cur.fetchone()
            return result['role'] if result else 'invitado'

    def admin_exists(self) -> bool:
        with self.db.get_cursor() as cur:
            cur.execute(
                """
                SELECT EXISTS(
                    SELECT 1 FROM usuarios WHERE role = 'admin'
                ) AS admin_exists
                """
            )
            result = cur.fetchone()
            return result['admin_exists']

    def _log_access_attempt(self, username: str, success: bool):
        with self.db.get_cursor() as cur:
            cur.execute(
                """
                INSERT INTO access_log (username, success, timestamp)
                VALUES (%s, %s, NOW())    
                """, (username, success)
            )
