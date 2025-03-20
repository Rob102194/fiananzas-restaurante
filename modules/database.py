import streamlit as st
from datetime import datetime as dt
from supabase import create_client, Client
from typing import Dict, List, Optional

class DatabaseManager:
    def __init__(self):
        # Obtener credenciales de Streamlit secrets
        self.url = st.secrets["SUPABASE_URL"].strip() 
        self.key = st.secrets["SUPABASE_KEY"].strip()
        
        # Inicializar cliente Supabase
        self.client: Client = create_client(self.url, self.key)
        
        # Crear tablas si no existen
        self._initialize_tables()

    def _initialize_tables(self):
        """Crear todas las tablas necesarias"""
        
        tables =  {
            "compras": """
                CREATE TABLE IF NOT EXISTS compras (
                    id SERIAL PRIMARY KEY,
                    fecha DATE NOT NULL,
                    categoria VARCHAR(50) NOT NULL DEFAULT 'Mercancía',
                    producto VARCHAR(100),
                    cantidad NUMERIC(10,3) NOT NULL DEFAULT 1,
                    unidad_medida VARCHAR(20) NOT NULL DEFAULT 'unidad',
                    monto NUMERIC(10,2) NOT NULL,
                    proveedor VARCHAR(100),
                    descripcion TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """,

            "gastos": """
                CREATE TABLE IF NOT EXISTS gastos (
                    id SERIAL PRIMARY KEY,
                    fecha DATE NOT NULL,
                    producto VARCHAR(100),
                    categoria VARCHAR(50) NOT NULL,
                    monto NUMERIC(10,2) NOT NULL,
                    descripcion TEXT,
                    proveedor VARCHAR(100),
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """,

            "ventas": """
            CREATE TABLE IF NOT EXISTS ventas (
                id SERIAL PRIMARY KEY,
                fecha DATE NOT NULL,
                producto VARCHAR(100) NOT NULL,
                cantidad INT NOT NULL,
                precio_unitario NUMERIC(10,2) NOT NULL,
                total NUMERIC(10,2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED,
                metodo_pago VARCHAR(50),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """
        }

        for table, script in tables.items():
                try:
                    self.client.rpc('execute_sql', params={'query': script}).execute()
                except Exception as e:
                    print(f"Error creando tabla {table}: {str(e)}")
    
    """ INSTERTAR DATOS"""

    def insert_registro(self, data: Dict):
        """Inserta en la tabla correspondiente según categoría"""
        if data["categoria"] == "Mercancía":
            required = ["fecha", "producto", "cantidad", "unidad_medida", "monto"]
            table = "compras"
        else:
            required = ["fecha", "categoria", "producto", "monto"]
            table = "gastos"
        
        if not all(key in data for key in required):
            raise ValueError(f"Campos requeridos faltantes: {required}")
        
        return self.client.table(table).insert(data).execute().data[0]
    
    def insert_venta(self, data: Dict) -> Dict:
        return self.client.table('ventas').insert(data).execute().data[0]
    
    """OBTENER DATOS"""
    
    def get_categorias(self):
        """Obtiene categorías únicas de ambas tablas"""
        # Obtener categorías de compras
        compras = self.client.table('compras').select('categoria').execute().data
        categorias_compras = {item['categoria'] for item in compras}
        
        # Obtener categorías de gastos
        gastos = self.client.table('gastos').select('categoria').execute().data
        categorias_gastos = {item['categoria'] for item in gastos}
        
        # Combinar y ordenar
        return sorted(categorias_compras.union(categorias_gastos))

    def execute_query(self, query: str):
        """Ejecuta consultas SQL personalizadas"""
        try:
            result = self.client.rpc('execute_sql', params={'query': query}).execute()
            return result.data
        except Exception as e:
            raise ValueError(f"Error en consulta: {str(e)}")























    """
    def get_all_gastos(self) -> List[Dict]:
        raw_data = self.client.table('gastos').select("*").execute().data
        for item in raw_data:
            if isinstance(item['fecha'], str):
                # Usar fromisoformat desde el módulo datetime
                item['fecha'] = dt.fromisoformat(item['fecha']).date()
        return raw_data

    def update_gasto(self, record_id: int, updates: Dict) -> Dict:
        # Convertir date a string ISO
        if 'fecha' in updates:
            updates['fecha'] = updates['fecha'].isoformat()
        return self.client.table('gastos').update(updates).eq('id', record_id).execute().data[0]
    
    def delete_gasto(self, record_id: int) -> None:
        self.client.table('gastos').delete().eq('id', record_id).execute()

    def edit_delete_table(self, data: List[Dict]) -> tuple:
        # Nueva configuración de columnas
        column_config = {
            "tipo": st.column_config.SelectboxColumn(
                "Tipo",
                options=["compra", "gasto"],
                required=True
            ),
            "fecha": st.column_config.DateColumn(format="YYYY-MM-DD"),
            "monto": st.column_config.NumberColumn(format="$%.2f"),
            "cantidad": st.column_config.NumberColumn(format="%.3f")
        }
        
        edited_data = st.data_editor(
            data,
            column_config=column_config,
            disabled=["id", "created_at"],
            key="editor",
            num_rows="dynamic"
        )
        """