import streamlit as st

class ComprasGastosLogic:
    def __init__(self, db):
        self.db = db
        
    def process_registro(self, categoria, fecha, producto, monto, 
                       proveedor, cantidad, unidad, descripcion):
        try:
            # Lógica de validación y procesamiento
            error_messages = []
            
            if not producto.strip():
                error_messages.append("- Producto es obligatorio")
                
            if monto <= 0:
                error_messages.append("- Monto debe ser mayor a 0")
                
            if categoria == "Mercancía":
                if cantidad <= 0:
                    error_messages.append("- Cantidad debe ser > 0 para Mercancía")
                if unidad == "N/A":
                    error_messages.append("- Seleccione una unidad válida para Mercancía")

            if error_messages:
                raise ValueError("\n".join(error_messages))
            
            # Construcción de datos y inserción
            base_data = {
                "fecha": fecha.isoformat(),
                "categoria": categoria,
                "proveedor": proveedor.strip() if proveedor else None,
                "monto": monto,
                "producto": producto.strip(),
                "descripcion": descripcion.strip() if descripcion else None
            }
            
            if categoria == "Mercancía":
                base_data.update({
                    "cantidad": cantidad,
                    "unidad_medida": unidad if unidad != "N/A" else None
                })
                
            table = "compras" if categoria == "Mercancía" else "gastos"
            
            if table == "gastos":
                base_data.pop('cantidad', None)
                base_data.pop('unidad_medida', None)

            self.db.client.table(table).insert(base_data).execute()
            st.success("✅ Registro guardado correctamente!")
            st.rerun()
            
        except Exception as e:
            st.error(f"**Errores detectados:**\n{str(e)}")