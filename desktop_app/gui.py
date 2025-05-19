import tkinter as tk
from tkinter import ttk, messagebox

from .logging_config import logger
from .api_client import (
    agregar_lote,
    consultar_stock,
    consumir_stock,
    precio_sugerido,
)


class InventoryApp(tk.Tk):
    """Aplicación de escritorio para gestión de inventario y consulta de precios."""

    def __init__(self):
        super().__init__()
        self.title("Gestión de Inventario y Costos")
        self.geometry("480x320")
        self.resizable(False, False)

        style = ttk.Style(self)
        style.configure("TNotebook.Tab", padding=[12, 8])
        style.configure("TFrame", padding=10)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self._build_add_tab()
        self._build_consult_tab()
        self._build_consume_tab()
        self._build_price_tab()

    def _build_add_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Agregar Lote")

        ttk.Label(frame, text="SKU:").grid(row=0, column=0, sticky="e")
        self.sku_add = ttk.Entry(frame, width=30)
        self.sku_add.grid(row=0, column=1, pady=4)

        ttk.Label(frame, text="Cantidad:").grid(row=1, column=0, sticky="e")
        self.qty_add = ttk.Entry(frame, width=30)
        self.qty_add.grid(row=1, column=1, pady=4)

        ttk.Label(frame, text="Costo unitario:").grid(row=2, column=0, sticky="e")
        self.cost_add = ttk.Entry(frame, width=30)
        self.cost_add.grid(row=2, column=1, pady=4)

        ttk.Button(frame, text="Agregar", command=self._on_add).grid(
            row=3, column=0, columnspan=2, pady=(10, 0)
        )

    def _build_consult_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Consultar Stock")

        ttk.Label(frame, text="SKU:").grid(row=0, column=0, sticky="e")
        self.sku_consult = ttk.Entry(frame, width=30)
        self.sku_consult.grid(row=0, column=1, pady=4)

        ttk.Button(frame, text="Consultar", command=self._on_consult).grid(
            row=1, column=0, columnspan=2, pady=(10, 0)
        )

    def _build_consume_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Consumir Stock")

        ttk.Label(frame, text="SKU:").grid(row=0, column=0, sticky="e")
        self.sku_consume = ttk.Entry(frame, width=30)
        self.sku_consume.grid(row=0, column=1, pady=4)

        ttk.Label(frame, text="Cantidad:").grid(row=1, column=0, sticky="e")
        self.qty_consume = ttk.Entry(frame, width=30)
        self.qty_consume.grid(row=1, column=1, pady=4)

        ttk.Button(frame, text="Consumir", command=self._on_consume).grid(
            row=2, column=0, columnspan=2, pady=(10, 0)
        )

    def _build_price_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Precio Sugerido")

        ttk.Label(frame, text="SKU:").grid(row=0, column=0, sticky="e")
        self.sku_price = ttk.Entry(frame, width=30)
        self.sku_price.grid(row=0, column=1, pady=4)

        ttk.Button(frame, text="Calcular", command=self._on_suggested_price).grid(
            row=1, column=0, columnspan=2, pady=(10, 0)
        )

    def _on_add(self):
        sku = self.sku_add.get().strip()
        qty = self.qty_add.get().strip()
        cost = self.cost_add.get().strip()

        if not (sku and qty.isdigit() and self._is_float(cost)):
            messagebox.showerror("Error", "SKU debe existir, cantidad entera y costo numérico.")
            return

        try:
            lote = agregar_lote(sku, int(qty), float(cost))
            messagebox.showinfo("Éxito", f"Lote creado con ID: {lote['id']}")
        except Exception as e:
            logger.exception("Al agregar lote")
            messagebox.showerror("Error al agregar", str(e))

    def _on_consult(self):
        sku = self.sku_consult.get().strip()
        if not sku:
            messagebox.showerror("Error", "SKU es obligatorio.")
            return

        try:
            stock = consultar_stock(sku)
            messagebox.showinfo("Stock Actual", f"{sku}: {stock} unidades")
        except Exception as e:
            logger.exception("Al consultar stock")
            messagebox.showerror("Error al consultar", str(e))

    def _on_consume(self):
        sku = self.sku_consume.get().strip()
        qty = self.qty_consume.get().strip()

        if not (sku and qty.isdigit()):
            messagebox.showerror("Error", "SKU es obligatorio y cantidad entera.")
            return

        try:
            total = consumir_stock(sku, int(qty))
            messagebox.showinfo("Consumido", f"Total costo: {total:.2f}")
        except Exception as e:
            logger.exception("Al consumir stock")
            messagebox.showerror("Error al consumir", str(e))

    def _on_suggested_price(self):
        sku = self.sku_price.get().strip()
        if not sku:
            messagebox.showerror("Error", "SKU es obligatorio.")
            return

        try:
            price = precio_sugerido(sku)
            messagebox.showinfo("Precio Sugerido", f"{sku}: {price:.2f}")
        except Exception as e:
            logger.exception("Al obtener precio sugerido")
            messagebox.showerror("Error al calcular", str(e))

    @staticmethod
    def _is_float(value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False


if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()
