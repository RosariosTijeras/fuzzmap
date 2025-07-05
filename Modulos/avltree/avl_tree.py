import json
import hashlib
import os

class AVLNode:
    def __init__(self, data):
        # Inicializa un nodo AVL con datos, punteros a hijos izquierdo y derecho y altura
        self.data = data  # Los datos almacenados en el nodo
        self.left = None  # Puntero al hijo izquierdo
        self.right = None  # Puntero al hijo derecho
        self.height = 1  # Altura del nodo (inicialmente 1)
        self.questions_by_subject = {}  # Diccionario para almacenar preguntas por materia

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

    def insert(self, data):
        # Inserta un nuevo nodo en el árbol
        if not isinstance(data, dict) or 'id' not in data:
            raise ValueError("Los datos deben ser un diccionario con un campo 'id'")  # Validación de entrada
        self.root = self._insert(self.root, data)  # Llama a la función recursiva de inserción
        self.size += 1  # Incrementa el tamaño del árbol

    def _insert(self, node, data):
        # Función recursiva para insertar un nuevo nodo
        if not node:
            new_node = AVLNode(data)  # Crea un nuevo nodo si no hay nodo
            self._add_to_subject_index(new_node)  # Agrega el nodo al índice de materias
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
        # Agrega el nodo al índice de preguntas por materia
        subject = node.data.get('subject', 'general')  # Obtiene la materia del nodo
        if subject not in node.questions_by_subject:
            node.questions_by_subject[subject] = []  # Crea una lista si la materia no existe
        node.questions_by_subject[subject].append(node.data)  # Agrega la pregunta a la lista de la materia

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
        print(f"Archivo {archivo} no encontrado")
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


if __name__ == '__main__':
    avl = AVLTree()  # Crea una instancia del árbol AVL
    
    # Carga preguntas de los archivos proporcionados
    preguntas_habilidades = cargar_preguntas('habilidades_vida_ordenado_completado.json', 'Habilidades_Vida')
    preguntas_ciencia = cargar_preguntas('ciencia_datos_ordenado_completado.json', 'Ciencia_Datos')
    
    # Inserta todas las preguntas en el árbol AVL
    for q in preguntas_habilidades + preguntas_ciencia:
        avl.insert(q)
    
    print("=== DEMOSTRACION ARBOL AVL ===")
    print(f"Total preguntas insertadas: {avl.size}")  # Muestra el total de preguntas insertadas
    print(f"¿El arbol esta balanceado?: {'Si' if avl.is_balanced() else 'No'}")  # Verifica el balance del árbol
    print("\nMaterias disponibles:", avl.get_all_subjects())  # Muestra las materias disponibles
    
    # Muestra preguntas por materia
    for materia in avl.get_all_subjects():
        print(f"\n=== PREGUNTAS DE {materia.upper()} ===")
        preguntas_materia = avl.search_by_subject(materia)  # Obtiene preguntas de la materia
        print(f"Total: {len(preguntas_materia)} preguntas")  # Muestra el total de preguntas
        for q in preguntas_materia[:3]:  # Muestra solo las primeras 3 preguntas por brevedad
            print(f"\nID {q['id']}: {q['question']}")  # Muestra la ID y pregunta
            print("Opciones:")
            for opcion in q['options']:
                print(f" - {opcion}")  # Muestra las opciones
            print(f"Respuesta correcta: {q['answer']}")  # Muestra la respuesta correcta

            if q.get('feedback'):
                print(f"\nRetroalimentación: {q['feedback']}")

            if q.get('explanation'):
                print(f"\nExplicación: {q['explanation']}")

            print("-" * 50)
    
    print("\n=== BUSQUEDA POR ID ===")
    target_id = preguntas_habilidades[0]['id'] if preguntas_habilidades else 1  # Usa el ID de la primera pregunta
    print(f"Buscando pregunta con ID {target_id}:")
    found = avl.search_by_id(target_id)  # Busca la pregunta por ID
    if found:
        print(f"Materia: {found['subject']}")  # Muestra la materia de la pregunta
        print(f"Pregunta: {found['question']}")  # Muestra la pregunta
        print(f"Respuesta: {found['answer']}")  # Muestra la respuesta
    else:
        print("Pregunta no encontrada")  # Mensaje si no se encuentra la pregunta
    
    print("\n=== DEMOSTRACION ALGORITMOS ===")
    sort_and_search_demo(preguntas_habilidades + preguntas_ciencia)  # Demuestra la ordenación y búsqueda