# Glosario Tactics

Este documento centraliza y clarifica toda la terminología técnica y estratégica utilizada en la plataforma Tactics. Diseñado para ser accesible tanto para perfiles de negocio como técnicos.

---

## A

### Adstock (Memoria Publicitaria)
El efecto residual que tiene un anuncio en la mente del consumidor después de haber sido visto. En Tactics, medimos cómo el gasto de "ayer" sigue generando ventas "hoy". El ritmo de ese decaimiento (parámetro de adstock) se ajusta a partir de tus propios datos históricos, no con un valor genérico.

### Algoritmo Bayesiano
Un método estadístico que combina el conocimiento previo (histórico del negocio, comportamiento del sector) con los datos observados para producir estimaciones probabilísticas. A diferencia de la estadística clásica, no da un número único sino una distribución de posibilidades, lo que permite cuantificar la incertidumbre de forma explícita.

## B

### Basket Affinity (Afinidad de Cesta)
El análisis de qué productos se compran juntos con mayor frecuencia. Ayuda a descubrir oportunidades de "bundles" o promociones conjuntas. Tactics lo mide usando el algoritmo ECLAT con métricas de lift, soporte y confianza.

### BG/NBD (Beta-Geométrico / Binomial Negativo)
El modelo probabilístico de referencia para predecir el comportamiento de compra de clientes en contextos non-contractual (es decir, donde el cliente puede dejar de comprar en cualquier momento sin avisar). Desarrollado en Wharton por Peter Fader y Bruce Hardie. Tactics lo usa como motor principal del cálculo de LTV.

## C

### CAC (Customer Acquisition Cost)
El coste total de adquirir un nuevo cliente: suma de gasto publicitario, comisiones y costes de venta dividido entre el número de nuevos clientes obtenidos en ese periodo.

### CAC Payback Period (Periodo de Recuperación del CAC)
El número de meses que tarda un cliente en generar suficiente margen para cubrir lo que costó adquirirlo. Se calcula como `CAC / (AOV × margen bruto)`. Es la métrica operativa más directa para saber si tu negocio es escalable: si el payback es de 4 meses, puedes permitirte gastar más en adquisición que si es de 14.

### CAC / LTV Ratio
La relación entre lo que te cuesta captar un cliente y lo que ese cliente te genera. Un ratio saludable (1:3 o superior) indica un negocio con margen para crecer. Por debajo de 1:1, cada nuevo cliente destruye capital.

### CAC Efficiency (Eficiencia de Adquisición)
La capacidad de atraer nuevos clientes al menor coste posible, pero sin sacrificar calidad. Tactics optimiza el CAC analizando qué canales traen clientes con el LTV más alto, no solo los más baratos. Un canal "barato" que trae clientes de una sola compra puede ser más caro que uno "caro" que trae clientes que compran diez veces.

### Churn (Tasa de Fuga)
El porcentaje de clientes que dejan de comprar en tu tienda. En Tactics, calculamos la **Probabilidad de Churn** de forma continua para cada cliente, permitiendo intervención antes de que el abandono sea definitivo.

### CLV / LTV (Customer Lifetime Value)
El valor económico total que un cliente aportará a tu empresa durante toda su relación contigo. Es la métrica central de Tactics. Ver también: BG/NBD, Gamma-Gamma.

### Cooldown (Periodo de Enfriamiento)
Tiempo de espera obligatorio entre re-entrenamientos de un modelo para evitar que el sistema sobrereaccione a fluctuaciones temporales. Necesario porque los modelos de machine learning pueden "aprender" ruido estadístico si se reentrenan demasiado frecuentemente.

## D

### Deep Synthesis
La capacidad de Tactics de cruzar múltiples capas de datos (ventas, stock, publicidad) para generar conclusiones estratégicas de alto nivel, en lugar de presentar métricas aisladas.

### Drift (Deriva de Datos)
Cuando los patrones de comportamiento de tus clientes cambian drásticamente (por una crisis externa, un cambio de temporada, o una modificación de la oferta), haciendo que el modelo entrenado con datos antiguos deje de ser preciso. Tactics lo detecta automáticamente y lo señala antes de que contamine las predicciones.

## G

### Gamma-Gamma
Modelo probabilístico que, combinado con BG/NBD, permite estimar no solo la frecuencia de compra futura sino también el valor monetario esperado de esas compras. Necesario para calcular LTV en términos de euros, no solo de número de transacciones.

### Gateway Product (Producto de Entrada)
El producto que, cuando es la primera compra de un cliente, maximiza la probabilidad de que ese cliente se convierta en un comprador recurrente de alto LTV. Identificarlo permite redirigir la inversión publicitaria hacia lo que realmente construye valor a largo plazo.

## I

### Intervalo de Confianza
Rango que acompaña a cada predicción de Tactics indicando el margen de incertidumbre. Un LTV de "280€ – 360€ (90% CI)" significa que, con el 90% de confianza estadística, el valor real está dentro de ese rango. Rangos estrechos indican alta confianza; rangos amplios indican que se necesitan más datos.

### iROAS (Incremental ROAS)
Una estimación de cuánto retorno real genera el último euro invertido en publicidad, ayudando a detectar si un canal está saturado. Difiere del ROAS tradicional en que intenta aislar el efecto causal de la publicidad, separándolo de ventas que habrían ocurrido de todos modos.

## L

### Lift (Fuerza de Asociación)
Una métrica que indica cuánto más probable es que dos productos se compren juntos en comparación a si se compraran de forma independiente. Un Lift de 2.0 significa que la combinación ocurre el doble de lo esperado por puro azar.

## M

### MMM (Marketing Mix Modeling)
Una técnica estadística para entender cómo cada canal de marketing contribuye a las ventas totales, incluso aquellos que no tienen un "clic" directo (como brand awareness o contenido orgánico). Tactics implementa MMM con adstock (memoria publicitaria) y curvas de saturación Hill para capturar rendimientos decrecientes.

## P

### Pareto (Regla del 80/20)
El fenómeno donde una pequeña parte de tus clientes (20%) genera la gran mayoría de tus ingresos (80%). Tactics audita este riesgo de concentración para evitar que tu negocio dependa de muy pocas personas.

### POAS (Profitability Over Ad Spend)
A diferencia del ROAS (que solo mira ingresos brutos), el POAS mide el **beneficio real** generado por cada euro invertido en publicidad, descontando el coste de los productos (COGS). Es la métrica que determina si realmente estás ganando dinero con tu publicidad.

## R

### Razones de Refuerzo (Reinforcement Reasons)
Notas en lenguaje natural que acompañan a cada predicción indicando los factores que más han influido en ese resultado. Por ejemplo: "LTV ajustado al alza por aceleración de compras en los últimos 45 días" o "Canal marcado como saturado: ROAS marginal por debajo de 1.2x en las últimas 3 semanas".

### ROAS (Return on Ad Spend)
Ingresos totales generados divididos por la inversión publicitaria. Una métrica fundamental pero secundaria frente al POAS, ya que ignora los costes de producto y puede llevar a optimizar canales que parecen rentables pero destruyen margen.

### Robust Scaling (Escalado Robusto)
Técnica de normalización de datos basada en la mediana y el rango intercuartílico (IQR) en lugar de la media. Permite que los modelos de Tactics sean resistentes a outliers: una compra masiva anómala no distorsiona el comportamiento esperado del resto de clientes.

---

*Para consultas sobre términos adicionales: soporte@tactics.es*
