"""
Modulo para la interfaz web creada con Flask
- Ruta de este archivo: Modulos/ui/app.py
"""
# Importa los módulos necesarios de Flask
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from Modulos.auth.auth import registrar_usuario, autenticar_usuario # Funciones de autenticación
from Modulos.auth.auth import _cargar_usuarios
from datetime import timedelta
import json
import random
from Modulos.fuzzylogic.fuzzy_evaluator import evaluate_performance, recommendation

# Crea el Blueprint 'ui' para la interfaz, configurando la carpeta de plantillas y estáticos
ui = Blueprint('ui', __name__,
               template_folder='templates',
               static_folder='src',
               static_url_path='/ui/src')

# Crear usuario admin automáticamente si no existe
from Modulos.auth.auth import registrar_usuario, _cargar_usuarios

@ui.before_app_request
def crear_admin():
    usuarios = _cargar_usuarios()
    if 'admin@unach.edu.ec' not in usuarios:
        registrar_usuario(
            'admin@unach.edu.ec',
            'admin',
            'Administrador',
            'Principal',
            30,
            'Otro'
        )

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
            # Redirigir a dashboard de admin si es admin
            if usuario == 'admin@unach.edu.ec':
                return redirect(url_for('ui.admin_dashboard'))
            else:
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
    usuarios = _cargar_usuarios()
    nombre = ""
    apellido = ""
    materias = []
    if usuario in usuarios:
        nombre = usuarios[usuario].get("nombre", "")
        apellido = usuarios[usuario].get("apellido", "")
        materias = usuarios[usuario].get("materias", [])
    return render_template('dashboard.html', usuario=usuario, nombre=nombre, apellido=apellido, materias=materias)

# Ruta para logout (cierra sesión y redirige al login)
@ui.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('ui.login'))

# Ruta para dashboard de administrador
@ui.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if 'user' not in session or session['user'] != 'admin@unach.edu.ec':
        return redirect(url_for('ui.login'))

    usuarios = _cargar_usuarios()
    mensaje = None
    if request.method == 'POST':
        # Registrar nuevo usuario desde el dashboard admin
        correo_parte = request.form.get('correo')
        correo = f"{correo_parte}@unach.edu.ec"
        pwd = request.form.get('contrasena')
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        edad = request.form.get('edad')
        sexo = request.form.get('sexo')
        materias = request.form.getlist('materias')  # Lista de materias seleccionadas
        if not all([correo_parte, pwd, nombres, apellidos, edad, sexo]):
            mensaje = 'Completa todos los campos.'
        else:
            try:
                edad_int = int(edad)
            except ValueError:
                mensaje = 'Edad inválida.'
                return render_template('admin_dashboard.html', usuarios=usuarios, mensaje=mensaje)
            ok = registrar_usuario(correo, pwd, nombres, apellidos, edad_int, sexo)
            if ok:
                # Guardar materias en el usuario
                usuarios = _cargar_usuarios()
                usuarios[correo]['materias'] = materias
                from Modulos.auth.auth import _guardar_usuarios
                _guardar_usuarios(usuarios)
                mensaje = 'Usuario registrado exitosamente.'
            else:
                mensaje = 'El usuario ya existe.'
        usuarios = _cargar_usuarios()  # Recargar lista
    return render_template('admin_dashboard.html', usuarios=usuarios, mensaje=mensaje)

# Ruta para comenzar un test de una materia
@ui.route('/comenzar_test/<materia>', methods=['GET', 'POST'])
def comenzar_test(materia):
    if 'user' not in session:
        return redirect(url_for('ui.login'))
    # Mapear nombre visible a nombre de archivo
    materia_map = {
        'Fundamentos de ciencia de datos': 'ciencia_datos',
        'Habilidades para la vida': 'habilidades_vida',
    }
    materia_key = materia_map.get(materia)
    if not materia_key:
        flash('Materia no válida o no implementada.', 'danger')
        return redirect(url_for('ui.dashboard'))
    # Cargar preguntas de ambos JSON
    ruta_json1 = f'Datos/{materia_key.capitalize()}/bancodepreguntas_global_{materia_key}.json'
    ruta_json2 = f'Datos/{materia_key.capitalize()}/preguntas_generadas_{materia_key}.json'
    preguntas = []
    import os
    # Cargar preguntas del banco global
    if os.path.exists(ruta_json1):
        with open(ruta_json1, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Detectar formato: lista de dicts o dict con 'lineas'
            if isinstance(data, dict) and 'lineas' in data:
                # Intentar parsear preguntas tipo generadas si es posible
                for l in data['lineas']:
                    if isinstance(l, dict) and 'pregunta' in l:
                        preguntas.append(l)
            elif isinstance(data, list):
                preguntas.extend(data)
    # Cargar preguntas generadas
    if os.path.exists(ruta_json2):
        with open(ruta_json2, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                preguntas.extend(data)
    # Filtrar solo preguntas válidas (dict con 'pregunta', 'opciones', ...)
    preguntas = [q for q in preguntas if isinstance(q, dict) and 'pregunta' in q and 'opciones' in q]
    if not preguntas:
        flash('No hay preguntas disponibles para esta materia.', 'danger')
        return redirect(url_for('ui.dashboard'))
    # Elegir aleatoriamente 10 preguntas sin repetición
    random.shuffle(preguntas)
    preguntas_seleccionadas = preguntas[:10] if len(preguntas) > 10 else preguntas
    # --- Cambios para control de test y timer ---
    import time
    if 'test_state' not in session or session.get('test_materia') != materia:
        # Nueva sesión de test
        session['test_state'] = {
            'preguntas': preguntas_seleccionadas,
            'respuestas': [],
            'inicio': int(time.time()),
            'duracion': 30*60,  # 30 minutos en segundos
        }
        session['test_materia'] = materia
    state = session['test_state']
    preguntas_seleccionadas = state['preguntas']
    pregunta_actual = int(request.args.get('q', 0))
    total_preguntas = len(preguntas_seleccionadas)
    feedback = None
    feedback_correcta = None
    tiempo_restante = max(0, state['duracion'] - (int(time.time()) - state['inicio']))
    # Si se acabó el tiempo, terminar test
    if tiempo_restante <= 0:
        return _finalizar_test(materia)
    if request.method == 'POST':
        respuesta = request.form.get('respuesta')
        correcta = preguntas_seleccionadas[pregunta_actual]['respuesta_correcta']
        state['respuestas'].append({
            'pregunta': preguntas_seleccionadas[pregunta_actual]['pregunta'],
            'respuesta_usuario': respuesta,
            'respuesta_correcta': correcta,
            'explicacion': preguntas_seleccionadas[pregunta_actual].get('explicacion', ''),
            'correcta': respuesta == correcta
        })
        session.modified = True
        siguiente = pregunta_actual + 1
        if siguiente < total_preguntas:
            return redirect(url_for('ui.comenzar_test', materia=materia, q=siguiente))
        else:
            return _finalizar_test(materia)
    return render_template('comenzar_test.html',
        materia_nombre=materia,
        pregunta=preguntas_seleccionadas[pregunta_actual],
        pregunta_actual=pregunta_actual,
        total_preguntas=total_preguntas,
        feedback=feedback,
        feedback_correcta=feedback_correcta,
        tiempo_restante=tiempo_restante
    )

def _finalizar_test(materia):
    # Guarda resultados y redirige a página de resultados
    state = session.get('test_state', {})
    respuestas = state.get('respuestas', [])
    correctas = sum(1 for r in respuestas if r.get('correcta'))
    incorrectas = len(respuestas) - correctas
    session['test_resultados'] = {
        'materia_nombre': materia,
        'preguntas': respuestas,
        'correctas': correctas,
        'incorrectas': incorrectas
    }
    session.pop('test_state', None)
    session.pop('test_materia', None)
    return redirect(url_for('ui.resultados_test', materia=materia))

# Ruta para mostrar resultados de un test
@ui.route('/resultados_test/<materia>')
def resultados_test(materia):
    if 'user' not in session or 'test_resultados' not in session:
        return redirect(url_for('ui.dashboard'))
    data = session.pop('test_resultados')
    # data: dict con claves: preguntas, correctas, incorrectas, materia_nombre
    score = evaluate_performance(data['correctas'], data['correctas'] + data['incorrectas'])
    fuzzy_message = recommendation(score)
    return render_template('resultados.html',
        materia_nombre=data['materia_nombre'],
        fuzzy_message=fuzzy_message,
        correctas=data['correctas'],
        incorrectas=data['incorrectas'],
        preguntas=data['preguntas']
    )
