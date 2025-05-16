from typing import Union


def check_permission(user: Union[str, object], action: str):
    """
    Valida si el usuario tiene permiso para realizar una acción.
    'user' puede ser un string (username) o un objeto con atributos 'username' y 'name'.
    """
    # Definición de permisos por rol o usuario
    permisos_mock = {
        "admin": ["add_batch", "consume_stock"],
        "usuario": ["consume_stock"]
    }

    # Obtener clave para lookup: nombre de usuario
    if hasattr(user, 'username'):
        username = user.username
    elif isinstance(user, str):
        username = user
    else:
        # objeto con atributo 'name'
        username = getattr(user, 'name', str(user))

    # verificar permiso
    if action not in permisos_mock.get(username, []):
        # para el mensaje, mostrar nombre real si existe
        display_name = getattr(user, 'name', username)
        raise PermissionError(f"El usuario '{display_name}' no tiene permiso para '{action}'")
