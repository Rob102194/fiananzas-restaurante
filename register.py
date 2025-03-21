# register.py
import streamlit as st
from auth.auth import init_auth
import hashlib
import secrets

def create_user(username: str, password: str) -> bool:
    """Crea un nuevo usuario de forma segura con verificación"""
    sb = init_auth()
    
    try:
        # Validación básica
        if not username or not password:
            st.error("❌ Usuario y contraseña son obligatorios")
            return False
            
        if len(password) < 8:
            st.error("❌ La contraseña debe tener al menos 8 caracteres")
            return False
        
        # Generar componentes de seguridad
        salt = secrets.token_hex(16)
        hashed_pwd = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        
        # Insertar en Supabase con verificación
        response = sb.table('usuarios').insert({
            'username': username,
            'password': hashed_pwd,
            'salt': salt
        }).execute()
        
        # Verificar respuesta
        if not response.data:
            st.error("⚠️ No se recibió confirmación de la base de datos")
            return False
            
        st.success("✅ Usuario creado exitosamente!")
        st.json(response.data[0])  # Muestra la respuesta de Supabase
        return True
        
    except Exception as e:
        st.error(f"🔥 Error crítico: {str(e)}")
        return False

# Interfaz mejorada
st.title("🆕 Registro de Nuevo Usuario")

with st.form("register"):
    username = st.text_input("Nombre de usuario (mín. 4 caracteres)")
    password = st.text_input("Contraseña (mín. 8 caracteres)", type="password")
    
    if st.form_submit_button("Crear Usuario"):
        if create_user(username.strip(), password):
            st.balloons()