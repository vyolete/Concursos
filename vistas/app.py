import streamlit as st

def mostrar_vista_app():
    st.title(f"¡Bienvenido a la aplicación, {st.session_state['username']}!")
    st.write("Este es el contenido principal de tu aplicación.")
    # Aquí puedes añadir el resto de la funcionalidad de tu app

    if st.button("Cerrar Sesión"):
        st.session_state['logged_in'] = False
        st.rerun()