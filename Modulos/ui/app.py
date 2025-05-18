"""
Modulo para la interfaz web creada con Streamlit
- Ruta de este archivo: Modulos/ui/app.py
"""

# Importar librerías
import streamlit as st
from Modulos.auth.auth import registrar_usuario, autenticar_usuario

# Páginas de la aplicación

def login_page(questions=None):
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
            "🔐 Login": login_page,
            "📝 Registro": register_page
        }

    selected = st.sidebar.radio("Menú", list(pages.keys()), index=list(pages.keys()).index(st.session_state.active_page), key="menu_selector")
    st.session_state.active_page = selected
    pages[selected](questions)

# Punto de entrada
questions = {"Demo": [("¿Qué es FuzzMap?", "Asistente inteligente de estudio") ]}
run_app(questions)
