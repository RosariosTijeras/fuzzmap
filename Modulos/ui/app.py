"""
Modulo para la interfaz web creada con Flask
- Ruta de este archivo: Modulos/ui/app.py
"""
# Importa los módulos necesarios de Flask
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from Modulos.auth.auth import registrar_usuario, autenticar_usuario # Funciones de autenticación
from Modulos.auth.auth import _cargar_usuarios
from datetime import timedelta

# Crea el Blueprint 'ui' para la interfaz, configurando la carpeta de plantillas y estáticos
ui = Blueprint('ui', __name__,
               template_folder='templates',
               static_folder='src',
               static_url_path='/ui/src')

# Ruta para login (GET muestra el formulario, POST procesa el login)
@ui.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Obtiene solo la primera parte del correo y arma el correo completo
        correo_parte = request.form['correo']
        usuario = f"{correo_parte}@unach.edu.ec"
        contrasena = request.form['contrasena']
        if autenticar_usuario(usuario, contrasena):
            session.permanent = True
            session['user'] = usuario
            return redirect(url_for('ui.dashboard'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html')

# Ruta para registro (GET muestra el formulario, POST procesa el registro)
@ui.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Obtiene solo la primera parte del correo y arma el correo completo
        correo_parte = request.form['correo']
        user = f"{correo_parte}@unach.edu.ec"
        pwd = request.form['contrasena']
        pwd2 = request.form['contrasena2']
        names = request.form['nombres']
        lastn = request.form['apellidos']
        age_str = request.form['edad']
        gender = request.form['sexo']
        # Validaciones
        if not all([correo_parte, pwd, pwd2, names, lastn, age_str, gender]):
            flash('Completa todos los campos.', 'danger')
        elif len(pwd) < 8:
            flash('La contraseña debe tener al menos 8 caracteres.', 'danger')
        elif pwd != pwd2:
            flash('Las contraseñas no coinciden.', 'danger')
        else:
            try:
                age_int = int(age_str)
            except ValueError:
                flash('Edad inválida.', 'danger')
                return render_template('register.html')
            ok = registrar_usuario(user, pwd, names, lastn, age_int, gender)
            if ok:
                flash('¡Registro exitoso! Ahora inicia sesión.', 'success')
                return redirect(url_for('ui.login'))
            else:
                flash('El usuario ya existe.', 'danger')
    return render_template('register.html')

# Ruta para dashboard (solo accesible si hay usuario en sesión)
@ui.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('ui.login'))
    usuario = session['user']
    # Cargar nombres y apellidos desde el archivo de usuarios
    usuarios = _cargar_usuarios()
    nombre = ""
    apellido = ""
    if usuario in usuarios:
        nombre = usuarios[usuario].get("nombre", "")
        apellido = usuarios[usuario].get("apellido", "")
    return render_template('dashboard.html', usuario=usuario, nombre=nombre, apellido=apellido)

# Ruta para logout (cierra sesión y redirige al login)
@ui.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('ui.login'))
