import os
import json
import re
import glob
import requests

#----------------------#
class CienciaDatosProcessor:
    def __init__(self):
        self.ruta_carpeta=os.path.join(os.path.dirname(__file__), "..","..", "Datos", "Ciencia_Datos", "json_quiz")
        self.carpeta_salida=os.path.join(os.path.dirname(__file__), "json_ordenados")
        self.salida=os.path.join(self.carpeta_salida, "ciencia_datos_ordenado.json")

    def es_pregunta(self, linea):
        return bool(re.match(r"^¿.*\?\s*$", linea.strip()))

    def extraer_opciones(self, lineas):
        opciones = []
        for linea in lineas:
            m=re.match(r"^([a-cA-C])[\.\)]\s?(.*)", linea)
            if m:
                letra, texto=m.groups()
                texto_limpio=re.sub(r"Sin contestar", "", texto, flags=re.IGNORECASE).strip()
                texto_limpio=re.sub(r"\s{2,}", " ", texto_limpio)
                opciones.append(f"{letra}) {texto_limpio}".strip())
        return opciones

    def ordenar_json_ciencia_datos(self, lineas):
        preguntas_ordenadas = []
        i=0
        num_pregunta=1
        while i<len(lineas):
            linea = lineas[i].strip()
            if self.es_pregunta(linea):
                pregunta=linea
                opciones=self.extraer_opciones(lineas[i+1:i+4])
                respuesta_correcta = ""
                j=i+4
                while j<len(lineas) and not self.es_pregunta(lineas[j]):
                    if lineas[j].startswith("La respuesta correcta es:"):
                        texto_resp=lineas[j].split(":", 1)[1].strip()
                        for op in opciones:
                            if texto_resp in op or op in texto_resp:
                                respuesta_correcta=op
                                break
                        break
                    j+=1
                preguntas_ordenadas.append({
                    "numero": num_pregunta,
                    "pregunta": pregunta,
                    "opciones": opciones,
                    "respuesta_correcta": respuesta_correcta
                })
                num_pregunta+=1
                i=j
            else:
                i+=1
        return preguntas_ordenadas

    def procesar(self):
        archivos_json=glob.glob(os.path.join(self.ruta_carpeta, "*.json"))
        todas_preguntas = []
        for archivo in archivos_json:
            with open(archivo, 'r', encoding='utf-8') as f:
                datos=json.load(f)
            lineas=datos.get('lineas', [])
            preguntas=self.ordenar_json_ciencia_datos(lineas)
            todas_preguntas.extend(preguntas)
        if not os.path.exists(self.carpeta_salida):
            os.makedirs(self.carpeta_salida)
        resultado = {
            "materia": "Ciencia_Datos",
            "preguntas": todas_preguntas
        }
        with open(self.salida, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=4)
        print(f"Archivo generado: {self.salida}")

if __name__ == "__main__":
    procesador=CienciaDatosProcessor()
    procesador.procesar()

#----------------------#
class HabilidadesVidaProcessor:
    def __init__(self):
        self.ruta_carpeta=os.path.join(os.path.dirname(__file__), "..", "..", "Datos", "Habilidades_Vida","json_quiz")
        self.carpeta_salida=os.path.join(os.path.dirname(__file__), "json_ordenados")
        self.salida=os.path.join(self.carpeta_salida, "habilidades_vida_ordenado.json")

    def limpiar_repeticion_una_respuesta_a(self, texto):
        primera=texto.find("una respuesta a")
        if primera==-1:
            return texto
        antes=texto[:primera+len("una respuesta a")]
        despues=texto[primera+len("una respuesta a"):].replace("una respuesta a", "")
        return (antes + despues).replace("  ", " ").strip(", ")

    def es_pregunta(self, linea):
        return bool(re.match(r"^¿.*\?\s*$", linea.strip()))

    def limpiar_opcion(self, texto):
        texto=re.sub(r'\\".*?\\"', '', texto)
        texto=re.split(r'\\"', texto)[0]
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
        patron_regex="|".join(patrones)
        texto=re.split(patron_regex, texto, flags=re.IGNORECASE)[0]
        return texto.strip()

    def extraer_opciones(self, lineas):
        opciones = []
        opcion_actual = ""
        letra_actual = ""
        for linea in lineas:
            m = re.match(r"^([a-cA-C])[\.\)]\s?(.*)$", linea)
            if m:
                if letra_actual and opcion_actual:
                    limpia=self.limpiar_opcion(opcion_actual)
                    opciones.append(f"{letra_actual}) {limpia}".strip() if limpia else f"{letra_actual})")
                letra_actual, texto=m.groups()
                opcion_actual=texto.strip()
            else:
                if opcion_actual:
                    opcion_actual+=" "+linea.strip()
        if letra_actual:
            limpia=self.limpiar_opcion(opcion_actual)
            opciones.append(f"{letra_actual}) {limpia}".strip() if limpia else f"{letra_actual})")
        return opciones

    def ordenar_json_habilidades_vida(self, lineas):
        preguntas_ordenadas = []
        i=0
        num_pregunta=1
        while i<len(lineas):
            linea = lineas[i].strip()
            if self.es_pregunta(linea):
                pregunta=linea
                opciones_lineas=[]
                j=i+1
                while j<len(lineas) and not self.es_pregunta(lineas[j]) and not lineas[j].startswith("La respuesta correcta es:"):
                    opciones_lineas.append(lineas[j])
                    j+=1
                opciones=self.extraer_opciones(opciones_lineas)
                respuesta_correcta = ""
                if j<len(lineas) and lineas[j].startswith("La respuesta correcta es:"):
                    texto_resp=lineas[j].split(":", 1)[1].strip()
                    texto_resp=self.limpiar_opcion(texto_resp)
                    for op in opciones:
                        if texto_resp in op or op in texto_resp:
                            respuesta_correcta = op
                            break
                    j+=1
                preguntas_ordenadas.append({
                    "numero": num_pregunta,
                    "pregunta": pregunta,
                    "opciones": opciones,
                    "respuesta_correcta": respuesta_correcta,
                })
                num_pregunta+=1
                i=j
            else:
                i+=1
        return preguntas_ordenadas

    def procesar(self):
        archivos_json=glob.glob(os.path.join(self.ruta_carpeta, "*.json"))
        todas_preguntas = []
        for archivo in archivos_json:
            with open(archivo, 'r', encoding='utf-8') as f:
                datos=json.load(f)
            lineas=datos.get('lineas', [])
            preguntas=self.ordenar_json_habilidades_vida(lineas)
            todas_preguntas.extend(preguntas)
        if not os.path.exists(self.carpeta_salida):
            os.makedirs(self.carpeta_salida)
        resultado = {
            "materia": "Habilidades_Vida",
            "preguntas": todas_preguntas
        }
        # Ajustes especiales (puedes quitar si no los necesitas)
        if resultado["preguntas"]:
            primera = resultado["preguntas"][0]
            primera["opciones"]=[self.limpiar_repeticion_una_respuesta_a(op) for op in primera["opciones"]]
            primera["respuesta_correcta"] = self.limpiar_repeticion_una_respuesta_a(primera["respuesta_correcta"])
        for pregunta in resultado["preguntas"]:
            if pregunta["numero"]==5:
                nuevas_opciones = []
                for op in pregunta["opciones"]:
                    if op.startswith("a)"):
                        op=op.replace(" abdomen con aire", "")
                    nuevas_opciones.append(op)
                pregunta["opciones"] = nuevas_opciones
        with open(self.salida, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=4)
        print(f"Archivo generado: {self.salida}")

if __name__ == "__main__":
    habilidades=HabilidadesVidaProcessor()
    habilidades.procesar()

#----------------------#

class RespuestaAutomaticaProcessor:
    def __init__(self):
        self.respuestas_manual_path=os.path.join(os.path.dirname(__file__), "respuestas_manual.json")
        if os.path.exists(self.respuestas_manual_path):
            with open(self.respuestas_manual_path, "r", encoding="utf-8") as f:
                self.RESPUESTAS_MANUAL=json.load(f)
        else:
            self.RESPUESTAS_MANUAL = {}
        self.OLLAMA_URL = "http://localhost:11434/api/generate"
        self.OLLAMA_MODEL = "mistral:7b-instruct"  # Modelo pequeño

    def obtener_respuesta_manual(self, pregunta):
        return self.RESPUESTAS_MANUAL.get(pregunta, "")

    def obtener_justificacion_ollama(self, pregunta, respuesta_correcta):
        prompt = (
            f"Pregunta: {pregunta}\n"
            f"Respuesta correcta: {respuesta_correcta}\n"
            "Explica brevemente por qué esta es la respuesta correcta. Sé claro, sencillo y corto."
        )
        try:
            response = requests.post(self.OLLAMA_URL, json={
                "model": self.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            }, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except Exception as e:
            print(f"[ERROR] Justificación Ollama: {e}")
            return "Justificación no disponible."

    def obtener_retroalimentacion_ollama(self, pregunta, respuesta_correcta):
        prompt = (
            f"Pregunta: {pregunta}\n"
            f"Respuesta correcta: {respuesta_correcta}\n"
            "Dale una retroalimentación breve y sencilla al usuario, como un apoyo de manera sencilla y corta."
        )
        try:
            response = requests.post(self.OLLAMA_URL, json={
                "model": self.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            }, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except Exception as e:
            print(f"[ERROR] Retroalimentación Ollama: {e}")
            return "Retroalimentación no disponible."

    def completar_respuestas_json(self, path_json):
        with open(path_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        for pregunta in data["preguntas"]:
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

            # Imprime en formato amigable como tu ejemplo
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

        carpeta_salida = os.path.join(os.path.dirname(__file__), "json_ordenados_completos")
        if not os.path.exists(carpeta_salida):
            os.makedirs(carpeta_salida)
        nombre_archivo = os.path.basename(path_json).replace(".json", "_completado.json")
        salida = os.path.join(carpeta_salida, nombre_archivo)

        with open(salida, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Archivo guardado: {salida}")

# Ejemplo de uso:
if __name__ == "__main__":
    procesador=RespuestaAutomaticaProcessor()
    procesador.completar_respuestas_json(
        os.path.join(os.path.dirname(__file__), "json_ordenados", "ciencia_datos_ordenado.json")
    )
    procesador.completar_respuestas_json(
        os.path.join(os.path.dirname(__file__), "json_ordenados", "habilidades_vida_ordenado.json")
    )

