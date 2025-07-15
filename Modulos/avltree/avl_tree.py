import json
import os
import random
import time
from collections import defaultdict

class AVLNode:
    def __init__(self, data):
        # Inicializa un nodo AVL con datos, punteros a hijos izquierdo y derecho y altura
        self.data = data  # Los datos almacenados en el nodo
        self.left = None  # Puntero al hijo izquierdo
        self.right = None  # Puntero al hijo derecho
        self.height = 1  # Altura del nodo (inicialmente 1)

    def update_height(self):
        # Actualiza la altura del nodo en base a las alturas de sus hijos
        left_height = self.left.height if self.left else 0  # Altura del hijo izquierdo
        right_height = self.right.height if self.right else 0  # Altura del hijo derecho
        self.height = 1 + max(left_height, right_height)  # Altura del nodo es 1 más la altura máxima de los hijos

    def balance_factor(self):
        # Calcula el factor de equilibrio del nodo
        left_height = self.left.height if self.left else 0  # Altura del hijo izquierdo
        right_height = self.right.height if self.right else 0  # Altura del hijo derecho
        return left_height - right_height  # Factor de equilibrio (altura izquierda - altura derecha)


class AVLTree:
    def __init__(self):
        # Inicializa el árbol AVL
        self.root = None  # Raíz del árbol
        self.size = 0  # Tamaño del árbol (número de nodos)
        # Índice compuesto para búsquedas ultrarrápidas
        self.composite_index = defaultdict(list)  # {(dificultad, materia): [preguntas]}
        self.difficulty_index = defaultdict(list)  # {dificultad: [preguntas]}
        self.subject_index = defaultdict(list)  # {materia: [preguntas]}
        self.all_questions = []  # Lista completa de preguntas para búsquedas rápidas

    def insert(self, data):
        # Inserta un nuevo nodo en el árbol
        if not isinstance(data, dict) or 'id' not in data:
            raise ValueError("Los datos deben ser un diccionario con un campo 'id'")  # Validación de entrada
        
        # Agregar a índices compuestos para búsquedas ultrarrápidas
        self._add_to_indexes(data)
        
        self.root = self._insert(self.root, data)  # Llama a la función recursiva de inserción
        self.size += 1  # Incrementa el tamaño del árbol

    def _add_to_indexes(self, data):
        """Agrega la pregunta a todos los índices para búsquedas O(1)"""
        dificultad = data.get('dificultad', 'medio')
        materia = data.get('materia', 'general')  # Cambio de 'subject' a 'materia'
        
        # Índice compuesto (dificultad, materia)
        composite_key = (dificultad, materia)
        self.composite_index[composite_key].append(data)
        
        # Índices individuales
        self.difficulty_index[dificultad].append(data)
        self.subject_index[materia].append(data)
        
        # Lista completa
        self.all_questions.append(data)

    def _insert(self, node, data):
        # Función recursiva para insertar un nuevo nodo
        if not node:
            new_node = AVLNode(data)  # Crea un nuevo nodo si no hay nodo
            return new_node  # Devuelve el nuevo nodo
        if data['id'] < node.data['id']:
            node.left = self._insert(node.left, data)  # Inserta en el subárbol izquierdo
        else:
            node.right = self._insert(node.right, data)  # Inserta en el subárbol derecho
        node.update_height()  # Actualiza la altura del nodo
        return self._balance(node)  # Balancea el nodo y devuelve el nodo equilibrado

    def _balance(self, node):
        # Balancea el nodo basado en el factor de equilibrio
        balance = node.balance_factor()  # Calcula el factor de equilibrio
        if balance > 1 and node.left.balance_factor() >= 0:
            return self._right_rotate(node)  # Rotación a la derecha
        if balance > 1 and node.left.balance_factor() < 0:
            node.left = self._left_rotate(node.left)  # Rotación a la izquierda en el hijo izquierdo
            return self._right_rotate(node)  # Rotación a la derecha
        if balance < -1 and node.right.balance_factor() <= 0:
            return self._left_rotate(node)  # Rotación a la izquierda
        if balance < -1 and node.right.balance_factor() > 0:
            node.right = self._right_rotate(node.right)  # Rotación a la derecha en el hijo derecho
            return self._left_rotate(node)  # Rotación a la izquierda
        return node  # Retorna el nodo si ya está balanceado

    def _left_rotate(self, z):
        # Realiza una rotación a la izquierda
        y = z.right  # Asigna el hijo derecho a y
        T2 = y.left  # Almacena el hijo izquierdo de y
        y.left = z  # El nodo z se convierte en hijo izquierdo de y
        z.right = T2  # El hijo izquierdo de y se convierte en hijo derecho de z
        z.update_height()  # Actualiza la altura de z
        y.update_height()  # Actualiza la altura de y
        return y  # Devuelve el nuevo nodo raíz

    def _right_rotate(self, z):
        # Realiza una rotación a la derecha
        y = z.left  # Asigna el hijo izquierdo a y
        T3 = y.right  # Almacena el hijo derecho de y
        y.right = z  # El nodo z se convierte en hijo derecho de y
        z.left = T3  # El hijo derecho de y se convierte en hijo izquierdo de z
        z.update_height()  # Actualiza la altura de z
        y.update_height()  # Actualiza la altura de y
        return y  # Devuelve el nuevo nodo raíz

    def _add_to_subject_index(self, node):
        # Método legacy - ahora usamos índices compuestos
        pass

    # =====================
    # MÉTODOS DE BÚSQUEDA OPTIMIZADOS
    # =====================
    
    def search_by_difficulty_and_subject(self, dificultad, materia, algorithm='composite'):
        """
        Busca preguntas por dificultad y materia usando diferentes algoritmos
        - composite: O(1) usando índice compuesto
        - binary: O(log n) usando búsqueda binaria en árbol
        - linear: O(n) recorrido lineal (para comparación)
        """
        start_time = time.time()
        
        if algorithm == 'composite':
            result = self._search_composite(dificultad, materia)
        elif algorithm == 'binary':
            result = self._search_binary(dificultad, materia)
        elif algorithm == 'linear':
            result = self._search_linear(dificultad, materia)
        else:
            raise ValueError("Algoritmo no válido. Use: 'composite', 'binary', o 'linear'")
        
        end_time = time.time()
        search_time = end_time - start_time
        
        # Registrar métrica de tiempo de búsqueda
        try:
            from ..metrics.metrics_collector import metrics_collector
            metrics_collector.record_search_time(search_time, f"avl_{algorithm}")
        except:
            pass  # Evitar errores si no se puede registrar la métrica
        
        return result
    
    def _search_composite(self, dificultad, materia):
        """Búsqueda O(1) usando índice compuesto - MÁS RÁPIDO"""
        composite_key = (dificultad, materia)
        return list(self.composite_index.get(composite_key, []))
    
    def _search_binary(self, dificultad, materia):
        """Búsqueda O(log n) + filtrado usando árbol binario"""
        # Primero buscar por dificultad en el índice
        questions_by_difficulty = self.difficulty_index.get(dificultad, [])
        # Filtrar por materia
        return [q for q in questions_by_difficulty if q.get('subject') == materia]
    
    def _search_linear(self, dificultad, materia):
        """Búsqueda O(n) recorrido lineal - MÁS LENTO (para comparación)"""
        result = []
        for question in self.all_questions:
            if (question.get('dificultad') == dificultad and 
                question.get('subject') == materia):
                result.append(question)
        return result
    
    def get_questions_for_user_level(self, materia, nivel_usuario, count=15):
        """
        Obtiene preguntas para el nivel del usuario, mezclando niveles cercanos si es necesario
        Args:
            materia: La materia de las preguntas
            nivel_usuario: El nivel del usuario (1-3)
            count: Cantidad de preguntas a devolver
        Returns:
            Lista de preguntas del nivel y niveles cercanos
        """
        preguntas = []
        
        # Primero intentar obtener del nivel exacto
        preguntas_nivel = self.search_by_difficulty_and_subject_composite(nivel_usuario, materia)
        preguntas.extend(preguntas_nivel)
        
        # Si no hay suficientes, agregar de niveles cercanos
        if len(preguntas) < count:
            # Agregar del nivel anterior si existe
            if nivel_usuario > 1:
                preguntas_anterior = self.search_by_difficulty_and_subject_composite(nivel_usuario - 1, materia)
                preguntas.extend(preguntas_anterior)
            
            # Agregar del nivel siguiente si existe
            if nivel_usuario < 3 and len(preguntas) < count:
                preguntas_siguiente = self.search_by_difficulty_and_subject_composite(nivel_usuario + 1, materia)
                preguntas.extend(preguntas_siguiente)
        
        # Eliminar duplicados manteniendo el orden
        seen = set()
        preguntas_unicas = []
        for pregunta in preguntas:
            pregunta_id = pregunta.get('id', str(pregunta))
            if pregunta_id not in seen:
                seen.add(pregunta_id)
                preguntas_unicas.append(pregunta)
        
        return preguntas_unicas[:count]

    def search_by_id(self, question_id):
        # Busca una pregunta por ID
        return self._search_by_id(self.root, question_id)  # Llama a la función recursiva de búsqueda

    def _search_by_id(self, node, question_id):
        # Función recursiva para buscar un ID
        if not node:
            return None  # Retorna None si el nodo no existe
        if question_id == node.data['id']:
            return node.data  # Retorna los datos del nodo si se encuentra el ID
        elif question_id < node.data['id']:
            return self._search_by_id(node.left, question_id)  # Busca en el subárbol izquierdo
        else:
            return self._search_by_id(node.right, question_id)  # Busca en el subárbol derecho

    def search_by_subject(self, subject):
        # Busca preguntas por materia
        questions = []  # Lista para almacenar preguntas encontradas
        self._collect_by_subject(self.root, subject, questions)  # Llama a la función recursiva de recolección
        return questions  # Retorna la lista de preguntas

    def _collect_by_subject(self, node, subject, questions):
        # Función recursiva para recopilar preguntas por materia
        if not node:
            return  # Retorna si el nodo no existe
        if subject in node.questions_by_subject:
            questions.extend(node.questions_by_subject[subject])  # Agrega preguntas de la materia
        self._collect_by_subject(node.left, subject, questions)  # Busca en el subárbol izquierdo
        self._collect_by_subject(node.right, subject, questions)  # Busca en el subárbol derecho

    def get_all_subjects(self):
        # Devuelve todas las materias disponibles en el árbol
        subjects = set()  # Conjunto para evitar duplicados
        self._collect_subjects(self.root, subjects)  # Llama a la función recursiva de recopilación
        return sorted(list(subjects))  # Retorna la lista ordenada de materias

    def _collect_subjects(self, node, subjects):
        # Función recursiva para recopilar materias
        if not node:
            return  # Retorna si el nodo no existe
        for subject in node.questions_by_subject.keys():
            subjects.add(subject)  # Agrega la materia al conjunto
        self._collect_subjects(node.left, subjects)  # Busca en el subárbol izquierdo
        self._collect_subjects(node.right, subjects)  # Busca en el subárbol derecho

    def in_order_traversal(self):
        # Realiza un recorrido en orden del árbol
        elements = []  # Lista para almacenar elementos
        self._in_order_traversal(self.root, elements)  # Llama a la función recursiva de recorrido
        return elements  # Retorna la lista de elementos

    def _in_order_traversal(self, node, elements):
        # Función recursiva para el recorrido en orden
        if node:
            self._in_order_traversal(node.left, elements)  # Visita el subárbol izquierdo
            elements.append(node.data)  # Agrega el nodo actual a la lista
            self._in_order_traversal(node.right, elements)  # Visita el subárbol derecho

    def is_balanced(self):
        # Verifica si el árbol está balanceado
        return self._check_balance(self.root) != -1  # Llama a la función recursiva de verificación

    def _check_balance(self, node):
        # Función recursiva para comprobar el balance
        if not node:
            return 0  # Retorna 0 si el nodo no existe
        left_height = self._check_balance(node.left)  # Comprueba la altura del subárbol izquierdo
        if left_height == -1:
            return -1  # Retorna -1 si el subárbol izquierdo no está balanceado
        right_height = self._check_balance(node.right)  # Comprueba la altura del subárbol derecho
        if right_height == -1:
            return -1  # Retorna -1 si el subárbol derecho no está balanceado
        if abs(left_height - right_height) > 1:
            return -1  # Retorna -1 si el nodo no está balanceado
        return max(left_height, right_height) + 1  # Retorna la altura del nodo

    # =====================
    # MÉTODOS DE BÚSQUEDA CON NOMBRES ESPECÍFICOS PARA COMPATIBILIDAD
    # =====================
    
    def search_by_difficulty_and_subject_composite(self, dificultad, materia):
        """Búsqueda ultrarrápida O(1) usando índice compuesto"""
        return self._search_composite(dificultad, materia)
    
    def search_by_difficulty_and_subject_binary(self, dificultad, materia):
        """Búsqueda O(log n) usando búsqueda binaria"""
        return self._search_binary(dificultad, materia)
    
    def search_by_difficulty_and_subject_linear(self, dificultad, materia):
        """Búsqueda O(n) lineal para comparación de rendimiento"""
        return self._search_linear(dificultad, materia)
    
    def get_questions_for_user_level(self, materia, nivel_usuario, count=15):
        """
        Obtiene preguntas para el nivel del usuario, mezclando niveles cercanos si es necesario
        Args:
            materia: La materia de las preguntas
            nivel_usuario: El nivel del usuario (1-3)
            count: Cantidad de preguntas a devolver
        Returns:
            Lista de preguntas del nivel y niveles cercanos
        """
        preguntas = []
        
        # Primero intentar obtener del nivel exacto
        preguntas_nivel = self.search_by_difficulty_and_subject_composite(nivel_usuario, materia)
        preguntas.extend(preguntas_nivel)
        
        # Si no hay suficientes, agregar de niveles cercanos
        if len(preguntas) < count:
            # Agregar del nivel anterior si existe
            if nivel_usuario > 1:
                preguntas_anterior = self.search_by_difficulty_and_subject_composite(nivel_usuario - 1, materia)
                preguntas.extend(preguntas_anterior)
            
            # Agregar del nivel siguiente si existe
            if nivel_usuario < 3 and len(preguntas) < count:
                preguntas_siguiente = self.search_by_difficulty_and_subject_composite(nivel_usuario + 1, materia)
                preguntas.extend(preguntas_siguiente)
        
        # Eliminar duplicados manteniendo el orden
        seen = set()
        preguntas_unicas = []
        for pregunta in preguntas:
            pregunta_id = pregunta.get('id', str(pregunta))
            if pregunta_id not in seen:
                seen.add(pregunta_id)
                preguntas_unicas.append(pregunta)
        
        return preguntas_unicas[:count]


def merge_sort(arr, key='id'):
    # Implementa el algoritmo de ordenamiento por mezcla (merge sort)
    if len(arr) <= 1:
        return arr  # Retorna si el arreglo tiene 1 o menos elementos
    mid = len(arr) // 2  # Encuentra el punto medio
    left_half = arr[:mid]  # Divide el arreglo en la mitad izquierda
    right_half = arr[mid:]  # Divide el arreglo en la mitad derecha
    left_sorted = merge_sort(left_half, key)  # Ordena la mitad izquierda
    right_sorted = merge_sort(right_half, key)  # Ordena la mitad derecha
    return _merge(left_sorted, right_sorted, key)  # Combina las dos mitades ordenadas


def _merge(left, right, key):
    # Combina dos listas ordenadas en una lista ordenada
    merged = []  # Lista para almacenar la combinación
    left_idx = right_idx = 0  # Índices para ambas listas
    while left_idx < len(left) and right_idx < len(right):
        if left[left_idx][key] < right[right_idx][key]:
            merged.append(left[left_idx])  # Agrega el elemento de la izquierda
            left_idx += 1  # Incrementa el índice izquierdo
        else:
            merged.append(right[right_idx])  # Agrega el elemento de la derecha
            right_idx += 1  # Incrementa el índice derecho
    merged.extend(left[left_idx:])  # Agrega los elementos restantes de la izquierda
    merged.extend(right[right_idx:])  # Agrega los elementos restantes de la derecha
    return merged  # Retorna la lista combinada


def binary_search(sorted_list, target, key='id'):
    # Implementa la búsqueda binaria en una lista ordenada
    low = 0  # Índice inferior
    high = len(sorted_list) - 1  # Índice superior
    while low <= high:
        mid = (low + high) // 2  # Encuentra el índice medio
        mid_val = sorted_list[mid][key]  # Valor del medio
        if mid_val < target:
            low = mid + 1  # Busca en la mitad superior
        elif mid_val > target:
            high = mid - 1  # Busca en la mitad inferior
        else:
            return mid  # Retorna el índice si se encuentra el objetivo
    return -1  # Retorna -1 si no se encuentra el objetivo


def sort_and_search_demo(questions):
    # Demuestra la ordenación y búsqueda
    if not questions:
        print("Lista de preguntas vacia")  # Mensaje si la lista está vacía
        return None
    print("\nAntes de ordenar:")
    for q in questions[:5]:
        print(f"ID: {q['id']}, Pregunta: {q['question'][:30]}...")  # Muestra las primeras 5 preguntas
    sorted_questions = merge_sort(questions)  # Ordena las preguntas
    print("\nDespues de ordenar:")
    for q in sorted_questions[:5]:
        print(f"ID: {q['id']}, Pregunta: {q['question'][:30]}...")  # Muestra las primeras 5 preguntas ordenadas
    target_id = sorted_questions[len(sorted_questions)//2]['id']  # Selecciona un ID objetivo
    print(f"\nBuscando pregunta con ID: {target_id}")
    result_idx = binary_search(sorted_questions, target_id)  # Realiza la búsqueda binaria
    if result_idx != -1:
        found = sorted_questions[result_idx]  # Encuentra la pregunta
        print(f"Pregunta encontrada: {found['question']}")  # Imprime la pregunta encontrada
        return found  # Retorna la pregunta encontrada
    else:
        print("Pregunta no encontrada")  # Mensaje si no se encuentra la pregunta
        return None


def cargar_preguntas(archivo, materia):
    """Carga preguntas desde un archivo JSON y las prepara para insertar en el árbol AVL.
    Genera IDs secuenciales comenzando desde 1 para cada materia.
    
    Args:
        archivo (str): Ruta al archivo JSON con las preguntas.
        materia (str): Nombre de la materia a la que pertenecen las preguntas.
        
    Returns:
        List[Dict]: Lista de diccionarios con los datos de las preguntas.
    """
    if not os.path.exists(archivo):
        logging.error(f"Archivo {archivo} no encontrado")
        return []
        
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            preguntas_json = json.load(f)  # Carga el archivo JSON completo
            
        questions = []  # Lista para almacenar las preguntas procesadas
        
        # Procesa cada pregunta del archivo JSON
        for i, pregunta in enumerate(preguntas_json.get('preguntas', []), start=1):
            try:
                # Genera un ID secuencial simple
                unique_id = i  # ID secuencial basado en la posición en la lista
                
                # Estructura los datos de la pregunta
                question_data = {
                    'id': unique_id,  # ID secuencial generado
                    'numero': pregunta['numero'],  # Número original de la pregunta
                    'question': pregunta['pregunta'],  # Texto de la pregunta
                    'answer': pregunta['respuesta_correcta'],  # Respuesta correcta
                    'subject': materia,  # Materia a la que pertenece
                    'options': pregunta['opciones'],  # Lista de opciones de respuesta
                    'feedback': pregunta.get('retroalimentacion', ''),  # Retroalimentación (si existe)
                    'explanation': pregunta.get('justificacion', '')  # Justificación (si existe)
                }
                questions.append(question_data)  # Agrega la pregunta a la lista
                
            except KeyError as e:
                print(f"Error en pregunta {i}: Falta campo {e}")
                continue
                
        return questions  # Devuelve la lista de preguntas procesadas
        
    except json.JSONDecodeError:
        print(f"Error al leer el archivo {archivo}")
        return []


# =====================
# ÁRBOL AVL PARA ESTUDIANTES
# =====================

class StudentAVLNode:
    def __init__(self, student_data):
        self.data = student_data  # Datos del estudiante (email, nombre, promedio, etc.)
        self.left = None
        self.right = None
        self.height = 1

    def update_height(self):
        left_height = self.left.height if self.left else 0
        right_height = self.right.height if self.right else 0
        self.height = 1 + max(left_height, right_height)

    def balance_factor(self):
        left_height = self.left.height if self.left else 0
        right_height = self.right.height if self.right else 0
        return left_height - right_height


class StudentAVLTree:
    def __init__(self):
        self.root = None
        self.size = 0
        self.students_by_average = []  # Lista ordenada por promedio para ranking rápido

    def insert_student(self, student_data):
        """Inserta un estudiante en el árbol ordenado por promedio general"""
        if not isinstance(student_data, dict) or 'email' not in student_data:
            raise ValueError("Los datos deben ser un diccionario con campo 'email'")
        
        # Asegurar que tenga promedio
        if 'promedio_general' not in student_data:
            student_data['promedio_general'] = 0.0
            
        self.root = self._insert_student(self.root, student_data)
        self.size += 1
        self._update_ranking_list()

    def _insert_student(self, node, student_data):
        if not node:
            return StudentAVLNode(student_data)
        
        # Ordenar por promedio (mayor primero)
        if student_data['promedio_general'] > node.data['promedio_general']:
            node.left = self._insert_student(node.left, student_data)
        else:
            node.right = self._insert_student(node.right, student_data)
        
        node.update_height()
        return self._balance_student(node)

    def _balance_student(self, node):
        balance = node.balance_factor()
        
        # Rotaciones para mantener equilibrio
        if balance > 1 and node.left.balance_factor() >= 0:
            return self._right_rotate_student(node)
        if balance > 1 and node.left.balance_factor() < 0:
            node.left = self._left_rotate_student(node.left)
            return self._right_rotate_student(node)
        if balance < -1 and node.right.balance_factor() <= 0:
            return self._left_rotate_student(node)
        if balance < -1 and node.right.balance_factor() > 0:
            node.right = self._right_rotate_student(node.right)
            return self._left_rotate_student(node)
        
        return node

    def _left_rotate_student(self, z):
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        z.update_height()
        y.update_height()
        return y

    def _right_rotate_student(self, z):
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        z.update_height()
        y.update_height()
        return y

    def _update_ranking_list(self):
        """Actualiza la lista de estudiantes ordenada por promedio"""
        self.students_by_average = []
        self._collect_students_inorder(self.root)
        # Ordenar por promedio descendente
        self.students_by_average.sort(key=lambda x: x['promedio_general'], reverse=True)

    def _collect_students_inorder(self, node):
        if node:
            self._collect_students_inorder(node.left)
            self.students_by_average.append(node.data)
            self._collect_students_inorder(node.right)

    def get_top_students(self, limit=10):
        """Obtiene el ranking de los mejores estudiantes - O(1) después de actualización"""
        return self.students_by_average[:limit]

    def search_student_by_email(self, email):
        """Busca un estudiante específico por email"""
        return self._search_student_by_email(self.root, email)

    def _search_student_by_email(self, node, email):
        if not node:
            return None
        if email == node.data['email']:
            return node.data
        
        # Buscar en ambos subárboles ya que no están ordenados por email
        left_result = self._search_student_by_email(node.left, email)
        if left_result:
            return left_result
        return self._search_student_by_email(node.right, email)

    def update_student_average(self, email, new_average):
        """Actualiza el promedio de un estudiante y reordena el árbol"""
        # Primero buscar y remover el estudiante
        student = self.search_student_by_email(email)
        if student:
            # Actualizar promedio
            student['promedio_general'] = new_average
            # Necesitaríamos reimplementar remove para AVL, por simplicidad recreamos
            self._update_ranking_list()
            return True
        return False