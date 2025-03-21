import streamlit as st
from datetime import datetime

# Configuración inicial de página (debe ser lo primero)
st.set_page_config(
    page_title="Gestión de Restaurante",
    page_icon="🍽️",
    layout="wide"
)

# Inicializar estado de sesión
if 'user' not in st.session_state:
    st.session_state.user = None
    st.session_state.authenticated = False

# Verificar autenticación
from auth.auth import login_form
if not st.session_state.authenticated:
    if not login_form():
        st.stop()

from modules.database import DatabaseManager
from interfaces.sidebar import SidebarManager
from modules.logic.ventas import VentasLogic
from modules.logic.compras_gastos import ComprasGastosLogic
from modules.logic.consultas import ConsultasLogic
from interfaces.registro.registro_ui import RegistroUI
from interfaces.registro.ventas_ui import VentasUI
from interfaces.registro.compras_gastos_ui import ComprasGastosUI
from interfaces.consultas.gastos_ui import ConsultasUI

# Inicializar componentes principales
@st.cache_resource
def inicializar_db():
    return DatabaseManager()

db = inicializar_db()
sidebar = SidebarManager()

# Inicializar lógicas de negocio
ventas_logic = VentasLogic(db)
compras_gastos_logic = ComprasGastosLogic(db)
consultas_logic = ConsultasLogic(db)

# Routing de vistas
if sidebar.menu_option == "Registro":
    registro_ui = RegistroUI(ventas_logic, compras_gastos_logic)
    registro_ui.mostrar_interfaz()

elif sidebar.menu_option == "Consulta":
    ConsultasUI(consultas_logic).mostrar_consulta_completa()

# Footer con información de sesión
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
**Usuario:** {st.session_state.user}  
**Última actualización:** {datetime.now().strftime("%d/%m/%Y %H:%M")}
""")

# Codigo de prueba
try:
    test_data = db.client.table("compras").select("*").limit(1).execute()
    st.sidebar.success(f"✅ Conexión exitosa a Supabase. Proyecto: {db.client.supabase_url}")
    st.sidebar.write("Datos de prueba:", test_data.data)
except Exception as e:
    st.sidebar.error(f"❌ Error de conexión: {str(e)}")
    st.stop()
