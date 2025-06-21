"""
Modulo para la autentificacion, registro y para guardar la informacion de los usuarios
Ruta de este archivo: Modulos/auth/auth.py

En este modulo cree las siguiente funciones:
- funcion para el registro de nuevos usuarios
- funcion para el loguin de usuarios ya creados
- funcion para el convertir las contraseñas en hash SHA256
- funcion para guardar los datos del usuario en un archivo JSON

"""

import json  # libreria para leer y guardar la información de los usuarios en formato JSON
import hashlib  # libreria para encriptar las contraseñas usando SHA256
from pathlib import Path  # libreria para manejar rutas de archivos de forma dinamica

# esta es la ruta al archivo JSON donde se guardan a los usuarios
archivo_usuario = Path ("Datos") / "users.json"
                  # Path("Datos") / "users.json" es una forma de crear una ruta relativa al directorio actual del script
                  # para que sea dinamico a pesar de la estructura de las carpetas

def _cargar_usuarios () -> dict:
    """
    Carga y devuelve el diccionario de usuarios desde el archivo JSON.

    Returns:
        dict: Diccionario con los usuarios registrados. Si el archivo no existe o está vacío, retorna un diccionario vacío.

    Example:
        >>> usuarios = _cargar_usuarios ()
        >>> print (usuarios)
        {'usuario1': {'usuario': 'usuario1', 'contrasena': '...', 'nombre': '...', ...}}
    """
    # Verifica si el archivo de usuarios existe
    
    if not archivo_usuario.exists():
        
        # Si nunca se registro un usuario, retorna un diccionario vacío
        return {}

    else:
        
        # Lee el archivo como texto (UTF-8 para soportar caracteres especiales)
        datos_raw = archivo_usuario.read_text(encoding="utf-8")
        
        # Si el archivo está vacío, retorna un diccionario vacío
        if not datos_raw:
            
            return {}
        
        # Convierte el contenido JSON a un diccionario de Python
        return json.loads(datos_raw)


def _guardar_usuarios(usuarios: dict) -> None:
    """
    Guarda el diccionario de usuarios en el archivo JSON.

    Args:
        usuarios (dict): Diccionario con los datos de los usuarios.

    Example:
        >>> _guardar_usuarios({'usuario1': {...}})
    """
    # Serializa el diccionario a un string JSON con indentación y soporte UTF-8
    datos_json = json.dumps(usuarios, indent=2, ensure_ascii=False)
    # Escribe el string JSON en el archivo (crea el archivo si no existe)
    archivo_usuario.write_text(datos_json, encoding="utf-8")


def hash_contrasena(contrasena: str) -> str:
    """
    Genera un hash SHA256 de la contraseña proporcionada.

    Args:
        contrasena (str): Contraseña en texto plano.

    Returns:
        str: Hash hexadecimal de la contraseña.

    Example:
        >>> hash_contrasena('mi_password')
        '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'
    """
    # Codifica la contraseña a bytes y genera el hash SHA256
    return hashlib.sha256(contrasena.encode("utf-8")).hexdigest()


def registrar_usuario(usuario: str, contrasena: str, nombre: str, apellido: str, edad: int, sexo: str) -> bool:
    """
    Registra un nuevo usuario en el sistema.

    Args:
        usuario (str): Nombre de usuario único.
        contrasena (str): Contraseña del usuario.
        nombre (str): Nombre real del usuario.
        apellido (str): Apellido del usuario.
        edad (int): Edad del usuario.
        sexo (str): Sexo del usuario.

    Returns:
        bool: True si el registro fue exitoso, False si el usuario ya existe.

    Example:
        >>> registrar_usuario('juan', '1234', 'Juan', 'Pérez', 20, 'M')
        True
    """
    # Carga los usuarios existentes para comprobar si el usuario ya existe
    usuarios = _cargar_usuarios()
    if usuario in usuarios:
        # Si el usuario ya existe, retorna False
        return False
    else:
        # Si el usuario no existe, lo agrega al diccionario con los datos y la contraseña encriptada
        usuarios[usuario] = {
            "usuario": usuario,
            "contrasena": hash_contrasena(contrasena),  # Guarda la contraseña encriptada
            "nombre": nombre,
            "apellido": apellido,
            "edad": edad,
            "sexo": sexo
        }
        # Guarda el diccionario actualizado en el archivo JSON
        _guardar_usuarios(usuarios)
        # Retorna True si el registro fue exitoso
        return True


def autenticar_usuario(usuario: str, contrasena: str) -> bool:
    """
    Autentica el acceso de un usuario.

    Args:
        usuario (str): Nombre de usuario.
        contrasena (str): Contraseña en texto plano.

    Returns:
        bool: True si la autenticación es exitosa, False en caso contrario.

    Example:
        >>> autenticar_usuario('juan', '1234')
        True
    """
    # Carga los usuarios registrados
    usuarios = _cargar_usuarios()
    # Si el usuario no existe, retorna False
    if usuario not in usuarios:
        return False
    else:
        # Obtiene el hash almacenado y compara con el hash de la contraseña ingresada
        store_hash = usuarios[usuario]["contrasena"]
        return hash_contrasena(contrasena) == store_hash
        # Si el hash coincide, la autenticación es exitosa