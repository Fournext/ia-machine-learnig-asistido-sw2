from fastapi.testclient import TestClient
from churn_prediction.main import app

client = TestClient(app)

def test_health_live():
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"

def test_health_ready():
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ready", "warming_up"]
    assert data["mode"] == "stateless_engine"

def test_post_prediction_individual():
    payload = {
        "cliente_id": "test-client-999",
        "horizonte_dias": 30
    }
    response = client.post("/api/v1/predictions", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["cliente_id"] == "test-client-999"
    assert 0.0 <= data["probabilidad_abandono"] <= 1.0
    assert data["nivel_riesgo"] in ["BAJO", "MEDIO", "ALTO"]
    assert len(data["factores_relevantes"]) > 0
    assert len(data["recomendaciones"]) > 0

def test_post_prediction_with_direct_features():
    payload = {
        "features": {
            "cliente_id": "cli-custom-123",
            "membership_type": "Mensual",
            "duration_days": 30,
            "days_until_expiration": 2,
            "previous_renewals_count": 0,
            "client_seniority_days": 28,
            "attendances_last_7d": 0,
            "attendances_last_30d": 1,
            "attendances_last_60d": 3,
            "days_since_last_attendance": 22,
            "weekly_frequency": 0.25,
            "frequency_variation": -1.5,
            "attendance_trend": -0.8,
            "pct_weeks_without_visit": 0.75,
            "inactivity_max_days": 22,
            "routine_compliance_score": 0.1
        },
        "horizonte_dias": 30
    }
    response = client.post("/api/v1/predictions", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["cliente_id"] == "cli-custom-123"
    assert data["probabilidad_abandono"] >= 0.50
    assert data["nivel_riesgo"] in ["MEDIO", "ALTO"]

def test_post_prediction_batch():
    payload = {
        "clientes_ids": ["test-batch-1", "test-batch-2"],
        "limite": 2,
        "horizonte_dias": 30
    }
    response = client.post("/api/v1/predictions/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_procesados"] == 2
    assert len(data["predicciones"]) == 2

def test_get_models_endpoints():
    resp_list = client.get("/api/v1/models")
    assert resp_list.status_code == 200
    assert isinstance(resp_list.json(), list)

    resp_active = client.get("/api/v1/models/active")
    assert resp_active.status_code in [200, 404]
