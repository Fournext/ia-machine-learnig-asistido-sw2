from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict, Any
from churn_prediction.domain.entities import (
    PrediccionDeAbandono,
    VersionDeModelo,
    CaracteristicasCliente,
    Cliente
)

class ModelRegistryPort(ABC):
    """Puerto para consultar y gestionar versiones del modelo entrenado."""
    @abstractmethod
    def get_active_model_version(self) -> Optional[VersionDeModelo]:
        pass

    @abstractmethod
    def get_model_version(self, version: str) -> Optional[VersionDeModelo]:
        pass

    @abstractmethod
    def list_models(self) -> List[VersionDeModelo]:
        pass

    @abstractmethod
    def activate_model(self, version: str) -> bool:
        pass


class PredictorPort(ABC):
    """Puerto para el modelo de ML (RandomForest). Desacoplado de Scikit-learn."""
    @abstractmethod
    def predict_churn(self, features: CaracteristicasCliente) -> Tuple[float, List[str]]:
        """Retorna (probabilidad_abandono, factores_relevantes)"""
        pass

    @abstractmethod
    def get_model_version_string(self) -> str:
        pass


class ClientDataProviderPort(ABC):
    """Puerto para obtener características de los clientes desde los módulos de ERP."""
    @abstractmethod
    def get_client_features(self, cliente_id: str) -> CaracteristicasCliente:
        pass

    @abstractmethod
    def get_eligible_clients(self, limit: int = 100) -> List[str]:
        pass


class EventPublisherPort(ABC):
    @abstractmethod
    def publish_prediction_completed(self, prediccion: PrediccionDeAbandono) -> None:
        pass
