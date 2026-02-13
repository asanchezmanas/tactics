# Tu Primer Análisis

> Acabas de conectar tus datos. Aquí te explicamos cómo interpretar lo que ves en el Dashboard y dar tus primeros pasos.

---

## ¿Qué veo en el Dashboard?

Al entrar por primera vez, verás tres secciones principales:

### 1. Resumen de Clientes 👥

| Métrica | Qué significa |
|---------|---------------|
| **Clientes totales** | Número de clientes únicos con al menos 1 compra |
| **Valor total proyectado** | Suma de todo lo que se espera que gasten en 12 meses |
| **Clientes en riesgo** | Cuántos muestran señales de abandonarte |

**Acción rápida**: Si ves muchos clientes en riesgo, ve directamente a "Radar de Fuga" para investigar.

### 2. Rendimiento de Canales 💰

| Métrica | Qué significa |
|---------|---------------|
| **Inversión total** | Lo que has gastado en publicidad (si conectaste Meta/Google) |
| **Ventas atribuidas** | Ventas que Tactics atribuye a esa publicidad |
| **ROAS** | Retorno por cada euro invertido (ej: ROAS 3x = 3€ por cada 1€) |
| **POAS** | El beneficio real (Ingreso - Coste Producto) por cada euro invertido. |

**Acción rápida**: Si un canal tiene ROAS < 1, estás perdiendo dinero ahí. Prioriza canales con **alto POAS** incluso si su ROAS parece menor.

### 2.1 Inteligencia 2.0: Más allá de los números 🧠

Tactics no solo te da números, te da **razonamientos**.

*   **Razones de Refuerzo**: En las tarjetas de LTV, verás un texto que explica *por qué* la IA ha ajustado un valor (ej: "Ajustado por patrón de retención positivo"). Lee esto para entender el "instinto" del algoritmo.
*   **Afinidad de Cesta**: Mira qué productos se compran juntos. Si el **Item A** tiene un fuerte vínculo con el **Item B**, crea una oferta combinada.

---

## Paso 0: Interpretando el Sandbox (Diagnóstico Rápido)

Si vienes de subir un CSV en el Sandbox, tu dashboard será una versión simplificada:
1. **Concentración de Pareto**: Si el 20% de tus clientes hace más del 60% de tus ventas, tu negocio es muy dependiente. ¡Cuidado con el riesgo de fuga!
2. **Afinidad de Cesta**: Los primeros pares de productos que veas son tus mejores candidatos para "cross-selling" inmediato.

| Métrica | Qué significa |
|---------|---------------|
| **Top rentables** | Productos que más beneficio generan |
| **Productos con pérdida** | Productos que te cuestan dinero (si tienes costes cargados) |

---

## He visto mis resultados en el Sandbox... ¿ahora qué?

El diagnóstico es solo el principio. Aquí tienes 3 acciones inmediatas que puedes tomar hoy mismo basadas en lo que has visto:

### 1. Activa tu "Afinidad de Cesta" (Cross-selling)
Si Tactics ha detectado que el **Producto A** y el **Producto B** tienen un **Lift > 2.0**:
- **Acción**: Crea un "Bundle" o pack con descuento en tu tienda (ej. Shopify Bundles).
- **Resultado**: Aumento inmediato del Ticket Medio (AOV).

### 2. Protege tu "Pareto" (VIPS en Riesgo)
Si tu **Concentración de Pareto** es alta (>60%) y ves clientes en la zona de riesgo:
- **Acción**: Exporta esa lista de emails y crea una campaña de "Win-back" en Klaviyo o Mailchimp con una oferta que no puedan rechazar.
- **Resultado**: Reducción drástica del Churn y protección de tus ingresos principales.

### 3. Ejecuta el "Corte POAS" (Eficiencia Publicitaria)
Si has visto que un canal tiene un **POAS bajo** comparado con otros:
- **Acción**: Reduce un 15% el presupuesto de ese canal y muévelo al canal con mayor POAS.
- **Resultado**: Más beneficio neto con la misma inversión total.

---

## Las primeras preguntas que deberías hacerte

### 1. "¿Quiénes son mis mejores clientes?"

1. Haz clic en **"Clientes"** en el menú lateral
2. Ordena por la columna **"LTV 12m"** de mayor a menor
3. Los primeros 50-100 son tus VIPs

**¿Qué hago con esto?**
- Exporta esta lista a un Excel
- Crea una campaña de email exclusiva para ellos
- Considera darles acceso anticipado a nuevos productos

### 2. "¿Estoy a punto de perder a alguien importante?"

1. Ve a **"Clientes"** → filtro **"En riesgo"**
2. Ordena por **"LTV"** para priorizar los más valiosos
3. Revisa la columna **"Última compra"**

**¿Qué hago con esto?**
- Envía un email de reactivación con oferta exclusiva
- Si es un cliente muy valioso, considera contacto personal

### 3. "¿Dónde estoy desperdiciando dinero en publicidad?"

1. Ve al **"Optimizador"**
2. Mira el widget de **"ROI por Canal"**
3. Identifica canales con ROAS < 2x

**¿Qué hago con esto?**
- Considera reducir presupuesto en canales saturados
- Usa el Simulador para probar redistribuciones

### 4. "¿Hay productos que me dan pérdidas?"

1. Ve a **"Productos"**
2. Busca productos con indicador rojo 🔴

**¿Qué hago con esto?**
- Revisa si puedes subir el precio
- Considera excluirlos de campañas de publicidad
- En casos extremos, deja de venderlos

---

## Primeros 7 días: Lista de acciones

### Día 1-2: Explorar
- [ ] Revisar el Dashboard principal
- [ ] Identificar tus 10 clientes más valiosos
- [ ] Identificar si hay clientes VIP en riesgo

### Día 3-4: Actuar
- [ ] Enviar email a 3-5 clientes VIP en riesgo
- [ ] Revisar si tienes productos con pérdidas

### Día 5-7: Optimizar
- [ ] Usar el Simulador de Presupuesto para probar escenarios
- [ ] Aplicar una recomendación de distribución de presupuesto
- [ ] Revisar bundles recomendados

---

## Entendiendo los niveles de confianza

Cada predicción en Tactics viene con un **nivel de confianza**:

| Indicador | Significado |
|-----------|-------------|
| 🟢 **Alta confianza** | Muchos datos, predicción muy fiable |
| 🟡 **Confianza media** | Suficientes datos, predicción razonable |
| 🟠 **Confianza baja** | Pocos datos, tomar con cautela |
| ⚪ **Datos insuficientes** | Necesitas más historial |

> **Consejo**: Empieza actuando sobre las predicciones de alta confianza. Las de confianza baja úsalas como referencia, no como verdad absoluta.

---

## Errores comunes de principiante

### ❌ "Voy a contactar a TODOS los clientes en riesgo"

**Mejor**: Empieza con los 10-20 de mayor LTV. Es más manejable y más impactante.

### ❌ "Voy a cambiar todo mi presupuesto de golpe"

**Mejor**: Haz cambios del 10-20% máximo. Mide durante 2 semanas. Ajusta.

### ❌ "Un producto tiene pérdidas, lo elimino ya"

**Mejor**: Investiga primero. A veces un producto con pérdida atrae clientes que compran otros productos rentables.

---

## ¿Qué sigue después de la primera semana?

1. **Establece una rutina**: Revisa Tactics al menos 1x por semana
2. **Mide tus acciones**: Si enviaste emails de rescate, ¿cuántos compraron?
3. **Refina tu estrategia**: A medida que acumules más datos, las predicciones mejoran

---

## Guías relacionadas

- [Valor del Cliente (LTV)](./customer_value.md)
- [Radar de Fuga](./churn_radar.md)
- [Simulador de Presupuesto](./budget_simulator.md)

---

**¿Dudas?** soporte@tactics.es
