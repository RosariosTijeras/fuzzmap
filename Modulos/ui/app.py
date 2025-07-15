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
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app  # Funciones principales de Flask
from Modulos.auth.auth import registrar_usuario, autenticar_usuario  # Funciones de autenticación
from Modulos.auth.auth import _cargar_usuarios  # Función para cargar usuarios
from Modulos.metrics.metrics_collector import metrics_collector  # Sistema de métricas
from datetime import timedelta  # Para manejo de sesiones
import json  # Para leer y escribir archivos JSON
import random  # Para seleccionar preguntas aleatoriamente
from Modulos.fuzzylogic.fuzzy_evaluator import evaluate_performance, recommendation_features, get_user_recommendations, recomendacion_fuzzy_con_qwen3, resumen_recomendacion  # Solo funciones avanzadas
import os  # Operaciones con el sistema de archivos
from datetime import datetime  # Manejo de fechas y horas
from urllib.parse import unquote  # Decodificar URLs
import asyncio  # Para operaciones asíncronas
import time  # Para medir tiempos de respuesta
import re  # Para procesar markdown básico en recomendaciones
import plotly.graph_objects as go  # Para gráficos interactivos
import plotly.utils  # Para convertir gráficos a JSON
import glob  # Para búsqueda de archivos

# Crea el Blueprint 'ui' para la interfaz, configurando la carpeta de plantillas y estáticos
ui = Blueprint('ui', __name__,
               template_folder='templates',
               static_folder='src',
               static_url_path='/ui/src')

# Decorador para medir tiempos de respuesta
def measure_response_time(f):
    """Decorador que mide el tiempo de respuesta de las rutas."""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        try:
            result = f(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            response_time = end_time - start_time
            try:
                metrics_collector.record_request(response_time)
            except:
                pass  # Evitar errores si no se puede registrar la métrica
    return decorated_function

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
@measure_response_time
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
            
            # Cargar información del usuario para determinar tipo
            usuarios = _cargar_usuarios()
            tipo_usuario = usuarios.get(usuario, {}).get('tipo_usuario', 'alumno')
            
            # Registrar métrica de login
            try:
                user_type = "teacher" if tipo_usuario == 'maestro' else "student"
                metrics_collector.record_user_login(usuario, user_type)
            except:
                pass  # Evitar errores si no se puede registrar la métrica
            
            # Redirigir según el tipo de usuario
            if usuario == 'admin@unach.edu.ec':
                return redirect(url_for('ui.admin_dashboard'))
            elif tipo_usuario == 'maestro':
                return redirect(url_for('ui.teacher_dashboard'))
            else:
                # Alumno normal, redirige a su dashboard
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
        tipo_usuario = request.form.get('tipo_usuario', 'alumno')  # Nuevo campo
        nivel_inicial_str = request.form.get('nivel_inicial', '1')  # Nuevo campo
        
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
                # Para maestros, no se requiere nivel inicial
                if tipo_usuario == 'maestro':
                    nivel_inicial = None  # Los maestros no tienen nivel
                else:
                    nivel_inicial = int(nivel_inicial_str)
            except ValueError:
                if tipo_usuario == 'alumno':
                    flash('Edad o nivel inicial inválido.', 'danger')
                else:
                    flash('Edad inválida.', 'danger')
                return render_template('register.html')
            
            # Registra el nuevo usuario usando la función correspondiente
            ok = registrar_usuario(user, pwd, names, lastn, age_int, gender, 
                                 tipo_usuario=tipo_usuario, nivel_inicial=nivel_inicial)
            if ok:
                # Añadir el usuario al árbol AVL de estudiantes si es alumno
                if tipo_usuario == 'alumno':
                    students_tree = get_students_tree()
                    if students_tree:
                        student_data = {
                            'correo': user,
                            'nombres': names,
                            'apellidos': lastn,
                            'promedio_general': 0.0,  # Inicial
                            'nivel_dificultad': nivel_inicial,
                            'tests_realizados': 0,
                            'edad': age_int,
                            'sexo': gender
                        }
                        students_tree.insert(student_data)
                
                flash(f'¡Registro exitoso como {tipo_usuario}! Ahora inicia sesión.', 'success')
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
@measure_response_time
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
    
    # Obtener nivel de dificultad actual del usuario
    nivel_actual = get_user_difficulty_level(usuario)
    
    # Leer recomendación general y tests del usuario
    user_folder = os.path.join('Datos', usuario.replace('@', '_at_'))
    recomendacion_general_raw = get_user_recommendations(user_folder)
    
    # Procesar la recomendación para mostrar correctamente
    if recomendacion_general_raw:
        recomendacion_general = markdown_to_html(str(recomendacion_general_raw))
    else:
        recomendacion_general = None
    
    historial_tests = []
    historial_tests_full = []
    
    if os.path.isdir(user_folder):
        tests = []
        # Recorre los archivos del usuario en la carpeta correspondiente
        for fname in sorted(os.listdir(user_folder)):
            if fname.startswith('test_') and fname.endswith('.json'):
                try:
                    with open(os.path.join(user_folder, fname), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        tests.append(data)
                except:
                    continue
        
        # Ordenar por fecha descendente y tomar los últimos 5 para el dashboard
        tests.sort(key=lambda x: x.get('fecha', ''), reverse=True)
        historial_tests = tests[:5]
        historial_tests_full = tests
    
    # Obtener información del árbol AVL de estudiantes
    students_tree = get_students_tree()
    mi_posicion = None
    total_estudiantes = 0
    mi_promedio = 0.0
    
    if students_tree:
        # Actualizar información del usuario en el árbol
        students_tree.load_all_students()  # Refrescar datos
        
        # Buscar información del usuario
        mi_info = students_tree.search_student_by_email(usuario)
        if mi_info:
            mi_promedio = mi_info.get('promedio_general', 0.0)
        
        # Obtener posición en el ranking
        top_students = students_tree.get_top_students(100)  # Obtener más para encontrar posición
        total_estudiantes = len(top_students)
        
        for i, student in enumerate(top_students, 1):
            if student['email'] == usuario:
                mi_posicion = i
                break
    
    # Crear gráficos
    ranking_chart = create_ranking_chart()
    evolution_chart = create_performance_evolution_chart(usuario)
    
    # Estadísticas generales del usuario
    total_tests = len(historial_tests_full)
    promedio_general = mi_promedio
    mejor_score = max([t.get('score', 0) for t in historial_tests_full], default=0)
    
    # Renderizar dashboard con toda la información
    return render_template('dashboard.html', 
                         usuario=usuario, 
                         nombre=nombre, 
                         apellido=apellido,
                         materias=materias,
                         nivel_actual=nivel_actual,
                         historial_tests=historial_tests,
                         recomendacion_general=recomendacion_general,
                         ranking_chart=ranking_chart,
                         evolution_chart=evolution_chart,
                         mi_posicion=mi_posicion,
                         total_estudiantes=total_estudiantes,
                         mi_promedio=promedio_general,
                         total_tests=total_tests,
                         mejor_score=mejor_score)

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
@measure_response_time
def admin_dashboard():
    if 'user' not in session or session['user'] != 'admin@unach.edu.ec':
        return redirect(url_for('ui.login'))

    usuarios = _cargar_usuarios()
    mensaje = None
    mensaje_tipo = 'info'
    
    if request.method == 'POST':
        # Registrar nuevo usuario desde el dashboard admin
        correo_parte = request.form.get('correo')
        correo = f"{correo_parte}@unach.edu.ec"
        pwd = request.form.get('contrasena')
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        edad = request.form.get('edad')
        sexo = request.form.get('sexo')
        tipo_usuario = request.form.get('tipo_usuario', 'alumno')
        nivel_inicial = request.form.get('nivel_inicial', '1')
        materias = request.form.getlist('materias')  # Lista de materias seleccionadas
        
        if not all([correo_parte, pwd, nombres, apellidos, edad, sexo]):
            mensaje = 'Completa todos los campos.'
            mensaje_tipo = 'danger'
        else:
            try:
                edad_int = int(edad)
                # Para maestros, el nivel inicial no es necesario
                if tipo_usuario == 'maestro':
                    nivel_int = None  # Los maestros no tienen nivel
                else:
                    nivel_int = int(nivel_inicial)
            except ValueError:
                if tipo_usuario == 'alumno':
                    mensaje = 'Edad o nivel inicial inválido.'
                else:
                    mensaje = 'Edad inválida.'
                mensaje_tipo = 'danger'
                return render_template('admin_dashboard_modern.html', 
                                     usuarios=usuarios, 
                                     mensaje=mensaje, 
                                     mensaje_tipo=mensaje_tipo,
                                     **_get_admin_stats())
            
            # Registra el nuevo usuario usando la función correspondiente
            ok = registrar_usuario(correo, pwd, nombres, apellidos, edad_int, sexo, 
                                 tipo_usuario=tipo_usuario, nivel_inicial=nivel_int)
            if ok:
                # Guardar materias en el usuario
                usuarios = _cargar_usuarios()
                usuarios[correo]['materias'] = materias
                usuarios[correo]['tipo_usuario'] = tipo_usuario
                # Solo asignar nivel de dificultad a alumnos
                if tipo_usuario == 'alumno' and nivel_int is not None:
                    usuarios[correo]['nivel_dificultad'] = nivel_int
                
                from Modulos.auth.auth import _guardar_usuarios
                _guardar_usuarios(usuarios)
                
                # Agregar al árbol AVL de estudiantes SOLO si es alumno
                students_tree = get_students_tree()
                if students_tree and tipo_usuario == 'alumno' and nivel_int is not None:
                    student_data = {
                        'correo': correo,
                        'nombres': nombres,
                        'apellidos': apellidos,
                        'promedio_general': 0,
                        'tests_realizados': 0,
                        'nivel_dificultad': nivel_int
                    }
                    students_tree.insert(student_data)
                
                mensaje = f'Usuario {tipo_usuario} registrado exitosamente.'
                mensaje_tipo = 'success'
            else:
                mensaje = 'El usuario ya existe.'
                mensaje_tipo = 'warning'
        
        usuarios = _cargar_usuarios()  # Recargar lista
    
    # Obtener estadísticas para el dashboard moderno
    admin_stats = _get_admin_stats()
    
    # Renderiza el template moderno del dashboard admin
    return render_template('admin_dashboard_modern.html', 
                         usuarios=usuarios, 
                         mensaje=mensaje, 
                         mensaje_tipo=mensaje_tipo,
                         **admin_stats)

# =====================
# RUTA DEL DASHBOARD EXCLUSIVO PARA MAESTROS
# =====================
@ui.route('/teacher_dashboard')
@measure_response_time
def teacher_dashboard():
    if 'user' not in session:
        return redirect(url_for('ui.login'))
    
    usuario = session['user']
    usuarios = _cargar_usuarios()
    
    # Verificar que el usuario sea realmente un maestro
    if usuarios.get(usuario, {}).get('tipo_usuario', 'alumno') != 'maestro':
        flash('Acceso denegado. Esta área es exclusiva para maestros.', 'danger')
        return redirect(url_for('ui.dashboard'))
    
    # Obtener información del maestro
    maestro_info = usuarios[usuario]
    nombre = maestro_info.get("nombre", "")
    apellido = maestro_info.get("apellido", "")
    materias_asignadas = maestro_info.get("materias", [])
    
    # Obtener estadísticas de alumnos del maestro
    teacher_stats = _get_teacher_stats(usuario, materias_asignadas)
    
    return render_template('teacher_dashboard.html',
                         usuario=usuario,
                         nombre=nombre,
                         apellido=apellido,
                         materias_asignadas=materias_asignadas,
                         **teacher_stats)

def _sort_by_fecha(item):
    """Función auxiliar para ordenar por fecha"""
    return item.get('fecha', '')

def _sort_by_promedio(item):
    """Función auxiliar para ordenar ranking por promedio"""
    return item[1]['promedio']

def _get_teacher_stats(teacher_email, materias_asignadas):
    """
    Obtiene estadísticas específicas para el dashboard del maestro
    """
    usuarios = _cargar_usuarios()
    students_tree = get_students_tree()
    
    # Filtrar solo alumnos
    alumnos = {email: data for email, data in usuarios.items() 
               if data.get('tipo_usuario', 'alumno') == 'alumno'}
    
    # Estadísticas por materia
    stats_por_materia = {}
    todos_los_alumnos = []
    
    for materia in materias_asignadas:
        # Obtener resultados de tests de esta materia
        resultados_materia = []
        niveles_distribucion = {'1': 0, '2': 0, '3': 0}
        
        # Recorrer carpetas de alumnos
        for alumno_email in alumnos.keys():
            alumno_folder = os.path.join('Datos', alumno_email.replace('@', '_at_'))
            if os.path.isdir(alumno_folder):
                # Buscar tests de esta materia
                pattern = os.path.join(alumno_folder, f'test_{materia}_*.json')
                test_files = glob.glob(pattern)
                
                for test_file in test_files:
                    try:
                        with open(test_file, 'r', encoding='utf-8') as f:
                            test_data = json.load(f)
                            resultados_materia.append({
                                'alumno': alumno_email,
                                'nombre': f"{alumnos[alumno_email].get('nombre', '')} {alumnos[alumno_email].get('apellido', '')}",
                                'fecha': test_data.get('fecha', ''),
                                'score': test_data.get('score', 0),
                                'nivel_usado': test_data.get('nivel_usado', '1')
                            })
                            
                            # Contar niveles
                            nivel = str(test_data.get('nivel_usado', '1'))
                            if nivel in niveles_distribucion:
                                niveles_distribucion[nivel] += 1
                    except:
                        continue
        
        # Estadísticas de la materia
        if resultados_materia:
            scores = [r['score'] for r in resultados_materia]
            # Crear resultados recientes sin objetos lambda
            resultados_ordenados = []
            for resultado in resultados_materia:
                # Crear copia serializable del resultado
                resultado_limpio = {
                    'alumno': str(resultado['alumno']),
                    'nombre': str(resultado['nombre']),
                    'fecha': str(resultado.get('fecha', '')),
                    'score': float(resultado['score']),
                    'nivel_usado': str(resultado.get('nivel_usado', '1'))
                }
                resultados_ordenados.append(resultado_limpio)
            
            # Ordenar por fecha usando función auxiliar
            try:
                resultados_ordenados.sort(key=_sort_by_fecha, reverse=True)
                resultados_recientes = resultados_ordenados[:10]
            except:
                # Si hay error en el ordenamiento, tomar los primeros 10
                resultados_recientes = resultados_ordenados[:10]
            
            stats_por_materia[materia] = {
                'total_tests': int(len(resultados_materia)),
                'promedio': float(round(sum(scores) / len(scores), 2)),
                'mejor_score': float(max(scores)),
                'peor_score': float(min(scores)),
                'alumnos_unicos': int(len(set(r['alumno'] for r in resultados_materia))),
                'resultados_recientes': resultados_recientes,
                'niveles_distribucion': {str(k): int(v) for k, v in niveles_distribucion.items()}
            }
        else:
            stats_por_materia[materia] = {
                'total_tests': 0,
                'promedio': 0.0,
                'mejor_score': 0.0,
                'peor_score': 0.0,
                'alumnos_unicos': 0,
                'resultados_recientes': [],
                'niveles_distribucion': {'1': 0, '2': 0, '3': 0}
            }
    
    # Ranking de alumnos general (todos los que han hecho tests en materias del maestro)
    ranking_alumnos = {}
    
    for materia in materias_asignadas:
        for resultado in stats_por_materia[materia]['resultados_recientes']:
            alumno = resultado['alumno']
            if alumno not in ranking_alumnos:
                ranking_alumnos[alumno] = {
                    'nombre': resultado['nombre'],
                    'scores': [],
                    'total_tests': 0,
                    'materias': set()
                }
            ranking_alumnos[alumno]['scores'].append(resultado['score'])
            ranking_alumnos[alumno]['total_tests'] += 1
            ranking_alumnos[alumno]['materias'].add(materia)
    
    # Calcular promedios para ranking y asegurar serialización
    for alumno_data in ranking_alumnos.values():
        if alumno_data['scores']:
            alumno_data['promedio'] = round(sum(alumno_data['scores']) / len(alumno_data['scores']), 2)
            # Convertir set a lista para serialización JSON
            alumno_data['materias'] = list(alumno_data['materias'])
        else:
            alumno_data['promedio'] = 0.0
            alumno_data['materias'] = []
    
    # Ordenar ranking por promedio y crear lista serializable
    ranking_items = list(ranking_alumnos.items())
    ranking_items.sort(key=_sort_by_promedio, reverse=True)
    ranking_ordenado = ranking_items[:10]
    
    # Crear datos serializables para gráficos
    charts_data = _create_teacher_charts(stats_por_materia, ranking_ordenado)
    
    # Limpiar todos los datos antes de retornar para asegurar serialización JSON
    return {
        'stats_por_materia': _clean_data_for_json(stats_por_materia),
        'ranking_alumnos': _clean_data_for_json(ranking_ordenado),
        'total_alumnos': int(len(ranking_alumnos)),
        'total_tests': int(sum(stats['total_tests'] for stats in stats_por_materia.values())),
        'promedio_general': float(round(sum(stats['promedio'] * stats['total_tests'] 
                                          for stats in stats_por_materia.values()) / 
                                       max(sum(stats['total_tests'] for stats in stats_por_materia.values()), 1), 2)),
        'charts_data': charts_data
    }

def _create_teacher_charts(stats_por_materia, ranking_alumnos):
    """
    Crea datos para gráficos interactivos del dashboard del maestro
    """
    # Gráfico de ranking de alumnos - Verificar que los datos sean serializables
    ranking_chart = {
        'labels': [str(data[1]['nombre']) for data in ranking_alumnos[:10] if 'nombre' in data[1]],
        'values': [float(data[1]['promedio']) for data in ranking_alumnos[:10] if 'promedio' in data[1]],
        'colors': ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', 
                  '#00f2fe', '#43e97b', '#38f9d7', '#fa709a', '#fee140']
    }
    
    # Gráfico de distribución de niveles
    niveles_totals = {'1': 0, '2': 0, '3': 0}
    for materia, stats in stats_por_materia.items():
        if 'niveles_distribucion' in stats:
            for nivel, count in stats['niveles_distribucion'].items():
                if nivel in niveles_totals:
                    niveles_totals[nivel] += int(count)
    
    niveles_chart = {
        'labels': ['Básico (Nivel 1)', 'Intermedio (Nivel 2)', 'Avanzado (Nivel 3)'],
        'values': [int(niveles_totals['1']), int(niveles_totals['2']), int(niveles_totals['3'])],
        'colors': ['#2ecc71', '#f39c12', '#e74c3c']
    }
    
    # Gráfico de rendimiento por materia
    materias_chart = {
        'labels': [str(materia) for materia in stats_por_materia.keys()],
        'values': [float(stats['promedio']) for stats in stats_por_materia.values() if 'promedio' in stats],
        'colors': ['#9b59b6', '#1abc9c', '#f1c40f', '#e67e22', '#95a5a6']
    }
    
    # Limpiar todos los datos para asegurar serialización JSON
    charts_data = {
        'ranking_chart': _clean_data_for_json(ranking_chart),
        'niveles_chart': _clean_data_for_json(niveles_chart),
        'materias_chart': _clean_data_for_json(materias_chart)
    }
    
    return charts_data

# =====================
# RUTA PARA COMENZAR UN TEST
# =====================
# Inicia un test para el usuario en la materia seleccionada, usando AVL para selección inteligente de preguntas.
@ui.route('/comenzar_test/<materia>', methods=['GET', 'POST'])
@measure_response_time
def comenzar_test(materia):
    if 'user' not in session:
        return redirect(url_for('ui.login'))
    
    usuario = session['user']
    
    # Obtener el árbol de preguntas
    questions_tree = get_questions_tree()
    if not questions_tree:
        flash('Error del sistema: no se pudieron cargar las preguntas.', 'danger')
        return redirect(url_for('ui.dashboard'))
    
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
    
    # Obtener nivel de dificultad del usuario (automático, sin selector)
    nivel_usuario = get_user_difficulty_level(usuario)
    
    # Medir tiempo de búsqueda y comparar algoritmos
    print(f"\n🔍 SELECCIONANDO PREGUNTAS PARA {usuario}")
    print(f"   Materia: {materia_key}")
    print(f"   Nivel: {nivel_usuario}")
    
    # Comparar algoritmos de búsqueda
    start_composite = time.time()
    preguntas_composite = questions_tree.search_by_difficulty_and_subject_composite(nivel_usuario, materia_key)
    end_composite = time.time()
    
    start_binary = time.time()
    preguntas_binary = questions_tree.search_by_difficulty_and_subject_binary(nivel_usuario, materia_key)
    end_binary = time.time()
    
    start_linear = time.time()
    preguntas_linear = questions_tree.search_by_difficulty_and_subject_linear(nivel_usuario, materia_key)
    end_linear = time.time()
    
    print(f"   🚀 Composite: {(end_composite - start_composite)*1000:.3f}ms ({len(preguntas_composite)} preguntas)")
    print(f"   🔍 Binary: {(end_binary - start_binary)*1000:.3f}ms ({len(preguntas_binary)} preguntas)")
    print(f"   🐌 Linear: {(end_linear - start_linear)*1000:.3f}ms ({len(preguntas_linear)} preguntas)")
    
    # Usar el resultado del índice compuesto (más eficiente)
    preguntas_disponibles = preguntas_composite or []
    
    # Si no hay suficientes preguntas del nivel exacto, obtener de niveles cercanos
    if len(preguntas_disponibles) < 3:
        print(f"   ⚠️ Solo {len(preguntas_disponibles)} preguntas de nivel {nivel_usuario}, mezclando niveles...")
        preguntas_disponibles = questions_tree.get_questions_for_user_level(materia_key, nivel_usuario, count=15)
    
    if len(preguntas_disponibles) < 3:
        flash(f'No hay suficientes preguntas para el nivel {nivel_usuario} en {materia}. Se requieren 3 preguntas mínimo.', 'danger')
        return redirect(url_for('ui.dashboard'))
    
    # Seleccionar preguntas aleatoriamente (máximo 10, mínimo 3)
    num_preguntas = min(10, len(preguntas_disponibles))
    random.shuffle(preguntas_disponibles)
    preguntas_seleccionadas = preguntas_disponibles[:num_preguntas]
    
    print(f"   ✅ Seleccionadas {len(preguntas_seleccionadas)} preguntas para el test")
    
    # Control de test y timer
    if 'test_state' not in session or session.get('test_materia') != materia:
        # Nueva sesión de test
        session['test_state'] = {
            'preguntas': preguntas_seleccionadas,
            'respuestas': [],
            'inicio': int(time.time()),
            'duracion': 30*60,  # 30 minutos en segundos
            'nivel_usado': nivel_usuario
        }
        session['test_materia'] = materia
    
    state = session['test_state']
    preguntas_seleccionadas = state['preguntas']
    pregunta_actual = int(request.args.get('q', 0))
    total_preguntas = len(preguntas_seleccionadas)
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
            'correcta': respuesta == correcta,
            'dificultad': preguntas_seleccionadas[pregunta_actual].get('dificultad', nivel_usuario)
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
                         tiempo_restante=tiempo_restante,
                         nivel_usuario=nivel_usuario)

# =====================
# FINALIZACIÓN DEL TEST
# =====================
# Finaliza el test, guarda los resultados, actualiza el nivel del usuario y genera recomendaciones.
def _finalizar_test(materia):
    state = session.get('test_state', {})
    respuestas = state.get('respuestas', [])
    correctas = sum(1 for r in respuestas if r.get('correcta'))
    incorrectas = len(respuestas) - correctas
    usuario = session.get('user')
    nivel_usado = state.get('nivel_usado', 'Principiante')
    
    # Calcular duración del test
    test_duration = time.time() - state.get('inicio', time.time())
    
    # Obtener número total de preguntas del test
    total_preguntas = len(respuestas)
    
    # Puntaje escalado a base 10
    score = round((correctas / total_preguntas) * 10, 1) if total_preguntas > 0 else 0
    
    # Registrar métricas del test
    try:
        metrics_collector.record_test_attempt(materia, score, test_duration)
    except:
        pass  # Evitar errores si no se puede registrar la métrica
    
    # Actualizar el nivel del usuario en el árbol AVL basado en el rendimiento
    update_user_level_after_test(usuario, score)
    nuevo_nivel = get_user_difficulty_level(usuario)
    
    print(f"\n📊 RESULTADO DEL TEST PARA {usuario}")
    print(f"   Materia: {materia}")
    print(f"   Nivel usado: {nivel_usado}")
    print(f"   Puntuación: {correctas}/{total_preguntas} = {score}/10")
    print(f"   Nuevo nivel: {nuevo_nivel}")
    
    # Evaluación difusa robusta (mantener para recomendación)
    fuzzy_score = evaluate_performance(correctas, total_preguntas)
    
    # Extraer temas fallados si existen
    temas_fallados = [r.get('tema') for r in respuestas if not r.get('correcta') and r.get('tema')]
    
    # Recomendación avanzada con IA
    preguntas_falladas = [
        {
            'pregunta': r.get('pregunta'),
            'respuesta_usuario': r.get('respuesta_usuario'),
            'respuesta_correcta': r.get('respuesta_correcta'),
            'explicacion': r.get('explicacion', ''),
            'tema': r.get('tema', ''),
            'dificultad': r.get('dificultad', nivel_usado)
        }
        for r in respuestas if not r.get('correcta')
    ]
    
    resultados_test = {
        'materia': materia,
        'correctas': correctas,
        'incorrectas': incorrectas,
        'total': correctas + incorrectas,
        'temas_fallados': temas_fallados,
        'preguntas_falladas': preguntas_falladas,
        'nivel_usado': nivel_usado,
        'nuevo_nivel': nuevo_nivel
    }
    
    # Recopilar historial de tests previos de la misma materia
    historial_materia = []
    user_folder = os.path.join('Datos', usuario.replace('@', '_at_'))
    if os.path.isdir(user_folder):
        for fname in os.listdir(user_folder):
            if fname.startswith('test_') and fname.endswith('.json') and materia in fname:
                try:
                    with open(os.path.join(user_folder, fname), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        historial_materia.append({
                            'fecha': data.get('fecha', ''),
                            'correctas': data.get('correctas', 0),
                            'incorrectas': data.get('incorrectas', 0),
                            'score': data.get('score', 0),
                            'nivel_usado': data.get('nivel_usado', 'N/A'),
                            'preguntas_falladas': [
                                {
                                    'pregunta': r.get('pregunta'),
                                    'respuesta_usuario': r.get('respuesta_usuario'),
                                    'respuesta_correcta': r.get('respuesta_correcta'),
                                    'explicacion': r.get('explicacion', ''),
                                    'tema': r.get('tema', '')
                                }
                                for r in data.get('respuestas', []) if not r.get('correcta')
                            ]
                        })
                except:
                    continue
    
    resultados_test['historial_materia'] = historial_materia
    
    try:
        # Generar recomendación usando el sistema de lógica difusa existente
        print(f"🤖 Generando recomendación para {usuario}...")
        
        # Usar el sistema de recomendaciones existente del módulo fuzzy_evaluator
        rec = recomendacion_fuzzy_con_qwen3(resultados_test)
        
        if not rec or len(str(rec).strip()) < 10:
            # Fallback a recomendación basada en reglas
            rec = generar_recomendacion_respaldo(score, nivel_usado, len(preguntas_falladas))
            
    except Exception as e:
        print(f"❌ Error generando recomendación IA: {e}")
        # Recomendación de respaldo basada en reglas
        rec = generar_recomendacion_respaldo(score, nivel_usado, len(preguntas_falladas))
    
    # Guardar resultados en archivo
    user_folder = os.path.join('Datos', usuario.replace('@', '_at_'))
    os.makedirs(user_folder, exist_ok=True)
    from datetime import datetime
    # Guardar resultados en Datos/<usuario>/test_<materia>_<fecha>.json
    fecha = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    fecha_archivo = datetime.now().strftime('%Y%m%d_%H%M%S')
    test_file = os.path.join(user_folder, f'test_{materia}_{fecha_archivo}.json')
    # Convertir PredictionResult y otros objetos no serializables a string en respuestas
    def serializar_respuesta(r):
        r_serial = dict(r)
        for k, v in r_serial.items():
            if hasattr(v, '__class__') and v.__class__.__name__ == 'PredictionResult':
                r_serial[k] = str(v)
        return r_serial
    respuestas_serializables = [serializar_respuesta(r) for r in respuestas]
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump({
            'materia': materia,
            'fecha': fecha,
            'respuestas': respuestas_serializables,
            'correctas': correctas,
            'incorrectas': incorrectas,
            'score': score,
            'fuzzy_score': fuzzy_score,
            'nivel_usado': nivel_usado,
            'nuevo_nivel': nuevo_nivel,
            'recomendacion': str(rec)  # Siempre texto plano
        }, f, ensure_ascii=False, indent=2)
    session['test_resultados'] = {
        'materia_nombre': materia,
        'preguntas': respuestas,
        'correctas': correctas,
        'incorrectas': incorrectas,
        'score': score,
        'fuzzy_score': fuzzy_score,
        'recomendacion': str(rec)  # Siempre texto plano
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
    # Renderiza la plantilla optimizada de resultados con recomendaciones inline
    return render_template('resultados_optimized.html',
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
    user_folder = os.path.join('Datos', usuario.replace('@', '_at_'))
    test_files = [f for f in os.listdir(user_folder) if f.startswith(f'test_{materia}_') and f.endswith('.json')]
    if not test_files:
        return jsonify({'recomendacion': 'No hay datos suficientes para recomendar.'})
    test_files.sort(reverse=True)
    with open(os.path.join(user_folder, test_files[0]), 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    # Usar la recomendación guardada, sin filtros ni generación nueva
    recomendacion = test_data.get('recomendacion', 'No hay recomendación generada.')
    recomendacion_html = markdown_to_html(recomendacion)
    return jsonify({'recomendacion': recomendacion_html})

def markdown_to_html(text):
    """
    Convierte texto markdown simple (**negrita**) a HTML seguro para mostrar en plantillas.
    - Elimina la palabra 'Recomendación' en negrita al inicio si existe.
    - Si la línea comienza con '* **texto**', elimina el asterisco y deja solo el texto en negrita.
    """
    if not isinstance(text, str):
        return text
    # Elimina "<b>Recomendación</b>" o "**Recomendación**" al inicio, con o sin espacios y saltos de línea
    text = re.sub(r'^(<b>Recomendación</b>|\*\*Recomendación\*\*)[\s:\n]*', '', text)
    # Convierte líneas que empiezan con '* **texto**' a solo <b>texto</b>
    text = re.sub(r'^\*\s*\*\*(.+?)\*\*', r'<b>\1</b>', text, flags=re.MULTILINE)
    # Solo negrita (**texto**)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Opcional: convierte saltos de línea dobles en <br><br> para mejor visualización
    text = text.replace('\n\n', '<br><br>')
    return text

# =====================
# API PARA RESPUESTA DE CHAT CON IA
# =====================
# Proporciona respuestas a consultas del usuario sobre el test y la materia, usando el modelo de IA con contexto.
@ui.route('/api/chat_ai', methods=['POST'])
def api_chat_ai():
    data = request.get_json()
    usuario = data.get('usuario', '')
    materia = data.get('materia', '')
    mensaje = data.get('mensaje', '')
    # Prompt para el modelo: contexto de materia y mensaje del usuario
    # Enriquecer el prompt con contexto estructurado y ejemplos
    prompt = (
        f"Eres un orientador académico universitario experto en retroalimentación personalizada. El usuario está realizando un test de la materia '{materia}'. "
        "Responde de forma clara, útil y profesional a la siguiente consulta del usuario, usando ejemplos y consejos prácticos si es posible. Si la pregunta es sobre un error concreto, explica cómo mejorar. "
        "Siempre responde únicamente en español, sin ninguna frase en inglés. "
        "\n\nEstructura tu respuesta así:\n"
        "1. Responde primero a la consulta del usuario de forma directa y específica.\n"
        "2. Si la consulta es sobre un error, explica el error y cómo corregirlo, usando ejemplos concretos.\n"
        "3. Si es una duda conceptual, da una explicación clara y breve, con ejemplos prácticos.\n"
        "4. Si el usuario pide recursos, sugiere materiales, ejercicios o estrategias de estudio.\n"
        "5. Si el usuario pregunta sobre su progreso, analiza su desempeño en la materia y sugiere cómo mejorar.\n"
        "\nEjemplo de formato:\n"
        "Consulta: ¿Por qué fallé la pregunta sobre resiliencia?\n"
        "Respuesta: Fallaste la pregunta sobre resiliencia porque confundiste el concepto con adaptación al cambio. La resiliencia se refiere a la capacidad de superar situaciones difíciles y recuperarse emocionalmente. Te recomiendo repasar ejemplos de resiliencia en la vida diaria y practicar ejercicios de autoevaluación.\n"
        f"\nMensaje del usuario: {mensaje}\n"
    )
    try:
        # Usar función de recomendación disponible
        respuesta = recomendacion_fuzzy_con_qwen3({'materia': materia}, prompt_extra=prompt)
        respuesta_html = markdown_to_html(str(respuesta))
    except Exception as e:
        respuesta_html = "No se pudo obtener respuesta de la IA. Intenta nuevamente más tarde."
    return jsonify({'respuesta': respuesta_html})

# =====================
# API PARA MÉTRICAS EN TIEMPO REAL
# =====================
@ui.route('/api/metrics', methods=['GET'])
def api_metrics():
    """Obtiene métricas de rendimiento en tiempo real para el dashboard de admin"""
    if 'user' not in session or session['user'] != 'admin@unach.edu.ec':
        return jsonify({'error': 'Acceso denegado'}), 403
    
    try:
        real_metrics = metrics_collector.get_performance_metrics()
        return jsonify({
            'success': True,
            'metrics': real_metrics
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =====================
# FUNCIONES AUXILIARES PARA OBTENER ÁRBOLES AVL
# =====================

def get_questions_tree():
    """Obtiene el árbol AVL de preguntas desde la configuración de la app"""
    try:
        return current_app.config.get('QUESTIONS_TREE')
    except:
        return None

def get_students_tree():
    """Obtiene el árbol AVL de estudiantes desde la configuración de la app"""
    try:
        return current_app.config.get('STUDENTS_TREE')
    except:
        return None

def get_user_difficulty_level(user_email):
    """
    Obtiene el nivel de dificultad actual del usuario basado en su promedio y configuración
    - 1 (Básico): 0-60 puntos de promedio
    - 2 (Intermedio): 61-80 puntos de promedio
    - 3 (Avanzado): 81-100 puntos de promedio
    """
    # Primero intentar obtener desde el registro de usuario
    usuarios = _cargar_usuarios()
    if user_email in usuarios:
        nivel_guardado = usuarios[user_email].get('nivel_dificultad', 1)
        # Si ya hay un promedio calculado, usar ese criterio
        students_tree = get_students_tree()
        if students_tree:
            student = students_tree.search_student_by_email(user_email)
            if student and student.get('promedio_general', 0) > 0:
                promedio = student.get('promedio_general', 0)
                if promedio >= 81:
                    return 3  # Avanzado
                elif promedio >= 61:
                    return 2  # Intermedio
                else:
                    return 1  # Básico
        
        # Si no hay promedio, usar el nivel inicial configurado
        return nivel_guardado
    
    # Default para usuarios no encontrados
    return 1

def update_user_level_after_test(user_email, test_score):
    """Actualiza el nivel del usuario después de completar un test"""
    students_tree = get_students_tree()
    if not students_tree:
        return
    
    # Recalcular promedio y actualizar en el árbol
    user_folder = os.path.join('Datos', user_email.replace('@', '_at_'))
    new_average = students_tree.calculate_student_average(user_email, user_folder)
    students_tree.update_student_average(user_email, new_average)

def create_ranking_chart():
    """Crea un gráfico de ranking de estudiantes usando Plotly"""
    students_tree = get_students_tree()
    if not students_tree:
        return None
    
    top_students = students_tree.get_top_students(10)
    if not top_students:
        return None
    
    # Preparar datos para el gráfico
    names = [f"{s['nombre']} {s['apellido']}" for s in top_students]
    averages = [s['promedio_general'] for s in top_students]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
              '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
    
    fig = go.Figure(data=[
        go.Bar(
            x=names,
            y=averages,
            marker=dict(
                color=colors[:len(names)],
                line=dict(color='rgba(50, 50, 50, 0.8)', width=1)
            ),
            text=[f'{avg:.1f}' for avg in averages],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title={
            'text': '🏆 Top 10 Mejores Estudiantes',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2c3e50'}
        },
        xaxis_title='Estudiantes',
        yaxis_title='Promedio General',
        yaxis=dict(range=[0, 100]),
        plot_bgcolor='rgba(245,245,245,0.9)',
        paper_bgcolor='rgba(255,255,255,1)',
        height=500,
        margin=dict(l=40, r=40, t=60, b=100),
        font=dict(family="Arial, sans-serif", size=12, color="#2c3e50")
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_performance_evolution_chart(user_email):
    """Crea un gráfico de evolución del rendimiento del usuario"""
    user_folder = os.path.join('Datos', user_email.replace('@', '_at_'))
    
    if not os.path.isdir(user_folder):
        return None
    
    # Obtener historial de tests
    tests = []
    for fname in sorted(os.listdir(user_folder)):
        if fname.startswith('test_') and fname.endswith('.json'):
            try:
                with open(os.path.join(user_folder, fname), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    tests.append({
                        'fecha': data.get('fecha', ''),
                        'score': data.get('score', 0),
                        'materia': data.get('materia', ''),
                        'file': fname
                    })
            except:
                continue
    
    if len(tests) < 2:
        return None
    
    # Preparar datos por materia
    materias = {}
    for test in tests:
        materia = test['materia']
        if materia not in materias:
            materias[materia] = {'fechas': [], 'scores': []}
        materias[materia]['fechas'].append(test['fecha'])
        materias[materia]['scores'].append(test['score'])
    
    fig = go.Figure()
    
    colors = {'Ciencia_Datos': '#4ECDC4', 'Habilidades_Vida': '#FF6B6B'}
    
    for materia, data in materias.items():
        fig.add_trace(go.Scatter(
            x=data['fechas'],
            y=data['scores'],
            mode='lines+markers',
            name=materia.replace('_', ' '),
            line=dict(color=colors.get(materia, '#45B7D1'), width=3),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title={
            'text': '📈 Tu Evolución en el Tiempo',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2c3e50'}
        },
        xaxis_title='Fecha',
        yaxis_title='Puntuación',
        yaxis=dict(range=[0, 100]),
        plot_bgcolor='rgba(245,245,245,0.9)',
        paper_bgcolor='rgba(255,255,255,1)',
        height=400,
        hovermode='x',
        font=dict(family="Arial, sans-serif", size=12, color="#2c3e50")
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

# =====================
# FUNCIONES AUXILIARES PARA ESTADÍSTICAS ADMINISTRATIVAS
# =====================

def _get_admin_stats():
    """
    Obtiene estadísticas completas REALES para el dashboard de administrador
    """
    import glob
    import os
    
    usuarios = _cargar_usuarios()
    students_tree = get_students_tree()
    questions_tree = get_questions_tree()
    
    # 1. CONTEO REAL DE USUARIOS
    alumnos = {email: data for email, data in usuarios.items() 
               if data.get('tipo_usuario', 'alumno') == 'alumno'}
    maestros = {email: data for email, data in usuarios.items() 
                if data.get('tipo_usuario', 'maestro') == 'maestro'}
    admins = {email: data for email, data in usuarios.items() 
              if data.get('tipo_usuario', 'admin') == 'admin'}
    
    total_usuarios = len(alumnos)
    total_maestros = len(maestros)
    
    print(f"📊 ESTADÍSTICAS REALES DEL ADMIN:")
    print(f"   👥 Alumnos: {total_usuarios}")
    print(f"   👨‍🏫 Maestros: {total_maestros}")
    print(f"   🛡️ Administradores: {len(admins)}")
    
    # 2. CONTEO REAL DE TESTS
    total_tests = 0
    materias_populares = {}
    suma_scores = 0
    
    # Buscar todos los archivos de test
    for usuario_email in alumnos.keys():
        user_folder = os.path.join('Datos', usuario_email.replace('@', '_at_'))
        if os.path.isdir(user_folder):
            test_files = [f for f in os.listdir(user_folder) 
                         if f.startswith('test_') and f.endswith('.json')]
            
            for test_file in test_files:
                try:
                    with open(os.path.join(user_folder, test_file), 'r', encoding='utf-8') as f:
                        test_data = json.load(f)
                        total_tests += 1
                        suma_scores += test_data.get('score', 0)
                        
                        # Contar materias populares
                        materia = test_data.get('materia', 'Desconocida')
                        materias_populares[materia] = materias_populares.get(materia, 0) + 1
                        
                except:
                    continue
    
    promedio_general = round(suma_scores / total_tests, 2) if total_tests > 0 else 0
    
    print(f"   📝 Tests realizados: {total_tests}")
    print(f"   📊 Promedio general: {promedio_general}")
    
    # 3. DISTRIBUCIÓN REAL POR NIVELES
    niveles_distribucion = {'Básico': 0, 'Intermedio': 0, 'Avanzado': 0}
    
    for email, data in alumnos.items():
        nivel = data.get('nivel_dificultad', 1)
        if nivel == 1:
            niveles_distribucion['Básico'] += 1
        elif nivel == 2:
            niveles_distribucion['Intermedio'] += 1
        else:
            niveles_distribucion['Avanzado'] += 1
    
    print(f"   📈 Niveles - Básico: {niveles_distribucion['Básico']}, Intermedio: {niveles_distribucion['Intermedio']}, Avanzado: {niveles_distribucion['Avanzado']}")
    
    # 4. CONTEO REAL DE PREGUNTAS
    total_preguntas = 0
    preguntas_por_nivel = {'1': 0, '2': 0, '3': 0}
    preguntas_por_materia = {}
    
    # Contar preguntas de Ciencia de Datos
    try:
        with open('Datos/Ciencia_Datos/preguntas_generadas/preguntas_generadas_ciencia_datos.json', 'r', encoding='utf-8') as f:
            cd_questions = json.load(f)
            total_preguntas += len(cd_questions)
            preguntas_por_materia['Ciencia de Datos'] = len(cd_questions)
            
            for q in cd_questions:
                nivel = str(q.get('dificultad', 2))
                if nivel in preguntas_por_nivel:
                    preguntas_por_nivel[nivel] += 1
    except:
        pass
    
    # Contar preguntas de Habilidades para la Vida
    try:
        with open('Datos/Habilidades_Vida/preguntas_generadas/preguntas_generadas_habilidades_vida.json', 'r', encoding='utf-8') as f:
            hv_questions = json.load(f)
            total_preguntas += len(hv_questions)
            preguntas_por_materia['Habilidades para la Vida'] = len(hv_questions)
            
            for q in hv_questions:
                nivel = str(q.get('dificultad', 2))
                if nivel in preguntas_por_nivel:
                    preguntas_por_nivel[nivel] += 1
    except:
        pass
    
    print(f"   ❓ Total preguntas: {total_preguntas}")
    
    # 5. OBTENER DATOS REALES DE ESTUDIANTES PARA RANKING
    estudiantes_data = []
    if students_tree:
        # Recargar todos los estudiantes
        students_tree.load_all_students()
        ranking = students_tree.get_top_students(limit=10)
        estudiantes_data = ranking
    
    # 6. DATOS PARA GRÁFICOS
    charts_data = {
        'niveles_chart': {
            'labels': list(niveles_distribucion.keys()),
            'values': list(niveles_distribucion.values()),
            'colors': ['#3498db', '#f39c12', '#e74c3c']
        },
        'materias_chart': {
            'labels': list(materias_populares.keys())[:5],
            'values': list(materias_populares.values())[:5],
            'colors': ['#9b59b6', '#1abc9c', '#f1c40f', '#e67e22', '#95a5a6']
        },
        'preguntas_chart': {
            'labels': ['Básico', 'Intermedio', 'Avanzado'],
            'values': [preguntas_por_nivel['1'], preguntas_por_nivel['2'], preguntas_por_nivel['3']],
            'colors': ['#2ecc71', '#f39c12', '#e74c3c']
        }
    }
    
    # 7. MÉTRICAS DE RENDIMIENTO DEL SISTEMA
    real_metrics = metrics_collector.get_performance_metrics()
    
    return {
        'total_usuarios': total_usuarios,
        'total_maestros': total_maestros,
        'total_tests': total_tests,
        'total_preguntas': total_preguntas,
        'promedio_general': promedio_general,
        'niveles_distribucion': niveles_distribucion,
        'materias_populares': materias_populares,
        'preguntas_por_nivel': preguntas_por_nivel,
        'preguntas_por_materia': preguntas_por_materia,
        'estudiantes_data': estudiantes_data,
        'charts_data': charts_data,
        'performance_metrics': {
            'avg_search_time': real_metrics.get('avg_search_time', 0),
            'avg_ai_time': real_metrics.get('avg_ai_time', 0),
            'total_requests': real_metrics.get('total_requests', 0),
            'avg_response_time': real_metrics.get('avg_response_time', 0)
        }
    }

# =====================
# FUNCIONES OPTIMIZADAS PARA GPU RTX 2050
# =====================

# =====================
# FUNCIONES AUXILIARES PARA RECOMENDACIONES
# =====================

def generar_recomendacion_respaldo(score, nivel_usado, num_falladas):
    """
    Recomendación de respaldo sin IA (instantánea)
    """
    if score >= 8:
        return f"🏆 ¡Excelente! Dominas el nivel {nivel_usado}. Considera avanzar al siguiente nivel."
    elif score >= 6:
        return f"👍 Buen trabajo en nivel {nivel_usado}. Repasa {num_falladas} temas específicos para perfeccionar."
    elif score >= 4:
        return f"📖 Progreso sólido. Dedica tiempo extra a los {num_falladas} conceptos que necesitan refuerzo."
    else:
        return f"💪 ¡No te rindas! Vuelve a estudiar los fundamentos. Práctica diaria de 20min mejorará tu rendimiento."

def _clean_data_for_json(data):
    """
    Limpia recursivamente los datos para asegurar que sean serializables JSON
    """
    import copy
    
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            cleaned[str(key)] = _clean_data_for_json(value)
        return cleaned
    elif isinstance(data, (list, tuple)):
        return [_clean_data_for_json(item) for item in data]
    elif hasattr(data, '__call__'):
        # Es una función o método, convertir a string
        return str(data)
    elif isinstance(data, (int, float, str, bool)) or data is None:
        return data
    else:
        # Cualquier otro tipo, convertir a string
        return str(data)
