import streamlit as st
from modules.database import DatabaseManager
from modules.ui import InterfaceManager
from modules.analytics import AnalyticsEngine
import pandas as pd

# Configuración inicial
st.set_page_config(page_title="Gestión de Gastos", layout="wide")

# Inicialización de módulos
@st.cache_resource
def init_db():
    return DatabaseManager()

db = init_db()
ui = InterfaceManager()
analytics = AnalyticsEngine()

# Flujo principal
tab1, tab2, tab3 = st.tabs(["Registro", "Consulta", "Análisis"])

with tab1:
    new_data = ui.input_form()
    if new_data:
        db.insert_gasto(new_data)
        st.rerun()

with tab2:
    raw_data = db.get_all_gastos()
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

with tab3:
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