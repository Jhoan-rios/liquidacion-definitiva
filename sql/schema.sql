-- =====================================================================
-- Liquidación definitiva - Esquema de la base de datos (PostgreSQL)
--
-- Este script es EQUIVALENTE a lo que crea el ORM (src/model/entidades.py)
-- cuando se llama a LiquidacionController.crear_tablas().
-- Sirve para crear las tablas a mano (por ejemplo con psql en Render) o
-- para documentar la estructura.
--
--   psql "<EXTERNAL DATABASE URL de Render>" -f sql/schema.sql
-- =====================================================================


-- ---------------------------------------------------------------------
-- 1. BORRAR TABLAS  (primero la que depende de la otra)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS liquidaciones;
DROP TABLE IF EXISTS empleados;


-- ---------------------------------------------------------------------
-- 2. CREAR TABLAS
-- ---------------------------------------------------------------------
CREATE TABLE empleados (
    id          SERIAL        PRIMARY KEY,
    documento   VARCHAR(20)   NOT NULL UNIQUE,
    nombre      VARCHAR(100)  NOT NULL
);

CREATE TABLE liquidaciones (
    id                      SERIAL         PRIMARY KEY,
    empleado_id             INTEGER        NOT NULL
                            REFERENCES empleados (id) ON DELETE CASCADE,

    -- Datos de entrada
    tipo_retiro             VARCHAR(40)    NOT NULL,
    salario                 NUMERIC(14,2)  NOT NULL,
    fecha_ingreso           DATE           NOT NULL,
    fecha_retiro            DATE           NOT NULL,
    vacaciones_disfrutadas  INTEGER        NOT NULL,

    -- Conceptos calculados
    salario_restante        NUMERIC(14,2)  NOT NULL,
    prima                   NUMERIC(14,2)  NOT NULL,
    cesantias               NUMERIC(14,2)  NOT NULL,
    intereses               NUMERIC(14,2)  NOT NULL,
    vacaciones              NUMERIC(14,2)  NOT NULL,
    indemnizacion           NUMERIC(14,2)  NOT NULL,
    total                   NUMERIC(14,2)  NOT NULL,

    creada_en               TIMESTAMPTZ    NOT NULL DEFAULT now(),

    CONSTRAINT ck_liquidaciones_salario_positivo
        CHECK (salario > 0),
    CONSTRAINT ck_liquidaciones_vacaciones_no_negativas
        CHECK (vacaciones_disfrutadas >= 0),
    CONSTRAINT ck_liquidaciones_fechas_validas
        CHECK (fecha_retiro >= fecha_ingreso)
);

CREATE INDEX ix_liquidaciones_empleado_id
    ON liquidaciones (empleado_id);


-- ---------------------------------------------------------------------
-- 3. INSERT INTO  (ejemplo de lo que ejecuta registrar_liquidacion)
--    Descomenta para probar a mano.
-- ---------------------------------------------------------------------
-- INSERT INTO empleados (documento, nombre)
-- VALUES ('1020304050', 'Jhoan Ríos');
--
-- INSERT INTO liquidaciones (
--     empleado_id, tipo_retiro, salario, fecha_ingreso, fecha_retiro,
--     vacaciones_disfrutadas, salario_restante, prima, cesantias,
--     intereses, vacaciones, indemnizacion, total
-- )
-- VALUES (
--     (SELECT id FROM empleados WHERE documento = '1020304050'),
--     'Despido sin justa causa', 3000000, '2025-01-01', '2025-12-31',
--     0, 3100000.00, 3033333.33, 3033333.33, 368044.44,
--     1516666.67, 3022222.22, 14073600.00
-- );


-- ---------------------------------------------------------------------
-- 4. SELECT  (ejemplos de lo que ejecutan buscar_por_documento / _por_id)
-- ---------------------------------------------------------------------
-- Liquidaciones de un empleado, por documento
-- SELECT l.*
-- FROM liquidaciones AS l
-- JOIN empleados     AS e ON e.id = l.empleado_id
-- WHERE e.documento = '1020304050'
-- ORDER BY l.id;
--
-- Una liquidación por id, con los datos del empleado
-- SELECT e.documento, e.nombre, l.*
-- FROM liquidaciones AS l
-- JOIN empleados     AS e ON e.id = l.empleado_id
-- WHERE l.id = 1;
