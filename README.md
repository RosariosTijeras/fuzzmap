FuzzMap: Asistente de Estudio Inteligente

> La herramienta definitiva para estudiantes universitarios, combinando extracción de preguntas desde PDFs, estructuras de datos avanzadas, procesamiento de lenguaje natural y lógica difusa.




---

📌 Descripción del Proyecto

FuzzMap es una aplicación modular en Python diseñada para ayudar a estudiantes universitarios a prepararse para exámenes de manera eficiente.
A partir de documentos PDF con preguntas y respuestas (incluyendo imágenes), FuzzMap organiza y presenta el contenido mediante:

Estructuras de datos avanzadas: Árboles de búsqueda (AVL), Grafos de conceptos, Pilas, Colas y Listas Enlazadas.

Procesamiento de Lenguaje Natural (PLN): Extracción y clasificación automática de preguntas, opciones y respuestas.

Lógica Difusa: Evaluación flexible del rendimiento del estudiante y recomendaciones personalizadas.

Interfaz Gráfica: Herramienta interactiva para repasar preguntas, gestionar cronogramas de estudio y visualizar progresos.


El proyecto es completamente modular, facilitando el trabajo en equipo y la ampliación futura.


---

👥 Equipo de Desarrollo

- Héctor

- Lenin 

- Yoryhi

- Mario 


Los 4 colaboradores trabajarán en paralelo, cada uno en su módulo, con integración continua para asegurar la coherencia del sistema.


---

🚀 Funcionalidades Principales

1. Extracción de Contenido

Lectura de PDFs con PyPDF2 y pdfminer.six.

Detección de preguntas, respuestas y opciones (texto e imágenes).



2. Procesamiento de Lenguaje Natural

Limpieza y tokenización con spaCy / NLTK.

Clasificación de frases y estructuración de datos.



3. Organización con Estructuras de Datos

Árbol AVL para búsqueda rápida de preguntas por tema.

Grafo de Conceptos para sugerir temas relacionados.

Pilas y Colas para gestionar secuencias de estudio y funcionalidades de deshacer.



4. Evaluación con Lógica Difusa

Definición de conjuntos difusos de rendimiento (scikit-fuzzy).

Reglas difusas para generar calificaciones y sugerencias adaptativas.



5. Interfaz de Usuario

Diseño con Tkinter (o Flask para versión web).

Panel de selección de temas, cronograma de estudio y visor de preguntas.



6. Planificador de Estudio

Gestión de horarios y recordatorios con Listas Enlazadas.

Visualización de progreso y métricas de aprendizaje.





---

## 🗂 Estructura de Carpetas

```text
FuzzMap/
├── docs/                # Documentación y diagramas
├── data/                # PDFs de ejemplo y datasets
├── src/                 # Código fuente principal
│   ├── extraction/      # Módulo de extracción PDF
│   ├── nlp/             # Módulo de PLN
│   ├── datastructures/  # Árboles, grafos, pilas y colas
│   ├── fuzzy/           # Módulo de lógica difusa
│   ├── ui/              # Interfaz gráfica o web
│   └── planner/         # Planificador de estudio
├── tests/               # Pruebas unitarias y de integración
├── requirements.txt     # Dependencias del proyecto
└── README.md            # Este archivo
```

---

🛠 Tecnologías y Librerías

- Python 3.10+

- Extracción de PDFs: PyPDF2, pdfminer.six

- PLN: spaCy, NLTK

- Lógica Difusa: scikit-fuzzy

- Estructuras de Datos: implementaciones propias + networkx (para visualización)

- Interfaz: Tkinter / Flask

- Pruebas: pytest



---
