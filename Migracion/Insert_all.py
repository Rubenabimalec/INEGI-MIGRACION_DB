import pandas as pd
import mysql.connector
import time
import json

# Configuración de conexión a MySQL
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your Password",
    database="ruben_inegi_2"
)
cursor = conexion.cursor()

# Ruta del archivo Excel con múltiples hojas
file_path = "muestra_test.xlsx"

#Definir la estructura esperada para cada tabla con orden correcto
orden_tablas = ["actividades", "municipio", "empresa", "contactos", "ubicacion"]

tablas_config = {
    "actividades": {
        "columnas": ["codigo_actividad", "descripcion"],
        "tipos": {"codigo_actividad": "Int64"}
    },
    "municipio": {
        "columnas": ["cve_municipio", "municipio"],
        "tipos": {"cve_municipio": "Int64"}
    },
    "empresa": {
        "columnas": ["codigo_empresa", "nombre", "razon_social", "codigo_actividad", "fecha_alta"],
        "tipos": {
            "codigo_empresa": "Int64",
            "codigo_actividad": "Int64",
            "fecha_alta": "datetime64"
        }
    },
    "contactos": {
        "columnas": ["codigo_empresa", "correo", "web", "telefono"],
        "tipos": {"codigo_empresa": "Int64"}
    },
    "ubicacion": {
        "columnas": ["codigo_empresa", "tipo_vial", "nombre_asentamiento", "codigo_postal", "cve_municipio", "latitud", "longitud"],
        "tipos": {
            "codigo_empresa": "Int64",
            "codigo_postal": "Int64",
            "cve_municipio": "Int64",
            "latitud": "float64",
            "longitud": "float64"
        }
    }
}

# Cargar el archivo Excel con todas las hojas
datos_excel = pd.read_excel(file_path, sheet_name=None)  # Lee todas las hojas disponibles

# Procesar cada tabla en el orden correcto
for tabla in orden_tablas:
    if tabla in datos_excel:
        print(f" Procesando tabla: {tabla}...")

        config = tablas_config[tabla]
        df = datos_excel[tabla]

        # Seleccionar solo las columnas necesarias
        df = df[config["columnas"]]

        # Convertir tipos de datos dinámicamente
        for col, tipo in config["tipos"].items():
            if col in df.columns:
                if tipo == "Int64":
                    df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
                elif tipo == "datetime64":
                    df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
                elif tipo == "float64":
                    df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")
                else:
                    df[col] = df[col].astype(str).replace("nan", None)

        #Procesar columna "web" como JSON
        if "web" in df.columns:
            def procesar_web(valor):
                if pd.notna(valor) and valor.strip():
                    return json.dumps({"web": valor.strip(), "tipo": "empresa"})
                return None
            df["web"] = df["web"].apply(procesar_web)

        # Procesar columna "telefono" como JSON
        if "telefono" in df.columns:
            def procesar_telefono(valor):
                if pd.notna(valor):  # Verifica que no sea NaN
                    valor = str(valor).strip()  # Convierte a string y elimina espacios
                    if valor:  # Si no está vacío
                        telefonos = [num.strip() for num in valor.split(",") if num.strip()]  # Manejo de múltiples teléfonos
                        return json.dumps({"telefonos": telefonos}) if telefonos else None
            df["telefono"] = df["telefono"].apply(procesar_telefono)

        # Asegurar que los valores NaN y pd.NA sean convertidos a None
        df = df.astype(object).where(pd.notna(df), None)

        # Dividir en lotes de 10,000 registros
        tamanio_lote = 10000
        total_registros = len(df)

        for i in range(0, total_registros, tamanio_lote):
            lote = df.iloc[i:i + tamanio_lote]  # Extraer lote
            valores = [tuple(row) for row in lote.to_numpy()]  # Convertir a lista de tuplas

            # Generar consulta SQL dinámica
            columnas_sql = ", ".join(config["columnas"])
            placeholders = ", ".join(["%s"] * len(config["columnas"]))
            consulta = f"INSERT INTO {tabla} ({columnas_sql}) VALUES ({placeholders})"

            # Ejecutar inserción en MySQL
            cursor.executemany(consulta, valores)
            conexion.commit()

            print(f"Insertados {len(lote)} registros en {tabla}. Pausa de 5 segundos...")
            time.sleep(5)

print(" Migración completada exitosamente.")

# Cerrar conexión
cursor.close()
conexion.close()
