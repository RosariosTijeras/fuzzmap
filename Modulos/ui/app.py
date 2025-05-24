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


logo = Image.open("../fuzzmap/Modulos/ui/src/Logo.png")
# esto configura la página de Streamlit
st.set_page_config(page_title = "FuzzMap", layout = "wide", page_icon = logo)
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
            st.image(logo, width=100, use_container_width=True)
            
        with title_col:
            
            # Mostrar el nombre de a aplicación
            st.markdown("<h1 style='color: #0dabda;'>FuzzMap</h1>", unsafe_allow_html=True)
            
            # mostrar el slogan de la aplicación de color gris
            st.markdown("<h5 style='color: #f26def;'>Asistente inteligente de estudio</h5>", unsafe_allow_html=True)
            
        # Formulario de inicio de sesión
        usuario = st.text_input("Usuario", icon="👤", key="usr_input_login")
        contraseña = st.text_input("Contraseña", type="password", icon="🔑", key="pass_input_login")
        
        # la variable sesion_activa guarda el estado de la sesión
        # con esto se puede saber si el usuario ha iniciado sesión o no, asi se mestra el dashboard o la pagina de login
        # sin tener que hacer un login cada vez que se recarga la página
        sesion_activa = st.session_state.get("login_triggered", False)
        
        col_btlogin, col_btregistro = st.columns([1.5, 2], border=True, gap="small")
        """
        boton_login y boton_registro son columnas que permiten alinear los botones de inicio de sesión y registro
        - boton_login: columna para el botón de inicio de sesión
        - boton_registro: columna para el botón de registro
        los parametros [1, 2] indican el tamaño de cada columna
        """
        
        # Crear un botón de inicio de sesión y un botón de registro
        with col_btlogin:
            
            if st.button("Iniciar Sesión", key="login_btn", icon="🔓") or sesion_activa:

                """
                Si el usuario y la contraseña son correctos, se inicia sesión
                - Se guarda el usuario en la sesión
                - Se cambia la página activa a Dashboard
                - Se muestra un mensaje de bienvenida
                - Se recarga la página
                """

                # Si el usuario y la contraseña son correctos, se inicia sesión
                if autenticar_usuario(usuario, contraseña):

                    # Se guarda el usuario en la sesión
                    # y se cambia la página activa a Dashboard
                    st.session_state.user = usuario
                    st.success(f"¡Bienvenido, {usuario}!")
                    st.session_state.active_page = "🏠 Dashboard"
                    st.rerun()

                else:
                    # Si el usuario y la contraseña son incorrectos, se muestra un mensaje de error
                    st.error("Usuario o contraseña incorrectos.")
                    st.session_state.login_triggered = False
        
        with col_btregistro:
            
            # Crear un botón para ir a la pagina de registro
            # Si el usuario no tiene cuenta, se le da la opción de registrarse
            st.markdown("¿No tienes una cuenta?", unsafe_allow_html=True)
            st.button("Regístrate aquí", key="register_btn", icon="📝", on_click=lambda: st.session_state.update({"active_page": "📝 Registro"}))

    with col2:
        
        # Imagen decorativa
        imagen = Image.open("/data/data/com.termux/files/home/storage/shared/Download/hola.png")
        st.image(imagen, use_container_width = True)



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
                
    st.button("Volver al Login", key="back_to_login", on_click=lambda: st.session_state.update({"active_page": "🔐 Login"}))


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
        
    
    # selecionar pagina con match-case
    match st.session_state.active_page:
        case "🔐 Login":
            pagina_login(questions)
        case "📝 Registro":
            register_page(questions)
        case "🏠 Dashboard":
            dashboard_page(questions)
        case "🧪 Test":
            test_page(questions)
        case "📜 Historial":
            history_page(questions)
        case "⚙️ Configuración":
            settings_page(questions)
        case "🔓 Cerrar sesión":
            logout(questions)
    
    """
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

    selected = st.sidebar.radio("Menú", 
                                list(pages.keys()), 
                                index=list(pages.keys()).index(st.session_state.active_page),
                                key=f"sidebar_{st.session_state.user}")
    st.session_state.active_page = selected
    pages[selected](questions)
    """
