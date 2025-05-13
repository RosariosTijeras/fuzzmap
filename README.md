# FuzzMap

> **Asistente de Estudio Inteligente** para estudiantes universitarios, combinando extracción de preguntas desde PDFs, estructuras de datos avanzadas, procesamiento de lenguaje natural y lógica difusa.

---

## 📋 Tabla de Contenidos

- [Descripción](https://github.com/RosariosTijeras/fuzzmap#-descripci%C3%B3n)  
- [Equipo de Desarrollo](https://github.com/RosariosTijeras/fuzzmap?tab=readme-ov-file#-equipo-de-desarrollo)  
- [Características Principales](https://github.com/RosariosTijeras/fuzzmap?tab=readme-ov-file#-caracter%C3%ADsticas-principales)  
- [Estructura de Carpetas](https://github.com/RosariosTijeras/fuzzmap?tab=readme-ov-file#-estructura-de-carpetas)  
- [Cronograma (2 Meses)](https://github.com/RosariosTijeras/fuzzmap?tab=readme-ov-file#-cronograma-2-meses)  
- [Asignación de Tareas](https://github.com/RosariosTijeras/fuzzmap?tab=readme-ov-file#-asignaci%C3%B3n-de-tareas)  
- [Tecnologías y Librerías](https://github.com/RosariosTijeras/fuzzmap?tab=readme-ov-file#%EF%B8%8F-tecnolog%C3%ADas-y-librer%C3%ADas)  
- [Cómo Empezar](https://github.com/RosariosTijeras/fuzzmap?tab=readme-ov-file#-c%C3%B3mo-empezar)  

---

## 📌 Descripción

**FuzzMap** es una aplicación **modular** en Python diseñada para:

1. **Leer** documentos PDF con preguntas, opciones y respuestas (texto e imágenes).  
2. **Procesar** el contenido usando **PLN** para extraer y clasificar preguntas.  
3. **Organizar** la información con **árboles de búsqueda (AVL)**, **grafos de conceptos**, **pilas**, **colas** y **listas enlazadas**.  
4. **Evaluar** el rendimiento del estudiante mediante **lógica difusa**, generando recomendaciones personalizadas. 
5. **Interactuar** con el usuario a través de una **interfaz visual basada en Streamlit**.

El enfoque modular facilita el trabajo en equipo y la escalabilidad futura.

---

## 👥 Equipo de Desarrollo

| Integrante | Rol                           |
|------------|-------------------------------|
|       | Módulo PLN                    |
|       | Módulo de Extracción de PDFs  |
|       | Módulo de Estructuras de Datos|
|       | Módulo de Lógica Difusa       |

---

## 🚀 Características Principales

1. **Extracción de Contenido**  
   - Bibliotecas: `PyPDF2`, `pdfminer.six`  
   - Detección de preguntas, respuestas y opciones (texto e imágenes).  

2. **Procesamiento de Lenguaje Natural**  
   - Bibliotecas: `spaCy`, `NLTK`  
   - Limpieza, tokenización y clasificación automática.  

3. **Estructuras de Datos**  
   - **Árbol AVL** para búsqueda eficiente por tema.  
   - **Grafo de Conceptos** para sugerir temas relacionados.  
   - **Pilas y Colas** para gestionar flujos de estudio y deshacer.  

4. **Lógica Difusa**  
   - Biblioteca: `scikit-fuzzy`  
   - Definición de conjuntos y reglas difusas para evaluar el rendimiento.  

5. **Interfaz de Usuario**  
   - `Streamlit` para una interfaz web interactiva y fácil de desplegar

---

## 🗂 Estructura de Carpetas

```text
FuzzMap/
├── docs/                # Documentación, diagramas y notebooks
├── data/                # PDFs de ejemplo y datasets
├── src/                 # Código fuente
│   ├── extraction/      # Módulo de extracción de PDFs
│   ├── nlp/             # Módulo de PLN
│   ├── datastructures/  # Árboles, grafos, pilas y colas
│   ├── fuzzy/           # Módulo de lógica difusa
│   └── ui/              # Interfaz gráfica Streamlit
├── tests/               # Pruebas unitarias e integración
├── requirements.txt     # Dependencias
└── README.md            # Este archivo
```

---

## 📅 Cronograma (2 Meses)

| Semana  | Actividad                                           |
|---------|-----------------------------------------------------|
| 1–2     | Configuración del entorno y módulo de extracción    |
| 3–4     | Desarrollo del módulo de PLN y pruebas iniciales    |
| 5–6     | Implementación de Árbol AVL y Grafo de Conceptos    |
| 7–8     | Desarrollo del módulo de Lógica Difusa              |
| 9–10    | Creación de la Interfaz de Usuario y pruebas de UX  |
| 11–12   | Integración final, ajustes, documentación y despliegue|

---

## 📝 Asignación de Tareas

| Integrante | Módulo               | Tareas Principales                                                        |
|------------|----------------------|----------------------------------------------------------------------------|
|       | PLN                  | - Extracción y clasificación de texto (spaCy, NLTK)                        |
|            |                      | - Diseño de pruebas unitarias de PLN                                       |
|       | Extracción de PDFs   | - Lectura y parsing de PDFs (PyPDF2, pdfminer.six)                         |
|            |                      | - Detección de preguntas e imágenes                                        |
|      | Estructuras de Datos | - Implementación de Árbol AVL y métodos de búsqueda                        |
|            |                      | - Creación de Grafo de Conceptos y algoritmos de recorrido                 |
|      | Lógica Difusa        | - Definición de conjuntos y reglas difusas (scikit-fuzzy)                  |
| Todos      | Integración & QA     | - Integración continua de módulos                                          |
|            |                      | - Pruebas de integración y calidad de código                               |

---

## ⚙️ Tecnologías y Librerías

- **Python 3.10+**
- `PyPDF2`, `pdfminer.six` – Extracción de contenido PDF  
- `spaCy`, `NLTK` – Procesamiento de Lenguaje Natural  
- `scikit-fuzzy` – Lógica difusa  
- `networkx` – Visualización de grafos  
- `Streamlit` – Interfaz web interactiva  
- `pytest` – Pruebas automatizadas

---

## 🚀 Cómo Empezar

Puedes instalar y ejecutar FuzzMap usando `pip` o `conda`, según tu entorno preferido.

#### ✅ Opción A: Usando `pip` (entorno virtual con `venv`)

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/RosariosTijeras/fuzzmap.git
   cd fuzzmap
   ```
2. **Crear y activar un entorno virtual:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```
4. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

---

#### ✅ Opción B: Usando conda

1. **Clonar el repositorio:**
  ```bash
   git clone https://github.com/RosariosTijeras/fuzzmap.git
cd fuzzmap
  ```

4. **Crear y activar un entorno conda:**
  ```bash
  conda create -n fuzzmap-env python=3.10
  conda activate fuzzmap-env
  ```

3. **Instalar dependencias desde requirements.txt:**
   ```bash
   pip install -r requirements.txt
   ```
---
