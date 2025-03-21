import pandas as pd
from datetime import datetime

class ConsultasLogic:
    def __init__(self, db):
        self.db = db
        
    def obtener_datos_consulta(self, tabla, filtros):
        """Obtiene datos filtrados para consultas"""
        try:
            query = self.db.client.table(tabla).select("*")
            
            # Aplicar filtros
            if 'fecha_inicio' in filtros and 'fecha_fin' in filtros:
                query = query.gte('fecha', filtros['fecha_inicio'])
                query = query.lte('fecha', filtros['fecha_fin'])
            
            if 'categoria' in filtros:
                query = query.ilike('categoria', f"%{filtros['categoria']}%")
            
            if 'busqueda' in filtros and filtros['busqueda']:
                if tabla == 'gastos':
                    query = query.or_(f"producto.ilike.%{filtros['busqueda']}%,descripcion.ilike.%{filtros['busqueda']}%")
                else:
                    query = query.ilike('producto', f"%{filtros['busqueda']}%")
            
            result = query.execute()
            return pd.DataFrame(result.data)
            
        except Exception as e:
            raise ValueError(f"Error en consulta: {str(e)}")
    
    def generar_metricas(self, df):
        """Calcula métricas básicas para los datos"""
        if df.empty:
            return {}
            
        return {
            'total': df['monto'].sum(),
            'promedio_diario': df.groupby('fecha')['monto'].sum().mean(),
            'categoria_mas_comun': df['categoria'].mode()[0] if not df['categoria'].mode().empty else 'N/A'
        }