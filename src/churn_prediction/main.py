from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from churn_prediction.infrastructure.config.settings import settings
from churn_prediction.presentation.dependencies import get_predictor, get_model_registry
from churn_prediction.presentation.api.v1.predictions_router import router as predictions_router
from churn_prediction.presentation.api.v1.models_router import router as models_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-calentar el modelo en memoria durante el arranque
    predictor = get_predictor()
    registry = get_model_registry()
    yield

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Motor de Inferencia de Abandono de Clientes (Stateless) para ERP de Gimnasio con Arquitectura Hexagonal y Random Forest.",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sondas de Salud
@app.get("/health/live", tags=["Sondas de Salud"])
def liveness():
    """Sonda Liveness para Kubernetes/Docker."""
    return {"status": "alive", "service": "gym-churn-engine"}

@app.get("/health/ready", tags=["Sondas de Salud"])
def readiness():
    """Sonda Readiness para verificar que el motor y el modelo en memoria están listos."""
    predictor = get_predictor()
    model_loaded = predictor._pipeline is not None
    return {
        "status": "ready" if model_loaded else "warming_up",
        "service": "gym-churn-engine",
        "model_loaded": model_loaded,
        "active_model_version": settings.active_model_version,
        "mode": "stateless_engine"
    }

# Registrar Routers API v1
app.include_router(predictions_router, prefix="/api/v1")
app.include_router(models_router, prefix="/api/v1")
