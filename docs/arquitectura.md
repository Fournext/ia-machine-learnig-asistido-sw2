# Arquitectura Hexagonal — Motor de Inferencia Stateless

El microservicio `gym-churn-prediction` opera como un **motor de inferencia puramente stateless (sin base de datos)**.
La persistencia y el historial residen en la base de datos principal del ERP.

```mermaid
flowchart TD
    subgraph ERP_Ecosystem ["Ecosistema ERP (Con Base de Datos Propia)"]
        ERP_App[Módulos ERP: Usuarios / Membresías / Asistencias]
        ERP_DB[(Base de Datos Principal del ERP)]
    end

    subgraph Churn_Engine ["gym-churn-prediction (Motor de Inferencia Puro)"]
        direction TB
        subgraph Ports_In ["Puertos de Entrada (Casos de Uso)"]
            UC1[PredecirAbandonoUseCase]
            UC2[PredecirAbandonoBatchUseCase]
            UC3[GestionarModelosUseCase]
        end

        subgraph Domain ["Dominio Puro en Memoria"]
            Entities[Cliente, PrediccionDeAbandono, CaracteristicasCliente]
            VO[NivelRiesgo, UmbralesRiesgo, Probabilidad]
            Services[ClasificadorDeRiesgoService]
        end

        subgraph Ports_Out ["Puertos de Salida (Contratos SPI)"]
            P_Pred[PredictorPort]
            P_Data[ClientDataProviderPort]
            P_Reg[ModelRegistryPort]
        end

        subgraph Adapters_Out ["Adaptadores Secundarios"]
            Scikit[RandomForestPredictorAdapter - model.joblib]
            ERPClient[ErpClientDataProviderAdapter - HTTP / Fallback]
            FileRegistry[FileSystemModelRegistry - artifacts/models]
        end
    end

    ERP_App -->|1. POST /api/v1/predictions (cliente_id o features directas)| UC1
    ERP_App -->|POST /api/v1/predictions/batch| UC2
    UC1 --> Domain
    UC1 --> P_Pred
    UC1 --> P_Data
    P_Pred -.-> Scikit
    P_Data -.-> ERPClient
    P_Reg -.-> FileRegistry

    UC1 -->>|2. Respuesta JSON en memoria| ERP_App
    ERP_App -->|3. El ERP almacena el resultado| ERP_DB
```

## Beneficios del Diseño Stateless
1. **Cero Mantenimiento de Bases de Datos Locales:** No requiere PostgreSQL dedicado ni SQLite.
2. **Consumo Mínimo de Recursos:** La imagen Docker corre con un consumo de memoria insignificante (inferior a 90 MB).
3. **Escalabilidad Horizontal Inmediata:** Se pueden levantar $N$ réplicas del contenedor tras un balanceador de carga sin preocuparse por replicación de datos ni bloqueos de transacciones.
4. **Flexibilidad de Entrada:** El ERP puede enviar únicamente el `cliente_id` (para que el motor consulte los datos) o enviar el objeto `features` completo en el cuerpo del JSON si ya los tiene en memoria.
