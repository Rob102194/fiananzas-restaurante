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

# Flujo principal
#@st.cache_data
#def load_data(_db):
#    query = """
#        SELECT * FROM compras
#        UNION ALL
#        SELECT *, NULL as cantidad, NULL as unidad_medida FROM gastos
#   """
#    return _db.execute_query(query)

# Cargar datos
#raw_data = load_data(db)

if ui.menu_option == "Registro":
    ui.registro_form()

elif ui.menu_option == "Consulta":
    ui.consulta_gastos()

elif ui.menu_option == "Análisis":
    st.warning("No hay datos para analizar")