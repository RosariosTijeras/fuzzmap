import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import os
import json

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

# Funciones de membresía para evaluación
# 0-40: deficiente, 30-70: regular, 60-100: excelente
evaluacion['deficiente'] = fuzz.trimf(evaluacion.universe, [0, 0, 40])
evaluacion['regular'] = fuzz.trimf(evaluacion.universe, [30, 60, 70])
evaluacion['excelente'] = fuzz.trimf(evaluacion.universe, [60, 100, 100])

# Reglas difusas
rule1 = ctrl.Rule(aciertos['bajo'] | porcentaje['bajo'], evaluacion['deficiente'])
rule2 = ctrl.Rule(aciertos['medio'] & porcentaje['medio'], evaluacion['regular'])
rule3 = ctrl.Rule(aciertos['alto'] & porcentaje['alto'], evaluacion['excelente'])
rule4 = ctrl.Rule(aciertos['alto'] & porcentaje['medio'], evaluacion['regular'])
rule5 = ctrl.Rule(aciertos['medio'] & porcentaje['alto'], evaluacion['regular'])

sistema_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5])
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

def recommendation(score: float) -> str:
    if score < 0.4:
        return "Revisa los conceptos básicos y repite el test."
    elif score < 0.7:
        return "Buen avance, pero aún puedes mejorar. Repasa los temas donde fallaste."
    else:
        return "¡Excelente desempeño! Puedes avanzar a temas más complejos."

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
