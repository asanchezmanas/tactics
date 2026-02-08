# Valor del Cliente (LTV)

> Entiende cuánto vale cada cliente a largo plazo y toma decisiones basadas en su valor futuro, no solo en su última compra.

---

## ¿Qué es el Valor del Cliente?

El **Valor del Cliente** (también llamado LTV o "Customer Lifetime Value") es una predicción de cuánto dinero te generará un cliente durante su relación contigo.

### Ejemplo simple:

| Cliente | Última compra | LTV Predicho |
|---------|---------------|--------------|
| María | 25€ hace 2 días | **320€** (comprará 12 veces más) |
| Pedro | 150€ hace 8 meses | **150€** (probablemente no volverá) |

María gastó menos recientemente, pero **vale más a largo plazo** porque su patrón de compra indica que seguirá comprando.

---

## ¿Cómo lo calcula Tactics?

Analizamos tres factores clave de cada cliente:

1. **Frecuencia**: ¿Cada cuánto compra?
2. **Recencia**: ¿Cuándo fue su última compra?
3. **Valor**: ¿Cuánto gasta en promedio?

Con esta información, Tactics predice:
- ¿Cuántas veces comprará en los próximos 12 meses?
- ¿Cuánto gastará en cada compra?
- **Total esperado** = Visitas futuras × Gasto promedio

> **Nivel de confianza**: Cada predicción incluye un rango (ejemplo: "280€ - 360€") que indica la certeza del análisis. Rangos más estrechos = mayor confianza.

---

## ¿Dónde lo veo?

### En el Dashboard principal:
- **Widget "Valor Total del Cliente Base"**: Suma de todos los LTVs predichos
- **Gráfico de distribución**: Cuántos clientes hay en cada rango de valor

### En la vista de Clientes:
- Columna **"LTV 12 meses"** junto a cada cliente
- Filtros para ver solo clientes de alto/medio/bajo valor
- Ordenar por LTV para ver tus clientes más valiosos

---

## ¿Cómo interpreto los números?

### Clasificación automática:

| Etiqueta | Significado | Acción recomendada |
|----------|-------------|-------------------|
| 🐋 **Ballena** | LTV muy alto (top 10%) | Proteger, premiar fidelidad |
| ⭐ **VIP** | LTV alto (top 25%) | Campañas exclusivas |
| 👤 **Estándar** | LTV medio | Estrategia general |
| 🔻 **Bajo valor** | LTV bajo | No invertir demasiado |

### Ejemplo práctico:

Si tienes 1,000 clientes con un LTV medio de 80€:
- **Valor total proyectado**: 80,000€ en los próximos 12 meses
- **Top 100 clientes** (ballenas): Probablemente representen 30-40% de ese valor
- **Conclusión**: Enfoca tus esfuerzos en retener a esos 100

---

## Casos de uso

### 1. Decidir cuánto gastar en adquirir clientes

Si tu LTV medio es 80€ y tu margen es 40%, tu beneficio por cliente es 32€.

**Regla**: No gastes más de 25-30€ en adquirir un cliente nuevo, o perderás dinero.

### 2. Identificar a tus mejores clientes

Exporta la lista de clientes con LTV > 200€ (por ejemplo) y:
- Crea una audiencia similar en Meta Ads para encontrar más como ellos
- Envíales emails exclusivos con ofertas VIP
- Prioriza su atención al cliente

### 3. Calcular el valor de una campaña

Si una campaña trajo 50 clientes nuevos:
- No mires solo el revenue inmediato
- Mira el **LTV total**: 50 clientes × 80€ LTV = 4,000€ de valor a largo plazo
- Compara con el coste de la campaña

---

## Preguntas frecuentes

### "¿Por qué el LTV de un cliente bajó respecto al mes pasado?"

El LTV se recalcula cada día con nuevos datos. Si un cliente no ha comprado en un tiempo, su LTV ajustado baja porque la predicción de que vuelva a comprar disminuye.

### "¿Puedo ver el LTV de clientes nuevos?"

Los clientes con solo 1 compra tienen un LTV estimado basado en el comportamiento típico de tu base. Es menos preciso que para clientes con historial, por eso mostramos un rango más amplio.

### "¿El LTV incluye el gasto pasado?"

No. El LTV es una **predicción futura**. Si necesitas el gasto total (pasado + futuro), suma la columna "Total gastado" + "LTV 12m".

### "¿Cómo puedo aumentar el LTV de mis clientes?"

- **Aumenta la frecuencia**: Emails de recordatorio, programas de suscripción
- **Aumenta el ticket**: Bundles, upsells, envío gratis a partir de X€
- **Reduce el churn**: Campañas de reactivación (ver Radar de Fuga)

---

## Métricas relacionadas

| Métrica | Descripción |
|---------|-------------|
| **LTV Medio** | Promedio de todos tus clientes |
| **LTV/CAC** | Ratio entre valor del cliente y coste de adquisición |
| **LTV por segmento** | Diferencias entre grupos de clientes |

---

## Siguiente paso

→ [Radar de Fuga (Churn)](./churn_radar.md) — Detecta quién está a punto de abandonarte

---

**¿Dudas?** soporte@tactics.es
