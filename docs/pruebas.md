# Estrategia de Pruebas Automatizadas

El proyecto cuenta con 18 pruebas automatizadas organizadas en capas:

## 1. Pruebas Unitarias de Dominio y Aplicación (`tests/unit/`)
- `test_probabilidad_valida`: Asegura el cumplimiento de invariantes en value objects.
- `test_probabilidad_fuera_de_rango`: Valida rechazo de valores `< 0.0` o `> 1.0`.
- `test_umbrales_riesgo_clasificacion`: Verifica límites exactos de corte de riesgo (`BAJO`, `MEDIO`, `ALTO`).
- `test_servicio_clasificador_recomendaciones_alto_riesgo`: Verifica derivación de recomendaciones según factores de inactividad.
- `test_predecir_abandono_individual_use_case`: Ejecuta el caso de uso con mocks para aislar lógica de negocio.
- `test_predecir_abandono_batch_use_case`: Verifica procesamiento ordenado y límites por lotes.

## 2. Pruebas de Machine Learning y Aislamiento Temporal (`tests/test_ml_scripts.py`)
- `test_reproducible_dataset`: Generación idéntica con semilla fija.
- `test_snapshot_constraints`: Verifica consistencia de columnas y tipos de datos.
- `test_temporal_label_isolation`: Asegura matemáticamente que ninguna variable use información posterior a la fecha de observación.
- `test_training_and_serialization`: Comprueba ciclo de entrenamiento, calibración, exportación y recarga del artefacto `.joblib`.

## 3. Pruebas de Integración y API (`tests/api/`)
- `test_health_live` y `test_health_ready`: Sondas operativas.
- `test_post_prediction_individual`: Ciclo completo HTTP -> Caso de uso -> Inferencia Random Forest -> Persistencia DB.
- `test_post_prediction_batch`: Inferencia y persistencia de múltiples registros.
- `test_get_risks_high_and_summary`: Consulta de clientes críticos y métricas agregadas.
- `test_get_models_endpoints`: Catálogo y estado de versiones del modelo.

Ejecución de la suite completa:
```bash
python -m pytest tests -v
```
