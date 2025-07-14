import os # Para manejar rutas de archivos
import json # Para manejar archivos JSON
import re # Para expresiones regulares
import glob # Para buscar archivos con patrones
import requests # Para hacer peticiones HTTP

#----------------------#
class CienciaDatosProcessor: # Procesador para los archivos de Ciencia de Datos
    def __init__(self): # Inicializa las rutas de los archivos
        # Ruta de la carpeta que contiene los archivos JSON
        self.ruta_carpeta=os.path.join(os.path.dirname(__file__), "..","..", "Datos", "Ciencia_Datos", "json_quiz")
        # Carpeta donde se guardarán los archivos ordenados
        self.carpeta_salida=os.path.join(os.path.dirname(__file__), "json_ordenados")
        # Ruta del archivo de salida
        self.salida=os.path.join(self.carpeta_salida, "ciencia_datos_ordenado.json")

    def es_pregunta(self, linea): # Verifica si una línea es una pregunta
        return bool(re.match(r"^¿.*\?\s*$", linea.strip())) # Devuelve True si es una pregunta

    def extraer_opciones(self, lineas): # Extrae las opciones de respuesta de las líneas
        opciones = [] # Lista para almacenar las opciones
        for linea in lineas: # Itera sobre cada línea
            m=re.match(r"^([a-cA-C])[\.\)]\s?(.*)", linea) # Busca el patrón de opción
            if m: # Si se encuentra una opción
                letra, texto=m.groups() # Obtiene la letra y el texto de la opción
                texto_limpio=re.sub(r"Sin contestar", "", texto, flags=re.IGNORECASE).strip() # Limpia el texto de la opción
                texto_limpio=re.sub(r"\s{2,}", " ", texto_limpio) # Reemplaza múltiples espacios por uno solo
                opciones.append(f"{letra}) {texto_limpio}".strip()) # Agrega la opción a la lista
        return opciones # Devuelve la lista de opciones

    def ordenar_json_ciencia_datos(self, lineas): # Ordena las preguntas y opciones de un JSON de Ciencia de Datos
        preguntas_ordenadas = [] # Lista para almacenar las preguntas ordenadas
        i=0 # Índice para iterar sobre las líneas
        num_pregunta=1 # Número de la pregunta actual
        while i<len(lineas): # Mientras haya líneas por procesar
            linea = lineas[i].strip() # Limpia la línea actual
            if self.es_pregunta(linea): # Si la línea es una pregunta
                pregunta=linea # Guarda la pregunta
                opciones=self.extraer_opciones(lineas[i+1:i+4]) # Extrae las opciones de las siguientes líneas
                respuesta_correcta = "" # Inicializa la respuesta correcta
                j=i+4 # Comienza a buscar la respuesta correcta después de las opciones
                while j<len(lineas) and not self.es_pregunta(lineas[j]): # Mientras no se encuentre otra pregunta o la respuesta correcta 
                    if lineas[j].startswith("La respuesta correcta es:"): # Si la línea indica la respuesta correcta
                        texto_resp=lineas[j].split(":", 1)[1].strip() # Obtiene el texto de la respuesta correcta
                        for op in opciones: # Compara la respuesta correcta con las opciones
                            if texto_resp in op or op in texto_resp: # Si hay coincidencia se guarda la respuesta
                                respuesta_correcta=op 
                                break 
                        break 
                    j+=1 # Avanza al siguiente índice
                # Agrega la pregunta ordenada a la lista
                preguntas_ordenadas.append({
                    "numero": num_pregunta, 
                    "pregunta": pregunta, 
                    "opciones": opciones,
                    "respuesta_correcta": respuesta_correcta
                })
                num_pregunta+=1 # Incrementa el número de la pregunta
                i=j # Avanza al índice de la respuesta correcta
            else: # Si la línea no es una pregunta simplemente avanza al siguiente índice
                i+=1 
        return preguntas_ordenadas 

    def procesar(self): # Procesa los archivos JSON de Ciencia de Datos
        archivos_json=glob.glob(os.path.join(self.ruta_carpeta, "*.json")) # Busca todos los archivos JSON en la carpeta
        todas_preguntas = [] # Lista para almacenar todas las preguntas
        for archivo in archivos_json: # Itera sobre cada archivo JSON encontrado
            with open(archivo, 'r', encoding='utf-8') as f: # Abre el archivo JSON con codificación UTF-8
                datos=json.load(f) # Carga el contenido del archivo JSON
            lineas=datos.get('lineas', []) # Obtiene las líneas del JSON
            preguntas=self.ordenar_json_ciencia_datos(lineas) # Ordena las preguntas y opciones
            todas_preguntas.extend(preguntas) # Agrega las preguntas ordenadas a la lista de todas las preguntas
        if not os.path.exists(self.carpeta_salida): # Si la carpeta de salida no existe la crea
            os.makedirs(self.carpeta_salida) 
        resultado = { # Crea un diccionario con el resultado final
            "materia": "Ciencia_Datos", 
            "preguntas": todas_preguntas 
        }
        with open(self.salida, 'w', encoding='utf-8') as f: # Abre el archivo de salida para escribir
            json.dump(resultado, f, ensure_ascii=False, indent=4) # Guarda el resultado en formato JSON
        print(f"Archivo generado: {self.salida}") # Imprime un mensaje indicando que el archivo ha sido generado

if __name__ == "__main__": # Si este archivo es ejecutado directamente
    procesador=CienciaDatosProcessor() # Crea una instancia del procesador
    procesador.procesar() # Llama al método para procesar los archivos JSON

#----------------------#
class HabilidadesVidaProcessor: # Procesador para los archivos de Habilidades de Vida
    def __init__(self): # Inicializa las rutas de los archivos
        # Ruta de la carpeta que contiene los archivos JSON
        self.ruta_carpeta=os.path.join(os.path.dirname(__file__), "..", "..", "Datos", "Habilidades_Vida","json_quiz")
        # Carpeta donde se guardarán los archivos ordenados
        self.carpeta_salida=os.path.join(os.path.dirname(__file__), "json_ordenados")
        # Ruta del archivo de salida
        self.salida=os.path.join(self.carpeta_salida, "habilidades_vida_ordenado.json")

    def limpiar_repeticion_una_respuesta_a(self, texto): # Limpia la repetición de "una respuesta a" en el texto
        primera=texto.find("una respuesta a")  # Busca la primera aparición de "una respuesta a"
        if primera==-1: # Si no se encuentra, devuelve el texto original
            return texto 
        antes=texto[:primera+len("una respuesta a")] # Parte del texto antes de "una respuesta a"
        despues=texto[primera+len("una respuesta a"):].replace("una respuesta a", "") # Parte del texto después de "una respuesta a"
        return (antes + despues).replace("  ", " ").strip(", ") # Combina ambas partes elimina espacios dobles y comas al final

    def es_pregunta(self, linea): # Verifica si una línea es una pregunta
        return bool(re.match(r"^¿.*\?\s*$", linea.strip())) # Devuelve True si es una pregunta

    def limpiar_opcion(self, texto): # Limpia el texto de una opción de respuesta
        texto=re.sub(r'\\".*?\\"', '', texto) # Elimina comillas dobles y su contenido
        texto=re.split(r'\\"', texto)[0] # Divide el texto por comillas y toma la primera parte
        # Elimina patrones específicos que no son relevantes para la opción
        patrones = [
            r'Bibliografía:', r'\"', r' adecuadamente,', r'atención de nuevo a la respiración,',
            r' preocupación persistente y excesiva sobre diversos aspectos de la vida cotidiana,',
            r'Incorrecta Incorrecta', r'suelen experimentar', r'focalizado en situaciones sociales específicas,',
            r'demandas o presiones específicas',
            r'ejercer una función adaptativa, motivando al estudiante a optimizar su preparación y rendimiento',
            r'a los estudiantes incluso en ausencia de una amenaza inmediata, impactando negativamente en su bienestar psicológico y rendimiento académico',
            r'relajación muscular progresiva pueden ser herramientas efectivas para aliviar tensiones y promover la calma',
            r'aprender de nuevas experiencias es crucial para enfrentar los retos académicos y personales',
            r'caracterizada por una preocupación y un temor desproporcionados en relación con la amenaza real percibida',
            r'puede usar la técnica de respiración profunda', r', el siguiente paso es', r'Justificaci[oó]n:'
        ]
        patron_regex="|".join(patrones) # Crea un patrón regex con los patrones a eliminar
        texto=re.split(patron_regex, texto, flags=re.IGNORECASE)[0] # Divide el texto por el patrón y toma la primera parte
        return texto.strip() # Devuelve el texto limpio

    def extraer_opciones(self, lineas): # Extrae las opciones de respuesta de las líneas
        opciones = [] # Lista para almacenar las opciones
        opcion_actual = "" # Variable para almacenar la opción actual
        letra_actual = "" # Variable para almacenar la letra de la opción actual
        for linea in lineas: # Itera sobre cada línea
            m = re.match(r"^([a-cA-C])[\.\)]\s?(.*)$", linea) # Busca el patrón de opción
            if m: # Si se encuentra una opción y hay una opción actual, la agrega a la lista y la limpia
                if letra_actual and opcion_actual: 
                    limpia=self.limpiar_opcion(opcion_actual) 
                    # Agrega la opción limpia a la lista
                    opciones.append(f"{letra_actual}) {limpia}".strip() if limpia else f"{letra_actual})")
                letra_actual, texto=m.groups() # Obtiene la letra y el texto de la opción
                opcion_actual=texto.strip() # Limpia el texto de la opción
            else: # Si no se encuentra un patrón de opción agrega el texto a la opción actual
                if opcion_actual: 
                    opcion_actual+=" "+linea.strip() 
        if letra_actual: # Si hay una opción actual al final la limpia y agrega a la lista
            limpia=self.limpiar_opcion(opcion_actual) 
            opciones.append(f"{letra_actual}) {limpia}".strip() if limpia else f"{letra_actual})") 
        return opciones 

    def ordenar_json_habilidades_vida(self, lineas): # Ordena las preguntas y opciones de un JSON de Habilidades de Vida
        preguntas_ordenadas = [] # Lista para almacenar las preguntas ordenadas
        i=0 # Índice para iterar sobre las líneas
        num_pregunta=1 # Número de la pregunta actual
        while i<len(lineas): # Mientras haya líneas por procesar, limpia la línea actual
            linea = lineas[i].strip() 
            if self.es_pregunta(linea): # Si la línea es una pregunta, la guarda en la lista
                pregunta=linea 
                opciones_lineas=[]
                j=i+1 # Comienza a buscar las opciones de respuesta después de la pregunta
                while j<len(lineas) and not self.es_pregunta(lineas[j]) and not lineas[j].startswith("La respuesta correcta es:"): 
                    opciones_lineas.append(lineas[j])
                    j+=1 # Mientras no se encuentre otra pregunta o la respuesta correcta, agrega las líneas a las opciones
                opciones=self.extraer_opciones(opciones_lineas) # Extrae las opciones de las líneas recopiladas
                respuesta_correcta = "" # Inicializa la respuesta correcta
                if j<len(lineas) and lineas[j].startswith("La respuesta correcta es:"): # Si la línea indica la respuesta correcta
                    texto_resp=lineas[j].split(":", 1)[1].strip() # Obtiene el texto de la respuesta correcta
                    texto_resp=self.limpiar_opcion(texto_resp) # Limpia el texto de la respuesta correcta
                    for op in opciones: # Compara la respuesta correcta con las opciones, si hay coincidencia se guarda la respuesta
                        if texto_resp in op or op in texto_resp: 
                            respuesta_correcta = op 
                            break
                    j+=1 # Avanza al siguiente índice
                # Agrega la pregunta ordenada a la lista
                preguntas_ordenadas.append({
                    "numero": num_pregunta,
                    "pregunta": pregunta,
                    "opciones": opciones,
                    "respuesta_correcta": respuesta_correcta,
                })
                num_pregunta+=1 # Incrementa el número de la pregunta
                i=j # Avanza al índice de la respuesta correcta
            else: # Si la línea no es una pregunta simplemente avanza al siguiente índice
                i+=1
        return preguntas_ordenadas 

    def procesar(self): # Procesa los archivos JSON de Habilidades de Vida
        archivos_json=glob.glob(os.path.join(self.ruta_carpeta, "*.json")) # Busca todos los archivos JSON en la carpeta
        todas_preguntas = [] # Lista para almacenar todas las preguntas
        for archivo in archivos_json: # Itera sobre cada archivo JSON encontrado
            with open(archivo, 'r', encoding='utf-8') as f: # Abre el archivo JSON con codificación UTF-8
                datos=json.load(f) # Carga el contenido del archivo JSON
            lineas=datos.get('lineas', []) # Obtiene las líneas del JSON
            preguntas=self.ordenar_json_habilidades_vida(lineas) # Ordena las preguntas y opciones
            todas_preguntas.extend(preguntas) # Agrega las preguntas ordenadas a la lista de todas las preguntas
        if not os.path.exists(self.carpeta_salida): # Si la carpeta de salida no existe la crea
            os.makedirs(self.carpeta_salida) 
        resultado = { # Crea un diccionario con el resultado final
            "materia": "Habilidades_Vida",
            "preguntas": todas_preguntas
        }
        
        if resultado["preguntas"]: # Si hay preguntas en el resultado, limpia la primera pregunta
            primera = resultado["preguntas"][0] 
            # Limpia las opciones y la respuesta correcta de la primera pregunta
            primera["opciones"]=[self.limpiar_repeticion_una_respuesta_a(op) for op in primera["opciones"]]
            primera["respuesta_correcta"] = self.limpiar_repeticion_una_respuesta_a(primera["respuesta_correcta"])
        for pregunta in resultado["preguntas"]: # Recorre todas las preguntas y limpia las opciones
            if pregunta["numero"]==5: # Si es la pregunta 5, limpia las opciones específicas
                nuevas_opciones = [] # Lista para almacenar las nuevas opciones
                for op in pregunta["opciones"]: # Recorre las opciones de la pregunta
                    if op.startswith("a)"): # Si la opción comienza con "a)", la limpia 
                        op=op.replace(" abdomen con aire", "") 
                    nuevas_opciones.append(op) # Agrega la opción limpia a la lista de nuevas opciones
                pregunta["opciones"] = nuevas_opciones 
        with open(self.salida, 'w', encoding='utf-8') as f: # Abre el archivo de salida para escribir
            json.dump(resultado, f, ensure_ascii=False, indent=4) # Guarda el resultado en formato JSON
        print(f"Archivo generado: {self.salida}") # Imprime un mensaje indicando que el archivo ha sido generado

if __name__ == "__main__": 
    habilidades=HabilidadesVidaProcessor() 
    habilidades.procesar() 

#----------------------#

class RespuestaAutomaticaProcessor: # Procesador para generar respuestas automáticas
    def __init__(self): # Inicializa las rutas de los archivos y el modelo de Ollama
        # Ruta del archivo de respuestas manuales
        self.respuestas_manual_path=os.path.join(os.path.dirname(__file__), "respuestas_manual.json")
        if os.path.exists(self.respuestas_manual_path): # Si el archivo de respuestas manuales existe, lo carga
            with open(self.respuestas_manual_path, "r", encoding="utf-8") as f: # Abre el archivo 
                self.RESPUESTAS_MANUAL=json.load(f) # Carga el contenido del archivo JSON
        else: # Si el archivo no existe, inicializa un diccionario vacío
            self.RESPUESTAS_MANUAL = {} # Diccionario para almacenar respuestas manuales
        self.OLLAMA_URL = "http://localhost:11434/api/generate" # URL del servicio Ollama
        self.OLLAMA_MODEL = "mistral:7b-instruct"  # Modelo pequeño

    def obtener_respuesta_manual(self, pregunta): # Obtiene la respuesta manual para una pregunta específica
        return self.RESPUESTAS_MANUAL.get(pregunta, "") # Devuelve la respuesta manual si existe, de lo contrario devuelve una cadena vacía
    
    # Obtiene una respuesta de Ollama para una pregunta específica
    def obtener_justificacion_ollama(self, pregunta, respuesta_correcta): 
        prompt = ( 
            f"Pregunta: {pregunta}\n" # Pregunta a justificar
            f"Respuesta correcta: {respuesta_correcta}\n" # Respuesta correcta a justificar
            "Explica brevemente por qué esta es la respuesta correcta. Sé claro, sencillo y corto." # Justificación a generar
        )
        try: # Intenta hacer una petición a Ollama para obtener la justificación
            response = requests.post(self.OLLAMA_URL, json={ # Petición a Ollama
                "model": self.OLLAMA_MODEL, # Modelo a utilizar
                "prompt": prompt, # Prompt con la pregunta y respuesta correcta
                "stream": False, # No usar streaming
            }, timeout=120) # Establece un tiempo de espera de 120 segundos
            response.raise_for_status() # Lanza un error si la respuesta no es exitosa
            data = response.json() # Convierte la respuesta a JSON
            return data.get("response", "").strip() # Devuelve la respuesta de Ollama, eliminando espacios al inicio y al final
        except Exception as e: # Si ocurre un error, imprime el error y devuelve un mensaje de error
            print(f"[ERROR] Justificación Ollama: {e}") # Imprime el error
            return "Justificación no disponible." # Mensaje de error si no se puede obtener la justificación
        
    # Obtiene una retroalimentación de Ollama para una pregunta y respuesta específica
    def obtener_retroalimentacion_ollama(self, pregunta, respuesta_correcta): 
        prompt = ( # Prompt con la pregunta y respuesta correcta
            f"Pregunta: {pregunta}\n" # Pregunta a retroalimentar
            f"Respuesta correcta: {respuesta_correcta}\n" # Respuesta correcta a retroalimentar
            "Dale una retroalimentación breve y sencilla al usuario, como un apoyo de manera sencilla y corta." # Retroalimentación a generar
        )
        try: # Intenta hacer una petición a Ollama para obtener la retroalimentación
            response = requests.post(self.OLLAMA_URL, json={ # Petición a Ollama
                "model": self.OLLAMA_MODEL, # Modelo a utilizar
                "prompt": prompt, # Prompt con la pregunta y respuesta correcta
                "stream": False, 
            }, timeout=120) # Establece un tiempo de espera de 120 segundos
            response.raise_for_status() # Lanza un error si la respuesta no es exitosa
            data = response.json() # Convierte la respuesta a JSON
            return data.get("response", "").strip() 
        except Exception as e: # Si ocurre un error, imprime el error y devuelve un mensaje de error
            print(f"[ERROR] Retroalimentación Ollama: {e}")
            return "Retroalimentación no disponible." # Mensaje de error si no se puede obtener la retroalimentación

    def completar_respuestas_json(self, path_json): # Completa las respuestas en un archivo JSON dado
        with open(path_json, "r", encoding="utf-8") as f: # Abre el archivo JSON 
            data = json.load(f) # Carga el contenido del archivo JSON

        for pregunta in data["preguntas"]: # Itera sobre cada pregunta en el JSON
            # Si ya tiene respuesta, la deja, si no, busca en el manual
            respuesta = pregunta.get("respuesta_correcta", "")
            if not respuesta or respuesta == "No disponible": 
                respuesta_manual = self.obtener_respuesta_manual(pregunta.get("pregunta", ""))
                if respuesta_manual: 
                    pregunta["respuesta_correcta"] = respuesta_manual
                else:
                    pregunta["respuesta_correcta"] = "No disponible"

            # Siempre genera justificación y retroalimentación con la respuesta que tenga
            pregunta["retroalimentacion"] = self.obtener_retroalimentacion_ollama(
                pregunta.get("pregunta", ""), pregunta["respuesta_correcta"]
            )
            pregunta["justificacion"] = self.obtener_justificacion_ollama(
                pregunta.get("pregunta", ""), pregunta["respuesta_correcta"]
            )

            # Imprime en formato amigable
            print(f'Pregunta: "{pregunta.get("pregunta", "")}"\n')
            print("Opciones:")
            for op in pregunta.get("opciones", []):
                print(op)
            print(f'\nRespuesta Correcta: {pregunta["respuesta_correcta"]}\n')
            print("Retroalimentación")
            print(pregunta["retroalimentacion"])
            print("\nJustificación")
            print(pregunta["justificacion"])
            print("\n" + "-"*60 + "\n") 
            
        # Guarda el JSON con las respuestas completadas en una carpeta específica
        carpeta_salida = os.path.join(os.path.dirname(__file__), "json_ordenados_completos")
        if not os.path.exists(carpeta_salida): # Si la carpeta de salida no existe, la crea
            os.makedirs(carpeta_salida) 
        # Define el nombre del archivo de salida basado en el nombre del archivo de entrada
        nombre_archivo = os.path.basename(path_json).replace(".json", "_completado.json") 
        salida = os.path.join(carpeta_salida, nombre_archivo) # Ruta completa del archivo de salida

        with open(salida, "w", encoding="utf-8") as f: # Abre el archivo de salida para escribir
            json.dump(data, f, ensure_ascii=False, indent=4) # Guarda el contenido del JSON con las respuestas completadas
        print(f"Archivo guardado: {salida}") # Imprime un mensaje indicando que el archivo ha sido guardado

# Ejemplo de uso:
if __name__ == "__main__": 
    procesador=RespuestaAutomaticaProcessor()
    # Completa las respuestas de los archivos JSON de Ciencia de Datos y Habilidades de Vida
    procesador.completar_respuestas_json( 
        os.path.join(os.path.dirname(__file__), "json_ordenados", "ciencia_datos_ordenado.json")
    )
    # Completa las respuestas de los archivos JSON de Habilidades de Vida
    procesador.completar_respuestas_json(
        os.path.join(os.path.dirname(__file__), "json_ordenados", "habilidades_vida_ordenado.json")
    )

