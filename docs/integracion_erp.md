# Integración con el ERP del Gimnasio

El microservicio se conecta con el ecosistema del ERP sin acoplar bases de datos ni consultar esquemas privados.

```mermaid
graph TD
    ERP_GW[API Gateway ERP] -->|HTTP /clients/{id}/churn-features| Microservice[gym-churn-prediction]
    Microservice --> Users[Microservicio Usuarios]
    Microservice --> Memberships[Microservicio Membresías]
    Microservice --> Attendances[Microservicio Asistencias]
```

## Contratos de Entrada
1. **Módulo de Usuarios**: Identificación del cliente, antigüedad (`client_seniority_days`) y estado activo.
2. **Módulo de Membresías**: Tipo de membresía, duración (`duration_days`), fecha de expiración (`days_until_expiration`) y número de renovaciones previas.
3. **Módulo de Asistencias**: Entradas registradas en torniquetes en las ventanas de 7, 30 y 60 días, así como días desde el último ingreso y tendencias.

El adaptador `ErpClientDataProviderAdapter` implementa fallback automático al modo dataset / demostración cuando los microservicios externos no se encuentran levantados.
