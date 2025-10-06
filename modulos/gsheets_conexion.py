# modulos/gsheets_conexion.py

import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def connect_to_gsheets():
    """Establece la conexión con Google Sheets usando la estructura de secretos del usuario."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Se ajusta para leer desde la sección [gcp]
    creds_dict = {
        "type": st.secrets["gcp"]["type"],
        "project_id": st.secrets["gcp"]["project_id"],
        "private_key_id": st.secrets["gcp"]["private_key_id"],
        "private_key": st.secrets["gcp"]["private_key"],  # Ya no es necesario el .replace()
        "client_email": st.secrets["gcp"]["client_email"],
        "client_id": st.secrets["gcp"]["client_id"],
        "auth_uri": st.secrets["gcp"]["auth_uri"],
        "token_uri": st.secrets["gcp"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["gcp"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["gcp"]["client_x509_cert_url"],
    }
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client


def get_worksheet():
    """Obtiene la hoja de trabajo específica usando el ID del spreadsheet."""
    client = connect_to_gsheets()

    # Se ajusta para usar el ID de la sección [spreadsheet]
    spreadsheet_id = st.secrets["spreadsheet"]["id"]
    sheet = client.open_by_key(spreadsheet_id).sheet1
    return sheet