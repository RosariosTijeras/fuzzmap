import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import os
import json
import ollama

# Definir el universo de variables
aciertos = ctrl.Antecedent(np.arange(0, 11, 1), 'aciertos')  # 0 a 10 preguntas
porcentaje = ctrl.Antecedent(np.arange(0, 101, 1), 'porcentaje')  # 0% a 100%
evaluacion = ctrl.Consequent(np.arange(0, 101, 1), 'evaluacion')  # 0% a 100%

# Funciones de membresía para aciertos
aciertos['bajo'] = fuzz.trimf(aciertos.universe, [0, 0, 5])
aciertos['medio'] = fuzz.trimf(aciertos.universe, [2, 5, 8])
aciertos['alto'] = fuzz.trimf(aciertos.universe, [6, 10, 10])

# Funciones de membresía para porcentaje
porcentaje['bajo'] = fuzz.trimf(porcentaje.universe, [0, 0, 50])
porcentaje['medio'] = fuzz.trimf(porcentaje.universe, [30, 60, 80])
porcentaje['alto'] = fuzz.trimf(porcentaje.universe, [70, 100, 100])

# Funciones de membresía para evaluación (más niveles)
evaluacion['muy_deficiente'] = fuzz.trimf(evaluacion.universe, [0, 0, 25])
evaluacion['deficiente'] = fuzz.trimf(evaluacion.universe, [15, 30, 45])
evaluacion['regular'] = fuzz.trimf(evaluacion.universe, [35, 50, 65])
evaluacion['bueno'] = fuzz.trimf(evaluacion.universe, [55, 70, 85])
evaluacion['excelente'] = fuzz.trimf(evaluacion.universe, [80, 100, 100])

# Reglas difusas más finas
rule1 = ctrl.Rule(aciertos['bajo'] & porcentaje['bajo'], evaluacion['muy_deficiente'])
rule2 = ctrl.Rule(aciertos['bajo'] & porcentaje['medio'], evaluacion['deficiente'])
rule3 = ctrl.Rule(aciertos['bajo'] & porcentaje['alto'], evaluacion['deficiente'])
rule4 = ctrl.Rule(aciertos['medio'] & porcentaje['bajo'], evaluacion['deficiente'])
rule5 = ctrl.Rule(aciertos['medio'] & porcentaje['medio'], evaluacion['regular'])
rule6 = ctrl.Rule(aciertos['medio'] & porcentaje['alto'], evaluacion['bueno'])
rule7 = ctrl.Rule(aciertos['alto'] & porcentaje['bajo'], evaluacion['regular'])
rule8 = ctrl.Rule(aciertos['alto'] & porcentaje['medio'], evaluacion['bueno'])
rule9 = ctrl.Rule(aciertos['alto'] & porcentaje['alto'], evaluacion['excelente'])

sistema_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9])
sistema = ctrl.ControlSystemSimulation(sistema_ctrl)

def evaluate_performance(correct_count: int, total: int) -> float:
    """
    Evalúa el rendimiento usando lógica difusa robusta (scikit-fuzzy).
    Devuelve un score entre 0 y 1.
    """
    if total == 0:
        return 0.0
    porcentaje_val = (correct_count / total) * 100
    sistema.input['aciertos'] = correct_count
    sistema.input['porcentaje'] = porcentaje_val
    sistema.compute()
    resultado = sistema.output['evaluacion'] / 100.0
    return resultado

def recommendation(score: float, correct_count: int, total: int, temas_fallados: list = None) -> str:
    porcentaje = (correct_count / total) * 100 if total else 0
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
    if temas_fallados:
        msg += f" Temas a reforzar: {', '.join(set(temas_fallados))}."
    msg += f" Aciertos: {correct_count}/{total} ({porcentaje:.1f}%)."
    return msg

def get_user_recommendations(user_folder: str):
    """
    Lee todas las recomendaciones de los tests de un usuario y genera una recomendación general.
    """
    recomendaciones = []
    if not os.path.isdir(user_folder):
        return "No hay datos suficientes para recomendar."
    for fname in os.listdir(user_folder):
        if fname.startswith('test_') and fname.endswith('.json'):
            with open(os.path.join(user_folder, fname), 'r', encoding='utf-8') as f:
                data = json.load(f)
                rec = data.get('recomendacion')
                if rec:
                    recomendaciones.append(rec)
    if not recomendaciones:
        return "No hay recomendaciones registradas."
    # Lógica simple: si la mayoría son excelentes, recomendación positiva, si no, sugerir repaso
    excelentes = sum('excelente' in r.lower() for r in recomendaciones)
    if excelentes > len(recomendaciones) // 2:
        return "¡Tu progreso es excelente en la mayoría de materias! Sigue así."
    return "Sigue practicando y revisa los temas donde tuviste dificultades."

async def ollama_recommendation_llama32(resultados_test: dict, prompt_extra: str = "") -> str:
    """
    Genera una recomendación personalizada usando el modelo llama3.2:latest de Ollama.
    resultados_test: dict con claves como 'correctas', 'incorrectas', 'temas_fallados', 'materia', etc.
    prompt_extra: texto adicional para personalizar el prompt (opcional).
    """
    resumen_usuario = (
        f"Materia: {resultados_test.get('materia', 'N/A')}\n"
        f"Aciertos: {resultados_test.get('correctas', 0)} / {resultados_test.get('total', 10)}\n"
        f"Temas fallados: {', '.join(resultados_test.get('temas_fallados', [])) if resultados_test.get('temas_fallados') else 'Ninguno'}\n"
        f"Porcentaje: {resultados_test.get('porcentaje', 0):.1f}%\n"
    )
    prompt = (
        "Eres un orientador académico universitario. Analiza el siguiente resultado de test y responde SOLO con una recomendación breve y concreta (máximo 3 frases), poca motivación, que puedes ofrecer más recursos, solo el consejo clave para mejorar en la materia y los temas fallados.\n"
        f"{resumen_usuario}\n"
        f"{prompt_extra}\n"
        "Recomendación breve:"
    )
    client = ollama.AsyncClient()
    response = await client.generate(
        model="llama3.2:latest",
        prompt=prompt,
        options={"temperature": 0.7, "num_ctx": 2048}
    )
    # Limitar a 2 frases
    texto = response['response'].strip()
    texto_corto = '.'.join(texto.split('.')[:2]).strip()
    if not texto_corto.endswith('.'):
        texto_corto += '.'
    return texto_corto

async def recomendacion_fuzzy_con_llama32(resultados_test: dict, score: float, correct_count: int, total: int, temas_fallados: list = None) -> str:
    """
    Genera una recomendación personalizada usando la lógica difusa y la refina con llama3.2:latest.
    resultados_test: dict con claves como 'materia', 'correctas', 'incorrectas', 'temas_fallados', etc.
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
