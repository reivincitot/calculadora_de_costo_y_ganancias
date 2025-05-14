# setup.py
from setuptools import setup, find_packages

setup(
    name="calculadora_de_costo_y_ganancias",
    version="0.1",
    packages=find_packages(exclude=["tests*", ".venv*"]),
)
