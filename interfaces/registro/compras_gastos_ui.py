import streamlit as st
from datetime import datetime

class ComprasGastosUI:
    def __init__(self, logic):
        self.logic = logic
        
    def show_form(self):
        with st.form("form_compras_gastos"):
            categoria = st.selectbox(
                "Categoría*",
                options=["Mercancía", "Servicios", "Equipos", "Nómina", "Otros"],
                index=0
            )
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                fecha = st.date_input("Fecha*", value=datetime.today())
                producto = st.text_input("Producto*", placeholder="Ej: Suministros varios")
                monto = st.number_input("Monto Total*", min_value=0.0, format="%.2f") 
                proveedor = st.text_input("Proveedor", placeholder="Opcional")
                
            with col2:
                cantidad = st.number_input("Cantidad", 
                    min_value=0.0, 
                    step=0.1, 
                    format="%.3f",
                    help="Requerido solo para Mercancía"
                )
                unidad = st.selectbox("Unidad Medida", 
                    options=["kg", "litro", "unidad", "paquete", "N/A"],
                    index=4 if categoria != "Mercancía" else 2,
                    help="Seleccione 'N/A' si no aplica"
                )
                
                descripcion = st.text_area("Descripción", 
                    placeholder="Detalles adicionales (opcional)", 
                    height=100
                )
                
            submitted = st.form_submit_button("💾 Guardar Registro")
        
        if submitted:
            self.logic.process_registro(
                categoria,
                fecha,
                producto,
                monto,
                proveedor,
                cantidad,
                unidad,
                descripcion
            )