import pytest
from churn_prediction.domain.value_objects import Probabilidad, UmbralesRiesgo, NivelRiesgo, TipoMembresia
from churn_prediction.domain.entities import CaracteristicasCliente, PrediccionDeAbandono
from churn_prediction.domain.services import ClasificadorDeRiesgoService
from churn_prediction.domain.exceptions import ClienteNoEncontradoException, ModeloNoDisponibleException

def test_probabilidad_valida():
    p = Probabilidad(0.85)
    assert p.valor == 0.85

def test_probabilidad_fuera_de_rango():
    with pytest.raises(ValueError):
        Probabilidad(1.5)
    with pytest.raises(ValueError):
        Probabilidad(-0.1)

def test_umbrales_riesgo_clasificacion():
    umbrales = UmbralesRiesgo(umbral_bajo_max=0.30, umbral_medio_max=0.70)
    assert umbrales.clasificar(0.15) == NivelRiesgo.BAJO
    assert umbrales.clasificar(0.30) == NivelRiesgo.MEDIO
    assert umbrales.clasificar(0.69) == NivelRiesgo.MEDIO
    assert umbrales.clasificar(0.70) == NivelRiesgo.ALTO
    assert umbrales.clasificar(0.95) == NivelRiesgo.ALTO

def test_caracteristicas_to_dict():
    f = CaracteristicasCliente(
        cliente_id="cli-123",
        membership_type="Mensual",
        duration_days=30,
        days_until_expiration=5,
        previous_renewals_count=2,
        client_seniority_days=180,
        attendances_last_7d=1,
        attendances_last_30d=4,
        attendances_last_60d=10,
        days_since_last_attendance=16,
        weekly_frequency=1.0,
        frequency_variation=-1.5,
        attendance_trend=-0.5,
        pct_weeks_without_visit=0.5,
        inactivity_max_days=16,
        routine_compliance_score=0.3
    )
    d = f.to_feature_dict()
    assert d["membership_type"] == "Mensual"
    assert d["days_since_last_attendance"] == 16
    assert d["attendance_trend"] == -0.5

def test_servicio_clasificador_recomendaciones_alto_riesgo():
    service = ClasificadorDeRiesgoService()
    f = CaracteristicasCliente(
        cliente_id="cli-123",
        membership_type="Mensual",
        duration_days=30,
        days_until_expiration=5,
        previous_renewals_count=0,
        client_seniority_days=30,
        attendances_last_7d=0,
        attendances_last_30d=1,
        attendances_last_60d=3,
        days_since_last_attendance=20,
        weekly_frequency=0.2,
        frequency_variation=-2.0,
        attendance_trend=-0.8,
        pct_weeks_without_visit=0.75,
        inactivity_max_days=20,
        routine_compliance_score=0.2
    )
    nivel = service.clasificar(0.85)
    assert nivel == NivelRiesgo.ALTO
    recs = service.generar_recomendaciones(nivel, f, ["Inactividad prolongada"])
    assert len(recs) >= 2
    assert any("Seguimiento y llamada proactiva" in r for r in recs)
