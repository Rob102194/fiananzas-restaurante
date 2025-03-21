import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

class ConsultasUI:
    def mostrar_filtros(self):
        """Muestra los controles de filtrado obligatorios"""
        with st.expander("⚙️ Filtros Obligatorios", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                categoria = st.selectbox(
                    "Categoría*",
                    options=["Mercancía", "Servicios", "Equipos", "Nómina", "Otros"],
                    index=0
                )
                
            with col2:
                fecha_inicio = st.date_input("Fecha inicial*", value=datetime.today() - timedelta(days=30))
                fecha_fin = st.date_input("Fecha final*", value=datetime.today())
        
        busqueda = st.text_input("Buscar en producto/descripción", "")
        
        return {
            'categoria': categoria,
            'fecha_inicio': fecha_inicio.isoformat(),
            'fecha_fin': fecha_fin.isoformat(),
            'busqueda': busqueda.strip()
        }

    def _mostrar_graficos(self, df, tipo):
        """Muestra gráfico de evolución temporal"""
        df_fecha = df.groupby('fecha')['monto'].sum().reset_index()
        fig = px.line(df_fecha, x='fecha', y='monto', 
                     title=f"Evolución de {'Compras' if tipo == 'compras' else 'Gastos'}",
                     labels={'monto': 'Monto Total ($)', 'fecha': 'Fecha'},
                     markers=True)
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    def mostrar_resultados(self, df, tipo):
        """Muestra los resultados de la consulta"""
        st.subheader("📊 Resultados")
        
        if df.empty:
            st.warning("No se encontraron registros con los filtros seleccionados")
            return
            
        # Mostrar métricas rápidas
        total = df['monto'].sum()
        max_dia = df.groupby('fecha')['monto'].sum().idxmax()
        
        col1, col2 = st.columns(2)
        col1.metric("Total general", f"${total:,.2f}")
        col2.metric("Día de mayor movimiento", max_dia.strftime("%d/%m/%Y"))
        
        # Mostrar tabla con formato
        columnas = ['fecha', 'producto', 'monto', 'categoria']
        if tipo == "compras":
            columnas.extend(['cantidad', 'unidad_medida'])
        else:
            columnas.append('descripcion')
            
        st.dataframe(
            df[columnas],
            height=400,
            use_container_width=True,
            column_config={
                'monto': st.column_config.NumberColumn(format="$%.2f"),
                'fecha': st.column_config.DateColumn(format="DD/MM/YYYY")
            }
        )
        
        # Mostrar gráficos
        self._mostrar_graficos(df, tipo)

    def mostrar_consulta_completa(self):
        """Interfaz completa de consultas"""
        st.header("🔍 Módulo de Consultas")
        filtros = self.mostrar_filtros()
        
        if st.button("🔍 Ejecutar Consulta", type="primary"):
            with st.spinner("Buscando registros..."):
                try:
                    # Determinar tabla automáticamente por categoría
                    tabla = "compras" if filtros['categoria'] == "Mercancía" else "gastos"
                    
                    # Obtener datos
                    df = self.logic.obtener_datos_consulta(
                        tabla=tabla,
                        filtros=filtros
                    )
                    
                    # Mostrar resultados
                    self.mostrar_resultados(df, tabla)
                    
                except Exception as e:
                    st.error(f"Error en la consulta: {str(e)}")