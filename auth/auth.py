# auth.py
import streamlit as st
import hashlib
import yaml
from supabase import create_client

# Configuración inicial
def init_auth():
    """Inicializa la conexión a Supabase para autenticación"""
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

# Función para verificar credenciales
def check_credentials(username: str, password: str) -> bool:
    """Verifica las credenciales contra Supabase"""
    sb = init_auth()
    
    try:
        user = sb.table('usuarios').select('*').eq('username', username).single().execute()
        hashed_pwd = user.data['password']
        salt = user.data['salt']
        
        # Verificar hash
        new_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        
        return new_hash == hashed_pwd
    except Exception as e:
        st.error("Error de autenticación")
        return False

# Interfaz de login
def login_form() -> bool:
    """Muestra el formulario de login y maneja la autenticación"""
    with st.container():
        st.title("🔐 Restaurante Manager Login")
        
        with st.form("login"):
            username = st.text_input("Usuario", autocomplete="username")
            password = st.text_input("Contraseña", type="password", autocomplete="current-password")
            submitted = st.form_submit_button("Ingresar")
            
            if submitted:
                if check_credentials(username, password):
                    st.session_state['authenticated'] = True
                    st.session_state['user'] = username
                    st.rerun()
                else:
                    st.error("Credenciales inválidas")
                    
        return st.session_state.get('authenticated', False)

# Función de logout
def logout():
    """Cierra la sesión y limpia el estado"""
    st.session_state['authenticated'] = False
    st.session_state['user'] = None
    st.rerun()