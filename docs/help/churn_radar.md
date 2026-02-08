# Radar de Fuga (Churn)

> Detecta qué clientes están a punto de abandonarte ANTES de que lo hagan, para que puedas actuar a tiempo.

---

## ¿Qué es el Radar de Fuga?

El **Radar de Fuga** es un sistema que analiza el comportamiento de tus clientes y detecta señales de que podrían estar dejando de comprarte.

A diferencia de esperar a que un cliente "desaparezca", Tactics te avisa cuando todavía estás a tiempo de recuperarlo.

---

## ¿Cómo funciona?

Tactics calcula una **Probabilidad de Actividad** para cada cliente:

| Probabilidad | Significado |
|--------------|-------------|
| 90-100% | Está activo, comprando regularmente |
| 70-89% | Activo, pero podría comprar más |
| 40-69% | En observación, comportamiento irregular |
| 20-39% | ⚠️ **En riesgo** — señales de abandono |
| 0-19% | Probablemente perdido |

### ¿Qué señales detectamos?

1. **Cambio en la frecuencia**: Si antes compraba cada mes y ahora no compra hace 3 meses
2. **Patrón respecto a su historial**: Un cliente que siempre tardaba 30 días entre compras y ahora lleva 60
3. **Comparación con clientes similares**: Si otros clientes como él compran y él no

---

## El caso más importante: VIP en Riesgo

La combinación más crítica es:
- **Alto LTV** (cliente valioso)
- **Baja probabilidad de actividad** (señales de abandono)

Estos son tus **"VIP en Riesgo"** — clientes que valen mucho pero que podrías perder.

### Ejemplo:

| Cliente | LTV | Prob. Actividad | Estado |
|---------|-----|-----------------|--------|
| Ana | 450€ | 25% | 🚨 **VIP EN RIESGO** |
| Carlos | 50€ | 20% | Bajo valor, baja prioridad |
| María | 300€ | 85% | VIP activa, todo bien |

**Ana** debería ser tu prioridad #1 para campañas de recuperación.

---

## ¿Dónde lo veo?

### En el Dashboard:
- **Widget "Clientes en Riesgo"**: Número total y valor en juego
- **Alerta roja** si hay VIPs en riesgo

### En la vista de Clientes:
- Columna **"Prob. Activo"** con indicador visual (verde/amarillo/rojo)
- Filtro **"En riesgo"** para ver solo estos clientes
- Pestaña especial **"VIPs en Riesgo"** con acciones recomendadas

---

## ¿Qué hago con los clientes en riesgo?

### Opción 1: Campaña de email personalizado

1. Filtra clientes con Prob. Activo < 40%
2. Exporta la lista a CSV
3. Sube a tu herramienta de email (Klaviyo, Mailchimp)
4. Envía un mensaje tipo:
   - "Te echamos de menos"
   - Oferta exclusiva de reactivación
   - Recordatorio de productos favoritos

### Opción 2: Exportar a Meta Ads

1. Ve a la lista de clientes en riesgo
2. Haz clic en **"Exportar a Meta"**
3. Tactics creará una audiencia personalizada en tu cuenta de Meta Ads
4. Lanza una campaña de remarketing específica para ellos

### Opción 3: Llamada personal (para clientes de muy alto valor)

Para clientes con LTV > 500€ (por ejemplo):
- Considera una llamada personal o mensaje de WhatsApp
- Un gesto personal puede marcar la diferencia

---

## Interpretando las alertas

| Alerta en Dashboard | Significado | Urgencia |
|---------------------|-------------|----------|
| "5 VIPs en riesgo" | 5 clientes valiosos muestran señales de abandono | 🔴 Alta — actúa esta semana |
| "Valor en riesgo: 2,500€" | El LTV combinado de clientes en riesgo | Cuantifica lo que podrías perder |
| "3 clientes rescatados" | Clientes que estaban en riesgo y volvieron a comprar | ✅ Tu campaña funcionó |

---

## Casos de éxito típicos

### Caso 1: Email de recuperación
- **Situación**: 50 clientes VIP en riesgo
- **Acción**: Email con 15% de descuento exclusivo
- **Resultado**: 12 clientes volvieron a comprar (24% de conversión)
- **Valor recuperado**: ~1,800€ en pedidos inmediatos + LTV futuro

### Caso 2: Remarketing en Meta
- **Situación**: 200 clientes en riesgo (todos los niveles)
- **Acción**: Campaña de remarketing con inversión de 150€
- **Resultado**: 18 compras, valor de 1,200€
- **ROAS**: 8x (1,200€ / 150€)

---

## Preguntas frecuentes

### "¿Cuándo se considera que un cliente está perdido?"

Cuando su probabilidad de actividad baja del 10% y no ha comprado en más de 6x su frecuencia habitual. Ejemplo: si solía comprar cada 2 meses y han pasado 12+ meses.

### "¿Por qué un cliente que compró hace 2 meses aparece en riesgo?"

Porque Tactics compara con su propio historial. Si ese cliente solía comprar cada 3 semanas, 2 meses es mucho para él aunque parezca reciente.

### "¿Puedo marcar clientes como 'recuperados' manualmente?"

No es necesario. Tactics detecta automáticamente cuando un cliente en riesgo vuelve a comprar y actualiza su estado.

### "¿Funciona para negocios con ciclos de compra largos?"

Sí. Tactics aprende los patrones de tu negocio. Si tus clientes compran cada 6 meses (ej: muebles), un cliente que lleva 9 meses sin comprar aparecerá en riesgo.

---

## Buenas prácticas

1. **Revisa el Radar semanalmente**: No dejes que los clientes en riesgo se acumulen
2. **Prioriza por LTV**: Enfócate primero en los clientes más valiosos
3. **Actúa rápido**: Cuanto antes contactes a un cliente en riesgo, más probable recuperarlo
4. **Mide resultados**: Compara cuántos clientes rescataste vs. cuántos perdiste

---

## Métricas relacionadas

| Métrica | Descripción |
|---------|-------------|
| **Tasa de Churn** | % de clientes perdidos en un periodo |
| **Clientes rescatados** | Clientes en riesgo que volvieron a comprar |
| **Valor en riesgo** | LTV total de clientes con probabilidad < 40% |

---

## Siguiente paso

→ [Segmentación Automática](./segmentation.md) — Grupos de clientes creados automáticamente

---

**¿Dudas?** soporte@tactics.es
