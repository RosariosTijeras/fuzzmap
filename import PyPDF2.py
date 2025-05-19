import PyPDF2
import json
import re

# Abrir el archivo PDF
pdf_file = open('1.pdf', 'rb')
pdf_reader = PyPDF2.PdfReader(pdf_file)

# Obtener el contenido del texto
texto = ""
for pagina in range(len(pdf_reader.pages)):
    pagina_texto = pdf_reader.pages[pagina].extract_text()
    texto += pagina_texto

# Reemplazar el patrón que precede a una fecha con un salto de línea
texto_con_saltos = re.sub(r'(.*?)(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2})', r'\1\n\2', texto)

# Dividir el texto en líneas
lineas = texto_con_saltos.split('\n')

# Carácter especial a eliminar
caracter_a_eliminar = ""

# Seleccionar las líneas a partir de la segunda línea y filtrar las que contienen "https://online"
lineas_relevantes = [linea.replace(caracter_a_eliminar, "").strip()
                     for linea in lineas[1:] 
                        if "https://online" not in linea 
                            and "puntúa" not in linea
                            and "calificación" not in linea
                            and "Pregunta" not in linea
                            and "Correcta" not in linea
                            and "|" not in linea
                            and  "Ir a..." not in linea
                            and "Actividad anterior" not in linea
                            and "Actividad siguiente" not in linea]

# Preparar los datos para el JSON
datos = {}
datos['lineas'] = lineas_relevantes

# Guardar en un archivo JSON
with open('bancodepreguntas.json', 'w', encoding='utf-8') as json_file:
    json.dump(datos, json_file, indent=4, ensure_ascii=False)

pdf_file.close()