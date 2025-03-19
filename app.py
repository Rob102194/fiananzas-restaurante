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
ui = InterfaceManager()
analytics = AnalyticsEngine()

# Flujo principal
@st.cache_data
def load_data(_db):
    return _db.get_all_gastos()

# Cargar datos
raw_data = load_data(db)

if ui.menu_option == "Registro":
    new_data = ui.input_form()
    if new_data:
        db.insert_gasto(new_data)
        st.cache_data.clear()  # Forzar recarga de datos
        st.rerun()


elif ui.menu_option == "Consulta":
    if raw_data:
        df = pd.DataFrame(raw_data)
        deleted_ids, edited_data = ui.edit_delete_table(df.to_dict('records'))
        
        if deleted_ids:
            for id in deleted_ids:
                db.delete_gasto(id)
            st.rerun()
            
        if edited_data is not None:
            for row in edited_data:
                db.update_gasto(row['id'], row)
            st.rerun()

elif ui.menu_option == "Análisis":
    if raw_data:
        df = pd.DataFrame(raw_data)
        metrics = analytics.generate_metrics(df)
        
        st.subheader("Métricas Clave")
        cols = st.columns(3)
        cols[0].metric("Gasto Total", f"${metrics['gasto_total']:,.2f}")
        cols[1].metric("Costo Promedio", f"${metrics['gasto_promedio']:,.2f}")
        cols[2].metric("Categoría Principal", metrics['categoria_mayor'])
        
        fig1, fig2 = analytics.create_visualizations(df)
        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)

    else:
        st.warning("No hay datos para analizar")