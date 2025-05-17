import json # se usa para leer y guardar informacion de los usuarios en un archivo json
from pathlib import Path # se usa para cargar el json desde la carpeta de datos

# la funcion Path() crea una ruta a un archivo o carpeta
# en este caso, la ruta es "Datos/users.json"
# por lo tanto carga el archivo users.json desde la carpeta Datos
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