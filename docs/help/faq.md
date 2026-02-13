# Preguntas Frecuentes (FAQ)

> Respuestas rápidas a las dudas más comunes sobre Tactics.

---

## Sobre los datos y la privacidad

### ¿Mis datos están seguros?
**Sí.** Utilizamos cifrado de nivel bancario (AES-256) tanto en tránsito como en reposo. Tus datos están completamente aislados de otros clientes. Nunca compartimos información con terceros.

### ¿Tactics accede a mis datos bancarios?
**No.** Solo leemos datos de pedidos, clientes y productos. Nunca accedemos a información de pago, contraseñas ni datos fiscales.

### ¿Pueden ver mis datos otros clientes de Tactics?
**No.** Cada cuenta está completamente separada. Tus datos nunca se mezclan ni se comparten. Es como si tuvieras tu propia instancia privada.

### ¿Qué pasa si cancelo mi suscripción?
Tus datos se conservan durante 30 días después de la cancelación. Si vuelves en ese plazo, todo estará como lo dejaste. Después de 30 días, los datos se eliminan permanentemente.

---

## Sobre la conexión de datos

### ¿Cuánto tarda la primera sincronización?
Depende del volumen de datos:
- Tiendas pequeñas (< 5,000 pedidos): 10-30 minutos
- Tiendas medianas (5,000-50,000 pedidos): 1-3 horas
- Tiendas grandes (> 50,000 pedidos): hasta 24 horas

### ¿Con qué frecuencia se actualizan los datos?
Automáticamente cada 24 horas. Puedes forzar una sincronización manual desde "Integraciones" si necesitas datos más recientes.

### ¿Funciona con WooCommerce además de Shopify?
Sí. Soportamos Shopify, WooCommerce, y estamos añadiendo más plataformas constantemente. Consulta la lista actualizada en Integraciones.

### ¿Necesito instalar algo en mi tienda?
No. La conexión es vía API, no requiere instalar plugins ni código en tu tienda. Es una autorización estándar de OAuth.

---

## Sobre los análisis

### ¿Cuánto historial necesito para que funcione?
Mínimo 3 meses. Cuanto más historial, mejor:
- 3-6 meses: Análisis básico
- 6-12 meses: Buena precisión
- +12 meses: Máxima precisión, incluyendo estacionalidad

### ¿Las predicciones son 100% precisas?
No, y nadie puede garantizar eso. Lo que sí garantizamos es que son **mucho mejores que la intuición** y se basan en análisis riguroso de tus datos. Mostramos rangos de confianza para que sepas qué tan seguro es cada número.

### ¿Puedo ver las fórmulas que usan?
No mostramos las fórmulas internas porque son propiedad de Tactics. Lo que sí mostramos es el resultado, el nivel de confianza, y los factores que más influyen en cada predicción.

### ¿Funciona para negocios B2B?
Sí, aunque está optimizado para ecommerce B2C. Los conceptos de valor del cliente y optimización de presupuesto aplican igual.

---

## Preguntas sobre Inteligencia 2.0 🧠

### ¿Cuál es la diferencia entre ROAS y POAS?
El **ROAS** mide ingresos brutos, mientras que el **POAS** mide beneficio neto después de descontar el coste de tus productos (COGS). En Tactics priorizamos el POAS porque es el que realmente te dice cuánto dinero estás ganando.

### ¿Mis datos se guardan al usar el Sandbox?
**No.** El Sandbox es una zona de diagnóstico 100% en memoria. 
- **Purga Inmediata**: Los datos se eliminan en cuanto cierras la pestaña.
- **Sin Entrenamiento**: No usamos tus datos del Sandbox para mejorar modelos de otros clientes. **Tus datos son tuyos.**
- **GDPR Ready**: Cumplimos con los estándares europeos de privacidad. No procesamos PII (emails/nombres) en este paso; solo usamos identificadores para medir frecuencia.

### ¿Qué son las "Razones de Refuerzo"?
Son notas explicativas generadas por la IA para que no tengas que adivinar por qué un número ha subido o bajado. Tactics explica su "juicio" para que tú mantengas siempre el control final.

---

## Solución de Problemas (CSV Sandbox) 🛠️

### ¿Por qué falló mi subida de CSV?
Si el sistema arroja un error, suele ser por uno de estos 3 motivos:
1. **Pocas filas**: Necesitamos al menos 20 transacciones para que el análisis tenga sentido estadístico.
2. **Formato de archivo**: Asegúrate de que los decimales usen el punto (`.`) y no la coma (`,`), y que el delimitador sea la coma o el punto y coma.
3. **Encoding (Codificación)**: Si tu archivo tiene caracteres extraños, intenta guardarlo como **"CSV (UTF-8)"** desde Excel o Google Sheets.

### "Mi archivo tiene 100 columnas, ¿tengo que limpiarlo?"
No. Tactics ignorará todo lo que no sea necesario. Sube el archivo tal cual sale de tu CMS o ERP.

---

## Sobre las predicciones de clientes (LTV/Churn)

### ¿Por qué el LTV de un cliente cambió?
El LTV se recalcula diariamente. Si un cliente no compra, su predicción de valor futuro baja. Si compra, sube. Es dinámico, no estático.

### ¿Cómo sé si un cliente está realmente "en riesgo"?
Analizamos su comportamiento respecto a su propio historial AND respecto a clientes similares. Si normalmente compra cada 4 semanas y han pasado 8, es señal de riesgo.

### ¿Puedo exportar segmentos a Meta Ads?
Sí. Puedes crear audiencias personalizadas directamente desde Tactics. Ve a Clientes → selecciona un segmento → "Exportar a Meta".

---

## Sobre el Optimizador de Presupuesto

### ¿Necesito conectar todas mis plataformas de publicidad?
No. Funciona con lo que tengas. Si solo usas Meta, conecta solo Meta. Las recomendaciones se adaptarán.

### ¿Tactics modifica mis campañas automáticamente?
**No.** Solo te da recomendaciones. Tú decides si aplicarlas manualmente en Meta/Google. Nunca hacemos cambios en tus cuentas publicitarias.

### ¿Funciona si gasto poco en publicidad?
Sí, aunque las predicciones son más fiables con más datos. Con menos de 500€/mes de inversión, las recomendaciones serán más generales.

---

## Sobre precios y facturación

### ¿Puedo cambiar de plan?
Sí, en cualquier momento desde Configuración → Suscripción. Los cambios se aplican en el siguiente ciclo de facturación.

### ¿Ofrecen periodo de prueba?
Sí. 14 días de prueba gratuita con acceso completo. No pedimos tarjeta hasta que termines la prueba.

### ¿Hay descuento por pago anual?
Sí. Ofrecemos 2 meses gratis (equivalente a ~16% de descuento) al pagar anualmente.

### ¿Puedo cancelar cuando quiera?
Sí. Sin permanencia ni penalizaciones. Cancela desde Configuración y mantendrás el acceso hasta el final del periodo pagado.

---

## Soporte

### ¿Cómo contacto con soporte?
- **Email**: soporte@tactics.es (respuesta en < 24h laborables)
- **Chat en vivo**: Disponible L-V, 9:00-18:00 CET
- **Base de conocimiento**: Este Centro de Ayuda

### ¿Ofrecen formación o llamadas de onboarding?
En los planes Agency y Enterprise sí. Para otros planes, esta documentación está diseñada para que no necesites formación adicional.

### ¿En qué idiomas está disponible?
Español e inglés. Estamos añadiendo más idiomas próximamente.

---

## ¿No encuentras tu pregunta?

Escríbenos a **soporte@tactics.es** y te responderemos en menos de 24 horas.

---

*Última actualización: Febrero 2026 - Tactics Intelligence 2.0*
