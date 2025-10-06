import streamlit as st
from modulos.autenticacion import login_usuario

def mostrar_vista_login():
    st.title("Inicio de Sesión")

    with st.form("formulario_login"):
        usuario = st.text_input("Nombre de Usuario")
        contrasena = st.text_input("Contraseña", type="password")
        enviado = st.form_submit_button("Iniciar Sesión")

        if enviado:
            if usuario and contrasena:
                exito, mensaje = login_usuario(usuario, contrasena)
                if exito:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = usuario
                    st.success(mensaje)
                    st.rerun()
                else:
                    st.error(mensaje)
            else:
                st.warning("Por favor, ingresa tu nombre de usuario y contraseña.")