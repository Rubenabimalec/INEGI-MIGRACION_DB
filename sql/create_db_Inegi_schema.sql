-- Crear la base de datos
CREATE DATABASE ruben_inegi_2;
USE ruben_inegi_2;

-- Crear la tabla actividades primero porque es referenciada por empresa
CREATE TABLE actividades (
    codigo_actividad INT NOT NULL PRIMARY KEY,
    descripcion VARCHAR(255) NOT NULL
);

-- Crear la tabla empresa
CREATE TABLE empresa (
    codigo_empresa INT NOT NULL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    razon_social VARCHAR(255),
    codigo_actividad INT NOT NULL,
    fecha_alta DATE NOT NULL,
    FOREIGN KEY (codigo_actividad) REFERENCES actividades(codigo_actividad)
);

-- Crear la tabla contactos que hace referencia a empresa
CREATE TABLE contactos (
    codigo_empresa INT NOT NULL PRIMARY KEY,
    correo VARCHAR(60),
    web JSON,
    telefono JSON,
    FOREIGN KEY (codigo_empresa) REFERENCES empresa(codigo_empresa)
);

-- Crear la tabla municipio antes de ubicacion para evitar errores de clave foranea
CREATE TABLE municipio (
    cve_municipio INT NOT NULL PRIMARY KEY,
    municipio VARCHAR(45) NOT NULL
);

-- Crear la tabla ubicación con `codigo_empresa` como clave primaria
CREATE TABLE ubicacion (
    codigo_empresa INT NOT NULL PRIMARY KEY, 
    tipo_vial VARCHAR(255),
    nombre_asentamiento VARCHAR(255),
    codigo_postal INT,
    cve_municipio INT NOT NULL,
    latitud DECIMAL(10,8) NOT NULL,
    longitud DECIMAL(11,8) NOT NULL,
    FOREIGN KEY (codigo_empresa) REFERENCES empresa(codigo_empresa),
    FOREIGN KEY (cve_municipio) REFERENCES municipio(cve_municipio)
);





