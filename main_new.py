"""
=======================================================================================
FUZZMAP - SISTEMA UNIFICADO DE EXÁMENES UNIVERSITARIOS
=======================================================================================

Aplicación moderna para exámenes universitarios con:
- Árbol AVL para preguntas con índices compuestos
- Ranking de estudiantes con AVL
- Selección automática de dificultad basada en rendimiento
- Dashboard moderno con visualizaciones interactivas
- Sistema de recomendaciones con lógica difusa

Autores: Mario Camacho y equipo
Universidad: UNACH
Fecha: 2025
"""

from flask import Flask, session, redirect, url_for
from Modulos.ui.app import ui, markdown_to_html
from Modulos.avltree.avl_tree import AVLTree
from Modulos.avltree.student_avl import StudentAVLTree
from datetime import timedelta
import json
import os
import time

# =====================
# CONFIGURACIÓN DE LA APLICACIÓN FLASK
# =====================
app = Flask(__name__)
app.secret_key = 'fuzzmap_unach_2025_sistema_examenes_avl'
app.permanent_session_lifetime = timedelta(hours=24)  # 24 horas

# Registrar filtros y blueprints
app.add_template_filter(markdown_to_html)
app.register_blueprint(ui, url_prefix='/')

# =====================
# VARIABLES GLOBALES PARA LOS ÁRBOLES AVL
# =====================
questions_tree = AVLTree()
students_tree = StudentAVLTree()

def load_all_questions():
    """
    Carga todas las preguntas al árbol AVL al iniciar la aplicación.
    Esto permite comparar eficiencia de algoritmos de búsqueda.
    """
    print("🔄 Cargando todas las preguntas en el árbol AVL...")
    start_time = time.time()
    total_questions = 0
    
    # Directorio base de datos
    data_dir = "Datos"
    
    # Cargar preguntas de Ciencia de Datos
    cd_file = os.path.join(data_dir, "Ciencia_Datos", "banco_preguntas", "bancodepreguntas_global_cienciadatos.json")
    if os.path.exists(cd_file):
        try:
            with open(cd_file, 'r', encoding='utf-8') as f:
                cd_questions = json.load(f)
                for question in cd_questions:
                    if isinstance(question, dict) and 'id' in question:
                        # Asegurar que tenga materia
                        question['materia'] = question.get('materia', 'Ciencia_Datos')
                        questions_tree.insert(question)
                        total_questions += 1
            print(f"✅ Cargadas {len(cd_questions)} preguntas de Ciencia de Datos")
        except Exception as e:
            print(f"❌ Error cargando preguntas de Ciencia de Datos: {e}")
    
    # Cargar preguntas de Habilidades para la Vida
    hv_file = os.path.join(data_dir, "Habilidades_Vida", "banco_preguntas", "bancodepreguntas_global_habilidadesvida.json")
    if os.path.exists(hv_file):
        try:
            with open(hv_file, 'r', encoding='utf-8') as f:
                hv_questions = json.load(f)
                for question in hv_questions:
                    if isinstance(question, dict) and 'id' in question:
                        # Asegurar que tenga materia
                        question['materia'] = question.get('materia', 'Habilidades_Vida')
                        questions_tree.insert(question)
                        total_questions += 1
            print(f"✅ Cargadas {len(hv_questions)} preguntas de Habilidades para la Vida")
        except Exception as e:
            print(f"❌ Error cargando preguntas de Habilidades para la Vida: {e}")
    
    end_time = time.time()
    load_time = round(end_time - start_time, 3)
    
    print(f"🎯 Total de preguntas cargadas: {total_questions}")
    print(f"⚡ Tiempo de carga: {load_time} segundos")
    print(f"📊 Estadísticas del árbol AVL:")
    print(f"   - Tamaño del árbol: {questions_tree.size}")
    print(f"   - Preguntas en índice compuesto: {len(questions_tree.all_questions)}")
    print(f"   - Materias disponibles: {list(questions_tree.subject_index.keys())}")
    
    return total_questions

def load_all_students():
    """Carga todos los estudiantes en el árbol AVL de estudiantes"""
    print("👥 Cargando estudiantes en el árbol AVL...")
    start_time = time.time()
    
    students_tree.load_all_students()
    
    end_time = time.time()
    load_time = round(end_time - start_time, 3)
    
    print(f"✅ Estudiantes cargados: {students_tree.size}")
    print(f"⚡ Tiempo de carga: {load_time} segundos")
    
    # Mostrar top 5 estudiantes
    top_students = students_tree.get_top_students(5)
    if top_students:
        print("🏆 Top 5 estudiantes:")
        for i, student in enumerate(top_students, 1):
            print(f"   {i}. {student['nombre']} {student['apellido']} - Promedio: {student['promedio_general']}")

def compare_search_algorithms():
    """
    Compara la eficiencia de los algoritmos de búsqueda implementados.
    Esto demuestra la superioridad del índice compuesto.
    """
    print("\n🔍 COMPARANDO ALGORITMOS DE BÚSQUEDA")
    print("=" * 50)
    
    if questions_tree.size == 0:
        print("❌ No hay preguntas cargadas para comparar")
        return
    
    # Parámetros de prueba
    dificultad = "Intermedio"
    materia = "Ciencia_Datos"
    num_searches = 1000
    
    print(f"Parámetros de prueba:")
    print(f"  - Dificultad: {dificultad}")
    print(f"  - Materia: {materia}")
    print(f"  - Número de búsquedas: {num_searches}")
    print()
    
    # 1. Búsqueda con índice compuesto (O(1))
    start_time = time.time()
    for _ in range(num_searches):
        result_composite = questions_tree.search_by_difficulty_and_subject_composite(dificultad, materia)
    end_time = time.time()
    composite_time = end_time - start_time
    
    # 2. Búsqueda binaria (O(log n))
    start_time = time.time()
    for _ in range(num_searches):
        result_binary = questions_tree.search_by_difficulty_and_subject_binary(dificultad, materia)
    end_time = time.time()
    binary_time = end_time - start_time
    
    # 3. Búsqueda lineal (O(n))
    start_time = time.time()
    for _ in range(num_searches):
        result_linear = questions_tree.search_by_difficulty_and_subject_linear(dificultad, materia)
    end_time = time.time()
    linear_time = end_time - start_time
    
    # Mostrar resultados
    print("RESULTADOS DE EFICIENCIA:")
    print(f"🚀 Índice Compuesto (O(1)): {composite_time:.6f} segundos")
    print(f"🔍 Búsqueda Binaria (O(log n)): {binary_time:.6f} segundos")
    print(f"🐌 Búsqueda Lineal (O(n)): {linear_time:.6f} segundos")
    print()
    print("MEJORA DE RENDIMIENTO:")
    if composite_time > 0:
        print(f"📈 El índice compuesto es {binary_time/composite_time:.1f}x más rápido que la búsqueda binaria")
        print(f"📈 El índice compuesto es {linear_time/composite_time:.1f}x más rápido que la búsqueda lineal")
    
    # Verificar que todos devuelven los mismos resultados
    print(f"\n✅ Verificación de consistencia:")
    print(f"   - Resultados compuesto: {len(result_composite) if result_composite else 0}")
    print(f"   - Resultados binarios: {len(result_binary) if result_binary else 0}")
    print(f"   - Resultados lineales: {len(result_linear) if result_linear else 0}")

def initialize_system():
    """Inicializa todo el sistema: carga preguntas, estudiantes y hace comparaciones"""
    print("🚀 INICIANDO SISTEMA FUZZMAP")
    print("=" * 50)
    
    # Cargar preguntas
    total_questions = load_all_questions()
    
    # Cargar estudiantes
    load_all_students()
    
    # Comparar algoritmos si hay preguntas
    if total_questions > 0:
        compare_search_algorithms()
    
    print("\n✅ SISTEMA INICIALIZADO CORRECTAMENTE")
    print("🌐 Aplicación lista en: http://localhost:5000")
    print("=" * 50)

# =====================
# HACER LOS ÁRBOLES DISPONIBLES GLOBALMENTE
# =====================
app.config['QUESTIONS_TREE'] = questions_tree
app.config['STUDENTS_TREE'] = students_tree

# =====================
# RUTA RAÍZ DEL SISTEMA
# =====================
@app.route('/')
def index():
    if 'user' in session:
        # Usuario autenticado: ir al dashboard
        if session['user'] == 'admin@unach.edu.ec':
            return redirect(url_for('ui.admin_dashboard'))
        else:
            return redirect(url_for('ui.dashboard'))
    else:
        # Usuario no autenticado: ir al login
        return redirect(url_for('ui.login'))

# =====================
# INICIO DEL SERVIDOR FLASK
# =====================
if __name__ == '__main__':
    # Inicializar sistema al arrancar
    initialize_system()
    
    # Ejecutar la aplicación Flask
    app.run(debug=True, host='0.0.0.0', port=5000)
