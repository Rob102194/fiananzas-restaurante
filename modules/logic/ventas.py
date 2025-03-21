import pandas as pd
import streamlit as st

class VentasLogic:
    def __init__(self, db):
        self.db = db
        
    def process_ventas(self, uploaded_file, fecha_venta):
        try:
            df = pd.read_csv(uploaded_file)
            required_cols = ["producto", "cantidad", "precio_unitario", "metodo_pago"]
            
            if not all(col in df.columns for col in required_cols):
                raise ValueError("Estructura CSV inválida")
                
            df['fecha'] = fecha_venta.isoformat()
            data = df.to_dict('records')
            
            response = self.db.client.table('ventas').insert(data).execute()
            st.success(f"✅ {len(response.data)} ventas registradas!")
            st.balloons()
            
        except Exception as e:
            st.error(f"Error: {str(e)}")