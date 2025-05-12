import os
import psycopg
import tkinter as tk
from core.logger_config import logger
from tkinter import ttk, messagebox, simpledialog
from core.application.report_exporter import ReportExporter
from core.application.inventory_service import InventoryService
from presentation.desktop.product_manager import ProductManagerWindow
from presentation.desktop.mvp_window_check_list import MVPChecklistWindow


class MainWindow(tk.Tk):
    def __init__(self, user_role='operador'):
        super().__init__()
        self.user_role = user_role
        self.service = InventoryService()
        self.title("Gestor de Inventario - CRM8102")
        self.geometry("800x600")

        # Menú principal
        self._build_menu()
        # Interfaz principal
        self._build_ui()

        # Carga inicial de datos y menú de usuario
        self._refresh_inventory()

    def _build_menu(self):
        self.menubar = tk.Menu(self)

        # Menú Archivo
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="Salir", command=self.destroy)
        self.menubar.add_cascade(label="Archivo", menu=file_menu)

        # Menú Acciones
        actions_menu = tk.Menu(self.menubar, tearoff=0)
        actions_menu.add_command(label="Actualizar", command=self._refresh_inventory)
        self.menubar.add_cascade(label="Acciones", menu=actions_menu)

        # Menú Reportes
        reports_menu = tk.Menu(self.menubar, tearoff=0)
        reports_menu.add_command(label="Generar Excel", command=self._generate_excel)
        reports_menu.add_command(label="Generar PDF", command=self._generate_pdf)
        self.menubar.add_cascade(label="Reportes", menu=reports_menu)

        # Menú Productos
        prod_menu = tk.Menu(self.menubar, tearoff=0)
        if self.user_role == 'admin':
            prod_menu.add_command(label="Gestionar Productos...", command=self._open_product_manager)
        self.menubar.add_cascade(label="Productos", menu=prod_menu)

        # Menú Administración
        admin_menu = tk.Menu(self.menubar, tearoff=0)
        if self.user_role == 'admin':
            admin_menu.add_command(label="Gestión de Usuarios", command=self._manage_users)
        self.menubar.add_cascade(label="Administración", menu=admin_menu)

        # Menú MVP (visible para todos)
        mvp_menu = tk.Menu(self.menubar, tearoff=0)
        mvp_menu.add_command(label="Ver Avance MVP", command=self._show_mvp_checklist)
        self.menubar.add_cascade(label="MVP", menu=mvp_menu)

        self.config(menu=self.menubar)

    def _open_system_config(self):
        """Abre la ventana de configuración del sistema"""
        self._show_mvp_checklist()

    def _show_mvp_checklist(self):
        """Muestra la ventana de checklist MVP"""
        checklist = MVPChecklistWindow(self)
        checklist.grab_set()

    def _build_ui(self):
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Búsqueda de SKU
        self._build_search_section(main_container)

        # Registro y consumo en un mismo frame
        input_frame = ttk.Frame(main_container)
        input_frame.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)
        self._build_registration_section(input_frame)
        self._build_consumption_section(input_frame)

        # Tabla de inventario
        self._build_inventory_table(main_container)

        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)

    def _build_registration_section(self, parent):
        frame = ttk.LabelFrame(parent, text="Registrar Producto")
        frame.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)

        ttk.Label(frame, text="Producto:").grid(row=0, column=0, sticky=tk.W)
        self.product_combo = ttk.Combobox(frame, state="readonly")
        self.product_combo.grid(row=0, column=1, padx=5, pady=2, sticky=tk.EW)

        ttk.Label(frame, text="Cantidad:").grid(row=1, column=0, sticky=tk.W)
        self.stock_entry = ttk.Spinbox(frame, from_=1, to=100000)
        self.stock_entry.grid(row=1, column=1, padx=5, pady=2, sticky=tk.EW)

        ttk.Label(frame, text="Costo Unitario (CLP):").grid(row=2, column=0, sticky=tk.W)
        self.cost_entry = ttk.Entry(frame)
        self.cost_entry.grid(row=2, column=1, padx=5, pady=2, sticky=tk.EW)

        ttk.Button(frame, text="Agregar Stock", command=self._add_stock).grid(row=3, columnspan=2, pady=5)
        frame.columnconfigure(1, weight=1)

        # Carga de productos base en combo
        self._load_product_list()

    def _build_search_section(self, parent):
        search_frame = ttk.Frame(parent)
        search_frame.grid(row=0, column=0, sticky=tk.EW, padx=5, pady=5)

        ttk.Label(search_frame, text="Buscar SKU:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Buscar", command=self._search_sku).pack(side=tk.LEFT)
        ttk.Button(search_frame, text='Limpiar', command=self._refresh_inventory).pack(side=tk.LEFT, padx=5)

    def _load_product_list(self):
        """Carga la lista de productos usando SKU"""
        with self.service.db.get_cursor() as cur:
            cur.execute("SELECT sku FROM productos")
            bases = [row['codigo_base'] for row in cur.fetchall()]
        self.product_combo['values'] = bases
        if bases:
            self.product_combo.current(0)

    def _add_stock(self):
        base = self.product_combo.get().strip()
        if not base:
            return messagebox.showerror("Error", "Selecciona un producto")
        try:
            qty = int(self.stock_entry.get())
            cost = float(self.cost_entry.get())
        except ValueError as e:
            return messagebox.showerror(f"Error {e}", "Cantidad/ costo inválidos")

        try:
            # Operación de base de datos
            self.service.registrar_lote_con_sku_auto(base, qty, cost)
            self._refresh_inventory()
            messagebox.showinfo("Éxito", f"Lote agregado para {base}")
        except psycopg.DatabaseError as e:
            logger.error(f"Error BD: {str(e)}")
            messagebox.showerror("Error", "Fallo en base de datos")
        except Exception as e:
            logger.critical(f"Error crítico: {str(e)}")
            messagebox.showerror("Error", "Fallo interno")

    def _consume_stock(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Error", "Selecciona un SKU de la tabla")
            return

        sku = self.tree.item(selected[0])['values'][0]
        self.cantidad = 0

        try:
            self.cantidad = int(self.consume_spin.get())
            if self.cantidad <= 0:
                raise ValueError
        except (ValueError, psycopg.DatabaseError) as e:
            messagebox.showerror("Error de Sistema", f"Error controlado: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error Crítico", "Error no controlado, contacte al administrador")
            logger.error(f"Error no controlado: {str(e)}")
            return

        try:
            with self.service.db.get_cursor() as cur:
                cur.execute("""
                    INSERT INTO movimientos (lote_id, tipo_movimiento, cantidad)
                    SELECT id, 'SALIDA', %s
                    FROM lotes
                    WHERE sku = %s
                    ORDER BY fecha_ingreso
                    LIMIT 1
                """, (self.cantidad, sku))

            self._refresh_inventory()
            messagebox.showinfo("Exito", f"Consumidas {self.cantidad} unidades del SKU {sku}")

        except (ValueError, psycopg.DatabaseError) as e:
            messagebox.showerror("Error de Sistema", f"Error controlado: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error Crítico", "Error no controlado, contacte al administrador")
            logger.error(f"Error no controlado: {str(e)}")

    def _build_consumption_section(self, parent):
        frame = ttk.LabelFrame(parent, text="Consumo de Inventario")
        frame.grid(row=1, column=1, sticky=tk.NSEW, padx=5, pady=5)
        ttk.Label(frame, text="Cantidad a consumir:").grid(row=0, column=0, sticky=tk.W)
        self.consume_spin = ttk.Spinbox(frame, from_=1, to=1000)
        self.consume_spin.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(frame, text="Consumir Stock", command=self._consume_stock).grid(row=1, columnspan=2, pady=5)

    def _build_inventory_table(self, parent):
        cols = ("SKU", "Stock", "Costo Promedio")
        self.tree = ttk.Treeview(parent, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW, padx=5, pady=5)
        scrollbar.grid(row=2, column=2, sticky=tk.NS)

    def _refresh_inventory(self):
        try:
            data = self.service.list_inventory()
        except (psycopg.DatabaseError, ValueError) as e:
            messagebox.showerror("Error de Sistema", f"Error al cargar inventario: {str(e)}")
            return
        except Exception as e:
            messagebox.showerror("Error Crítico", "Error no controlado, contacte al administrador")
            logger.error(f"Error no controlado en inventario: {str(e)}")
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

    def _generate_excel(self):
        sku = simpledialog.askstring("Generar Excel", "Ingresa el SKU:")
        if not sku:
            return
        try:
            report_data = self.service.generar_reporte_sii(sku)
            excel_data = ReportExporter.to_excel(report_data)
            with open(f"reporte_{sku}.xlsx", "wb") as f:
                f.write(excel_data)
            messagebox.showinfo("Éxito", f"Reporte Excel generado: reporte_{sku}.xlsx")
        except (ValueError, psycopg.DatabaseError) as e:
            messagebox.showerror("Erro de Sistema", f"Error controlado: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error Critico", "Error no controlado, contacte al administrador")
            logger.error(f"Error no controlado: {str(e)}")

    def _generate_pdf(self):
        sku = simpledialog.askstring("Generar PDF", "Ingresa el SKU:")
        if not sku:
            return
        try:
            report_data = self.service.generar_reporte_sii(sku)
            pdf_data = ReportExporter.to_pdf(report_data)
            with open(f"reporte_{sku}.pdf", "wb") as f:
                f.write(pdf_data)
            messagebox.showinfo("Éxito", f"Reporte PDF generado: reporte_{sku}.pdf")
        except (ValueError, psycopg.DatabaseError) as e:
            messagebox.showerror("Error de Sistema", f"Error controlado: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error Crítico", "Error no controlado, contacte al administrador")
            logger.error(f"Error no controlado: {str(e)}")

    def _add_user_menu(self, role):
        if role == 'admin':
            admin_menu = tk.Menu(self.menubar, tearoff=0)
            admin_menu.add_command(label="Gestión de Usuarios", command=self._manage_users)
            self.menubar.add_cascade(label="Administración", menu=admin_menu)

    def _manage_users(self):
        from presentation.desktop.user_manager import UserManagerWindow
        win = UserManagerWindow(self)
        win.grab_set()

    def _open_product_manager(self):
        """Abre la ventana de gestión de productos y actualiza la lista"""
        try:
            mgr = ProductManagerWindow(self)
            mgr.grab_set()
            self.wait_window(mgr)
            self._load_product_list()
            self._refresh_inventory()
        except (ValueError, psycopg.DatabaseError) as e:
            messagebox.showerror("Error de Sistema", f"Error controlado: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error Crítico", "Error no controlado, contacte al administrador")
            logger.error(f"Error no controlado: {str(e)}")

    def _show_mvp_checklist(self):
        """Muesta la ventana de checklist Mvp solo en desarrolo"""
        if self.is_development:
            checklist = MVPChecklistWindow(self)
            checklist.grab_set()



if __name__ == "__main__":
    MainWindow().mainloop()
