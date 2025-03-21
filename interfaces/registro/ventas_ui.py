import streamlit as st
import pandas as pd
from datetime import datetime

class VentasUI:
    def __init__(self, logic):
        self.logic = logic
        
    def show_form(self):
        opcion = st.radio(
            "Tipo de Registro",
            options=["Ventas", "Compras y Gastos", "Producción"],
            horizontal=True
        )
        
        if opcion == "Ventas":
            self._render_form()

    def _render_form(self):
        with st.form("form_ventas"):
            uploaded_file = st.file_uploader("Subir CSV de Ventas", type="csv")
            fecha_venta = st.date_input("Fecha de las ventas")
            
            preview_expander = st.expander("Vista Previa CSV", expanded=False)
            if uploaded_file:
                df = pd.read_csv(uploaded_file)
                with preview_expander:
                    st.dataframe(df.head(3))
                    
                required_cols = ["producto", "cantidad", "precio_unitario", "metodo_pago"]
                if not all(col in df.columns for col in required_cols):
                    st.error(f"El CSV debe contener las columnas: {', '.join(required_cols)}")
            
            submitted = st.form_submit_button("📤 Registrar Ventas")
            
        if submitted and uploaded_file:
            self.logic.process_ventas(uploaded_file, fecha_venta)