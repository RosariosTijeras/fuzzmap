import PyPDF2
import json
import os
import re

def es_posible_encabezado_pie(linea):
    """Intenta identificar si una línea podría ser parte de un encabezado o pie de página."""
    # Criterios comunes: números de página, fechas, texto corto y centrado/alineado
    return bool(re.search(r'^\s*(\d+|[A-Za-z]+\s+\d+|\d+\s+[A-Za-z]+|\d{1,4}[-/]\d{1,4}[-/]\d{2,4}|\w+\s+\w+)\s*$', linea)) or \
           bool(len(linea.strip()) < 50 and (linea.strip().lower() in ['https://'])) or \
           bool(re.search(r'^\s*[A-Z][a-z]+\s+[A-Z][a-z]+', linea)) or \    

def extraer_contenido_sin_header_footer(ruta_pdf):
    """
    Extrae el contenido principal de un archivo PDF, intentando omitir encabezados y pies de página.

    Args:
        ruta_pdf (str): La ruta al archivo PDF.

    Returns:
        list: Una lista de cadenas de texto representando el contenido principal,
              o None si el archivo no se encuentra o hay un error al leerlo.
    """
    contenido_principal = []
    try:
        with open(ruta_pdf, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_paginas = len(pdf_reader.pages)

            for pagina_num in range(num_paginas):
                pagina = pdf_reader.pages[pagina_num]
                texto_pagina = pagina.extract_text().split('\n')

                # Heurística: Omitir las primeras y últimas N líneas (ajustar según sea necesario)
                lineas_pagina_filtradas = []
                num_lineas = len(texto_pagina)
                lineas_a_omitir =   # Ajustar según la estructura típica del PDF

                for i, linea in enumerate(texto_pagina):
                    if linea.strip() and not (i < lineas_a_omitir or i >= num_lineas - lineas_a_omitir or es_posible_encabezado_pie(linea)):
                        contenido_principal.append(linea)

        return contenido_principal
    except FileNotFoundError:
        print(f"Error: El archivo PDF '{ruta_pdf}' no se encontró.")
        return None
    except Exception as e:
        print(f"Error al leer el archivo PDF '{ruta_pdf}': {e}")
        return None

def procesar_multiples_pdfs_sin_header_footer(directorio_pdf=".", prefijo_archivo=""):
    """
    Procesa múltiples archivos PDF en un directorio y guarda el contenido principal
    (sin encabezados y pies de página intentados) en archivos JSON separados.

    Args:
        directorio_pdf (str): El directorio donde se encuentran los archivos PDF.
        prefijo_archivo (str): Un prefijo para filtrar los archivos PDF (opcional).
    """
    archivos_pdf = [f for f in os.listdir(directorio_pdf) if f.endswith(".pdf") and f.startswith(prefijo_archivo)]
    if not archivos_pdf:
        print(f"No se encontraron archivos PDF con el prefijo '{prefijo_archivo}' en el directorio '{directorio_pdf}'.")
        return

    for nombre_pdf in archivos_pdf:
        ruta_pdf = os.path.join(directorio_pdf, nombre_pdf)
        contenido = extraer_contenido_sin_header_footer(ruta_pdf)

        if contenido is not None:
            nombre_base = os.path.splitext(nombre_pdf)[0]
            nombre_json = f"{nombre_base}_sin_header_footer.json"
            ruta_json = os.path.join(directorio_pdf, nombre_json)

            datos = {'contenido_principal': contenido}

            with open(ruta_json, 'w', encoding='utf-8') as json_file:
                json.dump(datos, json_file, indent=4, ensure_ascii=False)
                print(f"Contenido principal de '{nombre_pdf}' guardado en '{nombre_json}'.")

if __name__ == "__main__":
    procesar_multiples_pdfs_sin_header_footer()
    # procesar_multiples_pdfs_sin_header_footer(directorio_pdf="./documentos_pdf", prefijo_archivo="informe_")