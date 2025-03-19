import streamlit as st
import datetime
from supabase import create_client, Client
from typing import Dict, List, Optional

class DatabaseManager:
    def __init__(self):
        # 1. Obtener credenciales de Streamlit secrets
        self.url = st.secrets["SUPABASE_URL"].strip()  # Elimina espacios
        self.key = st.secrets["SUPABASE_KEY"].strip()
        
        # 2. Inicializar cliente Supabase
        self.client: Client = create_client(self.url, self.key)
        
        # 3. Crear tablas si no existen
        self._initialize_tables()

    def _initialize_tables(self):
        """Crea la estructura de la base de datos"""
        try:
            init_script = """
            CREATE TABLE IF NOT EXISTS gastos (
                id SERIAL PRIMARY KEY,
                fecha DATE NOT NULL,
                categoria VARCHAR(50) NOT NULL,
                proveedor VARCHAR(100),
                cantidad NUMERIC(10,3) NOT NULL DEFAULT 1,
                unidad_medida VARCHAR(20) NOT NULL DEFAULT 'unidad',
                monto NUMERIC(10,2) NOT NULL,
                descripcion TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """
            self.client.rpc('execute_sql', params={'query': init_script}).execute()
        except Exception as e:
            st.error(f"Error crítico en BD: {str(e)}")
            raise

        
    def insert_gasto(self, data: Dict) -> Dict:
        return self.client.table('gastos').insert(data).execute().data[0]
    
    def get_all_gastos(self) -> List[Dict]:
        raw_data = self.client.table('gastos').select("*").execute().data
        # Convertir datetime a string ISO
        for item in raw_data:
            if isinstance(item['fecha'], str):
                item['fecha'] = datetime.fromisoformat(item['fecha']).date()
        return raw_data

    def update_gasto(self, record_id: int, updates: Dict) -> Dict:
        # Convertir date a string ISO
        if 'fecha' in updates:
            updates['fecha'] = updates['fecha'].isoformat()
        return self.client.table('gastos').update(updates).eq('id', record_id).execute().data[0]
    
    def delete_gasto(self, record_id: int) -> None:
        self.client.table('gastos').delete().eq('id', record_id).execute()