import streamlit as st
from helpers import gen_code, add_or_update_user, find_user, send_code_email, set_verified

st.set_page_config(page_title="Auth con Google Sheets", layout="centered")

st.title("Registro / Login — Google Sheets")

menu = st.sidebar.selectbox("Ir a", ["Registro", "Login"])

if menu == "Registro":
    st.header("Registro")
    name = st.text_input("Nombre")
    email = st.text_input("Correo")
    if st.button("Enviar código"):
        if not email:
            st.error("Ingrese un correo")
        else:
            code = gen_code()
            add_or_update_user(email, name or "", code)
            try:
                send_code_email(email, code)
                st.success("Código enviado. Revisa tu correo.")
                st.session_state["pending_email"] = email
            except Exception as e:
                st.error(f"Error enviando correo: {e}")

    code_input = st.text_input("Introduce el código recibido")
    if st.button("Verificar"):
        email = st.session_state.get("pending_email") or st.text_input("Correo para verificar")
        if not email:
            st.error("Falta correo")
        else:
            user, _ = find_user(email)
            if not user:
                st.error("Correo no registrado")
            else:
                saved_code = user[3]  # columna code (0-index)
                if code_input == saved_code:
                    set_verified(email, True)
                    st.success("Cuenta verificada. Ya puedes iniciar sesión.")
                else:
                    st.error("Código incorrecto.")

if menu == "Login":
    st.header("Login")
    email = st.text_input("Correo")
    if st.button("Entrar"):
        if not email:
            st.error("Ingrese correo")
        else:
            user, _ = find_user(email)
            if not user:
                st.error("Correo no registrado")
            else:
                verified = user[2] == "True"
                if not verified:
                    st.warning("Correo no verificado. Enviando nuevo código...")
                    code = gen_code()
                    add_or_update_user(email, user[1] or "", code)
                    try:
                        send_code_email(email, code)
                        st.info("Código enviado. Verifica antes de entrar.")
                    except Exception as e:
                        st.error(f"Error enviando correo: {e}")
                else:
                    st.success(f"Bienvenido {user[1]} — acceso permitido.")
                    st.session_state["user"] = email
                    # aquí carga la app principal
                    st.write("Aquí va tu aplicación protegida.")