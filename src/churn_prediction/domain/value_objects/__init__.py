from enum import Enum
from dataclasses import dataclass
from typing import Optional

class NivelRiesgo(str, Enum):
    BAJO = "BAJO"
    MEDIO = "MEDIO"
    ALTO = "ALTO"

class TipoMembresia(str, Enum):
    MENSUAL = "Mensual"
    TRIMESTRAL = "Trimestral"
    ANUAL = "Anual"

@dataclass(frozen=True)
class Probabilidad:
    valor: float

    def __post_init__(self):
        if not (0.0 <= self.valor <= 1.0):
            raise ValueError(f"La probabilidad debe estar entre 0.0 y 1.0, recibido: {self.valor}")

@dataclass(frozen=True)
class UmbralesRiesgo:
    umbral_bajo_max: float = 0.30
    umbral_medio_max: float = 0.70

    def clasificar(self, probabilidad: float) -> NivelRiesgo:
        if probabilidad < self.umbral_bajo_max:
            return NivelRiesgo.BAJO
        elif probabilidad < self.umbral_medio_max:
            return NivelRiesgo.MEDIO
        else:
            return NivelRiesgo.ALTO
