import streamlit as st
import pandas as pd
from datetime import datetime  
from typing import Dict, List
from streamlit_option_menu import option_menu

class InterfaceManager:
    def __init__(self, db):
        self.menu_option = None
        self.db = db
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

    def registro_form(self):
        """Interfaz de registro con sub-opciones"""
        opcion = st.radio(
            "Tipo de Registro",
            options=["Ventas", "Compras y Gastos", "Producción"],
            horizontal=True
        )
        
        if opcion == "Ventas":
            self._ventas_form()
        elif opcion == "Compras y Gastos":
            self._compras_gastos_form()

    def _ventas_form(self):
        """Formulario específico para ventas"""
        with st.form("form_ventas"):
            # Subida de archivo CSV
            uploaded_file = st.file_uploader("Subir CSV de Ventas", type="csv")
            
            # Selector de fecha
            fecha_venta = st.date_input("Fecha de las ventas")
            
            # Vista previa de datos
            preview_expander = st.expander("Vista Previa CSV", expanded=False)
            if uploaded_file:
                df = pd.read_csv(uploaded_file)
                with preview_expander:
                    st.dataframe(df.head(3))
                    
                # Validar estructura del CSV
                required_cols = ["producto", "cantidad", "precio_unitario", "metodo_pago"]
                if not all(col in df.columns for col in required_cols):
                    st.error(f"El CSV debe contener las columnas: {', '.join(required_cols)}")
            
            # Botón de confirmación (SIEMPRE visible)
            submitted = st.form_submit_button("📤 Registrar Ventas")
            
        # Lógica fuera del form context manager
        if submitted and uploaded_file:
            try:
                if all(col in df.columns for col in required_cols):
                    # Convertir y guardar datos
                    df['fecha'] = fecha_venta.isoformat()
                    data = df.to_dict('records')
                    
                    # Insertar en batch
                    response = self.db.client.table('ventas').insert(data).execute()
                    st.success(f"✅ {len(response.data)} ventas registradas!")
                    st.balloons()
                else:
                    st.warning("Corrige los errores en el CSV antes de enviar")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    def _compras_gastos_form(self):
        
        """Formulario dinámico con layout mejorado"""
        with st.form("form_registro"):
            # Dividir en 2 columnas iguales
            col1, col2 = st.columns([1, 1], gap="large")
            
            with col1:
                # --- Campos Principales ---
                st.subheader("📝 Información Básica")
                fecha = st.date_input("Fecha*", value=datetime.today())
                proveedor = st.text_input("Proveedor", placeholder="Ej: Suministros S.A.")
                categoria = st.selectbox(
                    "Categoría*",
                    options=["Mercancía", "Servicios", "Equipos", "Nómina", "Otros"],
                    index=0,
                    help="Seleccione 'Mercancía' para insumos de producción"
                )
                monto = st.number_input("Monto Total*", min_value=0.0, format="%.2f")
            
            with col2:
                # --- Campos Condicionales ---
                st.subheader("📦 Detalles Específicos")
                if categoria == "Mercancía":
                    producto = st.text_input("Producto*", placeholder="Ej: Filete de res")
                    cantidad = st.number_input("Cantidad*", 
                        min_value=0.001, 
                        step=0.1, 
                        format="%.3f",
                        help="Cantidad exacta recibida"
                    )
                    unidad = st.selectbox(
                        "Unidad de Medida*",
                        options=["kg", "litro", "unidad", "paquete"],
                        index=0,
                        disabled=False  # Solo habilitado para Mercancía
                    )
                else:
                    descripcion = st.text_area(
                        "Descripción Detallada*",
                        placeholder="Detalle el gasto (Ej: Mantenimiento de equipos...)",
                        height=100
                    )
            
            # Botón de submit al final
            submitted = st.form_submit_button("💾 Guardar Registro", use_container_width=True)
        
        # Lógica de procesamiento
        if submitted:
            data = {
                "fecha": fecha.isoformat(),
                "proveedor": proveedor.strip(),
                "monto": monto,
                "categoria": categoria
            }
            
            try:
                # Validación condicional
                if categoria == "Mercancía":
                    if not producto.strip():
                        raise ValueError("Debe especificar el producto")
                    data.update({
                        "producto": producto.strip(),
                        "cantidad": cantidad,
                        "unidad_medida": unidad
                    })
                else:
                    if not descripcion.strip():
                        raise ValueError("Debe agregar una descripción del gasto")
                    data["descripcion"] = descripcion.strip()
                
                self.db.insert_registro(data)
                st.success("✅ Registro exitoso!")
                st.rerun()
                
            except Exception as e:
                st.error(f"🚨 Error: {str(e)}")

    def show_records(self, table_name: str):
        """Muestra registros con formato específico"""
        df = pd.DataFrame(self.db.client.table(table_name).select("*").execute().data)
        
        if not df.empty:
            if table_name == "compras":
                st.write("📦 **Registros de Mercancías**")
                st.dataframe(
                    df.style.format({
                        "cantidad": "{:.3f}",
                        "monto": "💰 ${:.2f}"
                    }),
                    column_config={
                        "created_at": st.column_config.DatetimeColumn("Fecha Registro")
                    }
                )
            else:
                st.write("🧾 **Registros de Gastos**")
                st.dataframe(
                    df[["fecha", "categoria", "proveedor", "monto", "descripcion"]],
                    column_config={
                        "monto": st.column_config.NumberColumn(format="$%.2f")
                    }
                )