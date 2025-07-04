class AVLNode:
    def __init__(self, data):
        self.data = data
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


class AVLTree:
    def __init__(self):
        self.root = None
        self.size = 0
        self.questions_by_subject = {}

    def _add_to_subject_index(self, data):
        subject = data.get('subject', 'general')
        if subject not in self.questions_by_subject:
            self.questions_by_subject[subject] = []
        self.questions_by_subject[subject].append(data)

    def insert(self, data):
        if not isinstance(data, dict):
            raise ValueError("Los datos deben ser un diccionario")
        if 'id' not in data:
            raise ValueError("El diccionario de datos debe contener un campo 'id'")
        
        # Verificar si el ID ya existe
        if self._find_id(data['id']) is not None:
            raise ValueError(f"El ID {data['id']} ya existe en el árbol")
        
        self._add_to_subject_index(data)
        self.root = self._insert(self.root, data)
        self.size += 1

    def _find_id(self, question_id):
        return self._search_by_id(self.root, question_id)

    def _insert(self, node, data):
        if not node:
            return AVLNode(data)
        
        if data['id'] < node.data['id']:
            node.left = self._insert(node.left, data)
        else:
            node.right = self._insert(node.right, data)
        
        node.update_height()
        return self._balance(node)
    
    def _balance(self, node):
        balance = node.balance_factor()
        
        if balance > 1 and node.left.balance_factor() >= 0:
            return self._right_rotate(node)
            
        if balance > 1 and node.left.balance_factor() < 0:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)
            
        if balance < -1 and node.right.balance_factor() <= 0:
            return self._left_rotate(node)
            
        if balance < -1 and node.right.balance_factor() > 0:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)
            
        return node

    def _left_rotate(self, z):
        y = z.right
        T2 = y.left
        
        y.left = z
        z.right = T2
        
        z.update_height()
        y.update_height()
        
        return y

    def _right_rotate(self, z):
        y = z.left
        T3 = y.right
        
        y.right = z
        z.left = T3
        
        z.update_height()
        y.update_height()
        
        return y

    def search_by_subject(self, subject):
        return self.questions_by_subject.get(subject, []).copy()

    def get_all_subjects(self):
        return sorted(list(self.questions_by_subject.keys()))

    def search_by_id(self, question_id):
        return self._search_by_id(self.root, question_id)

    def _search_by_id(self, node, question_id):
        if not node:
            return None
        if question_id == node.data['id']:
            return node.data
        elif question_id < node.data['id']:
            return self._search_by_id(node.left, question_id)
        else:
            return self._search_by_id(node.right, question_id)

    def in_order_traversal(self):
        elements = []
        self._in_order_traversal(self.root, elements)
        return elements

    def _in_order_traversal(self, node, elements):
        if node:
            self._in_order_traversal(node.left, elements)
            elements.append(node.data)
            self._in_order_traversal(node.right, elements)

    def is_balanced(self):
        return self._check_balance(self.root) != -1

    def _check_balance(self, node):
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


def merge_sort(arr, key='id'):
    if len(arr) <= 1:
        return arr
        
    mid = len(arr) // 2
    left_half = arr[:mid]
    right_half = arr[mid:]
    
    left_sorted = merge_sort(left_half, key)
    right_sorted = merge_sort(right_half, key)
    
    return _merge(left_sorted, right_sorted, key)


def _merge(left, right, key):
    merged = []
    left_idx = right_idx = 0
    
    while left_idx < len(left) and right_idx < len(right):
        if left[left_idx][key] < right[right_idx][key]:
            merged.append(left[left_idx])
            left_idx += 1
        else:
            merged.append(right[right_idx])
            right_idx += 1
    
    merged.extend(left[left_idx:])
    merged.extend(right[right_idx:])
    
    return merged


def binary_search(sorted_list, target, key='id'):
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
    if not questions:
        print("Lista de preguntas vacía")
        return None
        
    print("\nAntes de ordenar:")
    for q in questions[:5]:
        print(f"ID: {q['id']}, Pregunta: {q['question'][:30]}...")
        
    sorted_questions = merge_sort(questions)
    
    print("\nDespués de ordenar:")
    for q in sorted_questions[:5]:
        print(f"ID: {q['id']}, Pregunta: {q['question'][:30]}...")
        
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


if __name__ == '__main__':
    import json
    import os
    import hashlib
    
    avl = AVLTree()
    
    def cargar_preguntas(archivo, materia):
        if not os.path.exists(archivo):
            print(f"Archivo {archivo} no encontrado")
            return []
            
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                preguntas_json = json.load(f)
        except json.JSONDecodeError:
            print(f"Error al leer el archivo {archivo}")
            return []
            
        questions = []
        
        for i, pregunta in enumerate(preguntas_json.get('preguntas', [])):
            try:
                # Generar un ID único usando materia + número + índice para evitar duplicados
                unique_id = int(hashlib.sha256(
                    f"{materia}_{pregunta['numero']}_{i}_{pregunta['pregunta']}".encode()
                ).hexdigest()[:8], 16) % 10**6
                
                question_data = {
                    'id': unique_id,
                    'numero': pregunta['numero'],
                    'question': pregunta['pregunta'],
                    'answer': pregunta['respuesta_correcta'],
                    'subject': materia,
                    'options': pregunta['opciones'],
                    'feedback': pregunta.get('retroalimentacion', ''),
                    'explanation': pregunta.get('justificacion', '')
                }
                questions.append(question_data)
            except KeyError as e:
                print(f"Error en pregunta {i}: Falta campo {e}")
                continue
                
        return questions
    
    # Carga preguntas con manejo de errores
    preguntas_habilidades = cargar_preguntas('habilidades_vida_ordenado_completado.json', 'Habilidades para la Vida')
    preguntas_ciencia = cargar_preguntas('ciencia_datos_ordenado_completado.json', 'Ciencia de Datos')
    
    print(f"\nTotal preguntas cargadas de Habilidades: {len(preguntas_habilidades)}")
    print(f"Total preguntas cargadas de Ciencia de Datos: {len(preguntas_ciencia)}")
    
    # Inserta preguntas en el árbol AVL
    for q in preguntas_habilidades + preguntas_ciencia:
        try:
            avl.insert(q)
        except ValueError as e:
            print(f"Error insertando pregunta: {e}")
    
    print("\n=== DEMOSTRACIÓN ÁRBOL AVL ===")
    print(f"Total preguntas insertadas: {avl.size}")
    print(f"¿El árbol está balanceado?: {'Sí' if avl.is_balanced() else 'No'}")
    print("\nMaterias disponibles:", avl.get_all_subjects())
    
    # Muestra preguntas por materia
    for materia in avl.get_all_subjects():
        print(f"\n=== PREGUNTAS DE {materia.upper()} ===")
        preguntas_materia = avl.search_by_subject(materia)
        print(f"Total: {len(preguntas_materia)} preguntas")
        
        for q in preguntas_materia[:3]:  # Mostrar solo 3 para no saturar
            print(f"\nID {q['id']} (Número {q['numero']}): {q['question']}")
            print("Opciones:")
            for opcion in q['options']:
                print(f" - {opcion}")
            print(f"Respuesta correcta: {q['answer']}")
            print(f"Retroalimentación: {q.get('feedback', 'No disponible')}")
            print(f"Justificación: {q.get('explanation', 'No disponible')}")
    
    print("\n=== BÚSQUEDA POR ID ===")
    if preguntas_habilidades:
        target_id = preguntas_habilidades[0]['id']
        print(f"Buscando pregunta con ID {target_id}:")
        found = avl.search_by_id(target_id)
        if found:
            print(f"Materia: {found['subject']}")
            print(f"Pregunta: {found['question']}")
            print(f"Respuesta: {found['answer']}")
        else:
            print("Pregunta no encontrada")
    else:
        print("No hay preguntas de habilidades para buscar")
    
    print("\n=== DEMOSTRACIÓN ALGORITMOS ===")
    if preguntas_habilidades or preguntas_ciencia:
        sort_and_search_demo(preguntas_habilidades + preguntas_ciencia)
    else:
        print("No hay preguntas para ordenar y buscar")