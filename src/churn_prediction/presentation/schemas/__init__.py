from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class CaracteristicasClienteInputSchema(BaseModel):
    """Esquema de variables predictoras cuando el ERP las envía directamente en memoria."""
    cliente_id: Optional[str] = "cliente-directo"
    membership_type: str = Field(default="Mensual", description="Mensual, Trimestral o Anual")
    duration_days: int = Field(default=30, ge=1)
    days_until_expiration: int = Field(default=5)
    previous_renewals_count: int = Field(default=1, ge=0)
    client_seniority_days: int = Field(default=90, ge=0)
    attendances_last_7d: int = Field(default=1, ge=0)
    attendances_last_30d: int = Field(default=4, ge=0)
    attendances_last_60d: int = Field(default=10, ge=0)
    days_since_last_attendance: int = Field(default=12, ge=0)
    weekly_frequency: float = Field(default=1.0, ge=0.0)
    frequency_variation: float = Field(default=-0.5)
    attendance_trend: float = Field(default=-0.3)
    pct_weeks_without_visit: float = Field(default=0.2, ge=0.0, le=1.0)
    inactivity_max_days: int = Field(default=8, ge=0)
    routine_compliance_score: float = Field(default=0.5, ge=0.0, le=1.0)

class PredictionRequestSchema(BaseModel):
    cliente_id: Optional[str] = Field(default=None, description="ID del cliente en el ERP (si se omite, se debe enviar 'features')")
    features: Optional[CaracteristicasClienteInputSchema] = Field(default=None, description="Vector de características si el ERP ya las tiene calculadas")
    horizonte_dias: int = Field(default=30, ge=1, le=180, description="Horizonte predictivo en días")

class PredictionResponseSchema(BaseModel):
    id: str = Field(..., description="Identificador único generado para la predicción")
    cliente_id: str = Field(..., description="ID del cliente evaluado")
    probabilidad_abandono: float = Field(..., ge=0.0, le=1.0, description="Probabilidad calculada por Random Forest (calibrada)")
    nivel_riesgo: str = Field(..., description="Nivel de riesgo: BAJO, MEDIO o ALTO")
    horizonte_dias: int = Field(..., description="Horizonte predictivo")
    modelo_version: str = Field(..., description="Versión del modelo utilizada")
    factores_relevantes: List[str] = Field(default_factory=list, description="Factores explicativos de mayor impacto")
    recomendaciones: List[str] = Field(default_factory=list, description="Sugerencias administrativas/operativas no invasivas")
    fecha_prediccion: str = Field(..., description="Marca temporal ISO de la inferencia")

class BatchPredictionRequestSchema(BaseModel):
    clientes_ids: Optional[List[str]] = Field(default=None, description="Lista opcional de IDs de clientes")
    features_list: Optional[List[CaracteristicasClienteInputSchema]] = Field(default=None, description="Lista de vectores de características directas")
    limite: int = Field(default=50, ge=1, le=500, description="Límite de clientes a procesar")
    horizonte_dias: int = Field(default=30, ge=1, le=180)

class BatchPredictionResponseSchema(BaseModel):
    total_procesados: int
    predicciones: List[PredictionResponseSchema]

class ModelTrainRequestSchema(BaseModel):
    dataset_path: Optional[str] = Field(default="datasets/synthetic_gym_churn.csv", description="Ruta al dataset CSV")
    n_estimators: int = Field(default=150, ge=10, le=500)
    max_depth: Optional[int] = Field(default=8, ge=2, le=30)
    version: str = Field(default="1.0.1", description="Nueva versión a asignar")

class ModelVersionResponseSchema(BaseModel):
    id: str
    version: str
    algoritmo: str
    fecha_entrenamiento: str
    metricas: Dict[str, Any]
    activa: bool
    ruta_artefacto: Optional[str] = None
    sha256_hash: Optional[str] = None

class HealthCheckResponseSchema(BaseModel):
    status: str
    service: str
    active_model_version: str
