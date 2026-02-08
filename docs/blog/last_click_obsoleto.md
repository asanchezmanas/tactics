# Por Qué el Last-Click Attribution Está Obsoleto

> Un análisis de las limitaciones estructurales del modelo de atribución más extendido y sus consecuencias económicas.

---

## El Modelo Predominante

Durante la última década, el *last-click attribution* ha sido el estándar de facto para medir la efectividad del marketing digital. Su lógica es simple: el último punto de contacto antes de la conversión recibe el 100% del crédito.

Un usuario ve un anuncio en Instagram, busca la marca en Google, hace clic en un anuncio de búsqueda y compra. ¿Quién recibe el crédito? Google Search; Instagram no recibe nada.

Esta simplicidad ha sido su principal atractivo y, simultáneamente, su defecto fatal.

---

## Las Distorsiones del Last-Click

### 1. Sesgo Sistemático Contra el Awareness

Los canales de "descubrimiento" —aquellos que introducen la marca al usuario por primera vez— son sistemáticamente infravalorados. 

El usuario que vio el anuncio de Instagram no habría buscado la marca si no hubiera sido expuesto a ese anuncio. Sin embargo, el modelo asigna cero valor a esa exposición crucial.

**Consecuencia**: Desinversión en canales de awareness, reduciendo el tamaño del embudo a largo plazo.

### 2. Inflación de Canales de Captura

Los canales posicionados cerca de la conversión —principalmente búsqueda de marca y retargeting— capturan crédito desproporcionado.

Un anuncio de retargeting que aparece segundos antes de una compra que iba a ocurrir de todos modos recibe crédito completo.

**Consecuencia**: Sobre-inversión en canales que capturan demanda existente en lugar de generarla.

### 3. Ignorancia de Efectos Offline

El modelo solo mide lo medible digitalmente. Una campaña de televisión, una mención en prensa o una recomendación de un amigo no aparecen en el journey digital, pero influyen en la decisión.

**Consecuencia**: Visión incompleta que ignora canales potencialmente críticos.

---

## El Conflicto de Intereses Implícito

Es importante reconocer que el last-click no es solo una metodología deficiente; es una metodología que beneficia a ciertos actores:

- **Plataformas de búsqueda**: Google es el mayor beneficiario, ya que captura búsquedas de marca que fueron generadas por otros canales
- **Plataformas de retargeting**: Capturan usuarios ya convencidos, justo antes de la conversión

Estas mismas plataformas son las que proporcionan las herramientas de medición estándar. El árbitro tiene interés en el resultado.

---

## Caso Ilustrativo

Consideremos dos escenarios para una tienda de moda online:

### Escenario A: Inversión equilibrada
- 10,000€ en Instagram (awareness)
- 5,000€ en Google Search
- Resultado: 200 conversiones

### Escenario B: Siguiendo el last-click
- 0€ en Instagram
- 15,000€ en Google Search
- Resultado esperado según last-click: 600 conversiones
- Resultado real: 80 conversiones

¿Qué ocurrió? Sin la inversión en awareness, hay menos usuarios buscando la marca. Google Search captura demanda que ya no existe.

El last-click predijo un incremento porque no comprende la interdependencia de canales.

---

## Alternativas Metodológicas

### Multi-Touch Attribution (MTA)

Distribuye el crédito entre múltiples puntos de contacto. Modelos comunes:
- **Lineal**: Cada touchpoint recibe igual crédito
- **Time decay**: Más crédito a touchpoints cercanos a la conversión
- **Position-based**: Más crédito al primero y último touchpoint

**Limitación**: Sigue dependiendo de tracking individual, vulnerable a restricciones de privacidad.

### Marketing Mix Modeling (MMM)

Modelos estadísticos que correlacionan gasto agregado con ventas agregadas. No requiere tracking individual.

**Ventaja**: Funciona con datos de primera parte, incluye canales offline.
**Limitación**: Menor granularidad, requiere volumen de datos.

### Modelos Híbridos

Combinación de MTA para canales digitales y MMM para visión holística. Triangulación de resultados.

---

## El Impacto del Fin de las Cookies

La desaparición progresiva de las cookies de terceros y las restricciones de tracking (iOS 14.5+) han erosionado la base técnica del last-click:

- Ventanas de atribución reducidas
- Usuarios "invisibles" que no pueden ser rastreados
- Conversiones que no se pueden vincular a exposiciones previas

Paradójicamente, estas restricciones han forzado una transición hacia metodologías más robustas.

---

## Recomendaciones Prácticas

### Para empresas con inversión publicitaria significativa:

1. **No tome decisiones de presupuesto basadas únicamente en last-click**
2. **Implemente pruebas de incrementalidad**: Experimentos controlados donde se activa/desactiva un canal para medir impacto real
3. **Adopte MMM como complemento**: Para visión holística de la efectividad
4. **Desconfíe de reportes auto-atribuidos**: Cada plataforma tiende a sobre-atribuirse conversiones

### Para empresas pequeñas:

1. **Utilice last-click como indicador direccional, no como verdad**
2. **Mantenga inversión en awareness aunque no "convierta" según el tracking**
3. **Observe métricas de salud de marca**: Búsquedas de marca, tráfico directo

---

## Conclusión

El last-click attribution no es malo por ser simple; es malo porque sus simplificaciones producen decisiones sistemáticamente subóptimas. Favorece canales que capturan demanda sobre canales que la generan, creando un ciclo de desinversión en la parte superior del embudo que, a largo plazo, reduce el volumen total de conversiones.

La transición hacia metodologías más robustas no es opcional; es una respuesta necesaria tanto a las limitaciones metodológicas como a los cambios regulatorios y tecnológicos del ecosistema digital.

---

## Referencias

- Berman, R., & Van den Bulte, C. (2022). False Discovery in A/B Testing. *Management Science*.
- Shapiro, B., Hitsch, G.J., & Tuchman, A. (2021). TV Advertising Effectiveness and Profitability: Generalizable Results from 288 Brands. *Econometrica*.
- Zantedeschi, D., Feit, E.M., & Bradlow, E.T. (2017). Measuring Multi-channel Advertising Response. *Management Science*.

---

*Publicado por el equipo editorial de Tactics. Para consultas: editorial@tactics.es*
