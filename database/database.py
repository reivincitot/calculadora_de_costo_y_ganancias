import os
from dotenv import load_dotenv
from pathlib import Path
import psycopg
from psycopg.rows import dict_row
from contextlib import contextmanager

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / '.env')


class Database:
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
            # lotes y movimientos originales
            cur.execute("""
                CREATE TABLE IF NOT EXISTS lotes (
                    id SERIAL PRIMARY KEY,
                    sku VARCHAR(20) NOT NULL,
                    cantidad INTEGER NOT NULL CHECK(cantidad>=0),
                    costo_unitario NUMERIC(15,2) NOT NULL,
                    fecha_ingreso TIMESTAMP DEFAULT NOW(),
                    documento_asociado VARCHAR(20)
                );
                CREATE TABLE IF NOT EXISTS movimientos (
                    id SERIAL PRIMARY KEY,
                    lote_id INTEGER REFERENCES lotes(id),
                    tipo_movimiento VARCHAR(10) NOT NULL CHECK(tipo_movimiento IN ('ENTRADA','SALIDA')),
                    cantidad INTEGER NOT NULL,
                    usuario VARCHAR(50),
                    documento VARCHAR(20),
                    fecha TIMESTAMP DEFAULT NOW()
                );
            """)

            # nuevas tablas para el Inventario genérico
            cur.execute("""
                CREATE TABLE IF NOT EXISTS batches (
                    id SERIAL PRIMARY KEY,
                    product_sku VARCHAR(50) NOT NULL,
                    quantity INTEGER NOT NULL CHECK(quantity>=0),
                    unit_cost NUMERIC(15,2) NOT NULL
                );
                CREATE TABLE IF NOT EXISTS movements (
                    id SERIAL PRIMARY KEY,
                    product_sku VARCHAR(50) NOT NULL,
                    quantity INTEGER NOT NULL,
                    movement_type VARCHAR(3) NOT NULL CHECK(movement_type IN ('IN','OUT')),
                    unit_cost NUMERIC(15,2) NOT NULL,
                    related_batch_id INTEGER REFERENCES batches(id),
                    timestamp TIMESTAMP DEFAULT NOW()
                );
            """)
