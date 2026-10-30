from typing import List
from churn_prediction.domain.value_objects import NivelRiesgo, UmbralesRiesgo
from churn_prediction.domain.entities import CaracteristicasCliente

class ClasificadorDeRiesgoService:
    """
    Servicio de dominio que clasifica el nivel de riesgo de abandono y
    deriva recomendaciones operativas/administrativas no invasivas.
    """
    def __init__(self, umbrales: UmbralesRiesgo = UmbralesRiesgo()):
        self.umbrales = umbrales

    def clasificar(self, probabilidad: float) -> NivelRiesgo:
        return self.umbrales.clasificar(probabilidad)

    def generar_recomendaciones(
        self,
        nivel_riesgo: NivelRiesgo,
        caracteristicas: CaracteristicasCliente,
        factores: List[str]
    ) -> List[str]:
        recomendaciones = []

        if nivel_riesgo == NivelRiesgo.ALTO:
            recomendaciones.append("Seguimiento y llamada proactiva de cortesía por parte del staff o entrenador.")
            if caracteristicas.days_since_last_attendance > 14:
                recomendaciones.append("Indagar sobre motivos de inasistencia reciente y ofrecer reagendamiento de rutina.")
            if caracteristicas.days_until_expiration <= 10:
                recomendaciones.append("Presentar opciones flexibles de renovación o congelamiento de plan según política.")
        elif nivel_riesgo == NivelRiesgo.MEDIO:
            if caracteristicas.attendance_trend < 0:
                recomendaciones.append("Sugerir revisión de objetivos o prueba de clases grupales para reactivar motivación.")
            if caracteristicas.days_until_expiration <= 15:
                recomendaciones.append("Enviar recordatorio preventivo de fecha de vencimiento vía canal habitual del ERP.")
        else:
            recomendaciones.append("Mantener seguimiento estándar y registrar feedback positivo en próximas visitas.")

        return recomendaciones
