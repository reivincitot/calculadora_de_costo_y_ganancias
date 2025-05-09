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
                -- tabla de usuarios para login
                CREATE TABLE IF NOT EXISTS usuarios (
                    username VARCHAR(50) PRIMARY KEY,
                    password_hash VARCHAR(64) NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    salt VARCHAR(32) NOT NULL
                );

                -- tabla de access_log para auditoría
                CREATE TABLE IF NOT EXISTS access_log (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) NOT NULL,
                    success BOOLEAN NOT NULL,
                    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
                    FOREIGN KEY (username) REFERENCES usuarios(username)
                );

                -- tabla de lotes
                CREATE TABLE IF NOT EXISTS lotes (
                    id SERIAL PRIMARY KEY,
                    sku VARCHAR(20) NOT NULL,
                    cantidad INTEGER NOT NULL CHECK (cantidad >= 0),
                    costo_unitario NUMERIC(15,2) NOT NULL,
                    fecha_ingreso TIMESTAMP DEFAULT NOW(),
                    documento_asociado VARCHAR(20)
                );

                -- movimientos de inventario
                CREATE TABLE IF NOT EXISTS movimientos (
                    id SERIAL PRIMARY KEY,
                    lote_id INTEGER REFERENCES lotes(id),
                    tipo_movimiento VARCHAR(10) NOT NULL 
                        CHECK (tipo_movimiento IN ('ENTRADA','SALIDA')),
                    cantidad INTEGER NOT NULL,
                    usuario VARCHAR(50),
                    documento VARCHAR(20),
                    fecha TIMESTAMP DEFAULT NOW()
                );

                -- tabla de productos base
                CREATE TABLE IF NOT EXISTS productos (
                    id SERIAL PRIMARY KEY,
                    codigo_base VARCHAR(20) NOT NULL UNIQUE,
                    nombre VARCHAR(100) NOT NULL,
                    material VARCHAR(50),
                    grosor_mm NUMERIC(5,2),
                    color VARCHAR(50),
                    descripcion TEXT
                    activo BOOLEAN NOT NULL DEFAULT TRUE
                );

                -- columna para referenciar productos en lotes
                ALTER TABLE lotes 
                  ADD COLUMN IF NOT EXISTS producto_id 
                    INTEGER REFERENCES productos(id);
            """)
