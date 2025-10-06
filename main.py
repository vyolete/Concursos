import streamlit as st
from vistas.login import mostrar_vista_login
from vistas.registro import mostrar_vista_registro
from vistas.app import mostrar_vista_app

def main():
    st.set_page_config(page_title="Mi App Modular", layout="wide")

    # Inicializar el estado de la sesión si no existe
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # Si el usuario ha iniciado sesión, mostrar la aplicación principal
    if st.session_state['logged_in']:
        mostrar_vista_app()
    else:
        # Si no, mostrar las opciones de login/registro en la barra lateral
        st.sidebar.title("Navegación")
        pagina = st.sidebar.radio("Elige una opción", ["Iniciar Sesión", "Registrarse"])

        if pagina == "Iniciar Sesión":
            mostrar_vista_login()
        elif pagina == "Registrarse":
            mostrar_vista_registro()

if __name__ == "__main__":
    main()