from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from churn_prediction.domain.value_objects import NivelRiesgo, TipoMembresia, Probabilidad

@dataclass
class Cliente:
    id: str
    nombre: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    activo: bool = True
    fecha_registro: Optional[date] = None

@dataclass
class HistorialDeMembresia:
    cliente_id: str
    tipo_membresia: str
    duracion_dias: int
    dias_hasta_vencimiento: int
    renovaciones_previas: int
    antiguedad_dias: int

@dataclass
class HistorialDeAsistencia:
    cliente_id: str
    asistencias_7d: int
    asistencias_30d: int
    asistencias_60d: int
    dias_desde_ultima_asistencia: int
    frecuencia_semanal: float
    variacion_frecuencia: float
    tendencia_asistencia: float
    pct_semanas_sin_visita: float

@dataclass
class ComportamientoCliente:
    cliente_id: str
    inactividad_max_dias: int = 0
    cumplimiento_rutinas: float = 0.5

@dataclass
class CaracteristicasCliente:
    """Contenedor de las variables predictoras extraídas hasta el punto temporal de corte."""
    cliente_id: str
    membership_type: str
    duration_days: int
    days_until_expiration: int
    previous_renewals_count: int
    client_seniority_days: int
    attendances_last_7d: int
    attendances_last_30d: int
    attendances_last_60d: int
    days_since_last_attendance: int
    weekly_frequency: float
    frequency_variation: float
    attendance_trend: float
    pct_weeks_without_visit: float
    inactivity_max_days: int = 0
    routine_compliance_score: float = 0.5

    def to_feature_dict(self) -> Dict[str, Any]:
        return {
            "membership_type": self.membership_type,
            "duration_days": self.duration_days,
            "days_until_expiration": self.days_until_expiration,
            "previous_renewals_count": self.previous_renewals_count,
            "client_seniority_days": self.client_seniority_days,
            "attendances_last_7d": self.attendances_last_7d,
            "attendances_last_30d": self.attendances_last_30d,
            "attendances_last_60d": self.attendances_last_60d,
            "days_since_last_attendance": self.days_since_last_attendance,
            "weekly_frequency": self.weekly_frequency,
            "frequency_variation": self.frequency_variation,
            "attendance_trend": self.attendance_trend,
            "pct_weeks_without_visit": self.pct_weeks_without_visit,
            "inactivity_max_days": self.inactivity_max_days,
            "routine_compliance_score": self.routine_compliance_score,
        }

@dataclass
class PrediccionDeAbandono:
    cliente_id: str
    probabilidad_abandono: float
    nivel_riesgo: NivelRiesgo
    modelo_version: str
    horizonte_dias: int = 30
    factores_relevantes: List[str] = field(default_factory=list)
    recomendaciones: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))
    fecha_prediccion: datetime = field(default_factory=datetime.utcnow)

@dataclass
class VersionDeModelo:
    version: str
    algoritmo: str
    fecha_entrenamiento: datetime
    metricas: Dict[str, Any]
    activa: bool = False
    ruta_artefacto: Optional[str] = None
    sha256_hash: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid4()))
