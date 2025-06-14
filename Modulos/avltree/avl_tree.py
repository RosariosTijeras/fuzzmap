"""
Implementacion de estructuras de datos para FuzzMap

Este modulo contiene:
1. Implementacion completa de un Arbol AVL para almacenar y organizar preguntas
2. Algoritmos de ordenamiento (Merge Sort) y busqueda (Binary Search)
3. Funciones auxiliares para manejo de datos educativos
"""

## ----------------------------
## Clase AVLNode
## ----------------------------

class AVLNode:
    """
    Representa un nodo en el arbol AVL.
    
    Atributos:
        data (dict): Diccionario con los datos de la pregunta (id, pregunta, respuesta, materia)
        left (AVLNode): Hijo izquierdo del nodo
        right (AVLNode): Hijo derecho del nodo
        height (int): Altura del nodo en el arbol
        questions_by_subject (dict): Indice secundario que agrupa preguntas por materia
    """
    
    def __init__(self, data):
        """
        Inicializa un nuevo nodo AVL.
        
        Args:
            data (dict): Datos de la pregunta a almacenar en el nodo
        """
        self.data = data  # Diccionario con los datos de la pregunta
        self.left = None  # Referencia al hijo izquierdo
        self.right = None  # Referencia al hijo derecho
        self.height = 1   # Altura inicial del nodo (1 para nodos hoja)
        self.questions_by_subject = {}  # Indice de preguntas por materia

    def update_height(self):
        """
        Actualiza la altura del nodo basandose en las alturas de sus hijos.
        
        La altura de un nodo es 1 + la maxima altura entre sus dos hijos.
        Se llama automaticamente despues de inserciones o rotaciones.
        """
        left_height = self.left.height if self.left else 0
        right_height = self.right.height if self.right else 0
        self.height = 1 + max(left_height, right_height)

    def balance_factor(self):
        """
        Calcula el factor de balanceo del nodo.
        
        Returns:
            int: Diferencia entre altura del subarbol izquierdo y derecho
                 Valores positivos indican mas peso a la izquierda
                 Valores negativos indican mas peso a la derecha
        """
        left_height = self.left.height if self.left else 0
        right_height = self.right.height if self.right else 0
        return left_height - right_height


## ----------------------------
## Clase AVLTree
## ----------------------------

class AVLTree:
    """
    Implementacion del arbol AVL auto-balanceado para almacenar preguntas.
    
    El arbol mantiene las preguntas ordenadas por ID y proporciona:
    - Insercion balanceada O(log n)
    - Busqueda eficiente por ID o materia
    - Recuperacion de todas las materias disponibles
    """
    
    def __init__(self):
        """
        Inicializa un arbol AVL vacio.
        """
        self.root = None  # Raiz del arbol
        self.size = 0     # Contador de nodos en el arbol

    def insert(self, data):
        """
        Inserta una nueva pregunta en el arbol manteniendo el balance.
        
        Args:
            data (dict): Datos de la pregunta a insertar. Debe contener:
                        - id: Identificador unico (int)
                        - question: Texto de la pregunta (str)
                        - answer: Texto de la respuesta (str)
                        - subject: Materia de la pregunta (str)
        
        Raises:
            ValueError: Si los datos no tienen el formato correcto
        """
        if not isinstance(data, dict) or 'id' not in data:
            raise ValueError("Los datos deben ser un diccionario con un campo 'id'")

        self.root = self._insert(self.root, data)
        self.size += 1

    def _insert(self, node, data):
        """
        Metodo interno recursivo para insertar un nodo.
        
        Args:
            node (AVLNode): Nodo actual en la recursion
            data (dict): Datos a insertar
            
        Returns:
            AVLNode: El nodo (posiblemente nuevo) despues de la insercion
        """
        # Caso base: llegamos a una hoja, creamos nuevo nodo
        if not node:
            new_node = AVLNode(data)
            self._add_to_subject_index(new_node)
            return new_node

        # Insercion en subarbol izquierdo o derecho segun ID
        if data['id'] < node.data['id']:
            node.left = self._insert(node.left, data)
        else:
            node.right = self._insert(node.right, data)

        # Actualizar altura y balancear
        node.update_height()
        return self._balance(node)

    def _balance(self, node):
        """
        Balancea el arbol si es necesario despues de una insercion.
        
        Args:
            node (AVLNode): Nodo a balancear
            
        Returns:
            AVLNode: Nodo balanceado
        """
        balance = node.balance_factor()

        # Caso Left Left (rotacion simple derecha)
        if balance > 1 and node.left.balance_factor() >= 0:
            return self._right_rotate(node)

        # Caso Left Right (rotacion izquierda-derecha)
        if balance > 1 and node.left.balance_factor() < 0:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)

        # Caso Right Right (rotacion simple izquierda)
        if balance < -1 and node.right.balance_factor() <= 0:
            return self._left_rotate(node)

        # Caso Right Left (rotacion derecha-izquierda)
        if balance < -1 and node.right.balance_factor() > 0:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node

    def _left_rotate(self, z):
        """
        Realiza una rotacion izquierda sobre el nodo z.
        
        Args:
            z (AVLNode): Nodo desbalanceado
            
        Returns:
            AVLNode: Nueva raiz del subarbol
        """
        y = z.right
        T2 = y.left

        # Realizar rotacion
        y.left = z
        z.right = T2

        # Actualizar alturas (z primero porque ahora esta por debajo de y)
        z.update_height()
        y.update_height()

        return y

    def _right_rotate(self, z):
        """
        Realiza una rotacion derecha sobre el nodo z.
        
        Args:
            z (AVLNode): Nodo desbalanceado
            
        Returns:
            AVLNode: Nueva raiz del subarbol
        """
        y = z.left
        T3 = y.right

        # Realizar rotacion
        y.right = z
        z.left = T3

        # Actualizar alturas
        z.update_height()
        y.update_height()

        return y

    def _add_to_subject_index(self, node):
        """
        Agrega la pregunta al indice secundario por materia.
        
        Args:
            node (AVLNode): Nodo que contiene la pregunta a indexar
        """
        subject = node.data.get('subject', 'general')
        if subject not in node.questions_by_subject:
            node.questions_by_subject[subject] = []
        node.questions_by_subject[subject].append(node.data)

    def search_by_id(self, question_id):
        """
        Busca una pregunta por su ID.
        
        Args:
            question_id (int): ID de la pregunta a buscar
            
        Returns:
            dict: Datos de la pregunta si se encuentra, None en caso contrario
        """
        return self._search_by_id(self.root, question_id)

    def _search_by_id(self, node, question_id):
        """
        Busqueda recursiva por ID en el arbol.
        
        Args:
            node (AVLNode): Nodo actual en la recursion
            question_id (int): ID a buscar
            
        Returns:
            dict: Datos de la pregunta o None
        """
        if not node:
            return None

        if question_id == node.data['id']:
            return node.data
        elif question_id < node.data['id']:
            return self._search_by_id(node.left, question_id)
        else:
            return self._search_by_id(node.right, question_id)

    def search_by_subject(self, subject):
        """
        Obtiene todas las preguntas de una materia especifica.
        
        Args:
            subject (str): Nombre de la materia a buscar
            
        Returns:
            list: Lista de preguntas (diccionarios) de esa materia
        """
        questions = []
        self._collect_by_subject(self.root, subject, questions)
        return questions

    def _collect_by_subject(self, node, subject, questions):
        """
        Recorre el arbol recolectando preguntas de una materia.
        
        Args:
            node (AVLNode): Nodo actual en la recursion
            subject (str): Materia a buscar
            questions (list): Acumulador de resultados
        """
        if not node:
            return

        # Buscar en el indice de materias del nodo actual
        if subject in node.questions_by_subject:
            questions.extend(node.questions_by_subject[subject])

        # Recorrer los hijos
        self._collect_by_subject(node.left, subject, questions)
        self._collect_by_subject(node.right, subject, questions)

    def get_all_subjects(self):
        """
        Obtiene una lista de todas las materias disponibles.
        
        Returns:
            list: Lista ordenada de nombres de materias (str)
        """
        subjects = set()
        self._collect_subjects(self.root, subjects)
        return sorted(list(subjects))

    def _collect_subjects(self, node, subjects):
        """
        Recorre el arbol recolectando todas las materias.
        
        Args:
            node (AVLNode): Nodo actual en la recursion
            subjects (set): Conjunto acumulador de materias
        """
        if not node:
            return

        # Agregar materias del nodo actual
        for subject in node.questions_by_subject.keys():
            subjects.add(subject)

        # Recorrer los hijos
        self._collect_subjects(node.left, subjects)
        self._collect_subjects(node.right, subjects)

    def in_order_traversal(self):
        """
        Realiza un recorrido in-order del arbol (para debugging).
        
        Returns:
            list: Lista ordenada de todos los datos en el arbol
        """
        elements = []
        self._in_order_traversal(self.root, elements)
        return elements

    def _in_order_traversal(self, node, elements):
        """
        Recorrido in-order recursivo.
        
        Args:
            node (AVLNode): Nodo actual
            elements (list): Acumulador de resultados
        """
        if node:
            self._in_order_traversal(node.left, elements)
            elements.append(node.data)
            self._in_order_traversal(node.right, elements)

    def is_balanced(self):
        """
        Verifica si el arbol esta balanceado.
        
        Returns:
            bool: True si el arbol esta balanceado, False si no
        """
        return self._check_balance(self.root) != -1

    def _check_balance(self, node):
        """
        Metodo auxiliar recursivo para verificar balance.
        
        Args:
            node (AVLNode): Nodo actual
            
        Returns:
            int: Altura del subarbol si esta balanceado, -1 si no
        """
        if not node:
            return 0

        left_height = self._check_balance(node.left)
        if left_height == -1:
            return -1

        right_height = self._check_balance(node.right)
        if right_height == -1:
            return -1

        if abs(left_height - right_height) > 1:
            return -1

        return max(left_height, right_height) + 1


## ----------------------------
## Algoritmos de Ordenamiento y Busqueda
## ----------------------------

def merge_sort(arr, key='id'):
    """
    Implementacion del algoritmo Merge Sort para ordenar listas de preguntas.
    
    Args:
        arr (list): Lista a ordenar
        key (str): Clave del diccionario por la que ordenar (default: 'id')
        
    Returns:
        list: Lista ordenada
    """
    if len(arr) <= 1:
        return arr

    # Dividir
    mid = len(arr) // 2
    left_half = arr[:mid]
    right_half = arr[mid:]

    # Ordenar recursivamente
    left_sorted = merge_sort(left_half, key)
    right_sorted = merge_sort(right_half, key)

    # Combinar
    return _merge(left_sorted, right_sorted, key)

def _merge(left, right, key):
    """
    Funcion auxiliar para combinar dos listas ordenadas.
    
    Args:
        left (list): Mitad izquierda ordenada
        right (list): Mitad derecha ordenada
        key (str): Clave por la que ordenar
        
    Returns:
        list: Lista combinada y ordenada
    """
    merged = []
    left_idx = right_idx = 0

    while left_idx < len(left) and right_idx < len(right):
        if left[left_idx][key] < right[right_idx][key]:
            merged.append(left[left_idx])
            left_idx += 1
        else:
            merged.append(right[right_idx])
            right_idx += 1

    # Agregar elementos restantes
    merged.extend(left[left_idx:])
    merged.extend(right[right_idx:])

    return merged

def binary_search(sorted_list, target, key='id'):
    """
    Implementacion de busqueda binaria en listas ordenadas.
    
    Args:
        sorted_list (list): Lista ordenada donde buscar
        target: Valor a buscar
        key (str): Clave del diccionario donde buscar (default: 'id')
        
    Returns:
        int: Indice del elemento encontrado, -1 si no se encuentra
    """
    low = 0
    high = len(sorted_list) - 1

    while low <= high:
        mid = (low + high) // 2
        mid_val = sorted_list[mid][key]

        if mid_val < target:
            low = mid + 1
        elif mid_val > target:
            high = mid - 1
        else:
            return mid

    return -1

def sort_and_search_demo(questions):
    """
    Demostracion del uso combinado de Merge Sort y Binary Search.
    
    Args:
        questions (list): Lista de preguntas a procesar
        
    Returns:
        dict: Pregunta encontrada (en la demostracion) o None
    """
    if not questions:
        print("Lista de preguntas vacia")
        return None

    print("\nAntes de ordenar:")
    for q in questions[:5]:
        print(f"ID: {q['id']}, Pregunta: {q['question'][:30]}...")

    # Ordenar
    sorted_questions = merge_sort(questions)
    
    print("\nDespues de ordenar:")
    for q in sorted_questions[:5]:
        print(f"ID: {q['id']}, Pregunta: {q['question'][:30]}...")

    # Buscar
    target_id = sorted_questions[len(sorted_questions)//2]['id']
    print(f"\nBuscando pregunta con ID: {target_id}")
    
    result_idx = binary_search(sorted_questions, target_id)
    
    if result_idx != -1:
        found = sorted_questions[result_idx]
        print(f"Pregunta encontrada: {found['question']}")
        return found
    else:
        print("Pregunta no encontrada")
        return None


## ----------------------------
## Ejemplo de Uso
## ----------------------------

if __name__ == '__main__':
    import json
    
    # Crear arbol AVL
    avl = AVLTree()
    
    # Cargar preguntas desde el JSON
    with open('preguntas_generadas_habilidades_vida.json', 'r', encoding='utf-8') as f:
        preguntas_json = json.load(f)
    
    # Convertir el formato JSON al formato esperado por nuestro AVL
    questions = []
    for i, pregunta in enumerate(preguntas_json):
        question_data = {
            'id': i + 1,  # Asignamos un ID numérico secuencial
            'question': pregunta['pregunta'],
            'answer': pregunta['respuesta_correcta'],
            'subject': pregunta['tema'],
            'opciones': pregunta['opciones'],
            'explicacion': pregunta['explicacion'],
            'dificultad': pregunta['dificultad']
        }
        questions.append(question_data)
    
    # Insertar preguntas en el AVL
    for q in questions:
        avl.insert(q)
    
    # Demostracion
    print("=== DEMOSTRACION ARBOL AVL ===")
    print(f"Total preguntas insertadas: {avl.size}")
    print(f"¿El arbol esta balanceado?: {'Si' if avl.is_balanced() else 'No'}")
    
    print("\nMaterias disponibles:", avl.get_all_subjects())
    
    # Mostrar preguntas de una materia específica (ej: 'ciencia de datos')
    materia = 'ciencia de datos'
    print(f"\nPreguntas en '{materia}':")
    for q in avl.search_by_subject(materia):
        print(f"\nID {q['id']}: {q['question']}")
        print("Opciones:")
        for opcion in q['opciones']:
            print(f" - {opcion}")
        print(f"Respuesta correcta: {q['answer']}")
        print(f"Explicación: {q['explicacion']}")
    
    # Buscar una pregunta específica por ID
    target_id = 2
    print(f"\nBuscando pregunta con ID {target_id}:")
    found = avl.search_by_id(target_id)
    if found:
        print(f"Encontrada: {found['question']}")
        print(f"Respuesta: {found['answer']}")
    else:
        print("Pregunta no encontrada")
    
    # Demostracion algoritmos de ordenamiento y busqueda
    print("\n=== DEMOSTRACION ALGORITMOS ===")
    sort_and_search_demo(questions)