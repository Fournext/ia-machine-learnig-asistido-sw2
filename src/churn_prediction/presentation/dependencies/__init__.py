import os
from fastapi import Depends
from churn_prediction.infrastructure.http_clients.erp_client import ErpClientDataProviderAdapter
from churn_prediction.infrastructure.ml.inference.predictor import RandomForestPredictorAdapter
from churn_prediction.infrastructure.ml.model_registry.file_registry import FileSystemModelRegistry
from churn_prediction.domain.services import ClasificadorDeRiesgoService
from churn_prediction.domain.value_objects import UmbralesRiesgo
from churn_prediction.infrastructure.config.settings import settings
from churn_prediction.application.use_cases.predecir_abandono import PredecirAbandonoUseCase
from churn_prediction.application.use_cases.predecir_abandono_batch import PredecirAbandonoBatchUseCase
from churn_prediction.application.use_cases.gestionar_modelos import GestionarModelosUseCase

# Instancias compartidas en memoria
_file_registry = FileSystemModelRegistry()
_erp_client = ErpClientDataProviderAdapter(use_mock_fallback=True)
_predictor = RandomForestPredictorAdapter(model_version=settings.active_model_version)

def get_model_registry() -> FileSystemModelRegistry:
    return _file_registry

def get_erp_client() -> ErpClientDataProviderAdapter:
    return _erp_client

def get_predictor() -> RandomForestPredictorAdapter:
    return _predictor

def get_risk_service() -> ClasificadorDeRiesgoService:
    umbrales = UmbralesRiesgo(
        umbral_bajo_max=settings.umbral_riesgo_bajo_max,
        umbral_medio_max=settings.umbral_riesgo_medio_max
    )
    return ClasificadorDeRiesgoService(umbrales=umbrales)

def get_predict_use_case(
    predictor: RandomForestPredictorAdapter = Depends(get_predictor),
    risk_service: ClasificadorDeRiesgoService = Depends(get_risk_service),
    erp_client: ErpClientDataProviderAdapter = Depends(get_erp_client)
) -> PredecirAbandonoUseCase:
    return PredecirAbandonoUseCase(
        predictor=predictor,
        clasificador_service=risk_service,
        client_data_provider=erp_client
    )

def get_batch_predict_use_case(
    predictor: RandomForestPredictorAdapter = Depends(get_predictor),
    risk_service: ClasificadorDeRiesgoService = Depends(get_risk_service),
    erp_client: ErpClientDataProviderAdapter = Depends(get_erp_client)
) -> PredecirAbandonoBatchUseCase:
    return PredecirAbandonoBatchUseCase(
        predictor=predictor,
        clasificador_service=risk_service,
        client_data_provider=erp_client
    )

def get_gestionar_modelos_use_case(
    registry: FileSystemModelRegistry = Depends(get_model_registry)
) -> GestionarModelosUseCase:
    return GestionarModelosUseCase(registry=registry)
