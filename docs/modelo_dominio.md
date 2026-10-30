# Modelo de Dominio

El modelo de dominio contiene las entidades, objetos de valor y reglas esenciales de predicción de abandono.

## Entidades Principales
- **`Cliente`**: Identidad del cliente en el ERP (`id`, `nombre`, `email`, `activo`).
- **`CaracteristicasCliente`**: Vector de atributos predictivos procesados hasta la fecha de observación.
- **`PrediccionDeAbandono`**: Resultado persistible de una inferencia (`id`, `cliente_id`, `probabilidad_abandono`, `nivel_riesgo`, `factores_relevantes`, `recomendaciones`, `fecha_prediccion`).
- **`VersionDeModelo`**: Registro de ciclo de vida del modelo (`version`, `algoritmo`, `fecha_entrenamiento`, `metricas`, `activa`).

## Objetos de Valor
- **`Probabilidad`**: Float inmutable verificado en el intervalo `[0.0, 1.0]`.
- **`NivelRiesgo`**: Enum (`BAJO`, `MEDIO`, `ALTO`).
- **`UmbralesRiesgo`**: Regla de corte (`bajo < 0.30`, `0.30 <= medio < 0.70`, `alto >= 0.70`).

## Servicios de Dominio
- **`ClasificadorDeRiesgoService`**: Asigna el nivel de riesgo según los umbrales configurados y genera recomendaciones no invasivas basadas en reglas de negocio auditables.
