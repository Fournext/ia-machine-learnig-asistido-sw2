from typing import List, Optional
from churn_prediction.application.ports import (
    PredictorPort,
    ClientDataProviderPort,
    EventPublisherPort
)
from churn_prediction.application.dto import (
    BatchPredictionRequestDTO,
    BatchPredictionResponseDTO,
    PredictionRequestDTO,
    PredictionResponseDTO
)
from churn_prediction.application.use_cases.predecir_abandono import PredecirAbandonoUseCase
from churn_prediction.domain.services import ClasificadorDeRiesgoService

class PredecirAbandonoBatchUseCase:
    """Caso de uso: Procesar predicciones por lote en memoria para el ERP (Stateless)."""
    def __init__(
        self,
        predictor: PredictorPort,
        clasificador_service: ClasificadorDeRiesgoService,
        client_data_provider: Optional[ClientDataProviderPort] = None,
        event_publisher: Optional[EventPublisherPort] = None
    ):
        self.single_use_case = PredecirAbandonoUseCase(
            predictor=predictor,
            clasificador_service=clasificador_service,
            client_data_provider=client_data_provider,
            event_publisher=event_publisher
        )
        self.client_data_provider = client_data_provider

    def execute(self, request: BatchPredictionRequestDTO) -> BatchPredictionResponseDTO:
        resultados: List[PredictionResponseDTO] = []

        # Caso 1: Se envía lista de características directa
        if request.features_list:
            for feat in request.features_list[:request.limite]:
                try:
                    single_req = PredictionRequestDTO(
                        cliente_id=feat.cliente_id,
                        features=feat,
                        horizonte_dias=request.horizonte_dias
                    )
                    res = self.single_use_case.execute(single_req)
                    resultados.append(res)
                except Exception:
                    continue
            return BatchPredictionResponseDTO(
                total_procesados=len(resultados),
                predicciones=resultados
            )

        # Caso 2: Se envía lista de IDs o se consultan elegibles al ERP
        target_client_ids = request.clientes_ids
        if not target_client_ids and self.client_data_provider:
            target_client_ids = self.client_data_provider.get_eligible_clients(limit=request.limite)
        elif not target_client_ids:
            target_client_ids = []

        for c_id in target_client_ids[:request.limite]:
            try:
                single_req = PredictionRequestDTO(cliente_id=c_id, horizonte_dias=request.horizonte_dias)
                res = self.single_use_case.execute(single_req)
                resultados.append(res)
            except Exception:
                continue

        return BatchPredictionResponseDTO(
            total_procesados=len(resultados),
            predicciones=resultados
        )
