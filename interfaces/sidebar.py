import streamlit as st
from streamlit_option_menu import option_menu

class SidebarManager:
    def __init__(self):
        self.menu_option = None
        self._setup_sidebar()
    
    def _setup_sidebar(self):
        """Configuración de sidebar"""
        with st.sidebar:
            st.image("assets/logo.png", width=120)
            st.title("🍽️ Gestor Gastos")
            st.markdown("---")
            
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
            
            st.write(f"Usuario: {st.session_state.user}")
            if st.button("🚪 Cerrar Sesión"):
                from auth.auth import logout
                logout()