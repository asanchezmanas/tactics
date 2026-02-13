# Protocolo de Integridad y Trazabilidad de Datos

## Introducción
Este documento define los estándares y procedimientos para asegurar la veracidad, transparencia y trazabilidad de los datos ingeridos por la plataforma Tactics. En un entorno de Inteligencia 2.0, la calidad del dato es tan crítica como la del algoritmo.

## 1. Principios de Integridad
- **Soberanía del Dato**: Tactics no modifica los datos del cliente (ej. imputación automática de medias) sin su consentimiento explícito y visualización clara.
- **Transparencia Radical**: Cualquier anomalía detectada por el sistema debe ser reportada al usuario con su origen y causa probable.
- **Auditabilidad**: Cada registro debe ser rastreable hasta su lote de origen (Batch ID).

## 2. Capas de Protección

### Capa A: Ingestion Audit (api/ingestion_audit.py)
Captura metadatos en el momento de la carga:
- **Batch ID**: Identificador único por subida.
- **Row Count Audit**: Verificación de filas leídas vs. filas insertadas.
- **Checksum**: Hash del archivo original para detectar manipulaciones o subidas duplicadas.

### Capa B: Integrity Guard (core/integrity_guard.py)
Detección profunda post-ingesta:
- **Detección de Duplicados**: Identificación de colisiones basadas en `logic_key` (ej. `timestamp + customer_id + amount`).
- **Gap Analysis**: Identificación de discontinuidades temporales en datos de series temporales (ej. días sin gasto publicitario).

## 3. Visualización de la Trazabilidad (UI)
- **Traceability Matrix**: Una vista que correlaciona lotes de importación con el estado actual de la base de datos.
- **Shadow Zones**: Los periodos de tiempo con datos corruptos o faltantes se marcan visualmente en los dashboards para alertar de una posible reducción en la confianza de la predicción.

## 4. Respuesta Algorítmica (Robustez)
Los algoritmos (LTV, MMM) deben:
1. Detectar la presencia de datos de baja calidad.
2. Ajustar los intervalos de confianza (uncertainty propagation).
3. Emitir un aviso en los metadatos de la predicción explicando por qué la confianza es X%.
