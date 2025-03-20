import streamlit as st
import pandas as pd
from datetime import datetime, timedelta      
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
        """Formulario con campos siempre visibles pero condicionalmente requeridos"""
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
                # Campos siempre visibles
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
            try:
                # Validación condicional
                error_messages = []
                
                if not producto.strip():
                    error_messages.append("- Producto es obligatorio")
                    
                if monto <= 0:
                    error_messages.append("- Monto debe ser mayor a 0")
                    
                # Solo validar cantidad y unidad para Mercancía
                if categoria == "Mercancía":
                    if cantidad <= 0:
                        error_messages.append("- Cantidad debe ser > 0 para Mercancía")
                    if unidad == "N/A":
                        error_messages.append("- Seleccione una unidad válida para Mercancía")

                if error_messages:
                    raise ValueError("\n".join(error_messages))
                
                # Preparar datos (solo incluir campos relevantes)
                base_data = {
                    "fecha": fecha.isoformat(),
                    "categoria": categoria,
                    "proveedor": proveedor.strip() if proveedor else None,
                    "monto": monto,
                    "producto": producto.strip(),
                    "descripcion": descripcion.strip() if descripcion else None
                }
                
                # Agregar campos específicos solo para Mercancía
                if categoria == "Mercancía":
                    base_data.update({
                        "cantidad": cantidad,
                        "unidad_medida": unidad if unidad != "N/A" else None
                    })
                
                # Determinar tabla destino
                table = "compras" if categoria == "Mercancía" else "gastos"
                
                # Eliminar campos nulos para gastos
                if table == "gastos":
                    base_data = {k: v for k, v in base_data.items() if v is not None}
                    base_data.pop('cantidad', None)  # Eliminar por seguridad
                    base_data.pop('unidad_medida', None)

                # Insertar en la tabla correspondiente
                self.db.client.table(table).insert(base_data).execute()
                st.success("✅ Registro guardado correctamente!")
                st.rerun()
                
            except Exception as e:
                st.error(f"**Errores detectados:**\n{str(e)}")

        """INTERFAZ DE CONSULTA"""

    def consulta_gastos(self):
        """Consulta con categoría obligatoria y búsqueda segmentada"""
        st.subheader("🔍 Consulta de Registros")
        
        with st.expander("⚙️ Filtros Obligatorios", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                categoria_seleccionada = st.selectbox(
                    "Categoría*",
                    options=["Mercancía", "Servicios", "Equipos", "Nómina", "Otros"],
                    index=0
                )
                
            with col2:
                fecha_inicio = st.date_input("Fecha inicial*", value=datetime.today() - timedelta(days=30))
                fecha_fin = st.date_input("Fecha final*", value=datetime.today())
        
        producto_busqueda = st.text_input("Buscar por producto", placeholder="Opcional...")
        
        if st.button("🔍 Ejecutar Búsqueda", type="primary"):
            try:
                # Verificación de consistencia de fechas
                if fecha_inicio > fecha_fin:
                    st.error("❌ La fecha inicial no puede ser mayor a la final")
                    return
                    
                # Determinar tabla
                tabla = "compras" if categoria_seleccionada == "Mercancía" else "gastos"
                
                # Construir parámetros con valores normalizados
                filters = {
                    "categoria": categoria_seleccionada.strip(),
                    "fecha_inicio": fecha_inicio.isoformat(),
                    "fecha_fin": fecha_fin.isoformat(),
                    "search": producto_busqueda.strip() if producto_busqueda else None
                }
                
                st.write("⚙️ Filtros enviados a la consulta:", filters)  # Debug 7
                
                # Ejecutar consulta
                datos = self.db.execute_safe_query(tabla, filters)
                
                # Verificación de datos vacíos
                if not datos:
                    st.warning(f"⚠️ No hay registros de {categoria_seleccionada} entre {fecha_inicio} y {fecha_fin}")
                    return
                    
                # Procesamiento de datos con verificación de columnas
                df = pd.DataFrame(datos)
                columnas_requeridas = {
                    "compras": ["fecha", "producto", "monto", "categoria", "cantidad", "unidad_medida"],
                    "gastos": ["fecha", "producto", "monto", "categoria", "descripcion"]
                }
                
                # Verificar existencia de columnas
                columnas_faltantes = [col for col in columnas_requeridas[tabla] if col not in df.columns]
                if columnas_faltantes:
                    st.error(f"🚨 Columnas faltantes en la respuesta: {', '.join(columnas_faltantes)}")
                    return
                
                # Mostrar resultados
                st.dataframe(
                    df[columnas_requeridas[tabla]],
                    column_config={
                        "monto": st.column_config.NumberColumn(format="$%.2f"),
                        "fecha": st.column_config.DateColumn(format="DD/MM/YYYY"),
                        "cantidad": st.column_config.NumberColumn(format="%.3f") if tabla == "compras" else None
                    },
                    height=400,
                    use_container_width=True
                )
                
                # Cálculo de total con verificación
                try:
                    total = df['monto'].sum()
                    st.metric(f"📊 Total {categoria_seleccionada}", f"${total:,.2f}")
                except KeyError:
                    st.error("🔍 La columna 'monto' no existe en los datos recibidos")
                
            except Exception as e:
                st.error(f"🚑 Error crítico: {str(e)}")