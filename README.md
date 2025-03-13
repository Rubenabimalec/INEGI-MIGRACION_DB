# INEGI-MIGRACION_DB
El repositorio contiene una explicación de la creación de una solución aplicada para migrar datos en grandes cantidades, explica el proceso seguido para normalizar una base de datos de forma remota.
la carpeta Migracion presenta una muestra de datos que se utilizó para insertar los registros de un archivo originalmente de 138,124 registros con 15 columnas en total.
Tambien carpeta sql la cual contiene el esquema de la base de datos.

Estructura del proyecto
/migracion

|── insert_all.py

│── muestra_test.xlsx               

│── requeriments.txt

│── V1_insert_empresa.py

/sql

│── create_database_Inegi.sql

│── querys_test.sql

Ejecución:
1. Clonar repositorio.
2. Crear enviroment(opcional).
3. Ejecuta: “Migracion/requeriment.txt”.
4. Crea el esquema de la base de datos con el script “sql/create_db_Inegi_schema.sql”.
5. Modifica el archivo “Insert_all.py” o “V1_insert_empresa.py” con las credenciales de tu base de datos sql.
6. Visualiza con el script “sql/query_test.sql” la visualización de tus datos.


Proceso de Migración de Datos

Introducción

Para garantizar un entorno de prueba controlado, se creó una base de datos de prueba con una única tabla. De esta manera, se pudo testear la creación de cada columna de la tabla asegurando que coincidiera con las columnas del archivo de datos en Excel (empresa.xlsx).

LOAD DATA INFILE

Inicialmente se intentó migrar los datos del Excel a la tabla empresa de la tabla creada en mysql por medio de la función de LOAD DATA INFILE que nos proporciona mysql. LOAD DATA INFILE es una herramienta funcional para importar datos en formato csv pero al hacer las primeras pruebas, y tratar de importar de manera masiva se encontraron diferentes errores:
•	Problemas con el formato UTF-8, lo que impedía la correcta carga de ciertos registros.
•	Errores en distintas líneas del archivo sin una identificación clara.
•	Inconsistencias en los tipos de datos, ya que el formato CSV guarda todos los valores como texto plano.
En esta primera etapa de intentar importar datos, intentando con la herramienta workbench de mysql, se cambiaron a diferentes formatos de utf-8 para decodificar los datos al momento de insertar los datos a la tabla intentando corregir errores:

•	charset/collation: utf-8mb64	utf8mb4 
•	charset/collation: utf-8		utf8_unicode_
En ambos casos aun verificando que la compatibilidad fuera correcta siguieron apareciendo errores.
Migración con Pandas y Python
Entre las soluciones evaluadas, se identificó el uso de la librería Pandas de Python, ampliamente utilizada para el análisis y manipulación de datos. Pandas permite leer archivos en diferentes formatos como XLSX, CSV, JSON, entre otros, ofreciendo una mejor gestión de los datos antes de su inserción en la base de datos.

Tecnologías Utilizadas

Para llevar a cabo la migración de datos con Python, se desarrolló un script que hace uso de las siguientes librerías:
•	pandas: Para leer y procesar los datos del archivo Excel.
•	mysql.connector: Librería oficial de MySQL para establecer conexión y ejecutar consultas desde Python.
•	time: Utilizada para pausar la inserción de datos y evitar sobrecargar el servidor.
Beneficios de Usar Pandas
1.	Limpieza y conversión de datos: Antes de la inserción, Pandas permite transformar los datos al formato adecuado para MySQL. Ejemplo:
o	Conversión de fechas al formato YYYY-MM-DD.
o	Transformación de valores numéricos para que sean interpretados correctamente por MySQL.
2.	Manejo de valores nulos: MySQL no reconoce NaN como un valor válido, por lo que se convirtieron estos valores a NULL antes de la inserción.
3.	Inserción por lotes: Se dividió el conjunto de datos en lotes de 10,000 registros para mejorar el rendimiento y reducir la carga sobre el servidor.

Proceso de Migración con Pandas
1.	Carga de datos desde el archivo Excel a un DataFrame de Pandas.
2.	Conversión de tipos de datos para garantizar compatibilidad con MySQL.
3.	Manejo de valores nulos reemplazando NaN por NULL.
4.	Inserción por lotes de 10,000 registros a la base de datos.
5.	Control de flujo con pausas de 15 segundos entre lotes para evitar sobrecargar el servidor.

   Retos Encontrados Durante el Desarrollo del Código 

Mejorando el Uso de Pandas con Python

Después de llenar correctamente la primera tabla como prueba, se identificaron varias oportunidades de mejora. Una opción era modificar los tipos de datos de cada columna para permitir la carga de diferentes archivos de Excel, donde cada hoja representa una tabla. Aunque esta era una posibilidad, el objetivo principal era mejorar la versión inicial del código basado en Pandas para ejecutar un proceso de inserción en cascada. Es decir, a partir de una tabla ya cargada, el código debía insertar automáticamente todas las demás tablas respetando las dependencias entre ellas.
En la primera versión del código de Pandas, se identificó una limitación importante: el orden de las columnas en el archivo de Excel debía coincidir exactamente con el esquema de la base de datos. Si el archivo Excel tenía un orden diferente, se producían errores al insertar los datos.
Otro aspecto clave en la construcción del código fue la gestión de las relaciones entre tablas, donde se establecieron llaves primarias y foráneas. Por ejemplo, la tabla "actividades" debía llenarse antes que la tabla "empresa", ya que esta última contiene una clave foránea que hace referencia a codigo_actividad.
________________________________________

Reglas Generales para la Inserción de Datos

Para evitar problemas durante la migración, se estableció una regla general:
•	Primero deben insertarse las tablas que no dependen de otras y que son referenciadas por otras tablas.
•	Las tablas que contienen claves foráneas deben insertarse después.
Orden Correcto de Inserción
1.	Actividades → Se inserta primero porque empresa.codigo_actividad depende de esta tabla.
2.	Municipio → Debe insertarse antes que ubicacion, ya que ubicacion.cve_municipio hace referencia a esta tabla.
3.	Empresa → Se inserta antes que contactos y ubicacion, ya que ambas dependen de empresa.codigo_empresa.
4.	Contactos → Depende de empresa.
5.	Ubicación → Depende de empresa y municipio.
En este punto, se creó toda la estructura de la base de datos, incluyendo las tablas y sus relaciones. Se gestionó el archivo de Excel de tal manera que cada hoja correspondiera a una tabla específica, respetando el orden en el que las tablas fueron creadas en la base de datos. Esto aseguró que el flujo de inserción de arriba hacia abajo y de izquierda a derecha coincidiera con la estructura esperada por el código.
Una vez verificado este punto, comenzó la implementación del código.
________________________________________
Problemas Durante la Inserción de Datos

Error en la Tabla "Contactos"
El proceso de migración avanzó correctamente hasta que se llegó a la inserción de la tabla "contactos", donde surgió el primer gran desafío.
El problema estaba en los tipos de datos de las columnas "correo" y "teléfono", que debían almacenarse en formato JSON. Esto llevó a una decisión importante sobre cómo manejar la conversión de datos:
•	Opción 1: Convertir los valores a formato JSON directamente en el archivo Excel.
•	Opción 2: Aplicar una función en Python para transformar los datos antes de insertarlos.
Dado que trabajar con JSON en Excel de forma manual o mediante macros era demasiado complicado (especialmente porque había celdas vacías), se optó por la segunda opción.
________________________________________

Solución Implementada

1.	Convertir cada celda de las columnas "web" y "teléfono" a un formato JSON válido.
2.	Manejar los errores relacionados con valores NaN en Pandas. 
o	Las celdas vacías en Excel se interpretan como NaN en Pandas.
o	Antes de insertar los datos en MySQL, era necesario convertir estos valores en NULL.
3.	Asegurar que cada columna tenga la estructura JSON correcta: 
o	La columna "web" debía cumplir con el siguiente formato: 
{"web": "example.com", "tipo": "empresa"}
o	La columna "teléfono" debía estructurarse como:
{"telefonos": ["6461964121541", "6469897512"]}
Solución:
Para abordar los errores de formato en estas columnas, se implementaron dos funciones específicas:
1.	Función procesar_web(valor):
o	Propósito: Esta función recibe un valor de tipo str (la URL de la página web) y devuelve un objeto JSON con la estructura adecuada, o None si el valor está vacío.
o	Funcionamiento: Si el valor no es vacío, la función construye un JSON con los detalles del sitio web, incluyendo la URL y el tipo. Si el valor está vacío, la función retorna None.
2.	Función procesar_telefono(valor):
o	Propósito: Esta función recibe un valor de tipo str (un número de teléfono) y devuelve un JSON con la estructura correcta, o None si el valor está vacío.
o	Funcionamiento: Si el valor no está vacío, la función crea un JSON con una lista de números de teléfono. Si el valor está vacío, la función retorna None
