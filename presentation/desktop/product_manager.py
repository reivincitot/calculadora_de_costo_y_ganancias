import tkinter as tk
from tkinter import ttk, messagebox
from core.infrastructure.database.postgres_manager import DatabaseManager


class ProductManagerWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        self._build_ui()
        self._load_products()

    def _build_ui(self):
        # Treeview de productos
        cols = ("id", "codigo_base", "nombre", "material", "grosor_mm", "color")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for col in cols:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=100)
        self.tree.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        # Botones de acción
        ttk.Button(self, text="Nuevo", command=self._new_product).grid(row=1, column=0, padx=5)
        ttk.Button(self, text="Editar", command=self._edit_product).grid(row=1, column=1, padx=5)
        ttk.Button(self, text="Eliminar", command=self._delete_product).grid(row=1, column=2, padx=5)
        ttk.Button(self, text="Cerrar", command=self.destroy).grid(row=1, column=3, padx=5)

    def _load_products(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        with self.db.get_cursor() as cur:
            cur.execute("SELECT id, codigo_base, nombre, material, grosor_mm, color FROM productos")
            for prod in cur.fetchall():
                self.tree.insert("", tk.END, values=(
                    prod['id'], prod['codigo_base'], prod['nombre'],
                    prod['material'], prod['grosor_mm'], prod['color']
                ))

    def _new_product(self):
        self._open_form()

    def _edit_product(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un producto para editar")
            return
        values = self.tree.item(sel[0])['values']
        self._open_form(prod_id=values[0], data=dict(
            codigo_base=values[1], nombre=values[2], material=values[3], grosor_mm=values[4], color=values[5]
        ))

    def _delete_product(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un producto para eliminar")
            return
        prod_id = self.tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirmar", "¿Eliminar este producto? Esta acción no se puede deshacer."):
            with self.db.get_cursor() as cur:
                cur.execute("DELETE FROM productos WHERE id = %s", (prod_id,))
            self._load_products()

    def _open_form(self, prod_id=None, data=None):
        form = tk.Toplevel(self)
        form.title("Editar Product" if prod_id else "Nuevo Producto")
        labels = ["Código Base", "Nombre", "Material", "Grosor (mm)", "Color"]
        fields = {}
        for i, key in enumerate(["codigo_base", "nombre", "material", "grosor_mm", "color"]):
            ttk.Label(form, text=labels[i]).grid(row=i, column=0, pady=5, padx=5, sticky=tk.W)
            entry = ttk.Entry(form)
            entry.grid(row=i, column=1, pady=5, padx=5)
            if data:
                entry.insert(0, data[key])
            fields[key] = entry

        def save():
            vals = {k: fields[k].get().strip() for k in fields}
            if not all(vals.values()):
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            with self.db.get_cursor() as cur:
                if prod_id:
                    cur.execute(
                        """
                        UPDATE productos SET codigo_base=%s, nombre=%s, material=%s, grosor_mm=%s, color=%s WHERE id=%s
                        """, (*vals.values(), prod_id)
                    )
                else:
                    cur.execute(
                        """
                        INSERT INTO productos (codigo_base, nombre, material, grosor_mm, color)
                        VALUES (%s,%s,%s,%s,%s)
                        """, tuple(vals.values())
                    )
            form.destroy()
            self._load_products()
        ttk.Button(form, text="Guardar", command=save).grid(row=len(fields), columnspan=2, pady=10)
        form.transient(self)
        form.grab_set()
