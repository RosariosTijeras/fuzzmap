# Lógica difusa para evaluación de tests

def evaluate_performance(correct_count: int, total: int) -> float:
    """
    Devuelve un score difuso entre 0.0 y 1.0 basado en aciertos.
    """
    return correct_count / total if total else 0.0

def recommendation(score: float) -> str:
    if score < 0.5:
        return "Revisa los conceptos básicos."
    elif score < 0.8:
        return "Buen avance, practica más ejercicios."
    else:
        return "Excelente, avanza a temas avanzados."
