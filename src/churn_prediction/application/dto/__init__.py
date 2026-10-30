from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from churn_prediction.domain.entities import CaracteristicasCliente

@dataclass
class PredictionRequestDTO:
    cliente_id: Optional[str] = None
    features: Optional[CaracteristicasCliente] = None
    horizonte_dias: int = 30

@dataclass
class PredictionResponseDTO:
    id: str
    cliente_id: str
    probabilidad_abandono: float
    nivel_riesgo: str
    horizonte_dias: int
    modelo_version: str
    factores_relevantes: List[str]
    recomendaciones: List[str]
    fecha_prediccion: str

@dataclass
class BatchPredictionRequestDTO:
    clientes_ids: Optional[List[str]] = None
    features_list: Optional[List[CaracteristicasCliente]] = None
    limite: int = 50
    horizonte_dias: int = 30

@dataclass
class BatchPredictionResponseDTO:
    total_procesados: int
    predicciones: List[PredictionResponseDTO]

@dataclass
class ModelVersionDTO:
    id: str
    version: str
    algoritmo: str
    fecha_entrenamiento: str
    metricas: Dict[str, Any]
    activa: bool
    ruta_artefacto: Optional[str] = None
    sha256_hash: Optional[str] = None
