from typing import List, Optional, Dict, Any
from churn_prediction.application.ports import ModelRegistryPort
from churn_prediction.domain.entities import VersionDeModelo
from churn_prediction.domain.exceptions import ModeloNoDisponibleException

class GestionarModelosUseCase:
    def __init__(self, registry: ModelRegistryPort):
        self.registry = registry

    def obtener_modelo_activo(self) -> Optional[VersionDeModelo]:
        return self.registry.get_active_model_version()

    def listar_modelos(self) -> List[VersionDeModelo]:
        return self.registry.list_models()

    def activar_modelo(self, version: str) -> bool:
        exito = self.registry.activate_model(version)
        if not exito:
            raise ModeloNoDisponibleException(version)
        return True

    def obtener_metricas(self, version: str) -> Dict[str, Any]:
        modelo = self.registry.get_model_version(version)
        if not modelo:
            raise ModeloNoDisponibleException(version)
        return modelo.metricas
