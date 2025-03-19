import streamlit as st
import pandas as pd
from datetime import date
from typing import Dict, List
from streamlit_option_menu import option_menu

class InterfaceManager:
    def __init__(self):
        self.menu_option = None
        self._setup_sidebar()
    
    def _setup_sidebar(self):
        """Configuracion de sidebar"""
        with st.sidebar:
            st.image("assets/logo.png", width=120)
            st.title("🍽️ Gestor Gastos")
            st.markdown("---")
            
            # Menú con iconos
            self.menu_option = option_menu(
                menu_title=None,
                options=["Registro", "Consulta", "Análisis"],
                icons=["pencil-square", "search", "bar-chart-line"], 
                default_index=0,
                styles={
                    "container": {"padding": "0!important"},
                    "nav-link": {"font-size": "16px", "margin": "5px 0"}
                }
            )

    @staticmethod
    def input_form() -> Dict:
        with st.form("nuevo_gasto"):
            cols = st.columns(3)
            with cols[0]:
                fecha = st.date_input("Fecha", value=date.today())
            with cols[1]:
                categoria = st.selectbox("Categoría", ["Mercancía", "Servicios", "Equipos"])
            with cols[2]:
                proveedor = st.text_input("Proveedor")
            
            cols = st.columns([2,1,1])
            with cols[0]:
                descripcion = st.text_area("Descripción")
            with cols[1]:
                cantidad = st.number_input("Cantidad", min_value=0.001, step=0.1, format="%.3f")
            with cols[2]:
                unidad = st.selectbox("UM", ["kg", "litro", "unidad", "paquete"])
            
            monto = st.number_input("Monto Total (USD)", min_value=0.0, format="%.2f")
            
            if st.form_submit_button("💾 Guardar Gasto"):
                return {
                    "fecha": fecha.isoformat(),
                    "categoria": categoria,
                    "proveedor": proveedor,
                    "descripcion": descripcion,
                    "cantidad": cantidad,
                    "unidad_medida": unidad,
                    "monto": monto
                }
        return None

    @staticmethod
    def edit_delete_table(data: List[Dict]) -> tuple:
    # Convertir strings a datetime
        for row in data:
            if isinstance(row['fecha'], str):
                row['fecha'] = pd.to_datetime(row['fecha']).date()
        
        # Configurar columnas editables
        column_config = {
            "fecha": st.column_config.DateColumn(
                format="YYYY-MM-DD",
                required=True
            ),
            "monto": st.column_config.NumberColumn(
                format="$%.2f",
                required=True
            ),
            "cantidad": st.column_config.NumberColumn(
                format="%.3f",
                required=True
            )
        }
    
        edited_data = st.data_editor(
            data,
            column_config=column_config,
            key="editor",
            num_rows="dynamic"
    )
    
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Eliminar seleccionados"):
                deleted_ids = [row['id'] for row in st.session_state.editor['deleted_rows']]
                return deleted_ids, None
        with col2:
            if st.button("💾 Guardar cambios"):
                return None, edited_data
        
        return None, None