import tkinter as tk
from tkinter import ttk, messagebox
from core.application.inventory_service import InventoryService

class InventoryUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestión de Inventario - CRM8102")
        self.inventory = InventoryService()
        self._build_ui()

    def _build_ui(self):
        # Frame de entrada de datos
        input_frame = ttk.Frame(self)
        input_frame.pack(padx=10, pady=10, fill=tk.X)

        ttk.Label(input_frame, text="SKU").grid(row=0, column=0)
        self.sku_entry = ttk.Entry(input_frame)
        self.sku_entry.grid(row=0, column=1)

        ttk.Label(input_frame, text="Cantidad:").grid(row=1, column=0)
        self.quantity_spin = ttk.Spinbox(input_frame, from_=1, to=1000)
        self.quantity_spin.grid(row=1, column=1)

        ttk.Button(input_frame, text="Agregar Lote", command=self.add_batch). grid(row=2, columspan=2)

        # Tabla Stock
        self.tree = ttk.Treeview(self, columns=("SKU", "Cantidad", "Costo Unitario"), show="headings")
        self.tree.heading("SKU", text="SKU")
        self.tree.heading("Cantidad", text="Cantidad")
        self.tree.heading("Costo Unitario", text="Costo Unitario")
        self.tree.pack(padx=10, pady=10)

        self.load_data()

    def add_batch(self):
        sku = self.sku_entry.get()
        quantity = int(self.quantity_spin.get())
        unit_cost = 0.0 #Implementar entrada de costo

        try:
            self.inventory.add_batch(sku, quantity, unit_cost)
            self.load_data()
        except Exception as e:
            tk.messagebox.showerror("Error", str(e))

    def load_data(self):
        with self.inventory.db.get_cursor() as cur:
            cur.execute("SELECT sku, SUM(cantidad) as total, AVG(costo_unitario) as costo_promedio FROM lotes GROUP BY sku")
            for row in self.tree.get_children():
                self.tree.delete(row)
            for item in cur.fetchall():
                self.tree.insert("", "end", values=(item['sku'], item['total'], item['costo_promedio']))
