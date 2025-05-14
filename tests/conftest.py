import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from core.infrastructure.database.database import Database
from core.infrastructure.repositories import UsuarioPGRepository
from core.application.auth import AuthService


@pytest.fixture(scope='session', autouse=True)
def configurar_entorno_testing():
    os.environ['DB_NAME'] = 'erp8102_test'
    os.environ['DB_USER'] = 'postgres'
    os.environ['DB_PASSWORD'] = 'admin123'
    os.environ['DB_HOST'] = 'localhost'
    os.environ['DB_PORT'] = '5432'

# Fixture que inicializa la base de datos antes de cada prueba
@pytest.fixture(autouse=True)
def inicializar_db():
    pool = Database.get_pool()
    with pool.connection() as conn:
        conn.execute("""
            DROP TABLE IF EXISTS usuarios CASCADE;
            CREATE TABLE usuarios (
                id SERIAL PRIMARY KEY,
                rut VARCHAR(12) UNIQUE NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                rol VARCHAR(50) NOT NULL,
                hashed_password TEXT NOT NULL,
                activo BOOLEAN NOT NULL DEFAULT TRUE
            );
        """)
        conn.commit()

# Fixture que retorna una instancia lista del AuthService
@pytest.fixture
def auth_service():
    pool = Database.get_pool()
    repo = UsuarioPGRepository(pool)
    return AuthService(repo)

@pytest.fixture(scope='session', autouse=True)
def cerrar_pool_final():
    yield
    if Database._pool:
        Database._pool.close()
