# Calibración de Probabilidades

Las salidas en bruto de Random Forest (`predict_proba`) tienden a empujar las probabilidades hacia los extremos o concentrarse en torno a la media cuando los árboles votan en conjunto.

## Método de Calibración
Se utiliza `CalibratedClassifierCV` con método **Sigmoid (Platt Scaling)** ajustado sobre el conjunto de validación temporal:
- En scikit-learn >= 1.4: compatible con `FrozenEstimator` para calibrar el modelo base previamente entrenado sin sobreajustar en los datos de entrenamiento.
- En scikit-learn < 1.4: compatibilidad automática con `cv='prefit'`.

## Evaluación de Calibración
- **Brier Score**: **0.1061** (indica una calibración de probabilidad excelente; un Brier score < 0.15 representa predicciones probabilísticas altamente confiables).
