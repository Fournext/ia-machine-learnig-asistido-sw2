from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from churn_prediction.presentation.schemas import (
    PredictionRequestSchema,
    PredictionResponseSchema,
    BatchPredictionRequestSchema,
    BatchPredictionResponseSchema
)
from churn_prediction.presentation.dependencies import (
    get_predict_use_case,
    get_batch_predict_use_case
)
from churn_prediction.application.use_cases.predecir_abandono import PredecirAbandonoUseCase
from churn_prediction.application.use_cases.predecir_abandono_batch import PredecirAbandonoBatchUseCase
from churn_prediction.application.dto import PredictionRequestDTO, BatchPredictionRequestDTO
from churn_prediction.domain.entities import CaracteristicasCliente
from churn_prediction.domain.exceptions import (
    ClienteNoEncontradoException,
    ModeloNoDisponibleException,
    DatosInsuficientesException
)

router = APIRouter(tags=["Motor de Inferencia de Abandono"])

@router.post("/predictions", response_model=PredictionResponseSchema, status_code=status.HTTP_200_OK)
def predecir_cliente_individual(
    req: PredictionRequestSchema,
    use_case: PredecirAbandonoUseCase = Depends(get_predict_use_case)
):
    """
    Motor de cálculo: calcula en memoria la probabilidad de abandono para un cliente.
    Admite:
    1. Enviar 'cliente_id' (el microservicio consulta los datos al ERP).
    2. O enviar directamente el objeto 'features' si el ERP ya los tiene calculados en memoria.
    No persiste datos: el ERP es el encargado de almacenar la respuesta.
    """
    try:
        domain_features = None
        if req.features:
            f_dict = req.features.model_dump()
            domain_features = CaracteristicasCliente(**f_dict)

        dto = PredictionRequestDTO(
            cliente_id=req.cliente_id,
            features=domain_features,
            horizonte_dias=req.horizonte_dias
        )
        res = use_case.execute(dto)
        return PredictionResponseSchema(**res.__dict__)
    except ClienteNoEncontradoException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatosInsuficientesException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ModeloNoDisponibleException as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en inferencia: {str(e)}")

@router.post("/predictions/batch", response_model=BatchPredictionResponseSchema, status_code=status.HTTP_200_OK)
def predecir_por_lote(
    req: BatchPredictionRequestSchema,
    use_case: PredecirAbandonoBatchUseCase = Depends(get_batch_predict_use_case)
):
    """
    Calcula predicciones de abandono por lote en memoria de forma stateless.
    Retorna la lista de evaluaciones calculadas para que el ERP las guarde.
    """
    try:
        domain_features_list = None
        if req.features_list:
            domain_features_list = [
                CaracteristicasCliente(**f.model_dump()) for f in req.features_list
            ]

        dto = BatchPredictionRequestDTO(
            clientes_ids=req.clientes_ids,
            features_list=domain_features_list,
            limite=req.limite,
            horizonte_dias=req.horizonte_dias
        )
        res = use_case.execute(dto)
        return BatchPredictionResponseSchema(
            total_procesados=res.total_procesados,
            predicciones=[PredictionResponseSchema(**p.__dict__) for p in res.predicciones]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en inferencia por lotes: {str(e)}")
