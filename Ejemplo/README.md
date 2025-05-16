# FuzzMap – Prototipo de Referencia

El directorio `example/` contiene una implementación didáctica y funcional del sistema **FuzzMap**. Este ejemplo fue desarrollado para ayudar a los miembros del equipo a comprender la arquitectura modular del proyecto, probar su funcionamiento básico y familiarizarse con el uso de los módulos desde `main.py` o mediante pruebas desde Jupyter Notebook.

---

## 📑 Índice

1. [¿Qué aprenderás con este ejemplo?](#-qué-aprenderás-con-este-ejemplo)
2. [Estructura de Carpetas](#-estructura-de-carpetas)
3. [Cómo ejecutar este ejemplo](#-cómo-ejecutar-este-ejemplo)
4. [Notebook de Prueba](#-notebook-de-prueba)
5. [Explicación de Módulos y Archivos](#-explicación-de-módulos-y-archivos)
6. [Recomendaciones Finales](#-recomendaciones-finales)

---

## 🎯 ¿Qué aprenderás con este ejemplo?

Este prototipo proporciona una base clara y práctica para:

* Comprender la estructura modular del sistema.
* Ejecutar un flujo básico desde preguntas precargadas hasta recomendaciones.
* Importar y utilizar los módulos desde `main.py`.
* Realizar pruebas desde un cuaderno Jupyter.
* Aprender cómo se conecta la lógica difusa con la interfaz de usuario.

Este entorno es una introducción funcional que marca el inicio del proyecto completo del asistente inteligente FuzzMap.

---

## 🧱 Estructura de Carpetas

```text
example/
├── data/
│   ├── Habilidades_Vida/
│   └── Ciencia_Datos/
├── Módulos/
│   ├── extraction/
│   │   ├── __init__.py
│   │   └── pdf_extractor.py
│   ├── nlp/
│   │   ├── __init__.py
│   │   └── text_classifier.py
│   ├── avltree/
│   │   ├── __init__.py
│   │   └── avl_tree.py
│   ├── fuzzylogic/
│   │   ├── __init__.py
│   │   └── fuzzy_evaluator.py
│   └── ui/
│       ├── __init__.py
│       └── app.py
├── Notebooks/
│   └── ejemplo_test.ipynb
├── main.py
└── README.md
```

---

## ⚙️ ¿Cómo ejecutar este ejemplo?

### 1. Abre la consola (terminal) en tu sistema operativo

#### En Windows:

* Presiona `Win + R`, escribe `cmd` y pulsa Enter.
* O abre Visual Studio Code y abre la terminal integrada con `` Ctrl + ` ``.

### 2. Activa tu entorno Conda

Si ya tienes creado el entorno virtual (por ejemplo llamado `fuzzmap-example`), actívalo con:

```bash
conda activate fuzzmap-example
```

> Asegúrate de que el entorno tiene instaladas las dependencias necesarias como `streamlit`, `PyMuPDF`, etc. Caso contrario instala las dependencias con el archivo requirements.txt

### 3. Entra a la carpeta `example/`

```bash
cd ruta/al/proyecto/example
```

> Reemplaza `ruta/al/proyecto` por la ruta correcta en tu sistema.

### 4. Ejecuta el sistema desde la terminal con Streamlit

```bash
streamlit run main.py
```

### 5. O ejecuta desde Visual Studio Code

* Abre la carpeta `example/` en VSCode.
* Abre una terminal integrada.
* Asegúrate de que el entorno activo sea `fuzzmap-example`.
* Ejecuta:

```bash
streamlit run main.py
```

### 6. Interactúa con la interfaz web

* Selecciona una materia (por ejemplo, Ciencia\_Datos).
* Presiona **Comenzar Test**.
* Responde las preguntas que aparecen.
* Pulsa **Finalizar Test** para ver:

  * Respuestas correctas
  * Evaluación basada en lógica difusa
  * Recomendación final

> No es necesario cargar nuevos PDFs: el ejemplo ya contiene contenido listo para pruebas.

---

## 🧪 Notebook de Prueba

Dentro de la carpeta `Notebooks/`, encontrarás el archivo `ejemplo_test.ipynb`, el cual permite:

* Probar funciones individuales de cada módulo.
* Explorar cómo importar y usar los componentes desde el código principal.
* Realizar pruebas unitarias básicas.

Puedes abrir este notebook desde JupyterLab o directamente desde Visual Studio Code.

---

## 📁 Explicación de Módulos y Archivos

### Módulo `extraction`

* `pdf_extractor.py`: contiene funciones para extraer texto desde archivos PDF.
* `__init__.py`: permite importar funciones del módulo de forma sencilla, como `from Módulos.extraction import extract_text_from_pdf`.

### Módulo `nlp`

* `text_classifier.py`: clasifica pares pregunta-respuesta por materia.
* `__init__.py`: expone las funciones de PLN para importar directamente desde el módulo.

### Módulo `avltree`

* `avl_tree.py`: contiene una implementación simple de árbol AVL para organizar preguntas.
* `__init__.py`: centraliza el acceso a las clases/funciones del árbol AVL.

### Módulo `fuzzylogic`

* `fuzzy_evaluator.py`: implementa lógica difusa para evaluar las respuestas.
* `__init__.py`: simplifica la importación desde otros archivos del proyecto.

### Módulo `ui`

* `app.py`: contiene la lógica de la interfaz interactiva construida con Streamlit.
* `__init__.py`: conecta la interfaz con `main.py`.

### Archivo `main.py`

Es el punto de entrada del sistema. Aquí se importa cada módulo, se inicializa la aplicación y se gestiona el flujo general del test:

```python
from Módulos.extraction import extract_text_from_pdf
from Módulos.nlp import classify_questions
from Módulos.avltree import AVLTree
from Módulos.fuzzylogic import evaluate_fuzzy
from Módulos.ui import run_ui
```

Este archivo es el encargado de orquestar los componentes del sistema: carga preguntas, organiza datos, ejecuta la interfaz y procesa los resultados.

---

## ✅ Recomendaciones Finales

* Usa este entorno como base inicial para pruebas y desarrollo.
* Amplía cada módulo según sea necesario para el sistema completo.
* Usa `main.py` como guía para entender la integración general de componentes.

> Este prototipo marca un inicio claro y funcional del desarrollo de **FuzzMap**, permitiendo al equipo construir sobre una base organizada, comprensible y completamente operativa.

