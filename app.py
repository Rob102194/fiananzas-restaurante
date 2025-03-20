import streamlit as st
from modules.database import DatabaseManager
from modules.ui import InterfaceManager
from modules.analytics import AnalyticsEngine
import pandas as pd

# Configuración inicial
st.set_page_config(
    page_title="Gestión de Restaurante", 
    page_icon="🍽️", 
    layout="wide"
)

# Inicialización de módulos

@st.cache_resource
def init_db():
    return DatabaseManager()

db = init_db()
ui = InterfaceManager(db)
analytics = AnalyticsEngine()

# Codigo de prueba
try:
    test_data = db.client.table("compras").select("*").limit(1).execute()
    st.sidebar.success(f"✅ Conexión exitosa a Supabase. Proyecto: {db.client.supabase_url}")
    st.sidebar.write("Datos de prueba:", test_data.data)
except Exception as e:
    st.sidebar.error(f"❌ Error de conexión: {str(e)}")
    st.stop()

# Flujo principal
@st.cache_data
def load_data(_db):
    """Obtiene todos los registros combinados de compras y gastos"""
    query = """
        SELECT 
            'compra' as tipo,
            fecha,
            categoria,
            producto,
            monto,
            proveedor,
            cantidad,
            unidad_medida,
            NULL as descripcion
        FROM compras
        
        UNION ALL
        
        SELECT 
            'gasto' as tipo,
            fecha,
            categoria,
            producto,
            monto,
            proveedor,
            NULL as cantidad,
            NULL as unidad_medida,
            descripcion
        FROM gastos
    """
    return _db.execute_query(query)

# Cargar datos
#raw_data = load_data(db)

if ui.menu_option == "Registro":
    ui.registro_form()

elif ui.menu_option == "Consulta":
    ui.consulta_gastos()

elif ui.menu_option == "Análisis":
    st.warning("No hay datos para analizar")