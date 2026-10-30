# Entrenamiento y Evaluación del Modelo

## Algoritmo Obligatorio
- **Estimador**: `sklearn.ensemble.RandomForestClassifier`
- **Hiperparámetros base**:
  - `n_estimators`: 150
  - `max_depth`: 8
  - `min_samples_split`: 5
  - `min_samples_leaf`: 3
  - `class_weight`: "balanced"
  - `random_state`: 42

## Resultados Verificados en Prueba Independiente (560 clientes)
- **Accuracy**: 0.8607 (86.07%)
- **Precision (Abandono)**: 0.7692 (76.92%)
- **Recall (Abandono)**: 0.7692 (76.92%)
- **F1-Score**: 0.7692
- **ROC-AUC**: 0.8998
- **PR-AUC**: 0.8231
- **Brier Score**: 0.1061

## Matriz de Confusión
```text
                  Predicho: No Abandono    Predicho: Abandono
Real: No Abandono         352 (TN)                 39 (FP)
Real: Abandono             39 (FN)                130 (TP)
```

## Importancia de Variables por Permutación (Test Set)
1. `attendance_trend`: Disminución acelerada en frecuencia de visitas.
2. `frequency_variation`: Variación negativa entre el mes actual y el mes previo.
3. `days_since_last_attendance`: Días transcurridos desde el último acceso.
4. `attendances_last_7d`: Actividad en la última semana.
5. `inactivity_max_days`: Período prolongado sin registros.
