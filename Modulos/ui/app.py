"""
Modulo para la interfaz web creada con Streamlit
- Ruta de este archivo: Modulos/ui/app.py
"""
# Importar librerías
import streamlit as st # Librería para crear aplicaciones web
from Modulos.auth.auth import registrar_usuario, autenticar_usuario # Funciones de autenticación
from PIL import Image # Librería para manejar imágenes
from streamlit_toggle import st_toggle_switch # Librería para crear un switch de toggle

"""
Paginas de la aplicación:
- Login: sera el punto de entrada para los usuarios no registrados
- Registro: para crear una cuenta nueva
- Dashboard: donde se mostrará información relevante para el usuario
- Test: donde se seleccionará la materia y las preguntas para el test
- Historial: donde se mostrará el historial de pruebas del usuario
- Configuración: donde se podrá editar el perfil del usuario y opciones de la app
"""


# esto configura la página de Streamlit
st.set_page_config(page_title = "FuzzMap", layout = "wide")
"""
st.set_page_config() sirve para configurar la página de Streamlit
- page_title: Titulo de la página que se mostrará en la pestaña del navegador
- layout: Configura el diseño de la página. Puede ser "centered" o "wide"
"""

def pagina_login(questions = None) -> None:
    
    """
    Esta función crea la página de inicio de sesión de la aplicación
    - Se usa Streamlit para crear la interfaz
    - Se usa PIL para cargar la imagen del logo
    - Se usa streamlit_toggle para crear un botón deslizante que cambia el tema de la aplicación
    - Se usa st.columns() para crear dos columnas en la página
    - Se usa st.text_input() para crear campos de texto para el usuario y la contraseña
    - Se usa st.button() para crear un botón de inicio de sesión
    - Se usa st.markdown() para crear un enlace para registrarse
    - Se usa st.image() para mostrar la imagen del logo y el fondo
    - Se usa st.set_page_config() para configurar la página de Streamlit
    - Se usa st.session_state para guardar el estado de la aplicación
    - Se usa st.rerun() para recargar la página cuando se cambia el tema
    """
    

    # Crear dos columnas que permiten dividir la página
    # en dos partes: una para el formulario de inicio de sesión
    # y otra para la imagen de fondo
    col1, col2 = st.columns([2, 3], border = True)

    with col1:
        
        
        # logo_col y title_col son columnas que permiten alinear el logo y el título
        logo_col, title_col = st.columns([1, 2], border=True)
        """
        logo_col y title_col son columnas que permiten alinear el logo y el título
        - logo_col: columna para el logo
        - title_col: columna para el título
        los parametros [1, 4] indican el tamaño de cada columna
        """
        
        with logo_col:
            
            
            # Cargar y mostrar el logo
            logo = Image.open("../fuzzmap/Modulos/ui/src/Logo.png")
            st.image(logo, width=100, use_container_width=True)
            
        with title_col:
            
            # Mostrar el nombre de a aplicación
            st.markdown("<h1 style='color: #0dabda;'>FuzzMap</h1>", unsafe_allow_html=True)
            
            # mostrar el slogan de la aplicación de color gris
            st.markdown("<h5 style='color: #d1cfcf;'>Asistente inteligente de estudio</h5>", unsafe_allow_html=True)
            
        # Formulario de inicio de sesión
        usuario = st.text_input("Usuario", icon="👤", key="login_user")
        contraseña = st.text_input("Contraseña", type="password", icon="🔑", key="login_pwd")
        # boton con texto de fondo color gris
        st.markdown("")
        if st.button(label="Iniciar sesión", icon="🔓", key="login_btn"):
            st.success("Inicio de sesión exitoso")

        # Enlace para registrarse
        st.markdown("¿No tienes una cuenta? [Regístrate aquí](#)", unsafe_allow_html=True)

    with col2:
        
        # Imagen decorativa
        imagen = Image.open("/data/data/com.termux/files/home/storage/shared/Download/hola.png")
        st.image(imagen, use_container_width = True)



"""
def login_pagina (questions=None):
    
    
    st.title("🔐 Iniciar Sesión en FuzzMap")
    user = st.text_input("Usuario", key="login_user")
    pwd  = st.text_input("Contraseña", type="password", key="login_pwd")
    login_triggered = st.session_state.get("login_triggered", False)

    if st.button("Entrar", key="login_btn") or login_triggered:
        if autenticar_usuario(user, pwd):
            st.session_state.user = user
            st.session_state.active_page = "🏠 Dashboard"
            st.success(f"¡Bienvenido, {user}!")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")
            st.session_state.login_triggered = False
"""

def register_page(questions=None):
    st.title("📝 Registro de Nuevo Usuario")
    user   = st.text_input("Usuario", key="reg_user")
    pwd    = st.text_input("Contraseña", type="password", key="reg_pwd")
    pwd2   = st.text_input("Repite contraseña", type="password", key="reg_pwd2")
    names  = st.text_input("Nombres", key="reg_names")
    lastn  = st.text_input("Apellidos", key="reg_lastn")
    age    = st.number_input("Edad", min_value=0, max_value=120, key="reg_age")
    gender = st.selectbox("Sexo", ["M", "F", "O"], key="reg_gender")

    if st.button("Registrar", key="reg_btn"):
        if not all([user, pwd, pwd2, names, lastn]):
            st.error("Completa todos los campos.")
        elif pwd != pwd2:
            st.error("Las contraseñas no coinciden.")
        else:
            ok = registrar_usuario(user, pwd, names, lastn, age, gender)
            if ok:
                st.success("Registro exitoso. Ahora inicia sesión.")
                st.session_state.active_page = "🔐 Login"
                st.rerun()
            else:
                st.error("El usuario ya existe.")


def dashboard_page(questions=None):
    st.title("🏠 Dashboard")
    st.info("Aquí mostrarás información de usuario, estadísticas, recomendaciones y ranking.")


def test_page(questions):
    st.title("🧪 Test / Competición")
    st.info("Aquí irá la lógica de selección de materia y preguntas.")


def history_page(questions=None):
    st.title("📜 Historial de Pruebas")
    st.info("Aquí listarás los tests anteriores de este usuario.")


def settings_page(questions=None):
    st.title("⚙️ Configuración / Perfil")
    st.info("Aquí podrás editar datos de usuario y opciones de la app.")


def logout(questions=None):
    st.session_state.user = None
    st.session_state.active_page = "🔐 Login"
    st.info("Has cerrado sesión.")
    st.rerun()


def run_app(questions):
    
    
    if "user" not in st.session_state:
        st.session_state.user = None
    if "active_page" not in st.session_state:
        st.session_state.active_page = "🔐 Login" if st.session_state.user is None else "🏠 Dashboard"

    
    if st.session_state.user:
        pages = {
            "🏠 Dashboard": dashboard_page,
            "🧪 Test": test_page,
            "📜 Historial": history_page,
            "⚙️ Configuración": settings_page,
            "🔓 Cerrar sesión": logout
        }
    else:
        pages = {
            "🔐 Login": pagina_login,
            "📝 Registro": register_page
        }

    selected = st.sidebar.radio("Menú", list(pages.keys()), index=list(pages.keys()).index(st.session_state.active_page), key=f"menu_selector_{st.session_state.active_page}")
    st.session_state.active_page = selected
    pages[selected](questions)

# Punto de entrada
questions = {"Demo": [("¿Qué es FuzzMap?", "Asistente inteligente de estudio") ]}
run_app(questions)
