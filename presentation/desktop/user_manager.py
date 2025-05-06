import tkinter as tk
from tkinter import ttk
from core.infrastructure.security.auth_manager import AuthManager


class UserManagerWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Gestión de Usuarios")
        self.auth = AuthManager()
        self._build_ui()
        self._load_users()

    def _build_ui(self):
        # Código existente
        self.role_combo = ttk.Combobox(self, values=["admin", "operador"])

    def _add_user(self):
        add_window = tk.Toplevel(self)
        ttk.Label(add_window, text="Usuario:").grid(row=0, column=0)
        username_entry = ttk.Entry(add_window)
        username_entry.grid(row=0, column=1)

        ttk.Label(add_window, text="Contraseña:").grid(row=1, column=0)
        password_entry = ttk.Entry(add_window, show='*')
        password_entry.grid(row=1, column=1)

        ttk.Label(add_window, text="Rol:").grid(row=2, column=0)
        role_combo = ttk.Combobox(add_window, values=["admin", "operador"])
        role_combo.grid(row=2, column=1)

        def do_create():
            if self.auth.create_user(
                username_entry.get(),
                password_entry.get(),
                role_combo.get()
            ):
                self._load_users()
                add_window.destroy()

        ttk.Button(add_window, text="Crear", command=do_create).grid(row=3, columnspan=2)
