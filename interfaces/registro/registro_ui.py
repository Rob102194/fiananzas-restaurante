import streamlit as st
from interfaces.registro.ventas_ui import VentasUI
from interfaces.registro.compras_gastos_ui import ComprasGastosUI

class RegistroUI:
    def __init__(self, ventas_logic, compras_gastos_logic):
        self.ventas_ui = VentasUI(ventas_logic)
        self.compras_gastos_ui = ComprasGastosUI(compras_gastos_logic)
        
    def mostrar_interfaz(self):
        st.header("📥 Módulo de Registros")
        
        # Selector de tipo de registro
        tipo_registro = st.radio(
            "Tipo de Registro",
            options=["Ventas", "Compras y Gastos", "Producción"],
            horizontal=True,
            key="registro_selector"
        )
        
        # Contenedor para formularios
        with st.container():
            if tipo_registro == "Ventas":
                self.ventas_ui.mostrar_interfaz_completa()
                
            elif tipo_registro == "Compras y Gastos":
                self.compras_gastos_ui.show_form()
                
            else:  # Producción
                st.warning("🚧 Módulo en desarrollo")
                st.info("Próximamente: Registro de producción diaria")