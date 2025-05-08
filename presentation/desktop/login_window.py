import tkinter as tk
from tkinter import messagebox, ttk
from core.infrastructure.security.auth_manager import AuthManager
from .main_window import MainWindow

class LoginWindow(tk.Tk):
    MAX_ATTEMPTS = 3
    attempts = 0

    def __init__(self):
        super().__init__()
        self.title("Login")
        self.geometry("300x200")

        # Inicializar contador de intentos
        self.attempts = 0

        # Componentes de UI
        ttk.Label(self, text="Usuario:").pack(pady=(20, 5))
        self.username_entry = ttk.Entry(self)
        self.username_entry.pack()

        ttk.Label(self, text="Contraseña:").pack(pady=(10, 5))
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.pack()

        self.login_button = ttk.Button(self, text="Ingresar", command=self._login)
        self.login_button.pack(pady=(20, 0))

        self.status_label = ttk.Label(self, text="")
        self.status_label.pack(pady=(10, 0))

        # Configuración de seguridad
        self.auth = AuthManager()

    def _login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.status_label.config(text="Campos vacíos no permitidos", foreground="red")
            return

        if self.attempts >= self.MAX_ATTEMPTS:
            messagebox.showerror("Bloqueado", "Sistema bloqueado por exceso de intentos")
            self.login_button.config(state=tk.DISABLED)
            return

        if self.auth.authenticate(username, password):
            # Acceso concedido: abrir MainWindow
            self.destroy()
            main_win = MainWindow(user_role=self.auth.get_user_role(username))
            main_win.mainloop()
        else:
            self.attempts += 1
            remaining = self.MAX_ATTEMPTS - self.attempts
            if remaining > 0:
                self.status_label.config(
                    text=f"Usuario o contraseña incorrectos. Te quedan {remaining} intentos.",
                    foreground="red"
                )
            else:
                self.status_label.config(
                    text="Ha excedido el número de intentos. Contactar al admin.",
                    foreground="red"
                )
                self.login_button.config(state=tk.DISABLED)

if __name__ == '__main__':
    LoginWindow().mainloop()
