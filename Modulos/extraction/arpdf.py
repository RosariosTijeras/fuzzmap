import os
import json
import re
import PyPDF2

# Definir rutas de las carpetas independientes
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ruta_carpeta1 = os.path.join(base_dir, 'Datos', 'Ciencia_Datos')
ruta_carpeta2 = os.path.join(base_dir, 'Datos', 'Habilidades_Vida')

print(f"Ruta de la carpeta 1: {ruta_carpeta1}")  # Debug
print(f"Ruta de la carpeta 2: {ruta_carpeta2}")  # Debug

# Caracteres especiales a eliminar
caracteres_a_eliminar = ["", "'", ";", ""]

# Palabras o frases a excluir
palabras_a_excluir = [
    "https://online",
    "puntúa",
    "calificación",
    "Pregunta",
    "Correcta",
    "|",
    "Ir a...",
    "Actividad anterior",
    "Actividad siguiente",
]

def should_start_new_item(line):
    # print(f"should_start_new_item called with: {line}")  # Debug
    return line.strip().startswith("¿") or line.strip().startswith("a.") or line.strip().startswith("b.") or line.strip().startswith("c.") or line.strip().startswith("La respuesta correcta es:")

def procesar_carpeta(ruta_carpeta, nombre_archivo_json_global):
    todas_las_lineas = []
    for nombre_archivo in os.listdir(ruta_carpeta):
        if nombre_archivo.lower().endswith(".pdf"):
            print(f"Leyendo archivo PDF: {nombre_archivo}")
            ruta_archivo_pdf = os.path.join(ruta_carpeta, nombre_archivo)
            nombre_archivo_base = os.path.splitext(nombre_archivo)[0]
            nombre_archivo_json_individual = f"{nombre_archivo_base}_bancodepreguntas.json"
            ruta_archivo_json_individual = os.path.join(ruta_carpeta, nombre_archivo_json_individual)

            try:
                with open(ruta_archivo_pdf, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    texto_completo = ""
                    for pagina in range(len(pdf_reader.pages)):
                        pagina_texto = pdf_reader.pages[pagina].extract_text()
                        texto_completo += pagina_texto + "\n"

                    # Eliminamos los caracteres problemáticos del texto completo
                    for char_eliminar in caracteres_a_eliminar:
                        texto_completo = texto_completo.replace(char_eliminar, "")

                    # Borramos todo desde "Justificación" (ignorando mayúsculas) hasta el final de la línea
                    texto_modificado = re.sub(r'(.*?)Justificación.*', r'\1', texto_completo, flags=re.IGNORECASE)

                    lineas = texto_modificado.split('\n')
                    lineas_relevantes_archivo = []
                    linea_anterior = None
                    for linea in lineas[1:]:
                        linea_limpia = linea.strip()
                        if linea_limpia and not any(palabra in linea_limpia for palabra in palabras_a_excluir):
                            if linea_anterior is not None and not should_start_new_item(linea_limpia):
                                lineas_relevantes_archivo[-1] += " " + linea_limpia
                                linea_anterior = lineas_relevantes_archivo[-1]
                            else:
                                lineas_relevantes_archivo.append(linea_limpia)
                                linea_anterior = linea_limpia
                        elif not lineas_relevantes_archivo:
                            linea_anterior = None
                        elif linea_anterior is not None and not should_start_new_item(linea_limpia):
                            linea_anterior = linea_limpia
                        elif linea_anterior is not None and not linea_limpia:
                            linea_anterior = None

                    todas_las_lineas.extend(lineas_relevantes_archivo)

                    # Guardar las líneas relevantes del archivo actual en un archivo JSON individual
                    datos_individual = {"lineas": lineas_relevantes_archivo}
                    with open(ruta_archivo_json_individual, 'w', encoding='utf-8') as json_file_individual:
                        json.dump(datos_individual, json_file_individual, indent=4, ensure_ascii=False)
                    print(f"Se procesó el archivo: {nombre_archivo} y se guardaron sus preguntas en: {nombre_archivo_json_individual}")

            except Exception as e:
                print(f"Ocurrió un error al procesar el archivo {nombre_archivo}: {e}")

    # Guardar todas las líneas relevantes de todos los archivos (incluyendo duplicados) en un único archivo JSON global
    ruta_archivo_json_global = os.path.join(os.path.dirname(ruta_carpeta), nombre_archivo_json_global)
    datos_global = {"lineas": todas_las_lineas}
    with open(ruta_archivo_json_global, 'w', encoding='utf-8') as json_file_global:
        json.dump(datos_global, json_file_global, indent=4, ensure_ascii=False)

    print(f"\nSe procesaron todos los archivos PDF y todas las preguntas relevantes (incluyendo duplicados) se guardaron en: {nombre_archivo_json_global}")

# Procesar ambas carpetas de forma independiente
procesar_carpeta(ruta_carpeta1, 'bancodepreguntas_global_cienciadatos.json')
procesar_carpeta(ruta_carpeta2, 'bancodepreguntas_global_habilidadesvida.json')