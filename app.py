import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from passlib.hash import pbkdf2_sha256
from email.mime.text import MIMEText
from googleapiclient.discovery import build
import random
import string
import base64

# ======================================================
# CONFIGURACIÓN GOOGLE SHEETS
# ======================================================
credentials = Credentials.from_service_account_info(st.secrets["gcp"])
gc = gspread.authorize(credentials)
sheet = gc.open("registro_usuarios").sheet1  # Nombre de tu hoja

# ======================================================
# FUNCIONES AUXILIARES
# ======================================================
def generar_codigo(longitud=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=longitud))

def enviar_correo(destinatario, asunto, mensaje):
    service = build('gmail', 'v1', credentials=credentials)
    mime_message = MIMEText(mensaje, "plain")
    mime_message["to"] = destinatario
    mime_message["subject"] = asunto
    raw_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
    message = {'raw': raw_message}
    service.users().messages().send(userId="me", body=message).execute()

def obtener_usuarios():
    registros = sheet.get_all_records()
    return pd.DataFrame(registros)

def guardar_usuario(nombre, correo, contraseña_hash):
    sheet.append_row([nombre, correo, contraseña_hash])

def correo_existe(correo):
    usuarios = obtener_usuarios()
    return correo in usuarios["Correo"].values

def autenticar_usuario(correo, contraseña):
    usuarios = obtener_usuarios()
    if correo in usuarios["Correo"].values:
        user = usuarios[usuarios["Correo"] == correo].iloc[0]
        return pbkdf2_sha256.verify(contraseña, user["Contraseña"])
    return False

# ======================================================
# INTERFAZ STREAMLIT
# ======================================================
st.title("🔐 Sistema de Registro y Acceso ITM")

modo = st.sidebar.radio("Selecciona una opción", ["Registro", "Iniciar sesión", "Recuperar contraseña"])

if modo == "Registro":
    st.subheader("📝 Registro de nuevo usuario")
    nombre = st.text_input("Nombre completo")
    correo = st.text_input("Correo institucional")
    contraseña = st.text_input("Contraseña", type="password")
    if st.button("Registrar"):
        if correo_existe(correo):
            st.warning("⚠️ Este correo ya está registrado.")
        else:
            hash_pass = pbkdf2_sha256.hash(contraseña)
            guardar_usuario(nombre, correo, hash_pass)
            enviar_correo(
                correo,
                "Registro exitoso - Concurso ITM",
                f"Hola {nombre}, tu registro en el sistema fue exitoso."
            )
            st.success("✅ Registro completado. Se envió un correo de confirmación.")

elif modo == "Iniciar sesión":
    st.subheader("🔑 Iniciar sesión")
    correo = st.text_input("Correo institucional")
    contraseña = st.text_input("Contraseña", type="password")
    if st.button("Acceder"):
        if autenticar_usuario(correo, contraseña):
            st.success("Bienvenido al sistema 🎉")
        else:
            st.error("❌ Credenciales incorrectas.")

else:  # Recuperar contraseña
    st.subheader("🔄 Recuperar contraseña")
    correo = st.text_input("Correo registrado")
    if st.button("Enviar enlace de recuperación"):
        if correo_existe(correo):
            token = generar_codigo()
            enviar_correo(
                correo,
                "Recuperación de contraseña - Concurso ITM",
                f"Utiliza este código temporal para restablecer tu contraseña: {token}"
            )
            st.info("📩 Se envió un correo con tu código temporal.")
        else:
            st.warning("⚠️ Este correo no está registrado.")
