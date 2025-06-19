"""
Archivo principal para iniciar la aplicación web de exámenes universitarios basada en Flask.
Ruta de este archivo: main.py

Este archivo realiza:
- Configuración y creación de la instancia principal de Flask.
- Registro del blueprint de la interfaz de usuario (UI).
- Configuración de la clave secreta y la duración de las sesiones.
- Definición de la ruta raíz y el flujo de redirección según el estado de sesión.
- Ejecución del servidor Flask en modo desarrollo.

Dependencias principales:
- Flask
- Modulos.ui.app (blueprint de la interfaz)
- datetime, secrets
"""

# =====================
# IMPORTACIONES
# =====================
# Importa Flask y utilidades para sesión y redirección
from flask import Flask, session, redirect, url_for
# Importa el blueprint de la interfaz de usuario
from Modulos.ui.app import ui, markdown_to_html  # Importa el blueprint y el filtro markdown
# Para definir la duración de la sesión
from datetime import timedelta
# Para generar una clave secreta segura
import secrets

# =====================
# CREACIÓN Y CONFIGURACIÓN DE LA APP FLASK
# =====================
# Crea la instancia principal de la aplicación Flask
app = Flask(__name__)

# Genera una clave secreta aleatoria segura para la sesión (requerida por Flask para manejar sesiones y cookies)
app.secret_key = secrets.token_hex(32)  # 64 caracteres hexadecimales (~256 bits)

# Configura la duración de las sesiones (7 días)
app.permanent_session_lifetime = timedelta(days=7)

# Registra el filtro markdown_to_html para usar en plantillas Jinja2
app.add_template_filter(markdown_to_html)

# Registra el blueprint de la UI en la aplicación principal, todas las rutas de la interfaz pasan por aquí
app.register_blueprint(ui, url_prefix='/')

# =====================
# RUTA RAÍZ DEL SISTEMA
# =====================
# Si el usuario está autenticado, lo redirige a su dashboard; si no, lo envía al login
@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('ui.dashboard'))  # Usuario autenticado: dashboard
    else:
        return redirect(url_for('ui.login'))  # Usuario no autenticado: login

# =====================
# INICIO DEL SERVIDOR FLASK
# =====================
if __name__ == '__main__':
    # ADVERTENCIA: en producción, usa debug=False y una clave secreta fija
    # Si debug=True y el servidor recarga, la clave secreta cambia y se pierden las sesiones
    # Para pruebas locales, puedes dejar debug=True, pero si tienes problemas de sesión, pon debug=False
    app.run(debug=True)