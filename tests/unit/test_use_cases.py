from typing import List, Tuple
from churn_prediction.application.ports import (
    PredictorPort,
    ClientDataProviderPort
)
from churn_prediction.application.use_cases.predecir_abandono import PredecirAbandonoUseCase
from churn_prediction.application.use_cases.predecir_abandono_batch import PredecirAbandonoBatchUseCase
from churn_prediction.application.dto import PredictionRequestDTO, BatchPredictionRequestDTO
from churn_prediction.domain.entities import CaracteristicasCliente
from churn_prediction.domain.services import ClasificadorDeRiesgoService

class MockClientDataProvider(ClientDataProviderPort):
    def get_client_features(self, cliente_id: str) -> CaracteristicasCliente:
        return CaracteristicasCliente(
            cliente_id=cliente_id,
            membership_type="Mensual",
            duration_days=30,
            days_until_expiration=3,
            previous_renewals_count=1,
            client_seniority_days=60,
            attendances_last_7d=0,
            attendances_last_30d=2,
            attendances_last_60d=8,
            days_since_last_attendance=15,
            weekly_frequency=0.5,
            frequency_variation=-1.0,
            attendance_trend=-0.6,
            pct_weeks_without_visit=0.5,
            inactivity_max_days=15,
            routine_compliance_score=0.4
        )

    def get_eligible_clients(self, limit: int = 100) -> List[str]:
        all_clients = ["cli-001", "cli-002", "cli-003"]
        return all_clients[:limit]

class MockPredictor(PredictorPort):
    def predict_churn(self, features: CaracteristicasCliente) -> Tuple[float, List[str]]:
        return 0.82, ["Tendencia de asistencia en caída", "Inactividad reciente"]

    def get_model_version_string(self) -> str:
        return "1.0.0-test"

def test_predecir_abandono_individual_stateless():
    data_provider = MockClientDataProvider()
    predictor = MockPredictor()
    service = ClasificadorDeRiesgoService()

    use_case = PredecirAbandonoUseCase(
        predictor=predictor,
        clasificador_service=service,
        client_data_provider=data_provider
    )

    req = PredictionRequestDTO(cliente_id="cli-001", horizonte_dias=30)
    res = use_case.execute(req)

    assert res.cliente_id == "cli-001"
    assert res.probabilidad_abandono == 0.82
    assert res.nivel_riesgo == "ALTO"
    assert len(res.factores_relevantes) == 2
    assert len(res.recomendaciones) > 0

def test_predecir_abandono_con_features_directas():
    predictor = MockPredictor()
    service = ClasificadorDeRiesgoService()

    use_case = PredecirAbandonoUseCase(
        predictor=predictor,
        clasificador_service=service,
        client_data_provider=None  # Sin proveedor ERP
    )

    direct_features = CaracteristicasCliente(
        cliente_id="cli-directo",
        membership_type="Anual",
        duration_days=365,
        days_until_expiration=120,
        previous_renewals_count=3,
        client_seniority_days=400,
        attendances_last_7d=3,
        attendances_last_30d=14,
        attendances_last_60d=28,
        days_since_last_attendance=2,
        weekly_frequency=3.5,
        frequency_variation=0.2,
        attendance_trend=0.1,
        pct_weeks_without_visit=0.0,
        inactivity_max_days=3,
        routine_compliance_score=0.9
    )

    req = PredictionRequestDTO(features=direct_features, horizonte_dias=30)
    res = use_case.execute(req)

    assert res.cliente_id == "cli-directo"
    assert res.probabilidad_abandono == 0.82

def test_predecir_abandono_batch_stateless():
    data_provider = MockClientDataProvider()
    predictor = MockPredictor()
    service = ClasificadorDeRiesgoService()

    use_case = PredecirAbandonoBatchUseCase(
        predictor=predictor,
        clasificador_service=service,
        client_data_provider=data_provider
    )

    req = BatchPredictionRequestDTO(limite=2)
    res = use_case.execute(req)

    assert res.total_procesados == 2
    assert len(res.predicciones) == 2
