"""
Modulo para autentificar, registrar y guardar usuarios
Ruta de este archivo: Modulos/ui/auth.py
"""

import json # se usa para leer y guardar informacion de los usuarios en un archivo json
import hashlib # se usa para encriptar la contrasena del usuario
from pathlib import Path # se usa para cargar el json desde la carpeta de datos

"""
la funcion Path() crea una ruta a un archivo o carpeta
en este caso, la ruta es "Datos/users.json"
por lo tanto carga el archivo users.json desde la carpeta Datos
"""
archivo_usuario = Path("Datos") / "users.json"


# Cargar el archivo JSON de usuarios
def _cargar_usuarios () -> dict: # retorna un diccionario
    
    """
    lee y devuelve el contenido de archivo_usuario como un diccionario
    {
        usuario1: {
            "usuario": "usuario1",
            "contrasena": "contrasena1"
            "nombre": "Nombre1",
            "apellido": "Apellido1",
        },
        usuario2: {
            "usuario": "usuario2",
            "contrasena": "contrasena2"
            "nombre": "Nombre2",
            "apellido": "Apellido2",
        }
    }
    si el archivo no existe o esta vacio, devuelve un diccionario vacio {}
    """
    if not archivo_usuario.exists():
        
        # si nunca se registro un usuario retorna un diccionario vacio
        return {}
    
    else:
        
        # lee el archivo como texto y encoding es para evitar errores de codificacion
        datos_raw = archivo_usuario.read_text(encoding="utf-8")
        
        # si el archivo esta vacio, retorna un diccionario vacio
        if not datos_raw:
            
            return {}
    
        # parsear el contenido del archivo JSON a un diccionario
        return json.loads(datos_raw)
    
# Guardar el archivo JSON de usuarios
def _guardar_usuarios (usuarios: dict) -> None:
    
    """
    Guarda el diccionario de usuarios en archivo_usuario como un archivo JSON
    con la siguiente estructura.
    {
        usuario1: {
            "usuario": "usuario1",
            "contrasena": "contrasena1"
            "nombre": "Nombre1",
            "apellido": "Apellido1",
        },
        usuario2: {
            "usuario": "usuario2",
            "contrasena": "contrasena2"
            "nombre": "Nombre2",
            "apellido": "Apellido2",
        }
    }
    """
    
    
    # serializamos el diccionario a un string JSON
    # osea que convertimos el diccionario a un string JSON
    datos_json = json.dumps(usuarios, indent=2, ensure_ascii=False)
    """
    la funcion json.dumps: convierte un diccionario a un string JSON
    y como argmentos le pasamos:
    - usuarios: que es el diccionario a convertir
    - indent=4: para que el json tenga una sangria de 2 espacios
    - ensure_ascii=False: para que el json soporte caracteres especiales
    """
    # y ahora escribimos el string JSON en el archivo
    # en caso de no exitir el archivo, lo crea
    archivo_usuario.write_text(datos_json, encoding="utf-8")
    """
    la funcion write_text: escribe un string en un archivo
    y como argmentos le pasamos:
    - datos_json: que es el string JSON a escribir
    - encoding="utf-8": para evitar errores de codificacion, utf-8 es el encoding mas comun
    """
    
# Función para encriptar la contraseña
def hash_contrasena (contrasena: str) -> str:
    
    """
    encripta la contrasena del usuario
    y retorna un hash SHA256 de la contrasena
    """
    # codificamos la contrasena a bytes
    return hashlib.sha256(contrasena.encode("utf-8")).hexdigest()
    """
    la funcion hashlib.sha256: crea un hash SHA256 de la contrasena
    y como argmentos le pasamos:
    - contrasena.encode("utf-8"): que es la contrasena a encriptar
    - hexdigest(): convierte el hash a un string hexadecimal
    """


# Función para registrar un nuevo usuario
def registrar_usuario (usuario: str, contrasena: str, nombre: str, apellido: str, edad: int, sexo: str) -> bool:
    
    """
    registra un nuevo usuario con los siguientes parametros:
        - usuario: el nombre de usuario
        - contrasena: la contrasena del usuario
        - nombre: el nombre del usuario
        - apellido: el apellido del usuario
        - edad: la edad del usuario
        - sexo: el sexo del usuario
    y retorna True si el registro fue exitoso
    o False si el usuario ya existe
    """
    
    # se carga el archivo de usuarios
    # para comprobar si el usuario ya existe
    usuarios = _cargar_usuarios()
    
    if usuario in usuarios:
        
        # si el usuario ya existe, retorna False
        return False
    else:
        # si el usuario no existe, lo agrega al diccionario
        usuarios[usuario] = {
            "usuario": usuario,
            "contrasena": hash_contrasena(contrasena),
            "nombre": nombre,
            "apellido": apellido,
            "edad": edad,
            "sexo": sexo
        }
        
        # y guarda el diccionario en el archivo JSON
        _guardar_usuarios(usuarios)
        
        # retorna True si el registro fue exitoso
        return True
    
# funcion para autentificar el acceso de un usuario
def autenticar_usuario (usuario: str, contrasena: str) -> bool:
    """
    autentifica el acceso de un usuario con los siguientes parametros:
        - usuario: el nombre de usuario
        - contrasena: la contrasena del usuario
    y retorna True si el usuario existe y la contrasena es correcta
    o False si el usuario no existe o la contrasena es incorrecta
    """
    
    # primero se carga el archivo de usuarios
    usuarios = _cargar_usuarios()
    
    # si el usuario no existe, retorna False
    if usuario not in usuarios:
        
        return False
    
    else: 
        
        store_hash = usuarios[usuario]["contrasena"]
        return hash_contrasena(contrasena) == store_hash
        """
        si el hash de la contrasena es igual al hash guardado en el archivo
        entonces la contrasena es correcta y retorna True caso contrario retorna False
        """