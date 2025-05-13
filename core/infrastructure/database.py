import os
from dotenv import load_dotenv
from utils.logger import AuditLogger
from psycopg_pool import ConnectionPool


load_dotenv()


class Database:
    _pool = None

    @classmethod
    def get_pool(cls):
        if not cls._pool:
            cls._pool = ConnectionPool(
                conninfo=f"""
                dbname={os.getenv('DB_NAME')}
                user={os.getenv('DB_USER')}
                password={os.getenv('DB_HOST')}
                host={os.getenv('DB_HOST')}
                port={os.getenv('DB_PORT')}
            """,
                min_size=1,
                max_size=10
            )
        return cls._pool

    @classmethod
    def execute_query(cls, query: str, params: tuple = None):
        logger = AuditLogger()
        logger.log_event("DEBUG", "system", "DB_QUERY", f"Ejecutando: {query}")

        with cls.get_pool().connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor
            except Exception as e:
                logger.log_event("ERROR", "system", "DB_FAILURE", str(e))
                raise
