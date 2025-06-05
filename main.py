# Importa Flask y el blueprint de la UI
from flask import Flask
from Modulos.ui.app import ui
from datetime import timedelta

# Crea la aplicación Flask
app = Flask(__name__)
app.secret_key = 'TU_CLAVE_SECRETA'  # Cambia esto por una clave segura

# Hace que las sesiones sean permanentes y define su duración
app.permanent_session_lifetime = timedelta(days=7)

# Registra el blueprint de la UI
app.register_blueprint(ui, url_prefix='/')

# Ruta raíz que redirige a login o dashboard
@app.route('/')
def index():
    from flask import session, redirect, url_for
    if 'user' in session:
        return redirect(url_for('ui.dashboard'))
    else:
        return redirect(url_for('ui.login'))

# Ejecuta la aplicación si este archivo es el principal
if __name__ == '__main__':
    app.run(debug=True)