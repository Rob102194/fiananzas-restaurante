import streamlit as st
from supabase import create_client, Client
from typing import Dict

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

    def execute_safe_query(self, table: str, filters: dict):
        """Versión mejorada con logging de diagnóstico"""
        try:
            st.write("🔍 Parámetros de búsqueda recibidos:", filters)  # Debug 1
            
            query = self.client.table(table).select("*")
            
            # Aplicar filtros con verificación de valores
            if 'categoria' in filters:
                categoria = filters['categoria'].lower().strip()  # Normalización
                query = query.ilike("categoria", f"%{categoria}%")
                st.write(f"✅ Filtro categoría aplicado: {categoria}")  # Debug 2
                
            if all(k in filters for k in ['fecha_inicio', 'fecha_fin']):
                query = (
                    query
                    .gte("fecha", filters['fecha_inicio'])
                    .lte("fecha", filters['fecha_fin'])
                )
                st.write(f"📅 Rango fechas: {filters['fecha_inicio']} a {filters['fecha_fin']}")  # Debug 3
                
            if 'search' in filters and filters['search']:
                search_term = f"%{filters['search'].lower().strip()}%"
                if table == "gastos":
                    query = query.or_(f"producto.ilike.{search_term},descripcion.ilike.{search_term}")
                else:
                    query = query.ilike("producto", search_term)
                st.write(f"🔎 Término búsqueda: {search_term}")  # Debug 4
            
            st.write("⚡ Consulta final:", query)  # Debug 5
            result = query.execute()
            
            st.write("📦 Datos crudos recibidos:", result.data)  # Debug 6
            return result.data
            
        except Exception as e:
            st.error(f"🧨 Error en consulta: {str(e)}")
            raise

    # Métodos adicionales para acceso individual
    def get_compras(self):
        return self.client.table('compras').select('*').execute().data

    def get_gastos(self):
        return self.client.table('gastos').select('*').execute().data























    