import os
import random
import pandas as pd
from typing import List, Optional
import httpx
from churn_prediction.application.ports import ClientDataProviderPort
from churn_prediction.domain.entities import CaracteristicasCliente
from churn_prediction.infrastructure.config.settings import settings

class ErpClientDataProviderAdapter(ClientDataProviderPort):
    """
    Adaptador HTTP para obtener datos de clientes, membresías y asistencias
    desde los microservicios del ERP o desde el dataset sintético local si está en modo demostración.
    """
    def __init__(self, use_mock_fallback: bool = True):
        self.use_mock_fallback = use_mock_fallback
        self.dataset_path = "datasets/synthetic_gym_churn.csv"
        self._cached_dataset: Optional[pd.DataFrame] = None

    def _get_dataset(self) -> Optional[pd.DataFrame]:
        if self._cached_dataset is None:
            # Intentar ruta local o relativa
            paths = [
                self.dataset_path,
                os.path.join("gym-churn-prediction", self.dataset_path),
                os.path.join(os.getcwd(), "gym-churn-prediction", self.dataset_path)
            ]
            for p in paths:
                if os.path.exists(p):
                    self._cached_dataset = pd.read_csv(p)
                    break
        return self._cached_dataset

    def get_client_features(self, cliente_id: str) -> CaracteristicasCliente:
        # 1. Intentar llamar al ERP si no estamos forzando modo mock
        if not self.use_mock_fallback:
            try:
                # Ejemplo de llamada real a través del Gateway
                with httpx.Client(timeout=3.0) as client:
                    resp = client.get(f"{settings.erp_gateway_url}/clients/{cliente_id}/churn-features")
                    if resp.status_code == 200:
                        data = resp.json()
                        return CaracteristicasCliente(**data)
            except Exception:
                pass # Caer al modo dataset/mock si la conexión falla

        # 2. Modo fallback con datos locales/sintéticos
        df = self._get_dataset()
        if df is not None and not df.empty:
            client_rows = df[df["client_id"] == cliente_id]
            if not client_rows.empty:
                row = client_rows.iloc[-1]
                return CaracteristicasCliente(
                    cliente_id=cliente_id,
                    membership_type=str(row["membership_type"]),
                    duration_days=int(row["duration_days"]),
                    days_until_expiration=int(row["days_until_expiration"]),
                    previous_renewals_count=int(row["previous_renewals_count"]),
                    client_seniority_days=int(row["client_seniority_days"]),
                    attendances_last_7d=int(row["attendances_last_7d"]),
                    attendances_last_30d=int(row["attendances_last_30d"]),
                    attendances_last_60d=int(row["attendances_last_60d"]),
                    days_since_last_attendance=int(row["days_since_last_attendance"]),
                    weekly_frequency=float(row["weekly_frequency"]),
                    frequency_variation=float(row["frequency_variation"]),
                    attendance_trend=float(row["attendance_trend"]),
                    pct_weeks_without_visit=float(row["pct_weeks_without_visit"]),
                    inactivity_max_days=int(row.get("inactivity_max_days", 5)),
                    routine_compliance_score=float(row.get("routine_compliance_score", 0.6))
                )

        # 3. Datos sintéticos por defecto si el ID es nuevo o de prueba
        return CaracteristicasCliente(
            cliente_id=cliente_id,
            membership_type="Mensual",
            duration_days=30,
            days_until_expiration=random.randint(-15, 25),
            previous_renewals_count=random.randint(0, 5),
            client_seniority_days=random.randint(30, 400),
            attendances_last_7d=random.randint(0, 3),
            attendances_last_30d=random.randint(1, 12),
            attendances_last_60d=random.randint(2, 24),
            days_since_last_attendance=random.randint(1, 20),
            weekly_frequency=round(random.uniform(0.5, 3.5), 2),
            frequency_variation=round(random.uniform(-1.5, 0.5), 2),
            attendance_trend=round(random.uniform(-0.8, 0.3), 2),
            pct_weeks_without_visit=round(random.uniform(0.0, 0.6), 2),
            inactivity_max_days=random.randint(2, 14),
            routine_compliance_score=round(random.uniform(0.3, 0.8), 2)
        )

    def get_eligible_clients(self, limit: int = 100) -> List[str]:
        df = self._get_dataset()
        if df is not None and not df.empty and "client_id" in df.columns:
            return df["client_id"].drop_duplicates().head(limit).tolist()
        return [f"cli-{i:04d}" for i in range(1, limit + 1)]
