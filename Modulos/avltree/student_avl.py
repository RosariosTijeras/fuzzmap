# =====================
# ÁRBOL AVL PARA ESTUDIANTES Y RANKING
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
        # Primero buscar el estudiante
        student = self.search_student_by_email(email)
        if student:
            # Actualizar promedio
            student['promedio_general'] = new_average
            # Reordenar la lista de ranking
            self._update_ranking_list()
            return True
        return False

    def calculate_student_average(self, email, user_folder):
        """Calcula el promedio general de un estudiante basado en sus tests"""
        import os
        import json
        
        if not os.path.isdir(user_folder):
            return 0.0
            
        scores = []
        for fname in os.listdir(user_folder):
            if fname.startswith('test_') and fname.endswith('.json'):
                try:
                    with open(os.path.join(user_folder, fname), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        score = data.get('score', 0)
                        if isinstance(score, (int, float)):
                            scores.append(score)
                except:
                    continue
        
        return round(sum(scores) / len(scores), 2) if scores else 0.0

    def load_all_students(self):
        """Carga todos los estudiantes registrados y calcula sus promedios"""
        from Modulos.auth.auth import _cargar_usuarios
        import os
        
        usuarios = _cargar_usuarios()
        
        for email, user_data in usuarios.items():
            if email == 'admin@unach.edu.ec':
                continue  # Saltar admin
                
            user_folder = os.path.join('Datos', email.replace('@', '_at_'))
            promedio = self.calculate_student_average(email, user_folder)
            
            student_data = {
                'email': email,
                'nombre': user_data.get('nombre', ''),
                'apellido': user_data.get('apellido', ''),
                'promedio_general': promedio,
                'materias': user_data.get('materias', []),
                'total_tests': len([f for f in os.listdir(user_folder) 
                                  if f.startswith('test_') and f.endswith('.json')]) if os.path.isdir(user_folder) else 0
            }
            
            # Verificar si ya existe para evitar duplicados
            existing = self.search_student_by_email(email)
            if not existing:
                self.insert_student(student_data)
            else:
                self.update_student_average(email, promedio)
