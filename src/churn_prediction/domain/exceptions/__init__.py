class DomainException(Exception):
    """Excepción base del dominio de predicción de abandono."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class ClienteNoEncontradoException(DomainException):
    """Lanzada cuando un cliente solicitado no existe en el sistema."""
    def __init__(self, cliente_id: str):
        super().__init__(f"No se encontró el cliente con ID: {cliente_id}")
        self.cliente_id = cliente_id

class ModeloNoDisponibleException(DomainException):
    """Lanzada cuando no hay ningún modelo entrenado o activo para realizar inferencias."""
    def __init__(self, version: str = None):
        msg = f"El modelo versión '{version}' no está disponible o no ha sido entrenado." if version else "No hay ningún modelo activo cargado en el sistema."
        super().__init__(msg)
        self.version = version

class DatosInsuficientesException(DomainException):
    """Lanzada cuando las características del cliente no son suficientes para predecir con fiabilidad."""
    def __init__(self, cliente_id: str, detalle: str):
        super().__init__(f"Datos insuficientes para el cliente {cliente_id}: {detalle}")
        self.cliente_id = cliente_id
        self.detalle = detalle

class PrediccionInvalidaException(DomainException):
    """Lanzada cuando la predicción o sus parámetros no cumplen las reglas de negocio."""
    pass
