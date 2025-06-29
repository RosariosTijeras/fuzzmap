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
        self.questions_by_subject = {}  # Índice centralizado de preguntas por materia

    def _add_to_subject_index(self, data):  # Cambiado para recibir data directamente
        # Agrega una pregunta al índice por materia
        subject = data.get('subject', 'general')
        if subject not in self.questions_by_subject:
            self.questions_by_subject[subject] = []
        self.questions_by_subject[subject].append(data)

    def insert(self, data):
        # Inserta un nuevo nodo en el árbol
        if not isinstance(data, dict) or 'id' not in data:
            raise ValueError("Los datos deben ser un diccionario con un campo 'id'")  # Validación de entrada
        if 'id' not in data:
            data['id'] = self.size + 1  # Asignar un ID si no existe
        
        self._add_to_subject_index(data)  # Actualiza índice primero
        self.root = self._insert(self.root, data)
        self.size += 1

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

    def search_by_subject(self, subject):
        # Busca preguntas por materia usando el índice centralizado
        return self.questions_by_subject.get(subject, []).copy()  # Devuelve copia para evitar modificaciones

    def get_all_subjects(self):
        # Devuelve todas las materias disponibles en el árbol
        return sorted(list(self.questions_by_subject.keys()))  # Usa el índice centralizado
    
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
        return self.questions_by_subject.get(subject, []).copy()

    def get_all_subjects(self):
        return sorted(list(self.questions_by_subject.keys()))

   

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

if __name__ == '__main__':
    import json
    
    avl = AVLTree()
    
    def cargar_preguntas(archivo, materia):
        with open(archivo, 'r', encoding='utf-8') as f:
            preguntas_json = json.load(f)
        questions = []
        
        for i, pregunta in enumerate(preguntas_json['preguntas']):
            # Creamos un ID único combinando número de pregunta y materia
            unique_id = int(f"{pregunta['numero']}{hash(materia) % 1000}")
            
            question_data = {
                'id': unique_id,
                'numero': pregunta['numero'],
                'question': pregunta['pregunta'],
                'answer': pregunta['respuesta_correcta'],
                'subject': materia,
                'options': pregunta['opciones'],
                'feedback': pregunta['retroalimentacion'],
                'explanation': pregunta['justificacion']
            }
            questions.append(question_data)
        return questions
    
    # Carga preguntas
    preguntas_habilidades = cargar_preguntas('habilidades_vida_ordenado_completado.json', 'Habilidades para la Vida')
    preguntas_ciencia = cargar_preguntas('ciencia_datos_ordenado_completado.json', 'Ciencia de Datos')
    
    # Inserta preguntas en el árbol AVL
    for q in preguntas_habilidades + preguntas_ciencia:
        avl.insert(q)
    
    print("=== DEMOSTRACION ARBOL AVL ===")
    print(f"Total preguntas insertadas: {avl.size}")
    print(f"¿El arbol esta balanceado?: {'Si' if avl.is_balanced() else 'No'}")
    print("\nMaterias disponibles:", avl.get_all_subjects())
    
    # Muestra preguntas por materia
    for materia in avl.get_all_subjects():
        print(f"\n=== PREGUNTAS DE {materia.upper()} ===")
        preguntas_materia = avl.search_by_subject(materia)
        print(f"Total: {len(preguntas_materia)} preguntas")
        for q in preguntas_materia:
            print(f"\nID {q['id']} (Número {q['numero']}): {q['question']}")
            print("Opciones:")
            for opcion in q['options']:
                print(f" - {opcion}")
            print(f"Respuesta correcta: {q['answer']}")
            print(f"Retroalimentación: {q.get('feedback', 'No disponible')}")
            print(f"Justificación: {q.get('explanation', 'No disponible')}")
    
    print("\n=== BUSQUEDA POR ID ===")
    # Buscamos el ID de la primera pregunta de habilidades
    target_id = preguntas_habilidades[0]['id']
    print(f"Buscando pregunta con ID {target_id}:")
    found = avl.search_by_id(target_id)
    if found:
        print(f"Materia: {found['subject']}")
        print(f"Pregunta: {found['question']}")
        print(f"Respuesta: {found['answer']}")
    else:
        print("Pregunta no encontrada")
    
    print("\n=== DEMOSTRACION ALGORITMOS ===")
    sort_and_search_demo(preguntas_habilidades + preguntas_ciencia)