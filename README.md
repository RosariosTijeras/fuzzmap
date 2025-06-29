# FuzzMap: Asistente Académico Inteligente

FuzzMap es una plataforma web modular para la gestión, evaluación y retroalimentación de exámenes universitarios, integrando lógica difusa avanzada, análisis NLP y recomendaciones personalizadas generadas por LLM (Mistral-7B-Instruct vía LM Studio). El sistema es robusto, eficiente y extensible, ideal para instituciones educativas y proyectos de ciencia de datos.

---

## Características principales

- **Carga automática y centralizada de preguntas** usando AVLTree para búsquedas eficientes por materia, ID y dificultad.
- **Extracción y clasificación de preguntas** desde PDFs a JSON, con procesamiento NLP para justificación y retroalimentación.
- **Interfaz web Flask** para login, registro, dashboard, test, resultados y estadísticas.
- **Evaluación granular con lógica difusa** para un análisis más preciso del desempeño.
- **Recomendaciones personalizadas** generadas por LLM, integrando contexto, errores y feedback NLP.
- **Historial y estadísticas** por usuario y materia.

---

## Estructura del proyecto

```
├── main.py
├── requirements.txt
├── README.md
├── Datos/
│   └── ... (JSONs de preguntas y resultados)
├── Modulos/
│   ├── avltree/           # AVLTree para gestión de preguntas
│   ├── extraction/        # Extracción de texto desde PDFs
│   ├── fuzzylogic/        # Lógica difusa y recomendaciones
│   ├── generate_questions/# Generación automática de preguntas
│   ├── nlp/               # Procesamiento NLP y feedback
│   └── ui/                # Interfaz Flask y plantillas
└── Notebooks/             # Pruebas y experimentos
```

---

## Instalación

1. **Clona el repositorio:**
   ```bash
   git clone <URL-del-repo>
   cd fuzzmap
   ```

2. **Crea un entorno virtual (opcional pero recomendado):**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # En Windows
   # source venv/bin/activate  # En Linux/Mac
   ```

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura y ejecuta LM Studio (Mistral-7B-Instruct):**
   - Descarga e instala [LM Studio](https://lmstudio.ai/).
   - Descarga el modelo `mistral-7b-instruct` y actívalo en el puerto 11434.
   - Asegúrate de que la API esté disponible en `http://localhost:11434/api/generate`.

5. **Ejecuta la aplicación Flask:**
   ```bash
   python main.py
   ```
   O directamente desde el módulo UI:
   ```bash
   cd Modulos/ui
   flask run
   ```

---

## Uso

1. **Accede a la interfaz web:**
   - Abre tu navegador en `http://localhost:5000`.

2. **Regístrate o inicia sesión:**
   - El usuario admin se crea automáticamente si no existe (`admin@unach.edu.ec` / `admin`).

3. **Selecciona una materia y realiza un test:**
   - El sistema selecciona 10 preguntas aleatorias de la materia usando AVLTree.

4. **Recibe retroalimentación inteligente:**
   - Cada respuesta es analizada con NLP y lógica difusa.
   - El sistema genera una recomendación personalizada y motivadora usando LLM.

5. **Consulta tu historial y estadísticas:**
   - Visualiza tu progreso, errores frecuentes y sugerencias de mejora.

---

## Personalización y extensión

- **Agregar nuevas preguntas:**
  - Añade tus preguntas en formato JSON en las carpetas `Datos/Ciencia_Datos/preguntas_generadas/` o `Datos/Habilidades_Vida/preguntas_generadas/`.
  - El sistema las cargará automáticamente al iniciar.

- **Agregar nuevas materias:**
  - Crea un nuevo archivo JSON siguiendo el formato estándar y actualiza la función de carga en `app.py`.

- **Cambiar el modelo LLM:**
  - Modifica la configuración en `Modulos/nlp/text_classifier.py` para usar otro modelo compatible con LM Studio u Ollama.

- **Mejorar la UI:**
  - Edita los archivos en `Modulos/ui/templates/` y `Modulos/ui/src/`.

---

## Créditos y roles

- **Lenin:** Extracción de PDFs y generación de JSON.
- **Yoryhi:** Procesamiento NLP, clasificación y feedback.
- **Héctor:** Estructuras de datos (AVLTree, MergeSort, búsqueda).
- **Mario:** UI Flask, lógica difusa, integración LLM y unificación final.

---

## Notas técnicas

- El sistema es multiplataforma (Windows/Linux/Mac).
- Requiere Python 3.9+ y acceso a un modelo LLM local vía API.
- El árbol AVL se inicializa y carga automáticamente al iniciar la app.
- El análisis NLP y la recomendación LLM pueden tardar unos segundos según el hardware.

---

## Licencia

Este proyecto es de uso académico y experimental. Puedes adaptarlo y reutilizarlo citando a los autores originales.
