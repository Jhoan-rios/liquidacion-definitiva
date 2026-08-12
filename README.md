# Proyecto de Liquidación Definitiva

## 📖 Descripción

Este proyecto consiste en el desarrollo de una calculadora que permite calcular la **liquidación definitiva de un empleado** de acuerdo con el motivo de finalización del contrato. El programa automatiza el cálculo de las prestaciones sociales, la indemnización (cuando corresponda) y el valor total de la liquidación, a partir de la información suministrada del empleado.

El objetivo es reducir errores en los cálculos manuales y facilitar la obtención de una liquidación precisa a partir de la información suministrada.

---

## 🗂️ Estructura del proyecto

| Archivo | Responsabilidad |
|---|---|
| `logica_liquidacion.py` | Constantes, excepciones personalizadas y todas las funciones de cálculo (lógica de negocio pura, sin entrada/salida de consola). |
| `main.py` | Interfaz de consola: solicita los datos al usuario, invoca la lógica y muestra el resultado o los errores. |
| `test_liquidacion.py` | Pruebas unitarias (`unittest`) que validan cada función de cálculo y el manejo de errores. |
| `Liquidacion_actualizada_con_salario_restante.xlsx` | Tablero de casos de prueba en Excel: aplica manualmente la misma lógica de cálculo sobre casos normales, excepcionales y de error, para verificar los resultados de forma visual. |

---

## ▶️ Cómo ejecutar

**Calcular una liquidación por consola:**

```bash
python main.py
```

**Ejecutar las pruebas unitarias:**

```bash
python -m unittest test_liquidacion.py -v
```

---

## 📥 Entradas

El usuario debe ingresar la siguiente información a través de `main.py`:

- Tipo de retiro (seleccionado de una lista numerada).
- Salario mensual.
- Fecha de ingreso (`AAAA-MM-DD`).
- Fecha de retiro (`AAAA-MM-DD`).
- Días de vacaciones ya disfrutados.

## Tipos de retiro soportados

- `Renuncia`
- `Despido con justa causa`
- `Despido sin justa causa`

En los dos primeros casos **no** se calcula indemnización. En el tercero sí.

---

## ⚙️ Proceso

Una vez ingresada la información, el sistema realiza las siguientes operaciones (implementadas en `logica_liquidacion.py`):

1. **Valida el salario**: debe ser mayor que cero (`SalarioInvalidoException` en caso contrario).
2. **Valida las fechas**: la fecha de retiro no puede ser nula ni anterior a la fecha de ingreso (`FechaInvalidaException` en caso contrario).
3. **Calcula los días trabajados** entre la fecha de ingreso y la fecha de retiro.
4. **Calcula las prestaciones sociales**:
   - Salario restante del último mes trabajado.
   - Prima de servicios.
   - Cesantías.
   - Intereses sobre cesantías (12% anual proporcional a los días trabajados).
   - Vacaciones pendientes (descontando las ya disfrutadas, nunca negativas).
5. **Calcula la indemnización** únicamente si el tipo de retiro es `Despido sin justa causa`, incluyendo el incremento por años adicionales de servicio (`TipoRetiroInvalidoException` si el tipo ingresado no es ninguno de los tres soportados).
6. **Suma todos los conceptos** para obtener el valor total de la liquidación.
7. **Muestra mensajes de error** claros cuando los datos son inválidos.

---

## 📤 Salidas

El sistema genera como resultado:

- Valor total de la liquidación (impreso en consola por `main.py`).
- Mensajes de error específicos según el tipo de excepción capturada (salario inválido, fecha inválida o tipo de retiro inválido).

---

## 🧪 Casos de prueba (`test_liquidacion.py`)

El proyecto cuenta con **13 pruebas unitarias** que cubren:

### Casos normales

- Cálculo de prima para 180 días.
- Cálculo de cesantías para 360 días.
- Cálculo de intereses sobre cesantías para 360 días.
- Cálculo del salario restante según el día del mes de retiro.
- Cálculo de vacaciones con días ya disfrutados.
- Cálculo de vacaciones que nunca resulta negativo, aunque los días disfrutados excedan lo generado.
- Cálculo de indemnización para 360 días de servicio.
- Cálculo de días trabajados entre dos fechas.
- Liquidación completa por renuncia (resultado mayor que cero).

### Casos de error

- Salario negativo → `SalarioInvalidoException`.
- Salario igual a cero → `SalarioInvalidoException`.
- Fecha de retiro anterior a la fecha de ingreso → `FechaInvalidaException`.
- Tipo de retiro no soportado (ej. `"Vacaciones"`) → `TipoRetiroInvalidoException`.

---

## 📊 Casos de prueba en Excel (`Liquidacion_actualizada_con_salario_restante.xlsx`)

Además de las pruebas en Python, el proyecto incluye un tablero en Excel que aplica manualmente la misma lógica de cálculo, organizado en tres bloques:

### Casos normales

- Despido con justa causa.
- Renuncia voluntaria.
- Despido sin justa causa.

En todos se calculan días trabajados, salario restante, prima, cesantías, intereses y vacaciones; la indemnización solo aplica en el despido sin justa causa.

### Casos excepcionales

- Salario alto.
- Salario bajo.
- Vacaciones agotadas.
- Sin intereses de cesantía.

Estos casos ponen a prueba valores límite (salarios muy altos o muy bajos, vacaciones que superan lo generado, tasa de interés en cero), pero **no especifican un tipo de retiro** en su descripción. Para que la indemnización y la liquidación definitiva **siempre arrojen un resultado numérico** en lugar de quedar vacías, se asumió `Despido sin justa causa` en los cuatro casos; este supuesto queda documentado en un comentario sobre la celda del encabezado "Indemnización (Si aplica)" del bloque.

### Casos de error

- Salario en 0.
- Fecha de retiro anterior a la fecha de ingreso.
- Sin fecha de retiro.
- Días de vacaciones negativos.

Aquí el dato de salida esperado es la palabra `ERROR` junto con el mensaje de la excepción correspondiente (`SalarioInvalidoException` o `FechaInvalidaException`), reflejando que el sistema debe rechazar esos datos en vez de calcular una liquidación.

---

## 🛠️ Tecnologías utilizadas

- Python 3
- `unittest` (pruebas unitarias)
- Microsoft Excel (tablero de verificación de casos de prueba)

---

## 👥 Integrantes

| Nombre | GitHub |
|--------|--------|
| Jhoan Ríos | [@jhoan-rios](https://github.com/jhoan-rios) |
| Andrés Rosas | [@andres-rosas](https://github.com/andres-rosas) |
