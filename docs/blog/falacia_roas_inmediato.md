# La Falacia del ROAS Inmediato

> Por qué medir solo ventas directas es un error que distorsiona la asignación de presupuesto.

---

## El Razonamiento Fallido

La lógica parece irrefutable:

1. Invertimos 1,000€ en publicidad
2. Generamos 3,000€ en ventas atribuidas
3. ROAS = 3x
4. Como 3 > 1, la inversión es rentable
5. Invertir más

Este razonamiento, universalmente aplicado, contiene suposiciones problemáticas que conducen a decisiones subóptimas.

---

## Los Supuestos Ocultos

### Supuesto 1: Las ventas atribuidas son incrementales

La atribución asigna ventas a canales, pero no todas esas ventas son *incrementales*. Muchos usuarios que convierten tras ver un anuncio habrían convertido de todas formas.

Un usuario leal que iba a comprar de todos modos, ve un anuncio de retargeting segundos antes de la compra, y el canal se atribuye la venta entera. El ROAS aparente es excelente; el ROAS incremental es cero.

### Supuesto 2: El ROAS promedio aplica al siguiente euro

El ROAS de 3x es un promedio. Pero los primeros euros tienen ROAS mucho más alto (audiencia más relevante) y los últimos, más bajo (saturación). El próximo euro invertido puede tener ROAS de 1,5x aunque el promedio sea 3x.

### Supuesto 3: El periodo de medición captura el valor completo

Si la ventana de atribución es 7 días pero el ciclo de decisión del cliente es 30 días, el ROAS calculado subestima el impacto real. Inversamente, si hay devoluciones post-medición, el ROAS está inflado.

### Supuesto 4: Los canales son independientes

Un anuncio de Meta que genera awareness produce búsquedas en Google que producen conversiones. El ROAS de Meta parece bajo; el de Google, alto. Pero sin Mobile, Google tendría menos con qué trabajar.

---

## Las Distorsiones Resultantes

### Sobre-inversión en Captura de Demanda

Los canales que capturan demanda existente (Search de marca, retargeting) muestran ROAS inmediato espectacular porque operan al final del funnel. El resultado: concentración de presupuesto donde el impacto incremental es menor.

### Sub-inversión en Generación de Demanda

Los canales que generan demanda nueva (prospecting, awareness) muestran ROAS inmediato pobre porque su impacto es diferido e indirecto. El resultado: desinversión en la parte del funnel que alimenta el resto.

### Ciclo de Contracción

1. ROAS inmediato favorece captura sobre generación
2. Se reduce inversión en generación
3. Hay menos demanda para capturar
4. El ROAS de captura eventualmente cae (menos usuarios nuevos)
5. Se recorta todo el presupuesto

Este ciclo es invisible trimestre a trimestre pero devastador en el horizonte de años.

---

## Alternativas al ROAS Inmediato

### 1. Incrementalidad Medida

En lugar de atribución, medir el impacto causal mediante experimentos controlados:

- **Geo-holdouts**: Desactivar publicidad en ciertas regiones y comparar
- **Lift studies**: Grupos de control que no ven anuncios
- **PSA tests**: Mostrar anuncios neutrales al grupo control

El resultado es un ROAS incremental, no atribuido.

### 2. LTV-Adjusted ROAS

En lugar de medir ventas inmediatas, medir el Lifetime Value de los clientes adquiridos:

```
LTV-ROAS = (LTV promedio de clientes adquiridos) / CAC
```

Un canal con ROAS inmediato de 2x pero que adquiere clientes con alto LTV puede ser mejor inversión que uno con ROAS de 4x que adquiere clientes de una sola compra.

### 3. Marketing Mix Modeling

Medir la contribución de cada canal a ventas agregadas, capturando efectos diferidos y sinérgicos que la atribución no ve.

---

## El Caso del Upper Funnel

Los canales de upper funnel (YouTube, display de prospecting, podcasts) frecuentemente muestran ROAS inmediato < 1. Bajo el framework de ROAS inmediato, deberían eliminarse.

Sin embargo, estudios consistentemente muestran que:

1. Reducir awareness reduce el volumen total de conversiones meses después
2. El coste por conversión en lower funnel aumenta cuando upper funnel se recorta
3. El "ROAS total del sistema" es mejor con ambos que solo con lower funnel

El upper funnel no convierte directamente; crea las condiciones para que el lower funnel funcione.

---

## Framework Integrado

| Métrica | Propósito | Limitación |
|---------|-----------|------------|
| ROAS Inmediato | Optimización táctica, diagnóstico | Ignora efectos diferidos |
| Incrementalidad | Causalidad real | Costoso de implementar |
| LTV-ROAS | Valor largo plazo | Requiere madurez de datos |
| MMM | Visión holística | Menor granularidad |

Ninguna métrica individual es suficiente. La triangulación de múltiples perspectivas produce mejor comprensión.

---

## Recomendaciones Prácticas

### Para Optimización Diaria

Use ROAS inmediato como indicador direccional, no como verdad absoluta. Útil para ajustes tácticos dentro de un canal, no para decisiones estratégicas entre canales.

### Para Decisiones de Presupuesto

No base redistribuciones significativas únicamente en ROAS atribuido. Incorpore:
- Tests de incrementalidad periódicos
- Análisis de tendencias de volumen (¿está cayendo la demanda total?)
- Consideración del funnel completo

### Para Evaluación de Canales Nuevos

Los canales nuevos, especialmente de upper funnel, tendrán ROAS inmediato pobre. Permita periodo de aprendizaje y mida impacto sistémico antes de juzgar.

---

## Conclusión

El ROAS inmediato es una respuesta precisa a la pregunta equivocada. Mide lo que es fácil de medir (conversiones directas atribuidas) pero no lo que importa (incremento real de valor).

Las empresas que optimizan para ROAS inmediato experimentan rendimientos decrecientes a medida que sobre-invierten en captura y sub-invierten en generación. El punto final de esta trayectoria es un sistema publicitario que captura eficientemente una demanda cada vez menor.

La alternativa es aceptar que la medición perfecta es imposible, adoptar múltiples perspectivas complementarias, y tomar decisiones informadas pero no ciegas a las limitaciones de cada métrica.

---

## Referencias

- Lewis, R.A., & Rao, J.M. (2015). The Unfavorable Economics of Measuring the Returns to Advertising. *Quarterly Journal of Economics*, 130(4), 1941-1973.
- Shapiro, B., Hitsch, G.J., & Tuchman, A. (2021). TV Advertising Effectiveness and Profitability: Generalizable Results from 288 Brands. *Econometrica*, 89(4), 1855-1879.
- Gordon, B.R., Zettelmeyer, F., Bhargava, N., & Chapsky, D. (2019). A Comparison of Approaches to Advertising Measurement: Evidence from Big Field Experiments at Facebook. *Marketing Science*, 38(2), 193-225.

---

*Publicado por el equipo editorial de Tactics. Para consultas: editorial@tactics.es*
