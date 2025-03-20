import streamlit as st
import pandas as pd
from datetime import datetime, timedelta      
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

    """INTERFAZ DE REGISTRO"""
    
    def registro_form(self):
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
        """Formulario con validación en tiempo real y campos dinámicos"""
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
                if categoria == "Mercancía":
                    cantidad = st.number_input("Cantidad*", 
                        min_value=0.001, 
                        step=0.1, 
                        format="%.3f"
                    )
                    unidad = st.selectbox("Unidad Medida*", 
                        options=["kg", "litro", "unidad", "paquete"]
                    )
                    
                else:
                    cantidad = None
                    unidad = None

                descripcion = st.text_area("Descripción", 
                        placeholder="Detalles adicionales (opcional)", 
                        height=100
                    )
                
            submitted = st.form_submit_button("💾 Guardar Registro")
        
        if submitted:
            try:
                # Validación estricta
                error_messages = []
                
                if not producto.strip():
                    error_messages.append("- Producto es obligatorio para todas las categorías")
                    
                if monto <= 0:
                    error_messages.append("- Monto debe ser mayor a 0")
                    
                if categoria == "Mercancía":
                    if not cantidad or cantidad <= 0:
                        error_messages.append("- Cantidad debe ser mayor a 0")
                    if not unidad:
                        error_messages.append("- Unidad de medida es obligatoria")

                if error_messages:
                    raise ValueError("\n".join(error_messages))
                
                # Preparar datos
                base_data = {
                    "fecha": fecha.isoformat(),
                    "categoria": categoria,
                    "proveedor": proveedor.strip() if proveedor else None,
                    "monto": monto,
                    "producto": producto.strip()
                }
                
                if categoria == "Mercancía":
                    full_data = {
                        **base_data,
                        "cantidad": cantidad,
                        "unidad_medida": unidad,
                        "descripcion": descripcion.strip() if descripcion else None
                    }
                    table = "compras"
                else:
                    full_data = base_data
                    table = "gastos"
                
                # Insertar en tabla correcta
                self.db.client.table(table).insert(full_data).execute()
                st.success("✅ Registro guardado correctamente!")
                st.rerun()
                
            except Exception as e:
                st.error(f"**Errores detectados:**\n{str(e)}")

        """INTERFAZ DE CONSULTA"""

    def consulta_gastos(self):
        st.subheader("🔍 Consulta de Gastos y Compras")
        
        with st.expander("⚙️ Filtros", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Rango de fechas
                fecha_inicio = st.date_input("Fecha inicial", value=datetime.today() - timedelta(days=30))
                fecha_fin = st.date_input("Fecha final", value=datetime.today())
                
            with col2:
                # Selector de categorías desde la base de datos
                categorias = self.db.get_categorias()
                categoria_seleccionada = st.selectbox(
                    "Categoría",
                    options=["Todas"] + categorias,
                    index=0
                )
                
            with col3:
                # Búsqueda de producto
                producto_busqueda = st.text_input("Buscar por producto", placeholder="Ej: Carne de res")
        
        # Consultar datos
        if st.button("🔍 Aplicar Filtros"):
            try:
                # Construir query dinámico
                query = """
                    SELECT 
                        fecha,
                        categoria,
                        producto,
                        monto,
                        proveedor,
                        CASE WHEN cantidad IS NOT NULL THEN cantidad || ' ' || unidad_medida END as detalle
                    FROM compras
                    WHERE fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
                    UNION ALL
                    SELECT 
                        fecha,
                        categoria,
                        producto,
                        monto,
                        proveedor,
                        NULL as detalle
                    FROM gastos
                    WHERE fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
                """
                
                # Aplicar filtros
                if categoria_seleccionada != "Todas":
                    query += f" AND categoria = '{categoria_seleccionada}'"
                    
                if producto_busqueda.strip():
                    query += f" AND producto ILIKE '%{producto_busqueda.strip()}%'"
                
                # Ejecutar consulta
                datos = self.db.execute_query(query.format(
                    fecha_inicio=fecha_inicio.isoformat(),
                    fecha_fin=fecha_fin.isoformat()
                ))
                
                if not datos:
                    st.warning("❌ No se encontraron registros con los filtros aplicados")
                    return
                    
                df = pd.DataFrame(datos)
                
                # Mostrar resultados
                st.dataframe(
                    df.style.format({'monto': '💰 ${:.2f}'}),
                    column_config={
                        "fecha": st.column_config.DateColumn(format="DD/MM/YYYY"),
                        "detalle": "Cantidad"
                    },
                    height=500
                )
                
                # Exportar datos
                st.download_button(
                    label="📤 Exportar a CSV",
                    data=df.to_csv(index=False).encode('utf-8'),
                    file_name=f"consulta_gastos_{datetime.today().date()}.csv",
                    mime="text/csv"
                )
                
            except Exception as e:
                st.error(f"Error en la consulta: {str(e)}")