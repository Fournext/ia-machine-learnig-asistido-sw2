# Despliegue y Operación

## Ejecución Local
```bash
# Entorno virtual y dependencias
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -e .[dev]

# Iniciar motor de inferencia
uvicorn churn_prediction.main:app --host 0.0.0.0 --port 8000
```

## Ejecución con Docker Compose
```bash
docker compose up -d --build
```

El stack incluye:
1. Contenedor `gym-churn-engine`: Servicio FastAPI corriendo en Python 3.11-slim con usuario sin privilegios y health checks nativos en memoria.
2. Volumen montado en solo lectura `./artifacts/models:/app/artifacts/models:ro`: Proporciona los artefactos de Machine Learning (`model.joblib` y `metadata.json`) sin requerir base de datos ni servicios de base de datos secundarios.

## CI/CD (GitHub Actions)
Definido en `.github/workflows/ci.yml`:
- Análisis estático con **Ruff**.
- Verificación de tipos con **Mypy**.
- Auditoría de seguridad estática con **Bandit**.
- Auditoría de vulnerabilidades en dependencias con **pip-audit**.
- Ejecución de pruebas y reporte de cobertura con **Pytest & Coverage**.
- Verificación de compilación de imagen Docker.
