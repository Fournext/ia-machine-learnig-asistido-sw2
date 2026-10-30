# Especificación de la API REST

## Endpoints

### 1. Predicciones
- `POST /api/v1/predictions`: Realiza predicción individual por ID de cliente.
  ```json
  // Request
  { "cliente_id": "cli-0042", "horizonte_dias": 30 }
  
  // Response (201 Created)
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "cliente_id": "cli-0042",
    "probabilidad_abandono": 0.8245,
    "nivel_riesgo": "ALTO",
    "horizonte_dias": 30,
    "modelo_version": "1.0.0",
    "factores_relevantes": [
      "Inactividad prolongada: 18 días sin registrar asistencia",
      "Tendencia negativa marcada en visitas respecto al promedio histórico"
    ],
    "recomendaciones": [
      "Seguimiento y llamada proactiva de cortesía por parte del staff o entrenador."
    ],
    "fecha_prediccion": "2026-10-21T19:30:00Z"
  }
  ```

- `POST /api/v1/predictions/batch`: Procesa múltiples clientes por lotes de forma eficiente.
- `GET /api/v1/predictions/{prediction_id}`: Consulta una predicción histórica por su UUID.
- `GET /api/v1/clients/{client_id}/predictions`: Historial cronológico de predicciones de un cliente.

### 2. Gestión de Riesgos
- `GET /api/v1/risks/high?min_prob=0.70&limit=50`: Listado de clientes en alto riesgo de abandono.
- `GET /api/v1/risks/summary`: Resumen cuantitativo por categorías de riesgo (Bajo, Medio, Alto).

### 3. Gestión y Ciclo de Vida de Modelos
- `GET /api/v1/models`: Lista versiones registradas.
- `GET /api/v1/models/active`: Versión activa actualmente en inferencia.
- `GET /api/v1/models/{version}/metrics`: Métricas de evaluación independientes (ROC-AUC, PR-AUC, etc.).
- `POST /api/v1/models/{version}/activate`: Promover o revertir una versión de modelo.
- `POST /api/v1/models/train`: Disparo de trabajo de entrenamiento asíncrono.

### 4. Sondas de Salud
- `GET /health/live`: Liveness probe para contenedores.
- `GET /health/ready`: Readiness probe confirmando disponibilidad de base de datos y modelo.
