import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    app_name: str = "Gym Churn Prediction Engine"
    app_version: str = "1.0.0"
    environment: str = Field(default="development")

    # Modelos y artefactos en sistema de archivos
    model_artifacts_dir: str = Field(
        default="artifacts/models",
        description="Directorio donde se almacenan las versiones del modelo serializado"
    )
    active_model_version: str = Field(
        default="1.0.0",
        description="Versión del modelo activa por defecto"
    )

    # Umbrales de riesgo configurables
    umbral_riesgo_bajo_max: float = 0.30
    umbral_riesgo_medio_max: float = 0.70

    # Seguridad JWT
    jwt_secret_key: str = Field(default="super-secret-jwt-key-for-gym-erp-2026")
    jwt_algorithm: str = "HS256"

    # ERP Microservices URLs
    erp_gateway_url: str = "http://localhost:8000/api"
    users_service_url: str = "http://localhost:8001/api/v1/users"
    memberships_service_url: str = "http://localhost:8002/api/v1/memberships"
    attendances_service_url: str = "http://localhost:8003/api/v1/attendances"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
