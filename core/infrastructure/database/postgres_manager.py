import os
import psycopg
from psycopg.rows import dict_row
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()


class DatabaseManager:
    def __init__(self):
        self.conn_params = {
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT")
        }
        self._create_tables()

    @contextmanager
    def get_cursor(self):
        conn = psycopg.connect(**self.conn_params, row_factory=dict_row)
        try:
            with conn.cursor() as cur:
                yield cur
                conn.commit()
        finally:
            conn.close()

    def _create_tables(self):
        with self.get_cursor() as cur:
            cur.execute("""
            CREATE TABLE OF NOT EXiSTS lotes (
            id SERIAL PRIMARY KEY,
            sku VARCHAR(20) NOT NULL,
            cantidad INTEGER NOT NULL,
            costo_unitario Numeric(15,2),
            fecha_ingreso TIMESTAMP DEFAULT NOW(),
            documento_asociado VARCHAR(20)
            );
            CREATE TABLE IF NOT EXISTS movimientos (
            id SERIAL PRIMARY KEY,
            lote_id INTEGER REFERENCES lotes(id),
            tipo_movimiento VARCHAR(10) CHECK (tipo_movimiento IN ('ENTRADA', 'SALIDA')),
            cantidad INTEGER NOT NULL,
            fecha TIMESTAMP DEFAULT NOW()
            );
            """)
