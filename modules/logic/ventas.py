import pandas as pd
import streamlit as st

class VentasLogic:
    def __init__(self, db):
        self.db = db
        
    def procesar_ventas(self, archivo_csv, fecha_venta):
        """Procesa y guarda las ventas desde un CSV"""
        try:
            # Validar archivo
            if not archivo_csv:
                raise ValueError("Debes subir un archivo CSV")
                
            # Leer y validar CSV
            df = pd.read_csv(archivo_csv)
            columnas_requeridas = ["producto", "cantidad", "precio_unitario", "metodo_pago"]
            
            if not all(col in df.columns for col in columnas_requeridas):
                faltantes = [col for col in columnas_requeridas if col not in df.columns]
                raise ValueError(f"Columnas faltantes en CSV: {', '.join(faltantes)}")
            
            # Preparar datos
            df['fecha'] = fecha_venta.isoformat()
            df['total'] = df['cantidad'] * df['precio_unitario']
            
            # Convertir a diccionario
            datos = df[['fecha', 'producto', 'cantidad', 'precio_unitario', 'total', 'metodo_pago']].to_dict('records')
            
            # Insertar en batch
            respuesta = self.db.client.table('ventas').insert(datos).execute()
            
            # Feedback al usuario
            st.success(f"✅ {len(respuesta.data)} ventas registradas exitosamente!")
            st.balloons()
            
            return True
            
        except Exception as e:
            st.error(f"Error al procesar ventas: {str(e)}")
            return False