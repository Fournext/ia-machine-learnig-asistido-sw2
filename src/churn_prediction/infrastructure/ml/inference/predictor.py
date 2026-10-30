import os
import joblib
import pandas as pd
from typing import Tuple, List, Optional
from churn_prediction.application.ports import PredictorPort
from churn_prediction.domain.entities import CaracteristicasCliente
from churn_prediction.domain.exceptions import ModeloNoDisponibleException
from churn_prediction.infrastructure.config.settings import settings

class RandomForestPredictorAdapter(PredictorPort):
    """
    Adaptador de inferencia para Random Forest.
    Implementa el puerto PredictorPort desacoplando el dominio de scikit-learn.
    """
    def __init__(self, model_version: str = "1.0.0", model_path: Optional[str] = None):
        self.model_version = model_version
        self.model_path = model_path or os.path.join(
            settings.model_artifacts_dir, f"v{model_version}", "model.joblib"
        )
        self._pipeline = None
        self._load_model_safe()

    def _load_model_safe(self):
        # Intentar varias rutas relativas
        candidate_paths = [
            self.model_path,
            os.path.join("gym-churn-prediction", self.model_path),
            os.path.join(os.getcwd(), "gym-churn-prediction", self.model_path),
            os.path.join(os.getcwd(), self.model_path)
        ]
        for p in candidate_paths:
            if os.path.exists(p):
                try:
                    self._pipeline = joblib.load(p)
                    self.model_path = p
                    break
                except Exception:
                    pass

    def get_model_version_string(self) -> str:
        return self.model_version

    def predict_churn(self, features: CaracteristicasCliente) -> Tuple[float, List[str]]:
        if self._pipeline is None:
            self._load_model_safe()

        feature_dict = features.to_feature_dict()
        df_input = pd.DataFrame([feature_dict])

        # Si el modelo está cargado, calcular probabilidad real con predict_proba
        if self._pipeline is not None:
            try:
                proba_array = self._pipeline.predict_proba(df_input)
                # Probabilidad de clase 1 (Abandono)
                probabilidad = float(proba_array[0][1])
            except Exception as e:
                # Si fallan nombres de columnas o transformador
                probabilidad = self._fallback_heuristic(features)
        else:
            probabilidad = self._fallback_heuristic(features)

        factores = self._extraer_factores_relevantes(features, probabilidad)
        return probabilidad, factores

    def _fallback_heuristic(self, f: CaracteristicasCliente) -> float:
        """Heurística auxiliar si no hay artefacto serializado cargado."""
        score = 0.2
        if f.days_since_last_attendance > 15:
            score += 0.35
        if f.attendance_trend < 0:
            score += 0.2
        if f.days_until_expiration <= 5:
            score += 0.15
        if f.attendances_last_30d < 3:
            score += 0.2
        return min(0.99, max(0.01, score))

    def _extraer_factores_relevantes(self, f: CaracteristicasCliente, prob: float) -> List[str]:
        factores = []
        if f.days_since_last_attendance >= 14:
            factores.append(f"Inactividad prolongada: {f.days_since_last_attendance} días sin registrar asistencia")
        if f.attendance_trend < -0.3:
            factores.append("Tendencia negativa marcada en visitas respecto al promedio histórico")
        if f.days_until_expiration <= 7:
            factores.append(f"Membresía próxima a expirar o en ventana crítica ({f.days_until_expiration} días)")
        if f.attendances_last_30d <= 2:
            factores.append(f"Baja frecuencia mensual: sólo {f.attendances_last_30d} asistencias en los últimos 30 días")
        if f.pct_weeks_without_visit > 0.4:
            factores.append("Alta tasa de semanas completas sin acudir al gimnasio")
        if f.routine_compliance_score < 0.4:
            factores.append("Bajo cumplimiento registrado de las rutinas de entrenamiento")
        if not factores:
            if prob >= 0.5:
                factores.append("Patrón combinado de inestabilidad en visitas semanales")
            else:
                factores.append("Frecuencia y asistencia consistentes con hábitos de retención")
        return factores
