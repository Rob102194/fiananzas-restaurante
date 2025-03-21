import streamlit as st
import pandas as pd
from datetime import datetime

class VentasUI:
    def __init__(self, logic):
        self.logic = logic
        self._inicializar_estado()
        
    def _inicializar_estado(self):
        """Estado para controlar cada entidad por separado"""
        if 'restaurante' not in st.session_state:
            st.session_state.restaurante = {'archivo': None, 'registrado': False}
        if 'domicilio' not in st.session_state:
            st.session_state.domicilio = {'archivo': None, 'registrado': False}
            
    def _mostrar_selector_fecha(self):
        """Selector de fecha común para ambas entidades"""
        return st.date_input(
            "📅 Fecha de registro",
            value=datetime.today(),
            format="DD/MM/YYYY",
            key="fecha_comun"
        )
    
    def _mostrar_formulario_entidad(self, entidad):
        """Componente reusable para cada entidad"""
        label = "🍽️ Restaurante" if entidad == "restaurante" else "🚚 Domicilio"
        estado = st.session_state[entidad]
        
        with st.expander(label, expanded=True):
            # Subida de archivo
            nuevo_archivo = st.file_uploader(
                f"Subir Excel para {label}",
                type=["xlsx", "xls"],
                key=f"uploader_{entidad}",
                accept_multiple_files=False,
                help=f"Archivo debe contener: Grupo, Nombre, Cantidad, $ Venta",
                on_change=lambda: self._actualizar_estado(entidad, archivo=True)
            )
            
            # Vista previa
            if nuevo_archivo:
                try:
                    df = pd.read_excel(nuevo_archivo, engine='openpyxl')
                    st.dataframe(
                        df.head(3),
                        use_container_width=True,
                        hide_index=True,
                        column_config={"$ Venta": st.column_config.NumberColumn(format="$%.2f")}
                    )
                    estado['archivo'] = nuevo_archivo
                except Exception as e:
                    st.error(f"Error leyendo archivo: {str(e)}")
            
            # Botón de registro
            if st.button(
                f"💾 Registrar {label}",
                key=f"btn_{entidad}",
                disabled=estado['registrado'],
                type="primary" if not estado['registrado'] else "secondary"
            ):
                self._procesar_registro(entidad)
                
            # Mensaje de estado
            if estado['registrado']:
                st.success("✅ Registrado exitosamente")
                
    def _actualizar_estado(self, entidad, archivo=False):
        """Actualiza el estado de la entidad"""
        if archivo:
            st.session_state[entidad]['registrado'] = False
            
    def _procesar_registro(self, entidad):
        """Maneja el registro para cada entidad"""
        try:
            estado = st.session_state[entidad]
            fecha = st.session_state.fecha_comun.isoformat()
            
            resultado = self.logic.registrar_ventas(
                estado['archivo'],
                entidad,
                fecha
            )
            
            estado['registrado'] = True
            estado['archivo'] = None
            st.toast(f"✅ {len(resultado)} registros para {entidad}", icon="✅")
            st.rerun()
            
        except Exception as e:
            st.error(f"🚨 Error en {entidad}: {str(e)}")
            estado['registrado'] = False

    def mostrar_interfaz_completa(self):     
        # Fecha común
        fecha = self._mostrar_selector_fecha()
        
        # Dos columnas para cada entidad
        col1, col2 = st.columns(2)
        
        with col1:
            self._mostrar_formulario_entidad("restaurante")
            
        with col2:
            self._mostrar_formulario_entidad("domicilio")
        
        # Mensaje de ayuda
        st.markdown("""
        **Instrucciones:**
        1. Seleccione fecha común para ambos registros
        2. Suba archivos separados para cada entidad
        3. Registre cada entidad independientemente
        4. ¡Cada entidad solo puede registrarse una vez por fecha!
        """)