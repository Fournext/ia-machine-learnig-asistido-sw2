import subprocess
import sys
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from typing import List, Dict, Any
from churn_prediction.presentation.schemas import (
    ModelVersionResponseSchema,
    ModelTrainRequestSchema
)
from churn_prediction.presentation.dependencies import get_gestionar_modelos_use_case
from churn_prediction.application.use_cases.gestionar_modelos import GestionarModelosUseCase
from churn_prediction.domain.exceptions import ModeloNoDisponibleException

router = APIRouter(prefix="/models", tags=["Gestión de Modelos de ML"])

def _run_training_subprocess(dataset_path: str, version: str):
    cmd = [sys.executable, "scripts/train_and_evaluate.py"]
    subprocess.run(cmd, check=False)

@router.get("", response_model=List[ModelVersionResponseSchema])
def listar_versiones_modelos(
    use_case: GestionarModelosUseCase = Depends(get_gestionar_modelos_use_case)
):
    """Lista todas las versiones registradas del modelo Random Forest."""
    modelos = use_case.listar_modelos()
    return [
        ModelVersionResponseSchema(
            id=m.id,
            version=m.version,
            algoritmo=m.algoritmo,
            fecha_entrenamiento=m.fecha_entrenamiento.isoformat(),
            metricas=m.metricas,
            activa=m.activa,
            ruta_artefacto=m.ruta_artefacto,
            sha256_hash=m.sha256_hash
        )
        for m in modelos
    ]

@router.get("/active", response_model=ModelVersionResponseSchema)
def obtener_modelo_activo(
    use_case: GestionarModelosUseCase = Depends(get_gestionar_modelos_use_case)
):
    """Consulta la versión activa actual en producción."""
    modelo = use_case.obtener_modelo_activo()
    if not modelo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay modelo activo registrado")
    return ModelVersionResponseSchema(
        id=modelo.id,
        version=modelo.version,
        algoritmo=modelo.algoritmo,
        fecha_entrenamiento=modelo.fecha_entrenamiento.isoformat(),
        metricas=modelo.metricas,
        activa=modelo.activa,
        ruta_artefacto=modelo.ruta_artefacto,
        sha256_hash=modelo.sha256_hash
    )

@router.get("/{version}/metrics", response_model=Dict[str, Any])
def obtener_metricas_modelo(
    version: str,
    use_case: GestionarModelosUseCase = Depends(get_gestionar_modelos_use_case)
):
    """Retorna las métricas detalladas de evaluación de una versión específica (ROC-AUC, PR-AUC, etc.)."""
    try:
        return use_case.obtener_metricas(version)
    except ModeloNoDisponibleException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/{version}/activate", status_code=status.HTTP_200_OK)
def activar_version_modelo(
    version: str,
    use_case: GestionarModelosUseCase = Depends(get_gestionar_modelos_use_case)
):
    """Activa de forma controlada una versión específica para inferencia."""
    try:
        use_case.activar_modelo(version)
        return {"status": "success", "message": f"Modelo versión '{version}' activado exitosamente."}
    except ModeloNoDisponibleException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/train", status_code=status.HTTP_202_ACCEPTED)
def iniciar_entrenamiento_asincrono(
    req: ModelTrainRequestSchema,
    background_tasks: BackgroundTasks
):
    """
    Inicia un trabajo de reentrenamiento del modelo Random Forest en segundo plano (asíncrono).
    No bloquea la solicitud HTTP mientras se entrena.
    """
    background_tasks.add_task(_run_training_subprocess, req.dataset_path, req.version)
    return {
        "status": "accepted",
        "message": f"Entrenamiento para la versión '{req.version}' iniciado asíncronamente en segundo plano."
    }
