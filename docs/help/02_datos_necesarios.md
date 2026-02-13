# ¿Qué Datos Necesita Tactics?

> Esta guía te explica exactamente qué información utiliza Tactics y cómo afecta a la calidad de tus análisis.

---

## Resumen rápido

| Fuente | ¿Obligatorio? | ¿Para qué se usa? |
|--------|---------------|-------------------|
| Tienda (Shopify/WooCommerce) | ✅ Sí | Todo el análisis de clientes y productos |
| Meta Ads | ⚪ Recomendado | Optimización de presupuesto publicitario |
| Google Ads | ⚪ Opcional | Optimización de presupuesto publicitario |
| Costes de producto | ⚪ Opcional | Análisis de rentabilidad real |

---

## Datos de tu tienda (OBLIGATORIO)

Tactics necesita conectarse a tu tienda para funcionar. De aquí extraemos:

### 📦 Historial de pedidos

| Dato | Ejemplo | ¿Para qué? |
|------|---------|------------|
| Número de pedido | #1234 | Identificar transacciones únicas |
| Fecha del pedido | 15 enero 2024 | Analizar patrones de compra |
| Importe total | 75,50€ | Calcular valor por cliente |
| Email del cliente | cliente@email.com | Identificar clientes únicos |
| Productos comprados | Camiseta XL, Pantalón M | Análisis de cestas y bundles |

### 👥 Información de clientes

| Dato | Ejemplo | ¿Para qué? |
|------|---------|------------|
| Email | cliente@email.com | Identificador único |
| Fecha de registro | 10 marzo 2023 | Antigüedad del cliente |
| País/Ciudad | España, Madrid | Segmentación geográfica |
| Total gastado | 450€ | Clasificación por valor |

### 🛍️ Catálogo de productos

| Dato | Ejemplo | ¿Para qué? |
|------|---------|------------|
| Nombre del producto | Camiseta Premium | Identificación |
| Precio de venta | 29,90€ | Cálculos de ingresos |
| Coste (si disponible) | 8,50€ | Análisis de margen |
| Inventario | 45 unidades | Alertas de stock |

> **Nota sobre privacidad**: Tactics solo lee los datos necesarios. Nunca accedemos a contraseñas, datos bancarios, ni información personal sensible.

---

## Datos de publicidad (RECOMENDADO)

Si conectas tus plataformas de publicidad, Tactics puede calcular el verdadero retorno de tu inversión.

### Meta Ads (Facebook/Instagram)

| Dato | Ejemplo | ¿Para qué? |
|------|---------|------------|
| Gasto diario | 150€ | Correlacionar inversión con ventas |
| Impresiones | 25,000 | Medir alcance |
| Clics | 450 | Engagement |
| Nombre de campaña | "Rebajas Enero" | Agrupar resultados |

### Google Ads

| Dato | Ejemplo | ¿Para qué? |
|------|---------|------------|
| Gasto diario | 80€ | Correlacionar inversión con ventas |
| Clics | 200 | Tráfico generado |
| Impresiones | 10,000 | Visibilidad |
| Tipo de campaña | Search, Shopping | Diferenciar canales |

> **¿Qué pasa si no conecto publicidad?**  
> El análisis de clientes y productos funcionará perfectamente. Solo no podrás usar el Optimizador de Presupuesto ni ver el ROI por canal.

---

## Datos de costes (OPCIONAL pero valioso)

Para calcular la rentabilidad REAL de cada producto, necesitamos saber cuánto te cuesta.

### Lo que necesitamos:

| Dato | Descripción | Ejemplo |
|------|-------------|---------|
| **Coste del producto (COGS)** | Lo que pagas al proveedor | 8,50€ |
| **Coste de envío** | Tu coste medio por envío | 3,20€ |
| **Coste de almacenaje** | Si aplica, por unidad/mes | 0,15€ |
| **Coste de caducidad** | Para productos perecederos | 5% del valor |

### ¿Cómo proporcionar los costes?

**Opción A: Ya están en tu tienda**  
Si tienes los costes registrados en Shopify (campo "Coste por artículo"), Tactics los detecta automáticamente.

**Opción B: Subir un archivo**  
Puedes subir un Excel o CSV con esta estructura:

| SKU/Código | Coste producto | Coste envío | Coste almacén |
|------------|----------------|-------------|---------------|
| CAM-001 | 8,50€ | 3,20€ | 0,10€ |
| PAN-002 | 12,00€ | 4,50€ | 0,15€ |

**Opción C: Usar estimaciones**  
Si no tienes datos exactos, puedes indicar un porcentaje estimado de margen (ej: "Mi margen medio es del 40%") y Tactics calculará aproximaciones.

> **Sin costes, ¿qué pierdo?**  
> No podrás ver el margen neto por producto ni identificar "productos que pierden dinero". El resto de análisis funciona normalmente.

---

## ¿Cuánto historial necesito?

| Antigüedad de datos | Calidad del análisis |
|---------------------|----------------------|
| ❌ Menos de 3 meses | Insuficiente — espera a tener más datos |
| ⚠️ 3-6 meses | Básico — predicciones con margen de error amplio |
| ✅ 6-12 meses | Bueno — fiable para la mayoría de decisiones |
| ⭐ +12 meses | Excelente — máxima precisión, detecta estacionalidad |

> **Consejo**: Si tienes un negocio con temporadas muy marcadas (moda, decoración navideña, etc.), cuanto más historial tengas, mejor podremos predecir esos patrones.

---

## Calidad de los datos

Tactics te indicará automáticamente si hay problemas con tus datos:

| Alerta | Significado | Solución |
|--------|-------------|----------|
| "Datos insuficientes" | Menos de 3 meses | Espera a acumular más historial |
| "Pedidos sin email" | Clientes anónimos | Configura tu checkout para requerir email |
| "Costes no disponibles" | No hay info de costes | Sube un archivo de costes |
| "Canales sin conectar" | Falta Meta o Google | Conecta en Integraciones |

---

## Inteligencia de Mapeo (Fuzzy Mapping)

Una de las mayores preocupaciones al subir un archivo es: "¿Estará mi CSV en el formato correcto?".

En Tactics Intelligence 2.0, el sistema no busca nombres de columna exactos. Nuestro motor de **Fuzzy Mapping** utiliza lógica semántica para identificar tus datos:

- **Fecha**: Reconocemos `fecha`, `timestamp`, `order_date`, `created_at`, o incluso `día`.
- **Cliente**: Identificamos `email`, `cliente_id`, `user_hash`, o `id_usuario`.
- **Ventas**: Detectamos `monto`, `revenue`, `total`, `precio`, o `subtotal`.

> 💡 **No importa si tu CSV tiene 50 columnas extra**: Tactics ignorará el ruido y extraerá solo lo que necesita. No necesitas limpiar tu archivo antes de subirlo.

---

## Preguntas frecuentes

### "¿Tactics accede a datos bancarios o de tarjetas?"
No. Nunca accedemos a información de pago. Solo leemos datos de pedidos, clientes y productos.

### "¿Pueden ver mis datos otros clientes?"
No. Cada cuenta está completamente aislada. Tus datos nunca se mezclan ni se comparten.

### "¿Qué pasa si elimino un producto de mi tienda?"
Los análisis históricos se mantienen. Solo los nuevos pedidos no incluirán ese producto.

### "¿Con qué frecuencia se actualizan los datos?"
Cada 24 horas automáticamente. Puedes forzar una sincronización manual desde "Integraciones".

---

## Siguiente paso

→ [Tu primer análisis](./03_primer_analisis.md)

---

**¿Dudas?** Escríbenos a soporte@tactics.es
