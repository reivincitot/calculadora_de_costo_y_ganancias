def check_permission(user: str, action: str):
    permisos_mock = {
        "admin": ["add_batch", "consume_stock"],
        "usuario": ["consume_stock"]
    }

    if action not in permisos_mock.get(user, []):
        raise PermissionError(f"El usuario '{user}' no tiene permiso para '{action}'")
    