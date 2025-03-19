import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# Configurar conexión a Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# Interfaz de Usuario
st.title("📊 Gestor de Gastos Restaurante")

# Formulario para nuevos gastos
with st.form("nuevo_gasto"):
    fecha = st.date_input("Fecha")
    categoria = st.selectbox("Categoría", ["Mercancía", "Servicios", "Equipos", "Nómina"])
    proveedor = st.text_input("Proveedor")
    monto = st.number_input("Monto (USD)", min_value=0.0, format="%.2f")
    descripcion = st.text_area("Descripción")
    
    if st.form_submit_button("Guardar Gasto"):
        data = {
            "fecha": fecha.isoformat(),
            "categoria": categoria,
            "proveedor": proveedor,
            "monto": monto,
            "descripcion": descripcion
        }
        supabase.table("gastos").insert(data).execute()
        st.success("✅ Gasto registrado!")

# Visualización de Datos
st.header("Análisis")
df = pd.DataFrame(supabase.table("gastos").select("*").execute().data)

if not df.empty:
    # Filtros
    categorias = st.multiselect("Filtrar por categoría", df['categoria'].unique())
    if categorias:
        df = df[df['categoria'].isin(categorias)]
    
    # Gráficos
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(df, names='categoria', values='monto', title='Distribución por Categoría')
        st.plotly_chart(fig)
    
    with col2:
        fig2 = px.bar(df.groupby('proveedor')['monto'].sum().reset_index(), 
                     x='proveedor', y='monto', title='Gastos por Proveedor')
        st.plotly_chart(fig2)
    
    # Tabla editable
    st.data_editor(df, key="editor", num_rows="dynamic")
    
    # Actualizar base de datos
    if st.button("Guardar Cambios"):
        updated_data = st.session_state["editor"]["edited_rows"]
        # Lógica para actualizar en Supabase (requiere implementación)
        st.success("Base de datos actualizada")
else:
    st.warning("No hay datos registrados")