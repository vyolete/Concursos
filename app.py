# This is a sample Python script.
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from passlib.hash import pbkdf2_sha256
import smtplib
from email.mime.text import MIMEText
import random, string

# ==========================
# CONFIGURACIÓN SECRETS
# ==========================
# Gmail
GMAIL_USER = st.secrets["gmail"]["user"]
GMAIL_APP_PASSWORD = st.secrets["gmail"]["app_password"]

# Google Sheets
gcp_creds = st.secrets["gcp"]
spreadsheet_id = st.secrets["spreadsheet"]["id"]

credentials_dict = {
    "type": gcp_creds["type"],
    "project_id": gcp_creds["project_id"],
    "private_key_id": gcp_creds["private_key_id"],
    "private_key": gcp_creds["private_key"],
    "client_email": gcp_creds["client_email"],
    "client_id": gcp_creds["client_id"],
    "auth_uri": gcp_creds["auth_uri"],
    "token_uri": gcp_creds["token_uri"],
    "auth_provider_x509_cert_url": gcp_creds["auth_provider_x509_cert_url"],
    "client_x509_cert_url": gcp_creds["client_x509_cert_url"],
    "universe_domain": gcp_creds["universe_domain"]
}

scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]

creds = Credentials.from_service_account_info(credentials_dict, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(spreadsheet_id).sheet1  # Primera hoja

# ==========================
# FUNCIONES
# ==========================
def obtener_usuarios():
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    if not df.empty:
        return df
    else:
        return pd.DataFrame(columns=["email", "nombre", "password", "rol"])

def validar_correo_institucional(email):
    return email.endswith("@itm.edu.co")

def generar_contraseña_temporal(longitud=8):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(longitud))

def enviar_correo(destinatario, asunto, mensaje):
    msg = MIMEText(mensaje, "plain")
    msg["Subject"] = asunto
    msg["From"] = GMAIL_USER
    msg["To"] = destinatario
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"No se pudo enviar el correo: {e}")
        return False

# --------------------------
# CRUD de usuarios
# --------------------------
def registrar_usuario(email, nombre, password, rol):
    if not validar_correo_institucional(email):
        st.error("⚠ Solo se permiten correos institucionales.")
        return False
    usuarios = obtener_usuarios()
    if email in usuarios['email'].values:
        st.error("⚠ Este usuario ya está registrado.")
        return False
    hashed_password = pbkdf2_sha256.hash(password)
    sheet.append_row([email, nombre, hashed_password, rol])
    st.success(f"✅ Usuario registrado correctamente como {rol}.")
    asunto = "Registro en Sistema Concurso ITM"
    mensaje = f"Hola {nombre},\n\nTu cuenta ha sido creada correctamente.\nCorreo: {email}\nRol: {rol}\n\nGracias."
    enviar_correo(email, asunto, mensaje)
    return True

def autenticar_usuario(email, password):
    if not validar_correo_institucional(email):
        return False, None, None
    usuarios = obtener_usuarios()
    if email in usuarios['email'].values:
        usuario = usuarios[usuarios['email'] == email].iloc[0]
        if pbkdf2_sha256.verify(password, usuario['password']):
            return True, usuario['nombre'], usuario['rol']
    return False, None, None

def actualizar_usuario(email, nombre=None, password=None, rol=None):
    cell = sheet.find(email)
    row = cell.row
    if nombre:
        sheet.update_cell(row, 2, nombre)
    if password:
        hashed_password = pbkdf2_sha256.hash(password)
        sheet.update_cell(row, 3, hashed_password)
    if rol:
        sheet.update_cell(row, 4, rol)

def eliminar_usuario(email):
    cell = sheet.find(email)
    sheet.delete_row(cell.row)

def recuperar_contraseña(email):
    usuarios = obtener_usuarios()
    if email not in usuarios['email'].values:
        st.error("Correo no registrado.")
        return
    nueva_pass = generar_contraseña_temporal()
    actualizar_usuario(email, password=nueva_pass)
    asunto = "Recuperación de contraseña - Concurso ITM"
    mensaje = f"Hola,\n\nTu nueva contraseña temporal es: {nueva_pass}\nPor favor ingresa y cámbiala.\n\nGracias."
    enviar_correo(email, asunto, mensaje)
    st.success("Se ha enviado una nueva contraseña temporal a tu correo.")

# ==========================
# SESIÓN
# ==========================
if 'login' not in st.session_state:
    st.session_state.login = False
    st.session_state.usuario = ""
    st.session_state.rol = ""

# ==========================
# INTERFAZ STREAMLIT
# ==========================
st.title("🔐 Sistema Concurso ITM - PRO")

# Recuperación de contraseña
st.sidebar.subheader("¿Olvidaste tu contraseña?")
email_recuperar = st.sidebar.text_input("Correo institucional", key="recuperar")
if st.sidebar.button("Recuperar contraseña"):
    recuperar_contraseña(email_recuperar)

menu = st.sidebar.selectbox("Menú", ["Login", "Registro"])

# Registro
if menu == "Registro":
    st.subheader("📝 Crea una cuenta")
    email = st.text_input("Correo institucional")
    nombre = st.text_input("Nombre completo")
    password = st.text_input("Contraseña", type="password")
    rol = st.radio("Selecciona tu rol:", ["Estudiante", "Docente"])
    if st.button("Registrar"):
        registrar_usuario(email, nombre, password, rol)

# Login
elif menu == "Login":
    st.subheader("🔑 Ingresa a tu cuenta")
    email = st.text_input("Correo institucional", key="login_email")
    password = st.text_input("Contraseña", type="password", key="login_pass")
    if st.button("Ingresar"):
        valido, nombre_usuario, rol_usuario = autenticar_usuario(email, password)
        if valido:
            st.session_state.login = True
            st.session_state.usuario = nombre_usuario
            st.session_state.rol = rol_usuario
            st.success(f"Bienvenido {nombre_usuario} ({rol_usuario})")
        else:
            st.error("❌ Correo o contraseña incorrectos o no institucional.")

# --------------------------
# Panel de usuario logueado
# --------------------------
if st.session_state.login:
    st.write(f"🎉 Hola, {st.session_state.usuario} ({st.session_state.rol})!")

    # Panel docente
    if st.session_state.rol == "Docente":
        st.info("📚 Panel administrativo de usuarios")
        df = obtener_usuarios()
        if not df.empty:
            filtro_rol = st.selectbox("Filtrar por rol", ["Todos", "Estudiante", "Docente"])
            buscar = st.text_input("Buscar por nombre o correo", key="buscar_docente")
            df_filtrado = df.copy()
            if filtro_rol != "Todos":
                df_filtrado = df_filtrado[df_filtrado['rol'] == filtro_rol]
            if buscar:
                df_filtrado = df_filtrado[df_filtrado['nombre'].str.contains(buscar, case=False) |
                                          df_filtrado['email'].str.contains(buscar, case=False)]
            df_display = df_filtrado.drop(columns=["password"])
            st.dataframe(df_display)

            selected_email = st.selectbox("Selecciona un usuario para editar/eliminar", df_filtrado['email'])
            usuario = df_filtrado[df_filtrado['email'] == selected_email].iloc[0]

            with st.expander(f"Editar usuario: {usuario['nombre']}"):
                nuevo_nombre = st.text_input("Nombre", value=usuario['nombre'])
                nuevo_rol = st.radio("Rol", ["Estudiante", "Docente"], index=0 if usuario['rol']=="Estudiante" else 1)
                nueva_pass = st.text_input("Nueva contraseña (opcional)", type="password")
                if st.button("Guardar cambios"):
                    actualizar_usuario(selected_email, nombre=nuevo_nombre, rol=nuevo_rol, password=nueva_pass if nueva_pass else None)
                    st.success("Usuario actualizado correctamente.")
                    st.experimental_rerun()
                if st.button("Eliminar usuario"):
                    eliminar_usuario(selected_email)
                    st.warning(f"Usuario {selected_email} eliminado.")
                    st.experimental_rerun()
        else:
            st.info("No hay usuarios registrados aún.")

    # Panel estudiante
    elif st.session_state.rol == "Estudiante":
        st.info("👨‍🎓 Panel exclusivo para estudiantes")
        st.write("Aquí puedes acceder a tus recursos y ver tus actividades.")

    if st.button("Cerrar sesión"):
        st.session_state.login = False
        st.session_state.usuario = ""
        st.session_state.rol = ""
        st.success("Has cerrado sesión correctamente.")
