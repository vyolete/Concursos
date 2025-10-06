import streamlit as st
from modulos.autenticacion import registrar_usuario

def mostrar_vista_registro():
    st.title("Registro de Usuario")

    with st.form("formulario_registro"):
        nuevo_usuario = st.text_input("Nombre de Usuario")
        nueva_contrasena = st.text_input("Contraseña", type="password")
        nuevo_email = st.text_input("Correo Electrónico")
        enviado = st.form_submit_button("Registrarse")

        if enviado:
            if nuevo_usuario and nueva_contrasena and nuevo_email:
                exito, mensaje = registrar_usuario(nuevo_usuario, nueva_contrasena, nuevo_email)
                if exito:
                    st.success(mensaje)
                else:
                    st.error(mensaje)
            else:
                st.warning("Por favor, completa todos los campos.")