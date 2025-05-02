import tkinter as tk
from tkinter import ttk, messagebox
from core.application.inventory_service import InventoryService


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.service = InventoryService()
        self.title("Gestor de Inventario - CRM8102")
        self.geometry("800x600")
        self._build_ui()

    def _build_ui(self):
        # Panel de Control Principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Sección de Registro de Lotes
        ttk.Label(main_frame, text="Registro de Nuevo Lote", font=('Helvetica', 12, 'bold')).grid(row=0, column=0,
                                                                                                  pady=5, sticky=tk.W)

        ttk.Label(main_frame, text="SKU:").grid(row=1, column=0)
        self.sku_entry = ttk.Entry(main_frame)
        self.sku_entry.grid(row=1, column=1, padx=5)

        ttk.Label(main_frame, text="Cantidad:").grid(row=2, column=0)
        self.quantity_spin = ttk.Spinbox(main_frame, from_=1, to=1000)
        self.quantity_spin.grid(row=2, column=1, padx=5)

        ttk.Label(main_frame, text="Costo Unitario:").grid(row=3, column=0)
        self.cost_entry = ttk.Entry(main_frame)
        self.cost_entry.grid(row=3, column=1, padx=5)

        ttk.Button(main_frame, text="Agregar Lote", command=self._add_batch).grid(row=4, columnspan=2, pady=10)

        # Sección de Consumo de Stock
        ttk.Label(main_frame, text="Consumo de Inventario", font=('Helvetica', 12, 'bold')).grid(row=5, column=0,
                                                                                                 pady=5, sticky=tk.W)

        ttk.Label(main_frame, text="Cantidad a Consumir:").grid(row=6, column=0)
        self.consume_spin = ttk.Spinbox(main_frame, from_=1, to=1000)
        self.consume_spin.grid(row=6, column=1, padx=5)

        ttk.Button(main_frame, text="Consumir Stock", command=self._consume_stock).grid(row=7, columnspan=2, pady=10)

        # Tabla de Inventario
        self.tree = ttk.Treeview(main_frame, columns=("SKU", "Stock", "Costo Promedio"), show="headings")
        self.tree.heading("SKU", text="SKU")
        self.tree.heading("Stock", text="Stock Disponible")
        self.tree.heading("Costo Promedio", text="Costo Promedio (CLP)")
        self.tree.grid(row=8, columnspan=2, pady=10, sticky=tk.NSEW)

        # Actualizar datos iniciales
        self._refresh_inventory()

    def _add_batch(self):
        try:
            sku = self.sku_entry.get()
            quantity = int(self.quantity_spin.get())
            unit_cost = float(self.cost_entry.get())

            self.service.add_batch(sku, quantity, unit_cost)
            self._refresh_inventory()
            messagebox.showinfo("Éxito", "Lote registrado correctamente")
        except ValueError as e:
            messagebox.showerror("Error", f"Datos inválidos: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")

    def _consume_stock(self):
        try:
            sku = self.sku_entry.get()
            quantity = int(self.consume_spin.get())

            costo = self.service.consume(sku, quantity, "Usuario UI", "CONSUMO-UI")
            self._refresh_inventory()
            messagebox.showinfo("Éxito", f"Stock consumido. Costo total: ${costo:,.2f} CLP")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al consumir stock: {str(e)}")

    def _refresh_inventory(self):
        # Limpiar tabla
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Obtener datos actualizados
        with self.service.db.get_cursor() as cur:
            cur.execute("""
                SELECT sku, 
                       SUM(cantidad) as stock,
                       AVG(costo_unitario) as costo_promedio
                FROM lotes
                GROUP BY sku
            """)
            for row in cur.fetchall():
                self.tree.insert("", "end", values=(
                    row['sku'],
                    row['stock'],
                    f"${row['costo_promedio']:,.2f}" if row['costo_promedio'] else "N/A"
                ))


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()