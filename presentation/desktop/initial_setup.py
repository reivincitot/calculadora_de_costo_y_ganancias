import tkinter as tk
from tkinter import ttk, messagebox
from core.infrastructure.security.auth_manager import AuthManager


class InitialSetupWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Configuración Inicial")
        self.auth = AuthManager()
        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="Crear Superusuario Admin", font=('Helvetica', 14)).pack(pady=10)

        frame = ttk.Frame(self)
        frame.pack(padx=20, pady=10)

        ttk.Label(frame, text="Usuario:").grid(row=0, column=0, sticky=tk.W)
        self.user_entry = ttk.Entry(frame)
        self.user_entry.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Contraseña:").grid(row=1, column=0, sticky=tk.W)
        self.pass_entry = ttk.Entry(frame, show='*')
        self.pass_entry.grid(row=1, column=1, padx=5)

        ttk.Label(frame, text="Confirmar Contraseña:").grid(row=2, column=0, sticky=tk.W)
        self.confirm_entry = ttk.Entry(frame, show='*')
        self.confirm_entry.grid(row=2, column=1, padx=5)

        ttk.Button(frame, text="Crear Superusuario", command=self._create_superuser).grid(row=3, columnspan=2, pady=10)

    def _create_superuser(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        confirm = self.confirm_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        if password != confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return

        if self.auth.create_user(username, password, "admin"):
            messagebox.showinfo("Éxito", "Superusuario creado exitosamente")
            self.destroy()
            from .login_window import LoginWindow
            LoginWindow().mainloop()

        else:
            messagebox.showerror("Error", "No se pudo crear el usuario")
