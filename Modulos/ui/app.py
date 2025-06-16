"""
Módulo para la interfaz web de la aplicación de exámenes universitarios, construido con Flask.
Ruta de este archivo: Modulos/ui/app.py

En este módulo se implementan las siguientes funcionalidades:
- Definición y configuración del Blueprint principal de la interfaz.
- Rutas para login, registro, dashboard de usuario y administrador, inicio y finalización de tests, resultados y estadísticas.
- Integración con el sistema de autenticación y lógica difusa para recomendaciones personalizadas.
- Gestión de sesiones, control de acceso y almacenamiento de resultados de tests.
- API para recomendaciones automáticas vía AJAX.

Dependencias principales:
- Flask
- Modulos.auth.auth (autenticación de usuarios)
- Modulos.fuzzylogic.fuzzy_evaluator (evaluación y recomendaciones)
- json, os, datetime, random, asyncio
"""

# Importa los módulos necesarios de Flask y otros componentes del sistema
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify  # Funciones principales de Flask
from Modulos.auth.auth import registrar_usuario, autenticar_usuario  # Funciones de autenticación
from Modulos.auth.auth import _cargar_usuarios  # Función para cargar usuarios
from datetime import timedelta  # Para manejo de sesiones
import json  # Para leer y escribir archivos JSON
import random  # Para seleccionar preguntas aleatoriamente
from Modulos.fuzzylogic.fuzzy_evaluator import evaluate_performance, recommendation, get_user_recommendations, recomendacion_fuzzy_con_llama32  # Evaluación y recomendaciones
import os  # Operaciones con el sistema de archivos
from datetime import datetime  # Manejo de fechas y horas
from urllib.parse import unquote  # Decodificar URLs
import asyncio  # Para operaciones asíncronas

# Crea el Blueprint 'ui' para la interfaz, configurando la carpeta de plantillas y estáticos
ui = Blueprint('ui', __name__,
               template_folder='templates',
               static_folder='src',
               static_url_path='/ui/src')

# =====================
# CREACIÓN AUTOMÁTICA DEL USUARIO ADMINISTRADOR
# =====================
# Antes de cada petición, verifica si existe el usuario admin. Si no existe, lo crea automáticamente.
@ui.before_app_request
def crear_admin():
    usuarios = _cargar_usuarios()  # Carga todos los usuarios registrados desde el archivo JSON
    if 'admin@unach.edu.ec' not in usuarios:
        # Si el usuario admin no existe, lo registra con datos por defecto
        registrar_usuario(
            'admin@unach.edu.ec',  # Correo institucional
            'admin',               # Contraseña por defecto
            'Administrador',       # Nombre
            'Principal',           # Apellido
            30,                    # Edad
            'Otro'                # Sexo
        )

# =====================
# RUTA DE LOGIN (INICIO DE SESIÓN)
# =====================
# Permite a los usuarios iniciar sesión. Si el método es GET, muestra el formulario. Si es POST, procesa el login.
@ui.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Obtiene la parte inicial del correo (sin dominio) y lo completa con el dominio institucional
        correo_parte = request.form['correo']
        usuario = f"{correo_parte}@unach.edu.ec"
        contrasena = request.form['contrasena']
        # Verifica las credenciales usando la función de autenticación
        if autenticar_usuario(usuario, contrasena):
            session.permanent = True  # Hace la sesión persistente (no se cierra al cerrar el navegador)
            session['user'] = usuario  # Guarda el usuario en la sesión
            # Si el usuario es admin, redirige al dashboard de administrador
            if usuario == 'admin@unach.edu.ec':
                return redirect(url_for('ui.admin_dashboard'))
            else:
                # Si es usuario normal, redirige a su dashboard
                return redirect(url_for('ui.dashboard'))
        else:
            # Si las credenciales son incorrectas, muestra un mensaje de error
            flash('Usuario o contraseña incorrectos.', 'danger')
    # Si es GET o hubo error, muestra el formulario de login
    return render_template('login.html')  # Muestra el formulario de login

# =====================
# RUTA DE REGISTRO
# =====================
# Permite el registro de nuevos usuarios. Si el método es GET, muestra el formulario. Si es POST, procesa el registro.
@ui.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Obtiene la parte inicial del correo (sin dominio) y lo completa con el dominio institucional
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
            # Registra el nuevo usuario usando la función correspondiente
            ok = registrar_usuario(user, pwd, names, lastn, age_int, gender)
            if ok:
                flash('¡Registro exitoso! Ahora inicia sesión.', 'success')
                return redirect(url_for('ui.login'))
            else:
                flash('El usuario ya existe.', 'danger')
    # Si es GET o hubo error, muestra el formulario de registro
    return render_template('register.html')  # Muestra el formulario de registro

# =====================
# RUTA DEL DASHBOARD DE USUARIO
# =====================
# Muestra el dashboard del usuario con información personalizada y estadísticas de tests.
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
        # Obtiene los datos del usuario desde el registro
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
        # Recorre los archivos del usuario en la carpeta correspondiente
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
        # Ordenar por fecha y hora descendente
        def parse_fecha(fecha):
            try:
                return datetime.strptime(fecha, '%d/%m/%Y %H:%M:%S')
            except Exception:
                return datetime.min
        tests.sort(key=lambda t: parse_fecha(t['fecha']), reverse=True)
        historial_tests_full = tests
        historial_tests = tests[:6]  # Los 6 más recientes
    # Calcular estadística general para el dashboard
    puntajes = [t['puntaje'] for t in historial_tests]
    promedio = sum(puntajes) / len(puntajes) if puntajes else 0
    maximo = max(puntajes) if puntajes else 0
    minimo = min(puntajes) if puntajes else 0
    # Renderiza el template del dashboard con los datos del usuario y estadísticas
    return render_template('dashboard.html', usuario=usuario, nombre=nombre, apellido=apellido, materias=materias, recomendacion_general=recomendacion_general, historial_tests=historial_tests, promedio_general=promedio, maximo_general=maximo, minimo_general=minimo)

# =====================
# RUTA DE LOGOUT (CERRAR SESIÓN)
# =====================
# Cierra la sesión del usuario y lo redirige a la página de login.
@ui.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('ui.login'))

# =====================
# RUTA DEL DASHBOARD DE ADMINISTRADOR
# =====================
# Muestra el dashboard del administrador con la lista de usuarios y permite registrar nuevos usuarios.
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
            # Registra el nuevo usuario usando la función correspondiente
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
    # Renderiza el template del dashboard admin con la lista de usuarios y mensajes
    return render_template('admin_dashboard.html', usuarios=usuarios, mensaje=mensaje)

# =====================
# RUTA PARA COMENZAR UN TEST
# =====================
# Inicia un test para el usuario en la materia seleccionada, cargando las preguntas y gestionando el estado del test.
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
    # Renderiza la plantilla del test con la pregunta actual y el temporizador
    return render_template('comenzar_test.html',
        materia_nombre=materia,
        pregunta=preguntas_seleccionadas[pregunta_actual],
        pregunta_actual=pregunta_actual,
        total_preguntas=total_preguntas,
        feedback=feedback,
        feedback_correcta=feedback_correcta,
        tiempo_restante=tiempo_restante
    )

# =====================
# FINALIZACIÓN DEL TEST
# =====================
# Finaliza el test, guarda los resultados y genera recomendaciones personalizadas.
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
    # Extraer temas fallados si existen
    temas_fallados = [r.get('tema') for r in respuestas if not r.get('correcta') and r.get('tema')]
    # Recomendación avanzada con IA
    resultados_test = {
        'materia': materia,
        'correctas': correctas,
        'incorrectas': incorrectas,
        'total': correctas + incorrectas,
        'temas_fallados': temas_fallados,
    }
    try:
        rec = asyncio.run(recomendacion_fuzzy_con_llama32(resultados_test, fuzzy_score, correctas, correctas + incorrectas, temas_fallados))
    except Exception as e:
        rec = recommendation(fuzzy_score, correctas, correctas + incorrectas, temas_fallados)
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

# =====================
# RUTA PARA MOSTRAR RESULTADOS DE UN TEST
# =====================
# Muestra los resultados del test recién completado, incluyendo estadísticas y recomendaciones.
@ui.route('/resultados_test/<materia>')
def resultados_test(materia):
    if 'user' not in session or 'test_resultados' not in session:
        return redirect(url_for('ui.dashboard'))
    data = session.pop('test_resultados')
    # Renderiza la plantilla de resultados con los datos del test
    return render_template('resultados.html',
        usuario=session.get('user', ''),
        materia_nombre=data.get('materia_nombre', ''),
        fuzzy_message=data.get('recomendacion', ''),
        correctas=data['correctas'],
        incorrectas=data['incorrectas'],
        preguntas=data['preguntas']
    )

# =====================
# RUTA PARA ESTADÍSTICAS DEL USUARIO
# =====================
# Muestra estadísticas detalladas del rendimiento del usuario en los tests realizados.
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
    # Ordenar historial por fecha y hora descendente (más reciente primero)
    def parse_fecha(fecha):
        try:
            return datetime.strptime(fecha, '%d/%m/%Y %H:%M:%S')
        except Exception:
            return datetime.min
    historial_tests.sort(key=lambda t: parse_fecha(t['fecha']), reverse=True)
    # Agrupar por materia para estadística por materia
    estadisticas_materias = {}
    for test in historial_tests:
        mat = test['materia']
        if mat not in estadisticas_materias:
            estadisticas_materias[mat] = []
        estadisticas_materias[mat].append(test['score'])
    resumen_materias = [
        {
            'materia': mat,
            'promedio': round(sum(scores)/len(scores),2) if scores else 0,
            'maximo': max(scores) if scores else 0,
            'minimo': min(scores) if scores else 0,
            'cantidad': len(scores)
        }
        for mat, scores in estadisticas_materias.items()
    ]
    # Renderiza la plantilla de estadísticas con el historial de tests y resumen por materia
    return render_template('estadisticas_usuario.html', historial_tests=historial_tests, resumen_materias=resumen_materias)

# =====================
# API PARA RECOMENDACIONES AUTOMÁTICAS
# =====================
# Proporciona recomendaciones personalizadas a través de una solicitud AJAX, basada en el último test realizado por el usuario.
@ui.route('/api/recomendacion', methods=['POST'])
def api_recomendacion():
    data = request.get_json()
    usuario = data.get('usuario')
    materia = data.get('materia')
    fuzzy_message = data.get('fuzzy_message')
    # Recuperar el último test del usuario para la materia
    user_folder = os.path.join('Datos', usuario.replace('@', '_at_'))
    test_files = [f for f in os.listdir(user_folder) if f.startswith(f'test_{materia}_') and f.endswith('.json')]
    if not test_files:
        return jsonify({'recomendacion': 'No hay datos suficientes para recomendar.'})
    test_files.sort(reverse=True)
    with open(os.path.join(user_folder, test_files[0]), 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    resultados_test = {
        'materia': materia,
        'correctas': test_data.get('correctas', 0),
        'incorrectas': test_data.get('incorrectas', 0),
        'total': test_data.get('correctas', 0) + test_data.get('incorrectas', 0),
        'temas_fallados': [r.get('tema') for r in test_data.get('respuestas', []) if not r.get('correcta') and r.get('tema')],
    }
    fuzzy_score = test_data.get('fuzzy_score', 0)
    # Prompt corto y directo
    prompt_extra = (
        "Genera una recomendación breve y concreta (máximo 3 frases), solo lo esencial para mejorar en la materia y los temas fallados. Evita motivación genérica, sé directo y útil.\n" +
        f"Recomendación difusa: {fuzzy_message}"
    )
    try:
        import asyncio
        from Modulos.fuzzylogic.fuzzy_evaluator import ollama_recommendation_llama32
        recomendacion = asyncio.run(ollama_recommendation_llama32(resultados_test, prompt_extra=prompt_extra))
        # Limitar a 3 frases
        recomendacion = '.'.join(recomendacion.split('.')[:3]).strip() + '.'
    except Exception:
        from Modulos.fuzzylogic.fuzzy_evaluator import recommendation
        recomendacion = recommendation(fuzzy_score, resultados_test['correctas'], resultados_test['total'], resultados_test['temas_fallados'])
        recomendacion = '.'.join(recomendacion.split('.')[:3]).strip() + '.'
    return jsonify({'recomendacion': recomendacion})
