import tkinter as tk
from tkinter import ttk, messagebox
from core.application.inventory_service import InventoryService
from core.application.report_exporter import ReportExporter


class MainWindow(tk.Tk):
    def __init__(self, user_role='operador'):
        super().__init__()
        self.service = InventoryService()
        self.title("Gestor de Inventario - CRM8102")
        self.geometry("800x600")

        # Construcción de UI y menús
        self._build_menu()
        self._build_ui()

        # Inicializar datos
        self._refresh_inventory()
        self._add_user_menu(user_role)

    def _build_menu(self):
        """Configura la barra de menú superior"""
        self.menubar = tk.Menu(self)

        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="Salir", command=self.destroy)
        self.menubar.add_cascade(label="Archivo", menu=file_menu)

        actions_menu = tk.Menu(self.menubar, tearoff=0)
        actions_menu.add_command(label="Actualizar", command=self._refresh_inventory)
        self.menubar.add_cascade(label="Acciones", menu=actions_menu)

        reports_menu = tk.Menu(self.menubar, tearoff=0)
        reports_menu.add_command(label="Generar Excel", command=self._generate_excel)
        reports_menu.add_command(label="Generar PDF", command=self._generate_pdf)
        self.menubar.add_cascade(label="Reportes", menu=reports_menu)

        self.config(menu=self.menubar)

    def _build_ui(self):
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Búsqueda
        self._build_search_section(main_container)

        # Registro y consumo
        input_frame = ttk.Frame(main_container)
        input_frame.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)
        self._build_registration_section(input_frame)
        self._build_consumption_section(input_frame)

        # Tabla de inventario
        self._build_inventory_table(main_container)

        # Layout
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)

    def _build_search_section(self, parent):
        frame = ttk.LabelFrame(parent, text="Buscar SKU")
        frame.grid(row=0, column=0, sticky=tk.EW, padx=5, pady=5)
        self.search_entry = ttk.Entry(frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,0))
        ttk.Button(frame, text="Buscar", command=self._search_sku).pack(side=tk.LEFT, padx=5)

    def _build_registration_section(self, parent):
        frame = ttk.LabelFrame(parent, text="Registrar Producto")
        frame.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Label(frame, text="SKU:").grid(row=0, column=0, sticky=tk.W)
        self.sku_entry = ttk.Entry(frame)
        self.sku_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(frame, text="Stock:").grid(row=1, column=0, sticky=tk.W)
        self.stock_entry = ttk.Entry(frame)
        self.stock_entry.grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(frame, text="Agregar Stock", command=self._add_stock).grid(row=2, columnspan=2, pady=5)

    def _build_consumption_section(self, parent):
        frame = ttk.LabelFrame(parent, text="Consumo de Inventario")
        frame.grid(row=1, column=1, sticky=tk.NSEW, padx=5, pady=5)
        ttk.Label(frame, text="Cantidad a consumir:").grid(row=0, column=0, sticky=tk.W)
        self.consume_spin = ttk.Spinbox(frame, from_=1, to=1000)
        self.consume_spin.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(frame, text="Consumir Stock", command=self._consume_stock).grid(row=1, columnspan=2, pady=5)

    def _build_inventory_table(self, parent):
        columns = ("SKU", "Stock", "Costo Promedio")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW, padx=5, pady=5)
        scrollbar.grid(row=2, column=2, sticky=tk.NS)

    def _refresh_inventory(self):
        """Refresca los datos en la tabla de inventario"""
        # Ejemplo de implementación básica
        try:
            data = self.service.list_inventory()
        except Exception:
            messagebox.showerror("Error", "No se pudo cargar el inventario")
            return
        self.tree.delete(*self.tree.get_children())
        for item in data:
            self.tree.insert('', tk.END, values=(item.sku, item.stock, item.average_cost))

    def _search_sku(self):
        term = self.search_entry.get().strip().upper()
        for iid in self.tree.get_children():
            if self.tree.item(iid)['values'][0] == term:
                self.tree.selection_set(iid)
                self.tree.focus(iid)
                return
        messagebox.showinfo("Búsqueda", "SKU no encontrado")

    def _add_stock(self):
        sku = self.sku_entry.get().strip()
        try:
            qty = int(self.stock_entry.get().strip())
            self.service.add_stock(sku, qty)
            self._refresh_inventory()
            messagebox.showinfo("Éxito", f"Stock agregado a {sku}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _consume_stock(self):
        sku = self.sku_entry.get().strip()
        try:
            qty = int(self.consume_spin.get())
            self.service.consume_stock(sku, qty)
            self._refresh_inventory()
            messagebox.showinfo("Éxito", f"Stock consumido de {sku}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _generate_excel(self):
        sku = self.sku_entry.get().strip()
        try:
            report_data = self.service.generar_reporte_sii(sku)
            excel_data = ReportExporter.to_excel(report_data)
            with open(f"reporte_{sku}.xlsx", "wb") as f:
                f.write(excel_data)
            messagebox.showinfo("Éxito", f"Reporte Excel generado: reporte_{sku}.xlsx")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _generate_pdf(self):
        sku = self.sku_entry.get().strip()
        try:
            report_data = self.service.generar_reporte_sii(sku)
            pdf_data = ReportExporter.to_pdf(report_data)
            with open(f"reporte_{sku}.pdf", "wb") as f:
                f.write(pdf_data)
            messagebox.showinfo("Éxito", f"Reporte PDF generado: reporte_{sku}.pdf")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _add_user_menu(self, role):
        if role == 'admin':
            admin_menu = tk.Menu(self.menubar, tearoff=0)
            admin_menu.add_command(label="Gestión de Usuarios", command=self._manage_users)
            self.menubar.add_cascade(label="Administración", menu=admin_menu)

    def _manage_users(self):
        messagebox.showinfo("Usuarios", "Funcionalidad de gestión de usuarios pendiente")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
