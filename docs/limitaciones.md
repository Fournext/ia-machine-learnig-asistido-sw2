# Limitaciones y Supuestos del Modelo

## 1. Datos Sintéticos vs. Datos de Producción
- El modelo actual fue entrenado y evaluado sobre un dataset sintético calibrado con dinámicas estadísticas realistas de gimnasios (3,600 registros, 30.56% tasa de abandono).
- **Advertencia Obligatoria**: Las métricas reportadas (ROC-AUC 0.8998, Accuracy 86.07%) corresponden al conjunto sintético de prueba. **No deben asumirse como rendimiento garantizado en producción** hasta que el modelo sea reentrenado con datos históricos reales exportados desde el ERP.

## 2. No Causalidad
- El análisis de importancia por permutación identifica correlaciones estadísticas fuertes (ej. caída brusca en `attendance_trend` o `days_since_last_attendance`), pero **no implica causalidad directa**. La inasistencia es un síntoma del desenganche del usuario, no necesariamente la causa raíz (que puede deberse a motivos personales, precio, mudanza o insatisfacción con instalaciones).

## 3. Horizonte Predictivo Fijo
- El modelo actual evalúa una ventana fija de 30 días posteriores al vencimiento de la membresía. Para gimnasios con membresías de pase diario o modalidades por créditos, se recomienda ajustar el horizonte temporal o entrenar un clasificador multietiqueta específico.

## 4. Recomendaciones Administrativas
- Las recomendaciones sugeridas son de carácter orientativo y no invasivo. El ERP no debe enviar comunicaciones invasivas ni ejecutar cobros/cancelaciones sin la confirmación de las reglas administrativas del negocio.
