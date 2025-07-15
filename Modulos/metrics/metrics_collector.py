import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List

class MetricsCollector:
    """Recolector de métricas en tiempo real para el sistema de exámenes."""
    
    def __init__(self, metrics_file: str = "Datos/metrics.json"):
        self.metrics_file = metrics_file
        self.ensure_metrics_file()
        
    def ensure_metrics_file(self):
        """Asegura que el archivo de métricas existe con estructura inicial."""
        if not os.path.exists(self.metrics_file):
            os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)
            initial_metrics = {
                "system_performance": {
                    "search_times": [],
                    "ai_processing_times": [],
                    "total_requests": 0,
                    "avg_response_time": 0,
                    "last_updated": datetime.now().isoformat()
                },
                "user_activity": {
                    "total_users": 0,
                    "active_users_today": 0,
                    "students": 0,
                    "teachers": 0,
                    "last_login_times": {},
                    "test_attempts_today": 0
                },
                "question_stats": {
                    "total_questions": 0,
                    "questions_by_subject": {},
                    "difficulty_distribution": {
                        "facil": 0,
                        "medio": 0,
                        "dificil": 0
                    }
                },
                "test_performance": {
                    "total_tests": 0,
                    "avg_score": 0,
                    "completion_rate": 0,
                    "avg_duration": 0,
                    "tests_by_subject": {}
                }
            }
            self.save_metrics(initial_metrics)
    
    def load_metrics(self) -> Dict[str, Any]:
        """Carga las métricas desde el archivo JSON."""
        try:
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.ensure_metrics_file()
            return self.load_metrics()
    
    def save_metrics(self, metrics: Dict[str, Any]):
        """Guarda las métricas en el archivo JSON."""
        metrics["system_performance"]["last_updated"] = datetime.now().isoformat()
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
    
    def record_search_time(self, search_time: float, search_type: str = "avl"):
        """Registra el tiempo de búsqueda en el AVL."""
        metrics = self.load_metrics()
        metrics["system_performance"]["search_times"].append({
            "time": search_time,
            "type": search_type,
            "timestamp": datetime.now().isoformat()
        })
        
        # Mantener solo los últimos 1000 registros
        if len(metrics["system_performance"]["search_times"]) > 1000:
            metrics["system_performance"]["search_times"] = metrics["system_performance"]["search_times"][-1000:]
        
        self.save_metrics(metrics)
    
    def record_ai_processing_time(self, processing_time: float, operation: str = "generate_questions"):
        """Registra el tiempo de procesamiento de IA."""
        metrics = self.load_metrics()
        metrics["system_performance"]["ai_processing_times"].append({
            "time": processing_time,
            "operation": operation,
            "timestamp": datetime.now().isoformat()
        })
        
        # Mantener solo los últimos 500 registros
        if len(metrics["system_performance"]["ai_processing_times"]) > 500:
            metrics["system_performance"]["ai_processing_times"] = metrics["system_performance"]["ai_processing_times"][-500:]
        
        self.save_metrics(metrics)
    
    def record_request(self, response_time: float):
        """Registra una petición al sistema."""
        metrics = self.load_metrics()
        metrics["system_performance"]["total_requests"] += 1
        
        # Calcular promedio de tiempo de respuesta
        current_avg = metrics["system_performance"]["avg_response_time"]
        total_requests = metrics["system_performance"]["total_requests"]
        new_avg = ((current_avg * (total_requests - 1)) + response_time) / total_requests
        metrics["system_performance"]["avg_response_time"] = new_avg
        
        self.save_metrics(metrics)
    
    def record_user_login(self, username: str, user_type: str):
        """Registra el login de un usuario."""
        metrics = self.load_metrics()
        current_time = datetime.now().isoformat()
        
        metrics["user_activity"]["last_login_times"][username] = current_time
        
        # Actualizar contadores por tipo
        if user_type == "student":
            metrics["user_activity"]["students"] = len([u for u, _ in metrics["user_activity"]["last_login_times"].items() if u.endswith("_student")])
        elif user_type == "teacher":
            metrics["user_activity"]["teachers"] = len([u for u, _ in metrics["user_activity"]["last_login_times"].items() if u.endswith("_teacher")])
        
        metrics["user_activity"]["total_users"] = len(metrics["user_activity"]["last_login_times"])
        
        self.save_metrics(metrics)
    
    def record_test_attempt(self, subject: str, score: float, duration: float):
        """Registra un intento de examen."""
        metrics = self.load_metrics()
        
        metrics["user_activity"]["test_attempts_today"] += 1
        metrics["test_performance"]["total_tests"] += 1
        
        # Actualizar promedio de puntuación
        current_avg = metrics["test_performance"]["avg_score"]
        total_tests = metrics["test_performance"]["total_tests"]
        new_avg = ((current_avg * (total_tests - 1)) + score) / total_tests
        metrics["test_performance"]["avg_score"] = new_avg
        
        # Actualizar promedio de duración
        current_duration = metrics["test_performance"]["avg_duration"]
        new_duration = ((current_duration * (total_tests - 1)) + duration) / total_tests
        metrics["test_performance"]["avg_duration"] = new_duration
        
        # Actualizar tests por materia
        if subject not in metrics["test_performance"]["tests_by_subject"]:
            metrics["test_performance"]["tests_by_subject"][subject] = 0
        metrics["test_performance"]["tests_by_subject"][subject] += 1
        
        self.save_metrics(metrics)
    
    def update_question_stats(self, questions_data: Dict[str, Any]):
        """Actualiza las estadísticas de preguntas basadas en los datos cargados."""
        metrics = self.load_metrics()
        
        total_questions = 0
        subjects = {}
        difficulty_count = {"facil": 0, "medio": 0, "dificil": 0}
        
        for subject, questions in questions_data.items():
            if isinstance(questions, list):
                subject_count = len(questions)
                total_questions += subject_count
                subjects[subject] = subject_count
                
                # Analizar dificultad (esto es una aproximación, puedes ajustarlo)
                for question in questions:
                    if isinstance(question, dict):
                        # Asignar dificultad basada en longitud del texto o palabras clave
                        text_length = len(str(question.get('pregunta', '')))
                        if text_length < 100:
                            difficulty_count["facil"] += 1
                        elif text_length < 200:
                            difficulty_count["medio"] += 1
                        else:
                            difficulty_count["dificil"] += 1
        
        metrics["question_stats"]["total_questions"] = total_questions
        metrics["question_stats"]["questions_by_subject"] = subjects
        metrics["question_stats"]["difficulty_distribution"] = difficulty_count
        
        self.save_metrics(metrics)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas de rendimiento calculadas."""
        metrics = self.load_metrics()
        
        # Calcular promedios de tiempo de búsqueda
        search_times = metrics["system_performance"]["search_times"]
        avg_search_time = 0
        if search_times:
            avg_search_time = sum(item["time"] for item in search_times[-100:]) / min(len(search_times), 100)
        
        # Calcular promedios de tiempo de IA
        ai_times = metrics["system_performance"]["ai_processing_times"]
        avg_ai_time = 0
        if ai_times:
            avg_ai_time = sum(item["time"] for item in ai_times[-50:]) / min(len(ai_times), 50)
        
        return {
            "avg_search_time": round(avg_search_time, 4),
            "avg_ai_time": round(avg_ai_time, 4),
            "total_requests": metrics["system_performance"]["total_requests"],
            "avg_response_time": round(metrics["system_performance"]["avg_response_time"], 4),
            "total_users": metrics["user_activity"]["total_users"],
            "total_tests": metrics["test_performance"]["total_tests"],
            "avg_test_score": round(metrics["test_performance"]["avg_score"], 2),
            "total_questions": metrics["question_stats"]["total_questions"]
        }

# Instancia global del recolector de métricas
metrics_collector = MetricsCollector()
