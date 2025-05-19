# desktop_app/view/dashboard.py

import tkinter as tk
from tkinter import ttk, messagebox
from ..api_client import (
    agregar_lote,
    consultar_stock,
    consumir_stock,
    precio_sugerido
)

class InventoryDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dashboard de Inventario y Costos")
        self.geometry("500x400")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self._build_add_tab()
        self._build_consult_tab()
        self._build_consume_tab()
        self._build_price_tab()

    def _build_add_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Agregar Lote")

        ttk.Label(frame, text="SKU:").grid(row=0, column=0, sticky="e")
        self.sku_add = ttk.Entry(frame); self.sku_add.grid(row=0, column=1)

        ttk.Label(frame, text="Cantidad:").grid(row=1, column=0, sticky="e")
        self.qty_add = ttk.Entry(frame); self.qty_add.grid(row=1, column=1)

        ttk.Label(frame, text="Costo unitario:").grid(row=2, column=0, sticky="e")
        self.cost_add = ttk.Entry(frame); self.cost_add.grid(row=2, column=1)

        ttk.Button(frame, text="Agregar", command=self._on_add).grid(
            row=3, column=0, columnspan=2, pady=10
        )

    def _on_add(self):
        try:
            lote = agregar_lote(
                self.sku_add.get().strip(),
                int(self.qty_add.get()),
                float(self.cost_add.get())
            )
            messagebox.showinfo("Éxito", f"Lote ID {lote['id']} agregado.")
        except Exception as e:
            messagebox.showerror("Error al agregar", str(e))

    def _build_consult_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Consultar Stock")

        ttk.Label(frame, text="SKU:").grid(row=0, column=0, sticky="e")
        self.sku_consult = ttk.Entry(frame); self.sku_consult.grid(row=0, column=1)

        ttk.Button(frame, text="Consulta", command=self._on_consult).grid(
            row=1, column=0, columnspan=2, pady=10
        )

    def _on_consult(self):
        try:
            stock = consultar_stock(self.sku_consult.get().strip())
            messagebox.showinfo("Stock", f"Stock actual: {stock}")
        except Exception as e:
            messagebox.showerror("Error al consultar", str(e))

    def _build_consume_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Consumir Stock")

        ttk.Label(frame, text="SKU:").grid(row=0, column=0, sticky="e")
        self.sku_consume = ttk.Entry(frame); self.sku_consume.grid(row=0, column=1)

        ttk.Label(frame, text="Cantidad:").grid(row=1, column=0, sticky="e")
        self.qty_consume = ttk.Entry(frame); self.qty_consume.grid(row=1, column=1)

        ttk.Button(frame, text="Consumir", command=self._on_consume).grid(
            row=2, column=0, columnspan=2, pady=10
        )

    def _on_consume(self):
        try:
            total = consumir_stock(
                self.sku_consume.get().strip(),
                int(self.qty_consume.get())
            )
            messagebox.showinfo("Éxito", f"Se consumieron unidades. Costo total: {total:.2f}")
        except Exception as e:
            messagebox.showerror("Error al consumir", str(e))

    def _build_price_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Precio Sugerido")

        ttk.Label(frame, text="SKU:").grid(row=0, column=0, sticky="e")
        self.sku_price = ttk.Entry(frame); self.sku_price.grid(row=0, column=1)

        ttk.Button(frame, text="Calcular", command=self._on_price).grid(
            row=1, column=0, columnspan=2, pady=10
        )

    def _on_price(self):
        try:
            precio = precio_sugerido(self.sku_price.get().strip())
            messagebox.showinfo("Precio Sugerido", f"${precio:.2f}")
        except Exception as e:
            messagebox.showerror("Error al calcular precio", str(e))

if __name__ == "__main__":
    InventoryDashboard().mainloop()
