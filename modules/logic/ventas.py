import pandas as pd
import streamlit as st
from datetime import datetime

class VentasLogic:
    def __init__(self, db):
        self.db = db
        
    def registrar_ventas(self, archivo, entidad, fecha):
        """Registra ventas para una entidad específica con validaciones"""
        try:
            # Validar entidad permitida
            if entidad not in ["restaurante", "domicilio"]:
                raise ValueError("Entidad no válida")
                
            # Verificar registro existente
            if self._existe_registro(fecha, entidad):
                raise ValueError(f"¡Ya existe registro para {entidad} en esta fecha!")
            
            # Leer y validar Excel
            df = pd.read_excel(archivo, engine='openpyxl')
            
            # Validar estructura del archivo
            columnas_requeridas = ["Grupo", "Nombre", "Cantidad", "$ Venta"]
            if not all(col in df.columns for col in columnas_requeridas):
                faltantes = [col for col in columnas_requeridas if col not in df.columns]
                raise ValueError(f"Faltan columnas: {', '.join(faltantes)}")
            
            # Transformar datos
            datos = self._transformar_datos(df, entidad, fecha)
            
            # Insertar en base de datos
            respuesta = self.db.client.table('ventas').insert(datos).execute()
            
            if not respuesta.data:
                raise ValueError("No se insertaron registros")
            
            return respuesta.data
            
        except Exception as e:
            raise ValueError(f"Error en {entidad}: {str(e)}") from e
    
    def _transformar_datos(self, df, entidad, fecha):
        """Transformación y validación de datos"""
        try:
            df = df.rename(columns={
                "Grupo": "grupo",
                "Nombre": "nombre",
                "Cantidad": "cantidad",
                "$ Venta": "venta"
            })
            
            # Validar tipos de datos
            df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0).astype(int)
            df['venta'] = pd.to_numeric(df['venta'], errors='coerce').fillna(0).round(2)
            
            # Validar valores positivos
            if (df['cantidad'] < 0).any():
                raise ValueError("Cantidades no pueden ser negativas")
            if (df['venta'] < 0).any():
                raise ValueError("Valores de venta no pueden ser negativos")
            
            # Añadir metadatos
            df['fecha'] = pd.to_datetime(fecha).strftime('%Y-%m-%d')
            df['entidad'] = entidad
            df['cliente'] = 'clientes'
            
            return df[['fecha', 'entidad', 'cliente', 'grupo', 'nombre', 'cantidad', 'venta']].to_dict('records')
            
        except Exception as e:
            raise ValueError(f"Datos inválidos: {str(e)}") from e
    
    def _existe_registro(self, fecha, entidad):
        """Verifica registros existentes para la entidad y fecha"""
        response = self.db.client.table('ventas').select("id").match({
            'fecha': fecha,
            'entidad': entidad
        }).execute()
        
        return len(response.data) > 0