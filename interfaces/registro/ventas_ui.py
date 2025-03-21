import streamlit as st
import pandas as pd
from datetime import datetime

class VentasUI:
    def __init__(self, logic):
        self.logic = logic
        
    def mostrar_formulario(self):
        with st.form("form_ventas"):
            # Subida de archivo
            archivo_csv = st.file_uploader(
                "Subir CSV de Ventas",
                type="csv",
                help="El archivo debe contener: producto, cantidad, precio_unitario, metodo_pago"
            )
            
            # Selector de fecha
            fecha_venta = st.date_input(
                "Fecha de las ventas",
                value=datetime.today(),
                format="DD/MM/YYYY"
            )
            
            # Vista previa
            if archivo_csv:
                with st.expander("Vista Previa del CSV", expanded=False):
                    df = pd.read_csv(archivo_csv)
                    st.dataframe(df.head(3), use_container_width=True)
            
            # Botón de envío
            enviado = st.form_submit_button("Registrar Ventas", type="primary")
            
        # Procesar fuera del form para evitar reruns
        if enviado and archivo_csv:
            self.logic.procesar_ventas(archivo_csv, fecha_venta)
            
    def mostrar_interfaz_completa(self):
        self.mostrar_formulario()