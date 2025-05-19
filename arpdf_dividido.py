import os
import json
import re
import PyPDF2

# Ruta de la carpeta que contiene los archivos PDF
ruta_carpeta = r'E:\Unach\Semestre2\EstructuraDatos\PRG_Formativa\fuzzmap'
# Nombre del archivo JSON de salida global
nombre_archivo_json_global = 'bancodepreguntas_global.json'
ruta_archivo_json_global = os.path.join(ruta_carpeta, nombre_archivo_json_global)

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

def extraer_preguntas(texto):
    preguntas = []
    lineas = texto.strip().split('\n')
    i = 0
    while i < len(lineas):
        if lineas[i].startswith("¿"):
            pregunta = lineas[i].strip()
            opciones = {}
            respuesta = None
            i += 1
            while i < len(lineas) and (lineas[i].startswith("a.") or lineas[i].startswith("b.") or lineas[i].startswith("c.") or lineas[i].startswith("d.") or lineas[i].startswith("e.") or lineas[i].startswith("f.") or lineas[i].startswith("g.")):
                opcion_match = re.match(r'([a-z]\.)\s*(.*)', lineas[i])
                if opcion_match:
                    letra = opcion_match.group(1).replace('.', '').strip()
                    contenido = opcion_match.group(2).strip()
                    opciones[letra] = contenido
                i += 1
            if i < len(lineas) and lineas[i].startswith("La respuesta correcta es:"):
                respuesta = lineas[i].replace("La respuesta correcta es:", "").strip()
                preguntas.append({
                    "pregunta": pregunta,
                    "opciones": opciones,
                    "respuesta": respuesta
                })
                i += 1
            else:
                # Si no se encuentra la respuesta inmediatamente después de las opciones,
                # avanzamos para evitar un bucle infinito.
                i += 1
        else:
            i += 1
    return preguntas

# Iterar sobre todos los archivos en la carpeta especificada
for nombre_archivo in os.listdir(ruta_carpeta):
    if nombre_archivo.lower().endswith(".pdf"):
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

                preguntas_encontradas = extraer_preguntas(texto_modificado)

                # Guardar las preguntas del archivo actual en un archivo JSON individual
                with open(ruta_archivo_json_individual, 'w', encoding='utf-8') as json_file_individual:
                    json.dump({"preguntas": preguntas_encontradas}, json_file_individual, indent=4, ensure_ascii=False)
                print(f"Se procesó el archivo: {nombre_archivo} y se guardaron sus preguntas en: {nombre_archivo_json_individual}")

        except Exception as e:
            print(f"Ocurrió un error al procesar el archivo {nombre_archivo}: {e}")

# Guardar todas las preguntas de todos los archivos en un único archivo JSON global
todas_las_preguntas = []
for nombre_archivo in os.listdir(ruta_carpeta):
    if nombre_archivo.lower().endswith("_bancodepreguntas.json"):
        ruta_archivo_json_individual = os.path.join(ruta_carpeta, nombre_archivo)
        try:
            with open(ruta_archivo_json_individual, 'r', encoding='utf-8') as json_file_individual:
                datos_individual = json.load(json_file_individual)
                todas_las_preguntas.extend(datos_individual.get("preguntas", []))
        except Exception as e:
            print(f"Ocurrió un error al procesar el archivo JSON {nombre_archivo}: {e}")

# Guardar todas las preguntas de todos los archivos en un único archivo JSON global
ruta_archivo_json_global = os.path.join(ruta_carpeta, "banco_de_preguntas_global.json")
with open(ruta_archivo_json_global, 'w', encoding='utf-8') as json_file_global:
    json.dump({"preguntas": todas_las_preguntas}, json_file_global, indent=4, ensure_ascii=False)
print(f"Se guardaron todas las preguntas en: {ruta_archivo_json_global}")
