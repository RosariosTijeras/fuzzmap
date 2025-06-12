"""
ADVERTENCIA IMPORTANTE

Este código fue probado y ejecutado en una laptop ASUS TUF A15 FA506NF con los siguientes componentes:
- CPU: AMD Ryzen 5 7535HS
- GPU: NVIDIA GeForce GTX 2050 (4GB VRAM)
- RAM: 16GB DDR5
- Almacenamiento: SSD NVMe
Tiempo de ejecución de ejemplo en este equipo: 46m (10.483s)

Modelos de IA utilizados:
- llama3:instruct (~8GB en disco, modelo grande, requiere GPU para inferencia eficiente)
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
    def __init__(self, model_name: str = "llama3:instruct", explanation_model: str = "phi3:mini"):
        self.model = model_name
        self.explanation_model = explanation_model  # Modelo especializado en explicaciones
        self._response_cache = lru_cache(maxsize=20)(self._cache_response)
        self.generated_questions = set()  # Para evitar duplicados

    def _cache_response(self, key: str, response: str) -> str:
        return response

    def _prepare_prompt(self, context: str, num_questions: int) -> str:
        """Prompt optimizado para diversidad y explicaciones"""
        return (
            f"Eres un experto en creación de evaluaciones universitarias. Genera {num_questions} preguntas únicas "
            f"basadas en el siguiente contexto. Cada pregunta debe incluir:\n"
            "1. Enunciado claro y único\n"
            "2. 4 opciones con formato: A) ... , B) ... , C) ... , D) ...\n"
            "3. Respuesta correcta (coincidiendo con una opción)\n"
            "4. Explicación detallada de 1-2 oraciones\n"
            "5. Dificultad (baja/media/alta)\n"
            "6. Tema específico\n\n"
            "**Formato de salida EXCLUSIVAMENTE JSON:**\n"
            "[\n"
            "  {\n"
            '    "pregunta": "...",\n'
            '    "opciones": ["A) ...", "B) ...", "C) ...", "D) ..."],\n'
            '    "respuesta_correcta": "A) ...",\n'
            '    "explicacion": "...",\n'
            '    "dificultad": "media",\n'
            '    "tema": "..."\n'
            "  }\n"
            "]\n\n"
            f"**Contexto:**\n{context[:2500]}{'... [truncado]' if len(context) > 2500 else ''}"
        )

    async def generate_explanations(self, questions: List[Dict]) -> List[Dict]:
        """Genera explicaciones usando un modelo especializado"""
        print(f"[DEBUG] (Explicaciones) Modelo de explicación en uso: {self.explanation_model}")
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

    async def generate_new_questions(self, context_text: str, num_questions: int = 10) -> List[Dict]:
        """Genera preguntas con manejo de duplicados y explicaciones"""
        print(f"[DEBUG] (Preguntas) Modelo de generación en uso: {self.model}")
        prompt = self._prepare_prompt(context_text, num_questions)
        
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

    # Párrafos resumen sintetizados para cada materia
    resumenes_sintetizados = {
        "Ciencia_Datos": (
            "La Ciencia de Datos es una disciplina interdisciplinaria que combina estadística, matemáticas, informática y algoritmos para analizar grandes volúmenes de datos, extraer información relevante y apoyar la toma de decisiones. "
            "Su evolución ha estado marcada por el avance de la informática y la inteligencia artificial, permitiendo automatizar procesos, identificar patrones y predecir comportamientos en áreas como la salud, finanzas y tecnología. "
            "El objetivo principal es transformar datos en conocimiento útil, facilitando la innovación y el progreso en diversos campos."
        ),
        "Habilidades_Vida": (
            "Las Habilidades para la Vida son un conjunto de capacidades esenciales que permiten a las personas afrontar de manera efectiva los retos y demandas de la vida diaria, especialmente en el contexto universitario. "
            "Incluyen la gestión del estrés y la ansiedad, el autocuidado, la adaptabilidad, la toma de decisiones y la comunicación asertiva. "
            "Practicar técnicas como la respiración profunda, el mindfulness y la relajación muscular progresiva contribuye al bienestar psicológico, mejora el rendimiento académico y fortalece la resiliencia ante situaciones adversas."
        )
    }

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
        ruta_banco = os.path.join(ruta_base, materia["banco"])
        ruta_salida = os.path.join(ruta_base, f"preguntas_generadas_{materia['nombre'].lower()}.json")

        # Usar el resumen sintetizado en vez del PDF
        resumen = resumenes_sintetizados[materia["nombre"]]
        # Leer banco de preguntas
        preguntas_existentes = []
        if os.path.exists(ruta_banco):
            with open(ruta_banco, 'r', encoding='utf-8') as f:
                data = json.load(f)
                lineas = data.get("lineas", [])
                preguntas_existentes = [l for l in lineas if l.strip() and l.strip().startswith("¿")]
        # Unir contexto
        contexto = resumen + "\n\n" + "\n".join(preguntas_existentes)
        print(f"\nGenerando preguntas para {materia['nombre']}...")
        expander = QuestionExpander(
            model_name="llama3:instruct",
            explanation_model="phi3:mini"
        )
        print(f"[DEBUG] Modelo de generación: {expander.model} | Modelo de explicación: {expander.explanation_model}")
        preguntas = asyncio.run(expander.generate_new_questions(contexto, 10))
        # Eliminar duplicados por enunciado
        preguntas_unicas = []
        vistos = set()
        for p in preguntas:
            enunciado = p['pregunta'].strip().lower()
            if enunciado not in vistos:
                preguntas_unicas.append(p)
                vistos.add(enunciado)
        # Guardar en JSON limpio solo si hay preguntas
        if preguntas_unicas:
            with open(ruta_salida, 'w', encoding='utf-8') as f:
                json.dump(preguntas_unicas, f, indent=2, ensure_ascii=False)
            print(f"Preguntas guardadas en {ruta_salida}")
        else:
            print(f"[ADVERTENCIA] No se generó ninguna pregunta válida para {materia['nombre']}")