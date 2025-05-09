import tkinter as tk
from tkinter import ttk, messagebox
from core.logger_config import logger
from .product_manager import ProductManagerWindow
from core.application.inventory_service import InventoryService


class InventoryUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestión de Inventario - CRM8102")
        self.inventory = InventoryService()
        self._build_ui()

    def _build_ui(self):
        # Menú para gestionar productos base
        menubar = tk.Menu(self)
        prod_menu = tk.Menu(menubar, tearoff=0)
        prod_menu.add_command(label="Productos...", command=self._open_product_manager)
        menubar.add_cascade(label="Productos", menu=prod_menu)
        self.config(menu=menubar)

        # Frame de entrada de datos
        input_frame = ttk.Frame(self)
        input_frame.pack(padx=10, pady=10, fill=tk.X)

        # Selección de producto base (código SII)
        ttk.Label(input_frame, text="Producto:").grid(row=0, column=0, sticky=tk.W)
        self.product_combo = ttk.Combobox(input_frame, state="readonly")
        self.product_combo.grid(row=0, column=1, sticky=tk.EW)

        # Cantidad a registrar
        ttk.Label(input_frame, text="Cantidad:").grid(row=1, column=0, sticky=tk.W)
        self.quantity_spin = ttk.Spinbox(input_frame, from_=1, to=100000)
        self.quantity_spin.grid(row=1, column=1, sticky=tk.EW)

        # Costo unitario
        ttk.Label(input_frame, text="Costo Unitario (CLP):").grid(row=2, column=0, sticky=tk.W)
        self.cost_entry = ttk.Entry(input_frame)
        self.cost_entry.grid(row=2, column=1, sticky=tk.EW)

        # Botón para agregar lote
        ttk.Button(input_frame, text="Agregar Lote", command=self.add_batch).grid(row=3, columnspan=2, pady=10)

        input_frame.columnconfigure(1, weight=1)

        # Tabla de stock
        self.tree = ttk.Treeview(self, columns=("SKU", "Cantidad", "Costo Promedio"), show="headings")
        self.tree.heading("SKU", text="SKU")
        self.tree.heading("Cantidad", text="Cantidad")
        self.tree.heading("Costo Promedio", text="Costo Promedio (CLP)")
        self.tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Cargar datos iniciales
        self._load_product_list()
        self.load_data()

    def _open_product_manager(self):
        # Abre la ventana de gestión de productos y recarga cuando se cierre
        win = ProductManagerWindow(self)
        win.grab_set()
        self.wait_window(win)
        self._load_product_list()

    def _load_product_list(self):
        # Carga los códigos base desde tabla productos
        with self.inventory.db.get_cursor() as cur:
            cur.execute("SELECT codigo_base FROM productos")
            bases = [row['codigo_base'] for row in cur.fetchall()]
        self.product_combo['values'] = bases
        if bases:
            self.product_combo.current(0)

    def add_batch(self):
        base_sku = self.product_combo.get().strip()
        if not base_sku:
            messagebox.showerror("Error", "Selecciona un producto base")
            return
        try:
            quantity = int(self.quantity_spin.get())
            unit_cost = float(self.cost_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Cantidad y costo deben ser numéricos")
            return

        try:
            # Usa método que genera SKU automático
            self.inventory.registrar_lote_con_sku_auto(base_sku, quantity, unit_cost)
            self.load_data()
            messagebox.showinfo("Éxito", "Lote agregado correctamente")
        except Exception as e:
            messagebox.showerror("Error al agregar lote", str(e))

    def load_data(self):
        # Refrescar la tabla de inventario
        for row in self.tree.get_children():
            self.tree.delete(row)
        with self.inventory.db.get_cursor() as cur:
            cur.execute(
                "SELECT sku, SUM(cantidad) AS total, ROUND(AVG(costo_unitario),2) AS promedio "
                "FROM lotes GROUP BY sku"
            )
            for item in cur.fetchall():
                self.tree.insert("", tk.END, values=(item['sku'], item['total'], item['promedio']))
