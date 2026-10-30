import os
import json
from datetime import datetime
from typing import List, Optional
from churn_prediction.application.ports import ModelRegistryPort
from churn_prediction.domain.entities import VersionDeModelo
from churn_prediction.infrastructure.config.settings import settings

class FileSystemModelRegistry(ModelRegistryPort):
    """
    Implementación basada en sistema de archivos del ModelRegistryPort.
    No requiere base de datos relacional; lee y valida artefactos directamente en disco.
    """
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or settings.model_artifacts_dir
        self.active_version = settings.active_model_version
        self._resolve_base_dir()

    def _resolve_base_dir(self):
        candidate_paths = [
            self.base_dir,
            os.path.join("gym-churn-prediction", self.base_dir),
            os.path.join(os.getcwd(), "gym-churn-prediction", self.base_dir),
            os.path.join(os.getcwd(), self.base_dir)
        ]
        for p in candidate_paths:
            if os.path.exists(p):
                self.base_dir = p
                break

    def get_active_model_version(self) -> Optional[VersionDeModelo]:
        return self.get_model_version(self.active_version)

    def get_model_version(self, version: str) -> Optional[VersionDeModelo]:
        clean_version = version.lstrip("v")
        version_dirs = [f"v{clean_version}", clean_version]

        for vd in version_dirs:
            folder = os.path.join(self.base_dir, vd)
            meta_path = os.path.join(folder, "metadata.json")
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    artifact_path = os.path.join(folder, "model.joblib")
                    is_active = (clean_version == self.active_version.lstrip("v"))

                    return VersionDeModelo(
                        id=f"ver-{clean_version}",
                        version=clean_version,
                        algoritmo="RandomForestClassifier (Calibrated)",
                        fecha_entrenamiento=datetime.fromisoformat(data.get("created_at", datetime.utcnow().isoformat())),
                        metricas=data.get("metrics", {}),
                        activa=is_active,
                        ruta_artefacto=artifact_path if os.path.exists(artifact_path) else None,
                        sha256_hash=data.get("sha256")
                    )
                except Exception:
                    pass
        return None

    def list_models(self) -> List[VersionDeModelo]:
        modelos = []
        if not os.path.exists(self.base_dir):
            return modelos

        for item in os.listdir(self.base_dir):
            folder = os.path.join(self.base_dir, item)
            if os.path.isdir(folder):
                v_model = self.get_model_version(item)
                if v_model:
                    modelos.append(v_model)
        return modelos

    def activate_model(self, version: str) -> bool:
        clean_version = version.lstrip("v")
        v_model = self.get_model_version(clean_version)
        if not v_model:
            return False
        self.active_version = clean_version
        return True
