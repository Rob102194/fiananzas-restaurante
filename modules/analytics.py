import pandas as pd
import plotly.express as px
from typing import Dict

class AnalyticsEngine:
    @staticmethod
    def generate_metrics(df: pd.DataFrame) -> Dict:
        metrics = {
            "gasto_total": df['monto'].sum(),
            "gasto_promedio": df['monto'].mean(),
            "categoria_mayor": df.groupby('categoria')['monto'].sum().idxmax()
        }
        return metrics
    
    @staticmethod
    def create_visualizations(df: pd.DataFrame):
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['costo_unitario'] = df['monto'] / df['cantidad']
        
        fig1 = px.line(
            df.resample('W', on='fecha')['monto'].sum().reset_index(),
            x='fecha', y='monto',
            title="Gastos Semanales"
        )
        
        fig2 = px.treemap(
            df,
            path=['categoria', 'proveedor'],
            values='monto',
            title="Distribución por Categoría/Proveedor"
        )
        
        return fig1, fig2