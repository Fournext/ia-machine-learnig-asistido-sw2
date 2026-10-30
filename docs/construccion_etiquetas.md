# Construcción de Etiquetas y Aislamiento Temporal

## Definición de Abandono
Un cliente se considera que abandona (`churn_30d = 1`) si:
> **No renueva su membresía durante los 30 días posteriores a la fecha de vencimiento.**

## Prevención de Fuga de Información (Data Leakage)
1. **Punto de Corte Temporal**: Para cada registro de entrenamiento con fecha de observación $T_{obs}$, las variables predictoras (asistencias, rutinas, renovaciones) se calculan única y exclusivamente con eventos ocurridos en $t \le T_{obs}$.
2. **Ventana Futura de Resultado**: La etiqueta $y \in \{0, 1\}$ se evalúa en el intervalo futuro $[T_{exp}, T_{exp} + 30\text{ días}]$.
3. **División Temporal Estricta**: No se utiliza división aleatoria estándar `train_test_split`, ya que causaría que el modelo aprenda del futuro para predecir el pasado. En su lugar se ordenan cronológicamente las fechas de observación:
   - **Entrenamiento**: Primer 65% temporal (2022 a principios de 2024).
   - **Validación (Calibración)**: Siguiente 15% temporal.
   - **Prueba Independiente**: Último 20% temporal (segundo semestre de 2024).
