from core.infrastructure.security.auth_manager import AuthManager
from presentation.desktop.initial_setup import InitialSetupWindow
from presentation.desktop.login_window import LoginWindow

if __name__ == "__main__":
    auth = AuthManager()
    if not auth.admin_exists():
        InitialSetupWindow().mainloop()
    else:
        LoginWindow().mainloop()
