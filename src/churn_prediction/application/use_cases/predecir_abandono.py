import uuid
from datetime import datetime, timezone
from typing import Optional
from churn_prediction.application.ports import (
    PredictorPort,
    ClientDataProviderPort,
    EventPublisherPort
)
from churn_prediction.application.dto import PredictionRequestDTO, PredictionResponseDTO
from churn_prediction.domain.services import ClasificadorDeRiesgoService
from churn_prediction.domain.exceptions import ClienteNoEncontradoException, DatosInsuficientesException

class PredecirAbandonoUseCase:
    """Caso de uso: Calcular la probabilidad de abandono para un cliente en memoria (Stateless)."""
    def __init__(
        self,
        predictor: PredictorPort,
        clasificador_service: ClasificadorDeRiesgoService,
        client_data_provider: Optional[ClientDataProviderPort] = None,
        event_publisher: Optional[EventPublisherPort] = None
    ):
        self.predictor = predictor
        self.clasificador_service = clasificador_service
        self.client_data_provider = client_data_provider
        self.event_publisher = event_publisher

    def execute(self, request: PredictionRequestDTO) -> PredictionResponseDTO:
        # 1. Obtener características (directas o desde el ERP)
        features = request.features
        target_cliente_id = request.cliente_id

        if features is None:
            if not target_cliente_id:
                raise DatosInsuficientesException("desconocido", "Debe proporcionar cliente_id o el vector de features.")
            if not self.client_data_provider:
                raise DatosInsuficientesException(target_cliente_id, "No hay proveedor de datos de ERP configurado.")
            features = self.client_data_provider.get_client_features(target_cliente_id)
            if not features:
                raise ClienteNoEncontradoException(target_cliente_id)
        else:
            if not target_cliente_id:
                target_cliente_id = features.cliente_id

        # 2. Inferencia con Random Forest
        probabilidad, factores = self.predictor.predict_churn(features)

        # 3. Clasificación de riesgo y derivación de sugerencias
        nivel_riesgo = self.clasificador_service.clasificar(probabilidad)
        recomendaciones = self.clasificador_service.generar_recomendaciones(
            nivel_riesgo=nivel_riesgo,
            caracteristicas=features,
            factores=factores
        )

        # 4. Generar DTO de respuesta (Stateless)
        prediccion_id = str(uuid.uuid4())
        fecha_iso = datetime.now(timezone.utc).isoformat()

        response = PredictionResponseDTO(
            id=prediccion_id,
            cliente_id=target_cliente_id,
            probabilidad_abandono=round(probabilidad, 4),
            nivel_riesgo=nivel_riesgo.value,
            horizonte_dias=request.horizonte_dias,
            modelo_version=self.predictor.get_model_version_string(),
            factores_relevantes=factores,
            recomendaciones=recomendaciones,
            fecha_prediccion=fecha_iso
        )

        return response
