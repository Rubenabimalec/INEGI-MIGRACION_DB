use ruben_inegi_2;

SELECT * FROM ruben_inegi_2.contactos;


/*
--probar todas las tablas esten completas
SELECT * FROM ruben_inegi_2.empresa;

-codigo que consulta los 10 registros con el codigo de empresa mas alto con sus demas campos a modo de prueba y verificar la correcta insercion
SELECT codigo_empresa, nombre, razon_social, codigo_actividad, fecha_alta
FROM empresa
ORDER BY codigo_empresa DESC
LIMIT 10;

-ver algunos datos:
SELECT * FROM empresa LIMIT 10;

muestra las tablas creadas
show tables;

-verifica si existen registros de la columna fecha_alta que sean null
SELECT * FROM empresa WHERE fecha_alta IS NULL;

-ver estructura de tabla:
DESCRIBE empresa;

-conteo de todos los registros insertados:
SELECT COUNT(*) FROM empresa;
*/
