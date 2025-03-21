import streamlit as st

# Configuración inicial
st.set_page_config(
    page_title="Gestión de Restaurante",
    page_icon="🍽️",
    layout="wide"
)

# Inicializar estado de sesión
if 'user' not in st.session_state:
    st.session_state.user = None
    st.session_state.authenticated = False

# Verificar autenticación antes de cargar cualquier componente
from auth.auth import login_form
if not st.session_state.authenticated:
    if not login_form():
        st.stop()  # Detiene la ejecución si no está autenticado

from interfaces.sidebar import SidebarManager
from modules.logic.ventas import VentasLogic
from modules.logic.compras_gastos import ComprasGastosLogic
from modules.database import DatabaseManager
from modules.logic.consultas import ConsultasLogic
from interfaces.consultas.gastos_ui import ConsultasUI

# Inicialización de componentes
db = DatabaseManager()
sidebar = SidebarManager()
ventas_logic = VentasLogic(db)
compras_gastos_logic = ComprasGastosLogic(db)

consultas_logic = ConsultasLogic(db)
consultas_ui = ConsultasUI(consultas_logic)

# Routing de vistas
if sidebar.menu_option == "Registro":
    from interfaces.registro.ventas_ui import VentasUI
    from interfaces.registro.compras_gastos_ui import ComprasGastosUI
    
    VentasUI(ventas_logic).show_form()
    ComprasGastosUI(compras_gastos_logic).show_form()

elif sidebar.menu_option == "Consulta":
    consultas_ui.mostrar_consulta_completa()





# Codigo de prueba
try:
    test_data = db.client.table("compras").select("*").limit(1).execute()
    st.sidebar.success(f"✅ Conexión exitosa a Supabase. Proyecto: {db.client.supabase_url}")
    st.sidebar.write("Datos de prueba:", test_data.data)
except Exception as e:
    st.sidebar.error(f"❌ Error de conexión: {str(e)}")
    st.stop()
