# Estructura de Precios Tactics

> Los tiers de Tactics se basan en la **madurez de datos** del negocio, no en la restricción artificial de funcionalidades. Un negocio con 6 meses de historial y 200 clientes no puede aprovechar las mismas herramientas que uno con 3 años y 10.000 clientes, aunque pague lo mismo. Esta estructura refleja esa realidad.

---

## Tiers

### 🟢 INTELLIGENCE — 99€/mes

**Para quién**: Negocios que están empezando a tomar decisiones basadas en datos.

**Requisitos mínimos de datos**:
- 3 meses de historial de pedidos
- 100+ clientes con al menos 1 compra

**Qué incluye**:
- LTV predictivo (BG/NBD + Gamma-Gamma) con intervalos de confianza
- Probabilidad de churn por cliente
- Segmentación automática (Champions, At-Risk, Hibernating, etc.)
- Análisis Pareto (concentración de ingresos)
- Afinidad de cesta (ECLAT)
- Cohort retention básica

**Propuesta de valor**: *"Sé quiénes son tus mejores clientes y cuáles estás a punto de perder, antes de que sea demasiado tarde."*

---

### 🔵 OPTIMISATION — 299€/mes

**Para quién**: Negocios que invierten activamente en publicidad y quieren optimizar cómo distribuyen ese gasto.

**Requisitos mínimos de datos**:
- 12 meses de historial de pedidos
- 500+ clientes
- 2 o más canales de adquisición conectados

**Qué incluye**:
- Todo lo de INTELLIGENCE
- MMM (Marketing Mix Modeling) con adstock y curvas Hill
- Optimizador de presupuesto con simulador "¿Y si...?"
- POAS (Profit on Ad Spend) por canal
- LTV ponderado por canal de adquisición (LTV-Weighted ROAS)
- CAC Payback Period por canal
- Curvas de saturación por canal

**Propuesta de valor**: *"Para de adivinar qué canal funciona mejor. Los datos lo dicen."*

---

### 🟣 PRECISION — 799€/mes

**Para quién**: Negocios con datos suficientes para hacer inferencia causal y optimización avanzada.

**Requisitos mínimos de datos**:
- 24 meses de historial
- 1.000+ clientes
- 3 o más canales con historial de gasto

**Qué incluye**:
- Todo lo de OPTIMISATION
- Bayesian MMM (PyMC) con priors informativos y distribuciones completas
- Synergy Matrix: efectos cruzados entre canales
- Forecasting de revenue por escenario
- Full Attribution audit vs. last-click
- SLA prioritario
- Acceso API para integración con sistemas propios

**Propuesta de valor**: *"Cuando los márgenes son estrechos y el volumen alto, la diferencia entre 3.1x y 3.4x de ROAS real vale más que este plan."*

---

## Filosofía de Precios

> *"Si te parece caro, probablemente no vendes suficiente para tener datos que valga la pena analizar. Resuélve eso primero."*

El objetivo no es vender el tier más alto. Es que el cliente esté en el tier que puede aprovechar realmente. Un negocio en INTELLIGENCE con 200 clientes y 6 meses de datos no necesita Bayesian MMM; necesita saber quiénes son sus mejores clientes y no perderlos.

Cuando crezca, subirá de tier. Y lo hará porque verá el valor, no porque le hayamos bloqueado funcionalidades artificialmente.

---

## Comparativa de Competidores

| Plataforma | ROI Esperado | Dolor que Resuelve | Limitación |
|-----------|---------------|---------|------------|
| **Klaviyo** | Retención básica | "No hablo con mi audiencia" | Sin MMM ni LTV predictivo real |
| **Triple Whale** | Attribution | "No sé qué anuncio trajo la venta" | Sensible a cambios de iOS/Cookies |
| **Tactics v3.3** | **Multiplicador de LTV** | **"Meta optimiza clicks baratos, no clientes que vuelven"** | Tier Precision requiere >24 meses datos |

---

*Actualizado: Febrero 2026*
