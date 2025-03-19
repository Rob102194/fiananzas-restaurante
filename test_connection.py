import os
from supabase import create_client

def test_connection():
    url = os.getenv("https://nfqhpyouiypmineqvigw.supabase.co")
    key = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5mcWhweW91aXlwbWluZXF2aWd3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MjM1Mjc0OCwiZXhwIjoyMDU3OTI4NzQ4fQ.h3QeGj0QLAFtCz0CECuPM8YclfVi_SHVjeBertbYL_w")
                      
    try:
        client = create_client(url, key)
        print("✔️ Conexión a Supabase exitosa")
        
        # Verificar existencia de tabla
        response = client.table('gastos').select("*").limit(1).execute()
        print(f"✅ Tabla 'gastos' accesible. Datos: {response.data}")
        
    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")

test_connection()