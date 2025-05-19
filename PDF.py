import PyPDF2
import json

# Abrir el archivo PDF
pdf_file = open('1.pdf', 'rb')
pdf_reader = PyPDF2.PdfReader(pdf_file)

# Obter el contenido del texto
texto = ""
for pagina in range(len(pdf_reader.pages)):
    pagina_texto = pdf_reader.pages[pagina].extract_text()
    texto += pagina_texto

# Dividir el texto en líneas
lineas = texto.split('\n')

# Seleccionar las líneas a partir de la quinta línea
lineas_relevantes = lineas[1:]

# Preparar los datos para el JSON
datos = {}
datos['lineas'] = lineas_relevantes

# Guardar en un archivo JSON
with open('nombre_del_archivo.json', 'w', encoding='utf-8') as json_file:
    json.dump(datos, json_file, indent=4, ensure_ascii=False)

pdf_file.close()