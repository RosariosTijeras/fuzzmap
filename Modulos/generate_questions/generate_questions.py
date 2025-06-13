"""
ADVERTENCIA IMPORTANTE

Este código fue probado y ejecutado en una laptop ASUS TUF A15 FA506NF con los siguientes componentes:
- CPU: AMD Ryzen 5 7535HS
- GPU: NVIDIA GeForce GTX 2050 (4GB VRAM)
- RAM: 16GB DDR5
- Almacenamiento: SSD NVMe
Tiempo de ejecución de ejemplo en este equipo es de aproximadamente: 46m (2760 segundos) para generar 10 preguntas únicas con explicaciones.
Este script utiliza modelos de IA que requieren recursos significativos. Asegúrate de tener un entorno adecuado antes de ejecutarlo.

Modelos de IA utilizados:
- mistral:7b-instruct-q4_K_M (~7GB en disco, modelo de tamaño medio, recomendado para generación de preguntas)
- phi3:mini (~2GB en disco, modelo ligero, puede correr en CPU pero se recomienda GPU)

Requisitos mínimos recomendados:
- CPU multinúcleo moderno
- 16GB de RAM
- GPU dedicada con al menos 4GB VRAM (NVIDIA recomendado para aceleración)
- Al menos 20GB de espacio libre en disco para modelos y dependencias
- Python 3.10+

Este script puede requerir mucho tiempo y recursos dependiendo del tamaño del contexto y la cantidad de preguntas a generar.
"""

# Modulos/nlp/question_expander.py
import ollama
import json
import re
import asyncio
from typing import List, Dict
from functools import lru_cache
import random
import os

class QuestionExpander:
    def __init__(self, model_name: str = "mistral:7b-instruct-q4_K_M", explanation_model: str = "phi3:mini"):
        self.model = model_name
        self.explanation_model = explanation_model  # Modelo especializado en explicaciones
        self._response_cache = lru_cache(maxsize=20)(self._cache_response)
        self.generated_questions = set()  # Para evitar duplicados

    def _cache_response(self, key: str, response: str) -> str:
        return response

    def _prepare_prompt(self, preguntas_originales: str, resumen: str, num_questions: int) -> str:
        """Prompt avanzado para máxima calidad y diversidad"""
        return (
            f"Eres un experto en educación universitaria y generación de evaluaciones. Tienes dos fuentes de información:\n"
            f"1. Lista de preguntas originales:\n{preguntas_originales}\n\n"
            f"2. Extracto del PDF de resumen:\n{resumen}\n\n"
            f"Tu tarea es generar {num_questions} preguntas nuevas, únicas y variadas, combinando ambos contextos. Cada pregunta debe:\n"
            f"- Ser clara y relevante para estudiantes universitarios.\n"
            f"- Tener 4 opciones de respuesta (A, B, C, D), bien redactadas y plausibles.\n"
            f"- Indicar la respuesta correcta (debe coincidir exactamente con una de las opciones).\n"
            f"- Incluir una breve explicación (1-2 oraciones) de por qué la respuesta es correcta.\n"
            f"- Indicar el nivel de dificultad (baja, media o alta).\n"
            f"- Indicar el tema específico.\n\n"
            f"**IMPORTANTE: Genera absolutamente todas las preguntas, opciones, explicaciones y temas SOLO en español. No utilices ningún texto en inglés.**\n"
            f"**Formato de salida exclusivamente JSON:**\n"
            f"[\n  {{\n    'pregunta': '...',\n    'opciones': ['A) ...', 'B) ...', 'C) ...', 'D) ...'],\n    'respuesta_correcta': 'A) ...',\n    'explicacion': '...',\n    'dificultad': 'media',\n    'tema': '...'}}\n]\n\n"
            f"Genera las preguntas en español y asegúrate de que sean diferentes a las originales."
        )

    async def generate_explanations(self, questions: List[Dict]) -> List[Dict]:
        """Genera explicaciones usando un modelo especializado"""
        logging.debug(f"(Explicaciones) Modelo de explicación en uso: {self.explanation_model}")
        explained_questions = []
        for q in questions:
            prompt = (
                f"Explica por qué la respuesta correcta es '{q['respuesta_correcta']}' "
                f"para la pregunta: '{q['pregunta']}'. Explicación breve (1-2 oraciones)."
            )
            
            client = ollama.AsyncClient()
            response = await client.generate(
                model=self.explanation_model,
                prompt=prompt,
                options={"num_gpu": 70}  # Más GPU para este modelo ligero
            )
            q['explicacion'] = response['response'].strip()
            explained_questions.append(q)
        return explained_questions

    async def generate_new_questions(self, preguntas_originales: str, resumen: str, num_questions: int = 10) -> List[Dict]:
        """Genera preguntas con manejo de duplicados y explicaciones"""
        print(f"[DEBUG] (Preguntas) Modelo de generación en uso: {self.model}")
        prompt = self._prepare_prompt(preguntas_originales, resumen, num_questions)
        
        # Generar preguntas en lotes
        preguntas = []
        intentos = 0
        batch_size = min(5, num_questions)  # Generar en lotes pequeños
        
        while len(preguntas) < num_questions and intentos < 5:
            try:
                response = await self._call_model(prompt)
                batch = self._parse_response(response, batch_size)
                
                for q in batch:
                    # Evitar duplicados
                    pregunta_hash = hash(q['pregunta'].strip().lower())
                    if pregunta_hash not in self.generated_questions:
                        preguntas.append(q)
                        self.generated_questions.add(pregunta_hash)
                
                intentos += 1
            except Exception as e:
                print(f"Error en generación: {str(e)}")
                intentos += 1
        
        # Generar explicaciones si faltan
        preguntas_sin_explicacion = [q for q in preguntas if not q.get('explicacion')]
        if preguntas_sin_explicacion:
            preguntas_con_explicacion = await self.generate_explanations(preguntas_sin_explicacion)
            # Reemplazar en la lista original
            for i, q in enumerate(preguntas):
                if not q.get('explicacion'):
                    for eq in preguntas_con_explicacion:
                        if eq['pregunta'] == q['pregunta']:
                            preguntas[i] = eq
                            break
        
        return preguntas[:num_questions]

    async def _call_model(self, prompt: str) -> str:
        """Llama al modelo con configuración optimizada"""
        client = ollama.AsyncClient()
        response = await client.generate(
            model=self.model,
            prompt=prompt,
            format="json",
            options={
                "num_gpu": 45,
                "temperature": 0.8,  # Mayor creatividad para diversidad
                "num_ctx": 4096,
                "seed": random.randint(1, 1000)  # Semilla aleatoria para variedad
            }
        )
        return response['response']

    def _parse_response(self, raw_response: str, expected_count: int) -> List[Dict]:
        """Analiza respuesta con validación mejorada"""
        try:
            data = json.loads(raw_response)
            if isinstance(data, list):
                return data[:expected_count]
        except json.JSONDecodeError:
            pass
        
        # Plan B: Extraer objetos JSON individuales
        preguntas = []
        pattern = r'\{[^{}]*\}'
        matches = re.findall(pattern, raw_response, re.DOTALL)
        
        for match in matches:
            try:
                q = json.loads(match)
                if self._is_valid_question(q):
                    preguntas.append(q)
                    if len(preguntas) >= expected_count:
                        break
            except json.JSONDecodeError:
                continue
        
        return preguntas

    def _is_valid_question(self, question: Dict) -> bool:
        """Valida estructura y contenido con foco en explicaciones"""
        required_keys = {'pregunta', 'opciones', 'respuesta_correcta', 'dificultad', 'tema'}
        if not all(key in question for key in required_keys):
            return False
        
        # Validar opciones
        if not (isinstance(question['opciones'], list) and len(question['opciones']) == 4):
            return False
        
        # Validar respuesta
        if question['respuesta_correcta'] not in question['opciones']:
            return False
        
        # Validar dificultad
        if question['dificultad'].lower() not in {'baja', 'media', 'alta'}:
            return False
        
        return True

# Ejemplo de uso mejorado
if __name__ == "__main__":
    import asyncio
    import os

    materias = [
        {
            "nombre": "Ciencia_Datos",
            "carpeta": "Datos/Ciencia_Datos",
            "resumen": "resumen_ciencia_datos.json",
            "banco": "bancodepreguntas_global_cienciadatos.json"
        },
        {
            "nombre": "Habilidades_Vida",
            "carpeta": "Datos/Habilidades_Vida",
            "resumen": "resumen_habilidades_vida.json",
            "banco": "bancodepreguntas_global_habilidadesvida.json"
        }
    ]

    for materia in materias:
        ruta_base = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), materia["carpeta"])
        ruta_resumen = os.path.join(ruta_base, materia["resumen"])
        ruta_banco = os.path.join(ruta_base, materia["banco"])
        ruta_salida = os.path.join(ruta_base, f"preguntas_generadas_{materia['nombre'].lower()}.json")

        # Leer resumen desde el archivo JSON
        resumen = ""
        if os.path.exists(ruta_resumen):
            with open(ruta_resumen, 'r', encoding='utf-8') as f:
                data = json.load(f)
                resumen = data.get("resumen", "")
        if not resumen:
            print(f"[ADVERTENCIA] No se encontró resumen en {ruta_resumen}, se omite materia {materia['nombre']}")
            continue

        # Leer preguntas originales del banco si existe
        preguntas_originales = []
        if os.path.exists(ruta_banco):
            with open(ruta_banco, 'r', encoding='utf-8') as f:
                data = json.load(f)
                lineas = data.get("lineas", [])
                preguntas_originales = [l for l in lineas if l.strip().startswith("¿")]  # Solo preguntas
        preguntas_originales_str = "\n".join(preguntas_originales)

        print(f"\nGenerando preguntas para {materia['nombre']}...")
        expander = QuestionExpander(
            model_name="mistral:7b-instruct-q4_K_M",
            explanation_model="phi3:mini"
        )
        print(f"[DEBUG] Modelo de generación: {expander.model} | Modelo de explicación: {expander.explanation_model}")

        # Forzar generación hasta obtener 10 preguntas únicas
        preguntas = []
        vistos = set()
        while len(preguntas) < 10:
            nuevas = asyncio.run(expander.generate_new_questions(preguntas_originales_str, resumen, 10 - len(preguntas)))
            for p in nuevas:
                enunciado = p['pregunta'].strip().lower()
                if enunciado not in vistos:
                    preguntas.append(p)
                    vistos.add(enunciado)
            if not nuevas:
                print("[ERROR] No se pudieron generar más preguntas únicas. Se detiene para evitar bucle infinito.")
                break
        if len(preguntas) < 10:
            print(f"[ADVERTENCIA] Solo se generaron {len(preguntas)} preguntas para {materia['nombre']}")
        # Guardar en JSON limpio solo si hay preguntas
        if preguntas:
            with open(ruta_salida, 'w', encoding='utf-8') as f:
                json.dump(preguntas, f, indent=2, ensure_ascii=False)
            print(f"Preguntas guardadas en {ruta_salida}")
        else:
            print(f"[ADVERTENCIA] No se generó ninguna pregunta válida para {materia['nombre']}")