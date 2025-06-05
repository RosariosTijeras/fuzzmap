# Importa Flask y el blueprint de la UI
from flask import Flask, session, redirect, url_for
from Modulos.ui.app import ui
from datetime import timedelta
import secrets  # Para generar una clave secreta segura

# Crea la aplicación Flask
app = Flask(__name__)

# Genera una clave secreta aleatoria segura para la sesión
app.secret_key = secrets.token_hex(32)  # 64 caracteres hexadecimales (~256 bits)

# Hace que las sesiones sean permanentes y define su duración
app.permanent_session_lifetime = timedelta(days=7)

# Registra el blueprint de la UI
app.register_blueprint(ui, url_prefix='/')

# Ruta raíz que redirige a login o dashboard
@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('ui.dashboard'))
    else:
        return redirect(url_for('ui.login'))

# Ejecuta la aplicación si este archivo es el principal
if __name__ == '__main__':
    app.run(debug=True)