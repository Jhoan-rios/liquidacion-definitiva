# Proyecto de Liquidación Definitiva en Excel

## 📖 Descripción

Este proyecto consiste en el desarrollo de una hoja de cálculo en Microsoft Excel que permite calcular la **liquidación definitiva de un empleado** de acuerdo con el motivo de finalización del contrato. El archivo automatiza el cálculo de las prestaciones sociales, indemnizaciones (cuando corresponda) y demás valores relacionados con la terminación del vínculo laboral.

El objetivo es reducir errores en los cálculos manuales y facilitar la obtención de una liquidación precisa a partir de la información suministrada del empleado.

---

# Entradas

El usuario debe ingresar la siguiente información:

## Datos del empleado

- Nombre del empleado.
- Salario mensual.
- Fecha de ingreso.
- Fecha de retiro.
- Días de vacaciones utilizados
- Tipo de terminación del contrato.

## Tipo de terminación

### Casos normales

- Renuncia del empleado.
- Terminación con justa causa.
- Terminación sin justa causa.

### Casos extraordinarios

- Empleado con salario alto.
- Empleado con salario bajo.
- Vacaciones agotadas
- sin intereses de cesantías

### Casos de error o datos inválidos.


- 
---

# Proceso

Una vez ingresada la información, el sistema realiza automáticamente las siguientes operaciones:

1. Valida que los datos ingresados sean correctos.
2. Identifica el tipo de terminación del contrato.
3. Calcula los días trabajados.
4. Calcula las prestaciones sociales:
   - Cesantías.
   - Intereses sobre cesantías.
   - Prima de servicios.
   - Vacaciones.
5. Calcula la indemnización cuando corresponda.
6. Suma todos los conceptos para obtener el valor total de la liquidación.
7. Muestra mensajes de error cuando existan datos inválidos.

---

# Salidas

El sistema genera como resultado:

- Días trabajados.
- Valor de intereses sobre cesantías.
- Valor de prima de servicios.
- Valor de vacaciones.
- Valor de indemnización (cuando aplique).
- Valor total de la liquidación.
- Mensajes de validación o error.

---

# 🧪 Casos de Prueba

## Casos Normales

### 1. Renuncia

**Entrada**

- Tipo de terminación: Renuncia.
- Datos completos del empleado.

**Resultado esperado**

- Se calculan las prestaciones sociales.
- No se calcula indemnización.

---

### 2. Terminación con Justa Causa

**Entrada**

- Tipo de terminación: Con justa causa.

**Resultado esperado**

- Se calculan las prestaciones sociales.
- No se calcula indemnización.

---

### 3. Terminación sin Justa Causa

**Entrada**

- Tipo de terminación: Sin justa causa.

**Resultado esperado**

- Se calculan las prestaciones sociales.
- Se calcula la indemnización correspondiente.

---

# Casos Extraordinarios

## 1. Empleado con Salario Alto

**Objetivo**

Verificar el correcto cálculo para empleados con salarios elevados.

**Resultado esperado**

- Todos los valores se calculan correctamente.
- No existen errores por valores altos.

---

## 2. Empleado con Salario Bajo

**Objetivo**

Verificar el cálculo para empleados con salarios bajos.

**Resultado esperado**

- Se calculan correctamente las prestaciones sociales.
- Se aplica el auxilio de transporte cuando corresponda.

---

# Casos de Error

## 1. Salario Negativo

**Entrada**

- Salario menor que cero.

**Resultado esperado**

- Mostrar un mensaje indicando que el salario no puede ser negativo.

---

## 2. Fecha de Retiro Anterior a la Fecha de Ingreso

**Resultado esperado**

- Mostrar un mensaje indicando que las fechas son inválidas.

---

## 3. Campos Vacíos

**Resultado esperado**

- Solicitar al usuario completar todos los datos antes de realizar el cálculo.

---

## 4. Tipo de Terminación Inválido

**Resultado esperado**

- Mostrar un mensaje indicando que el tipo de terminación no existe.

---

## 5. Datos No Numéricos

**Resultado esperado**

- Mostrar un mensaje indicando que el dato ingresado es inválido.

---

# Tecnologías Utilizadas

- Microsoft Excel
- Fórmulas de Excel
- Python

---

# Objetivo del Proyecto

Desarrollar una herramienta en Microsoft Excel que permita calcular de forma rápida, precisa y confiable la liquidación definitiva de un empleado, considerando distintos escenarios de terminación del contrato y validando posibles errores en la información ingresada.

## 👥 Integrantes

| Nombre | GitHub |
|--------|--------|
| Jhoan Ríos | [@jhoan-rios](https://github.com/jhoan-rios) |
| Andrés Rosas | [@andres-rosas](https://github.com/andres-rosas) |
