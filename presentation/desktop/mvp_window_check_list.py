import tkinter as tk
from tkinter import ttk

class MVPChecklistWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Checklist MVP")
        self.geometry("400x400")
        self.resizable(False, False)

        # Elementos del checklist
        items = [
            ("Login con roles", True),
            ("Gestión de inventario (stock y consumo)", True),
            ("Gestión de productos", True),
            ("Autogeneración de SKU", True),
            ("Control FIFO", True),
            ("Reportes en Excel y PDF", True),
            ("Historial de movimientos (ingresos/consumos)", False),
            ("Historial de costos por producto", False),
            ("Sugerencia de precio de venta", False),
            ("Gestión de usuarios (crear/editar)", False),
            ("Exportación de datos completa", False),
            ("Configuración de costos fijos/margen", False)
        ]

        self.vars = []
        for i, (text, checked) in enumerate(items):
            var = tk.BooleanVar(value=checked)
            cb = ttk.Checkbutton(self, text=text, variable=var)
            cb.pack(anchor="w", padx=10, pady=4)
            self.vars.append(var)

        ttk.Button(self, text="Cerrar", command=self.destroy).pack(pady=10)
