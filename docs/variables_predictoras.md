# Variables Predictoras (Feature Engineering)

Todas las variables se calculan de manera estricta utilizando únicamente la información disponible **hasta la fecha de observación** ($T_{obs}$).

| Variable | Tipo | Origen | Descripción | Tratamiento Faltantes |
|---|---|---|---|---|
| `membership_type` | Categórico | Membresías | Tipo de plan (Mensual, Trimestral, Anual) | OneHotEncoder (manejo de desconocidos) |
| `duration_days` | Numérico | Membresías | Duración contractual del plan en días | Imputación por mediana (30) |
| `days_until_expiration` | Numérico | Membresías | Días restantes antes del vencimiento actual | Cero |
| `previous_renewals_count` | Numérico | Membresías | Total de renovaciones exitosas previas | Cero |
| `client_seniority_days` | Numérico | Usuarios | Días de antigüedad desde la primera inscripción | Mediana |
| `attendances_last_7d` | Numérico | Asistencias | Conteo de ingresos en los últimos 7 días | Cero |
| `attendances_last_30d` | Numérico | Asistencias | Conteo de ingresos en los últimos 30 días | Cero |
| `attendances_last_60d` | Numérico | Asistencias | Conteo de ingresos en los últimos 60 días | Cero |
| `days_since_last_attendance`| Numérico | Asistencias | Días transcurridos desde el último acceso | Imputación por 999 días |
| `weekly_frequency` | Numérico | Asistencias | Promedio de visitas semanales en el periodo | Cero |
| `frequency_variation` | Numérico | Asistencias | Diferencia de frecuencia (últimos 30d vs 30-60d) | Cero |
| `attendance_trend` | Numérico | Asistencias | Pendiente / tendencia de visitas (negativo = caída) | Cero |
| `pct_weeks_without_visit` | Numérico | Asistencias | Proporción de semanas del periodo sin asistencia | Cero |
| `inactivity_max_days` | Numérico | Comportamiento| Período contiguo más largo de inactividad | Cero |
| `routine_compliance_score`| Numérico | Entrenamiento | Nivel de completitud de rutinas registradas | Imputación por 0.5 |
