from Modulos.ui.app import run_app
from Modulos.auth.auth import registrar_usuario, autenticar_usuario

# Diccionario mínimo de prueba
questions = {"Demo": [("¿Qué es FuzzMap?", "Asistente inteligente de estudio")]}
run_app(questions)
