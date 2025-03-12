import pandas as pd
import mysql.connector
import time

# Conexión a MySQL
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="4220",
    database="inegi_ruben_DB"
)
cursor = conexion.cursor()

# Cargar datos desde el archivo Excel
file_path = "muestra_test.xlsx"
df = pd.read_excel(file_path)

# Convertir tipos de datos para que coincidan con la base de datos
df["codigo_empresa"]= pd.to_numeric(df["codigo_empresa"],errors="coerce").astype("Int64")
df["codigo_actividad"]=pd.to_numeric(df["codigo_actividad"],errors="coerce").astype("Int64")
df["razon_social"]=df["razon_social"].astype(str).replace("nan",None) #convertir NaN a None
df["fecha_alta"]=pd.to_datetime(df["fecha_alta"],errors="coerce").dt.date #asegura el formato DATE YY-MM-DD

#remplazar NaN con None (equivalente a NULL en MYSQL)
df=df.where(pd.notna(df), None)

# Dividir en lotes de 10,000 registros
tamanio_lote = 10000
total_registros = len(df)

for i in range(0, total_registros, tamanio_lote):
    lote = df.iloc[i:i + tamanio_lote]  # Extraer 10,000 registros

    # Convertir lote a una lista de tuplas para MySQL
    valores = [tuple(row) for row in lote.to_numpy()]

    # Insertar en la base de datos
    consulta = """
    INSERT INTO empresa (codigo_empresa, nombre, razon_social, codigo_actividad, fecha_alta)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.executemany(consulta, valores)
    conexion.commit()  # Guardar los cambios

    print(f"Se insertaron {len(lote)} registros. Pausa de 15 segundos...")
    time.sleep(15)  # Pausar 10 segundos

# Cerrar conexión
cursor.close()
conexion.close()
print("Importación completada.")
