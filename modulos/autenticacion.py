import streamlit as st
from .gsheets_conexion import get_worksheet
import pandas as pd

def registrar_usuario(username, password, email):
    """Registra un nuevo usuario en la hoja de Google Sheets."""
    try:
        sheet = get_worksheet()
        users_df = pd.DataFrame(sheet.get_all_records())

        if not users_df.empty and username in users_df['username'].values:
            return False, "El nombre de usuario ya existe."

        # Asegúrate de que el orden coincida con las columnas de tu Google Sheet
        nuevo_usuario = [username, password, email]
        sheet.append_row(nuevo_usuario)
        return True, "Registro exitoso."
    except Exception as e:
        return False, f"Error al registrar: {e}"

def login_usuario(username, password):
    """Verifica las credenciales de un usuario."""
    try:
        sheet = get_worksheet()
        users_df = pd.DataFrame(sheet.get_all_records())

        if users_df.empty or username not in users_df['username'].values:
            return False, "Nombre de usuario no encontrado."

        user_data = users_df[users_df['username'] == username].iloc[0]

        if str(user_data['password']) == password:
            return True, "Inicio de sesión exitoso."
        else:
            return False, "Contraseña incorrecta."
    except Exception as e:
        return False, f"Error al iniciar sesión: {e}"