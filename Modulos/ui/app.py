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
from Modulos.fuzzylogic.fuzzy_evaluator import evaluate_performance, recommendation, get_user_recommendations
import os
from datetime import datetime
from urllib.parse import unquote

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
    # Leer recomendación general y tests del usuario
    user_folder = os.path.join('Datos', usuario.replace('@', '_at_'))
    recomendacion_general = get_user_recommendations(user_folder)
    historial_tests = []
    historial_tests_full = []
    if os.path.isdir(user_folder):
        tests = []
        for fname in sorted(os.listdir(user_folder)):
            if fname.startswith('test_') and fname.endswith('.json'):
                with open(os.path.join(user_folder, fname), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Si la fecha es tipo '20250612_162754', formatear a legible
                    fecha = data.get('fecha', '')
                    if '_' in fname and (not fecha or len(fecha) < 10):
                        # Extraer fecha del nombre del archivo si no está en el JSON
                        try:
                            raw = fname.split('_')[-2] + '_' + fname.split('_')[-1].replace('.json','')
                            dt = datetime.strptime(raw, '%Y%m%d_%H%M%S')
                            fecha = dt.strftime('%d/%m/%Y %H:%M:%S')
                        except Exception:
                            fecha = raw
                    tests.append({
                        'fecha': fecha,
                        'nombre_test': data.get('materia', ''),
                        'puntaje': data.get('score', 0),
                        'estado': 'Aprobado' if data.get('score', 0) >= 7 else 'Reprobado',
                        'recomendacion': data.get('recomendacion', '')
                    })
        historial_tests_full = tests
        historial_tests = tests[-6:]
    return render_template('dashboard.html', usuario=usuario, nombre=nombre, apellido=apellido, materias=materias, recomendacion_general=recomendacion_general, historial_tests=historial_tests)

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
    # Decodificar y normalizar el nombre de la materia
    materia_decodificada = unquote(materia).strip().lower()
    materia_map = {
        'fundamentos de ciencia de datos': 'Ciencia_Datos',
        'habilidades para la vida': 'Habilidades_Vida',
    }
    materia_key = materia_map.get(materia_decodificada)
    if not materia_key:
        flash('Materia no válida o no implementada.', 'danger')
        return redirect(url_for('ui.dashboard'))
    ruta_json = f'Datos/{materia_key}/preguntas_generadas_{materia_key.lower()}.json'
    preguntas = []
    import os
    if os.path.exists(ruta_json):
        with open(ruta_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                preguntas.extend(data)
    preguntas = [q for q in preguntas if isinstance(q, dict) and 'pregunta' in q and 'opciones' in q]
    if len(preguntas) < 10:
        flash('No hay suficientes preguntas para este test. Se requieren 10 preguntas únicas.', 'danger')
        return redirect(url_for('ui.dashboard'))
    random.shuffle(preguntas)
    preguntas_seleccionadas = preguntas[:10]
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

# Modifica _finalizar_test para guardar resultados y recomendaciones por usuario

def _finalizar_test(materia):
    state = session.get('test_state', {})
    respuestas = state.get('respuestas', [])
    correctas = sum(1 for r in respuestas if r.get('correcta'))
    incorrectas = len(respuestas) - correctas
    usuario = session.get('user')
    # Puntaje de 0 a 10
    score = correctas
    # Evaluación difusa robusta (mantener para recomendación)
    fuzzy_score = evaluate_performance(correctas, 10)
    rec = recommendation(fuzzy_score)
    user_folder = os.path.join('Datos', usuario.replace('@', '_at_'))
    os.makedirs(user_folder, exist_ok=True)
    from datetime import datetime
    # Guardar resultados en Datos/<usuario>/test_<materia>_<fecha>.json
    fecha = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    fecha_archivo = datetime.now().strftime('%Y%m%d_%H%M%S')
    test_file = os.path.join(user_folder, f'test_{materia}_{fecha_archivo}.json')
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump({
            'materia': materia,
            'fecha': fecha,
            'respuestas': respuestas,
            'correctas': correctas,
            'incorrectas': incorrectas,
            'score': score,
            'fuzzy_score': fuzzy_score,
            'recomendacion': rec
        }, f, ensure_ascii=False, indent=2)
    session['test_resultados'] = {
        'materia_nombre': materia,
        'preguntas': respuestas,
        'correctas': correctas,
        'incorrectas': incorrectas,
        'score': score,
        'fuzzy_score': fuzzy_score,
        'recomendacion': rec
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

@ui.route('/estadisticas_usuario')
def estadisticas_usuario():
    if 'user' not in session:
        return redirect(url_for('ui.login'))
    usuario = session['user']
    user_folder = os.path.join('Datos', usuario.replace('@', '_at_'))
    historial_tests = []
    if os.path.isdir(user_folder):
        for fname in sorted(os.listdir(user_folder)):
            if fname.startswith('test_') and fname.endswith('.json'):
                with open(os.path.join(user_folder, fname), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    historial_tests.append({
                        'fecha': data.get('fecha', ''),
                        'materia': data.get('materia', ''),
                        'score': data.get('score', 0),
                        'correctas': data.get('correctas', 0),
                        'incorrectas': data.get('incorrectas', 0),
                        'recomendacion': data.get('recomendacion', '')
                    })
    return render_template('estadisticas_usuario.html', historial_tests=historial_tests)
