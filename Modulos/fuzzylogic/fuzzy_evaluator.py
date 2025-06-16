"""
Módulo para la evaluación de desempeño estudiantil mediante lógica difusa y generación de recomendaciones personalizadas.
Ruta de este archivo: Modulos/fuzzylogic/fuzzy_evaluator.py

En este módulo se implementan las siguientes funcionalidades:
- Definición de variables y reglas difusas para evaluar el rendimiento en tests.
- Cálculo del desempeño del usuario usando lógica difusa (skfuzzy).
- Generación de recomendaciones automáticas según el puntaje obtenido y los temas fallados.
- Obtención de recomendaciones generales a partir del historial de tests de un usuario.
- Integración con modelos de lenguaje (Ollama) para recomendaciones personalizadas y breves.

Dependencias principales:
- numpy
- scikit-fuzzy (skfuzzy)
- ollama (cliente para modelos de lenguaje)
- json, os
"""

import numpy as np  # Librería para operaciones numéricas y manejo de arrays
import skfuzzy as fuzz  # Librería para lógica difusa
from skfuzzy import control as ctrl  # Módulo de control difuso
import os  # Para operaciones del sistema de archivos
import json  # Para leer y escribir archivos JSON
import ollama  # Cliente para recomendaciones AI (Ollama)

# ===============================
# Definición del sistema difuso para evaluación de desempeño
# ===============================

# Universo de variables difusas:
# - aciertos: número de respuestas correctas (0 a 10)
# - porcentaje: porcentaje de aciertos (0% a 100%)
# - evaluacion: calificación final (0% a 100%)
aciertos = ctrl.Antecedent(np.arange(0, 11, 1), 'aciertos')  # Número de aciertos: 0 a 10
porcentaje = ctrl.Antecedent(np.arange(0, 101, 1), 'porcentaje')  # Porcentaje de aciertos: 0% a 100%
evaluacion = ctrl.Consequent(np.arange(0, 101, 1), 'evaluacion')  # Evaluación final: 0% a 100%

# Funciones de membresía para la variable 'aciertos'
# - bajo: pocos aciertos (0-5)
# - medio: cantidad intermedia de aciertos (2-8)
# - alto: muchos aciertos (6-10)
aciertos['bajo'] = fuzz.trimf(aciertos.universe, [0, 0, 5])
aciertos['medio'] = fuzz.trimf(aciertos.universe, [2, 5, 8])
aciertos['alto'] = fuzz.trimf(aciertos.universe, [6, 10, 10])

# Funciones de membresía para la variable 'porcentaje'
# - bajo: bajo porcentaje de aciertos (0-50%)
# - medio: porcentaje intermedio (30-80%)
# - alto: alto porcentaje de aciertos (70-100%)
porcentaje['bajo'] = fuzz.trimf(porcentaje.universe, [0, 0, 50])
porcentaje['medio'] = fuzz.trimf(porcentaje.universe, [30, 60, 80])
porcentaje['alto'] = fuzz.trimf(porcentaje.universe, [70, 100, 100])

# Funciones de membresía para la variable 'evaluacion'
# - muy_deficiente: desempeño muy bajo (0-25%)
# - deficiente: desempeño bajo (15-45%)
# - regular: desempeño regular (35-65%)
# - bueno: buen desempeño (55-85%)
# - excelente: desempeño sobresaliente (80-100%)
evaluacion['muy_deficiente'] = fuzz.trimf(evaluacion.universe, [0, 0, 25])
evaluacion['deficiente'] = fuzz.trimf(evaluacion.universe, [15, 30, 45])
evaluacion['regular'] = fuzz.trimf(evaluacion.universe, [35, 50, 65])
evaluacion['bueno'] = fuzz.trimf(evaluacion.universe, [55, 70, 85])
evaluacion['excelente'] = fuzz.trimf(evaluacion.universe, [80, 100, 100])

# Reglas difusas para determinar la evaluación final
# Cada regla combina los niveles de aciertos y porcentaje para asignar una evaluación
rule1 = ctrl.Rule(aciertos['bajo'] & porcentaje['bajo'], evaluacion['muy_deficiente'])
rule2 = ctrl.Rule(aciertos['bajo'] & porcentaje['medio'], evaluacion['deficiente'])
rule3 = ctrl.Rule(aciertos['bajo'] & porcentaje['alto'], evaluacion['deficiente'])
rule4 = ctrl.Rule(aciertos['medio'] & porcentaje['bajo'], evaluacion['deficiente'])
rule5 = ctrl.Rule(aciertos['medio'] & porcentaje['medio'], evaluacion['regular'])
rule6 = ctrl.Rule(aciertos['medio'] & porcentaje['alto'], evaluacion['bueno'])
rule7 = ctrl.Rule(aciertos['alto'] & porcentaje['bajo'], evaluacion['regular'])
rule8 = ctrl.Rule(aciertos['alto'] & porcentaje['medio'], evaluacion['bueno'])
rule9 = ctrl.Rule(aciertos['alto'] & porcentaje['alto'], evaluacion['excelente'])

# Crear el sistema de control difuso y la simulación
# sistema_ctrl: contiene todas las reglas
# sistema: permite simular el sistema con valores de entrada
sistema_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9])
sistema = ctrl.ControlSystemSimulation(sistema_ctrl)


def evaluate_performance(correct_count: int, total: int) -> float:
    """Evalúa el desempeño del usuario basado en el número de aciertos y el total de preguntas.

    Args:
        correct_count (int): Número de respuestas correctas.
        total (int): Número total de preguntas.

    Returns:
        float: Desempeño del usuario en una escala de 0 a 1.
    """
    if total == 0:
        return 0.0  # Evita división por cero
    porcentaje_val = (correct_count / total) * 100  # Calcula el porcentaje de aciertos
    sistema.input['aciertos'] = correct_count  # Asigna aciertos al sistema difuso
    sistema.input['porcentaje'] = porcentaje_val  # Asigna porcentaje al sistema difuso
    sistema.compute()  # Realiza la inferencia difusa
    resultado = sistema.output['evaluacion'] / 100.0  # Normaliza a escala 0-1
    return resultado


def recommendation(score: float, correct_count: int, total: int, temas_fallados: list = None) -> str:
    """
    Genera una recomendación textual basada en el puntaje y los temas fallados.

    Args:
        score (float): Puntaje del usuario.
        correct_count (int): Número de respuestas correctas.
        total (int): Número total de preguntas.
        temas_fallados (list, opcional): Lista de temas donde el usuario tuvo errores.

    Returns:
        str: Recomendación personalizada.
    """
    porcentaje = (correct_count / total) * 100 if total else 0  # Calcula el porcentaje
    # Selecciona el mensaje base según el score
    if score < 0.25:
        msg = "Desempeño muy bajo. Es fundamental repasar los conceptos básicos y practicar ejercicios introductorios. Considera buscar apoyo adicional (videos, tutorías, grupos de estudio)."
    elif score < 0.45:
        msg = "Resultado insuficiente. Identifica los temas que más te cuestan y utiliza recursos adicionales como resúmenes, videos o sesiones de consulta."
    elif score < 0.65:
        msg = "Avance regular. Repasa especialmente los temas donde cometiste errores y realiza ejercicios prácticos para afianzar el conocimiento."
    elif score < 0.8:
        msg = "¡Buen trabajo! Solo algunos detalles por pulir. Refuerza los temas donde tuviste dudas y realiza autoevaluaciones para consolidar tu aprendizaje."
    else:
        msg = "¡Excelente! Dominio sobresaliente del tema. Puedes avanzar a nuevos retos y profundizar en contenidos avanzados."
    # Si hay temas fallados, los agrega al mensaje
    if temas_fallados:
        msg += f" Temas a reforzar: {', '.join(set(temas_fallados))}."
    # Agrega resumen de aciertos
    msg += f" Aciertos: {correct_count}/{total} ({porcentaje:.1f}%)."
    return msg


def get_user_recommendations(user_folder: str):
    """
    Lee todas las recomendaciones de los tests de un usuario y genera una recomendación general.

    Args:
        user_folder (str): Ruta a la carpeta del usuario donde se encuentran los archivos de test.

    Returns:
        str: Recomendación general basada en el análisis de los tests.
    """
    recomendaciones = []  # Lista para almacenar recomendaciones
    if not os.path.isdir(user_folder):
        return "No hay datos suficientes para recomendar."
    # Recorre los archivos de test del usuario
    for fname in os.listdir(user_folder):
        if fname.startswith('test_') and fname.endswith('.json'):
            with open(os.path.join(user_folder, fname), 'r', encoding='utf-8') as f:
                data = json.load(f)
                rec = data.get('recomendacion')
                if rec:
                    recomendaciones.append(rec)
    if not recomendaciones:
        return "No hay recomendaciones registradas."
    # Si la mayoría de recomendaciones son excelentes, mensaje positivo
    excelentes = sum('excelente' in r.lower() for r in recomendaciones)
    if excelentes > len(recomendaciones) // 2:
        return "¡Tu progreso es excelente en la mayoría de materias! Sigue así."
    return "Sigue practicando y revisa los temas donde tuviste dificultades."


async def ollama_recommendation_llama32(resultados_test: dict, prompt_extra: str = "") -> str:
    """
    Genera una recomendación personalizada usando el modelo llama3.2:latest de Ollama.
    resultados_test: dict con claves como 'correctas', 'incorrectas', 'temas_fallados', 'materia', etc.
    prompt_extra: texto adicional para personalizar el prompt (opcional).

    Args:
        resultados_test (dict): Resultados del test del usuario.
        prompt_extra (str, opcional): Información adicional para el modelo.

    Returns:
        str: Recomendación generada por el modelo.
    """
    # Construye un resumen de los resultados del usuario
    resumen_usuario = (
        f"Materia: {resultados_test.get('materia', 'N/A')}\n"
        f"Aciertos: {resultados_test.get('correctas', 0)} / {resultados_test.get('total', 10)}\n"
        f"Temas fallados: {', '.join(resultados_test.get('temas_fallados', [])) if resultados_test.get('temas_fallados') else 'Ninguno'}\n"
        f"Porcentaje: {resultados_test.get('porcentaje', 0):.1f}%\n"
    )
    # Prompt para el modelo AI, pidiendo una recomendación breve y concreta
    prompt = (
        "Eres un orientador académico universitario. Analiza el siguiente resultado de test y responde SOLO con una recomendación breve y concreta (máximo 3 frases), poca motivación, que puedes ofrecer más recursos, solo el consejo clave para mejorar en la materia y los temas fallados.\n"
        f"{resumen_usuario}\n"
        f"{prompt_extra}\n"
        "Recomendación breve:"
    )
    client = ollama.AsyncClient()  # Cliente asíncrono de Ollama
    response = await client.generate(
        model="llama3.2:latest",
        prompt=prompt,
        options={"temperature": 0.7, "num_ctx": 2048}
    )
    # Limita la respuesta a 2 frases
    texto = response['response'].strip()
    texto_corto = '.'.join(texto.split('.')[:2]).strip()
    if not texto_corto.endswith('.'):
        texto_corto += '.'
    return texto_corto


async def recomendacion_fuzzy_con_llama32(resultados_test: dict, score: float, correct_count: int, total: int, temas_fallados: list = None) -> str:
    """
    Genera una recomendación personalizada usando la lógica difusa y la refina con llama3.2:latest.
    resultados_test: dict con claves como 'materia', 'correctas', 'incorrectas', 'temas_fallados', etc.

    Args:
        resultados_test (dict): Resultados del test del usuario.
        score (float): Puntaje del usuario.
        correct_count (int): Número de respuestas correctas.
        total (int): Número total de preguntas.
        temas_fallados (list, opcional): Lista de temas donde el usuario tuvo errores.

    Returns:
        str: Recomendación refinada generada por el modelo.
    """
    # Obtener recomendación difusa base
    rec_fuzzy = recommendation(score, correct_count, total, temas_fallados)
    resultados_test = dict(resultados_test)  # Copia para no modificar el original
    resultados_test['porcentaje'] = (correct_count / total) * 100 if total else 0
    # Prompt extra con la recomendación difusa
    prompt_extra = f"Recomendación generada por el sistema de lógica difusa: {rec_fuzzy}"
    # Llamar al modelo para refinar la recomendación
    recomendacion_final = await ollama_recommendation_llama32(resultados_test, prompt_extra=prompt_extra)
    return recomendacion_final
