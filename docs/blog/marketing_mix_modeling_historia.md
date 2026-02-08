# Marketing Mix Modeling: Historia y Evolución

> De las ecuaciones de regresión de los años 60 a los modelos probabilísticos contemporáneos.

---

## Orígenes: El Nacimiento de la Econometría Publicitaria

El Marketing Mix Modeling (MMM) tiene sus raíces en la aplicación de métodos econométricos al análisis de la efectividad publicitaria. Los primeros trabajos formales aparecieron en la década de 1960, cuando investigadores comenzaron a aplicar análisis de regresión para cuantificar la relación entre gasto publicitario y ventas.

El contexto era específico: grandes corporaciones de bienes de consumo masivo (CPG) como Procter & Gamble, Unilever y Nestlé necesitaban entender cómo funcionaban sus inversiones en televisión, radio y prensa. La respuesta vino de la estadística aplicada.

---

## La Era de la Regresión Lineal (1960-1990)

### El Modelo Básico

Los primeros modelos MMM adoptaron la forma:

```
Ventas = β₀ + β₁(TV) + β₂(Radio) + β₃(Prensa) + ε
```

Donde los coeficientes β representaban la contribución de cada canal a las ventas, y ε el error no explicado.

### Limitaciones Reconocidas

Incluso en esta etapa temprana, los practicantes reconocían limitaciones fundamentales:

1. **Linealidad**: La relación entre gasto y ventas no es lineal; existe saturación
2. **Efectos diferidos**: La publicidad no actúa instantáneamente
3. **Colinealidad**: Los canales suelen activarse simultáneamente

---

## Refinamientos: Adstock y Saturación (1990-2010)

### El Concepto de Adstock

En 1979, Simon Broadbent introdujo el concepto de *adstock*: la idea de que el impacto publicitario no desaparece inmediatamente, sino que decae gradualmente.

```
Adstock(t) = Gasto(t) + decay × Adstock(t-1)
```

Este modelo captura el hecho de que la publicidad de la semana pasada sigue teniendo efecto esta semana, aunque atenuado.

### Funciones de Saturación

Para modelar el fenómeno de rendimientos decrecientes —donde cada euro adicional genera menos impacto—, se incorporaron funciones no lineales:

**Función Hill:**
```
Efecto = (Gasto^α) / (K^α + Gasto^α)
```

Esta función produce una curva en forma de "S" que captura tanto la inercia inicial como la saturación posterior.

---

## La Era Digital y la Crisis de Atribución (2010-2020)

### El Problema del Last-Click

Con la llegada del marketing digital, surgió una metodología alternativa: la atribución basada en tracking. El modelo predominante —*last-click attribution*— asignaba todo el crédito de una conversión al último punto de contacto.

Esta aproximación, aunque simple, introdujo distorsiones sistemáticas:
- Sobrevaloraba canales de captura (Google Search)
- Infravaloraba canales de awareness (Display, YouTube)
- Ignoraba efectos offline

### Coexistencia Incómoda

Durante esta década, MMM y atribución digital coexistieron como metodologías paralelas, a menudo con resultados contradictorios. Las agencias de medios promovían MMM para justificar inversión en televisión; las plataformas digitales promovían sus propios modelos de atribución.

---

## El Renacimiento del MMM (2020-presente)

### Catalizadores del Cambio

Varios factores convergieron para revitalizar el interés en MMM:

1. **Restricciones de privacidad**: iOS 14.5 y el fin de las cookies de terceros limitaron la atribución basada en tracking
2. **Fragmentación de canales**: La proliferación de plataformas hizo inviable el tracking individualizado
3. **Madurez de código abierto**: Liberación de frameworks como Robyn (Meta) y Lightweight MMM (Google)

### Evolución Metodológica

Los modelos contemporáneos incorporan avances significativos:

**Inferencia Bayesiana**: En lugar de producir estimaciones puntuales, los modelos modernos generan distribuciones de probabilidad que capturan la incertidumbre inherente.

**Inclusión de priors informativos**: Conocimiento experto (por ejemplo, que el gasto en cierto canal no puede tener ROI negativo) se incorpora formalmente al modelo.

**Validación automática**: Los frameworks modernos incluyen diagnósticos automáticos de calidad del modelo.

---

## Consideraciones para el Contexto Europeo

### Regulación y Datos

El GDPR y la ePrivacy Directive han acelerado la adopción de MMM en Europa más que en otras regiones. Paradójicamente, las restricciones regulatorias han impulsado metodologías más robustas y menos dependientes de tracking individual.

### Mercados Fragmentados

A diferencia de Estados Unidos, Europa presenta mercados fragmentados con múltiples idiomas, regulaciones locales y comportamientos de consumo diferenciados. Los modelos MMM deben adaptarse a esta heterogeneidad.

---

## Estado del Arte Actual

El MMM contemporáneo se caracteriza por:

| Característica | Enfoque Tradicional | Enfoque Moderno |
|----------------|---------------------|-----------------|
| Estimación | Puntual | Distribución probabilística |
| Incertidumbre | Ignorada o secundaria | Central |
| Validación | Manual, posterior | Automatizada, integrada |
| Tiempo de modelado | Semanas/meses | Días/horas |
| Accesibilidad | Consultoras especializadas | Software accesible |

---

## Limitaciones Persistentes

A pesar de los avances, el MMM conserva limitaciones fundamentales:

1. **Correlación no es causalidad**: Sin experimentación controlada, la causalidad es difícil de establecer
2. **Datos agregados**: La pérdida de granularidad individual limita ciertos análisis
3. **Complejidad de interacción**: Los efectos sinérgicos entre canales son difíciles de modelar completamente

---

## Conclusión

El Marketing Mix Modeling ha evolucionado desde las regresiones lineales de hace seis décadas hasta los frameworks probabilísticos actuales. Esta evolución ha sido impulsada tanto por avances metodológicos como por cambios en el entorno regulatorio y tecnológico.

Para las empresas europeas, el MMM representa una alternativa robusta y respetuosa con la privacidad para entender la efectividad de sus inversiones en marketing. La pregunta ya no es si adoptar MMM, sino cómo implementarlo de manera que capture las particularidades de cada negocio.

---

## Referencias

- Broadbent, S. (1979). One way TV advertisements work. *Journal of the Market Research Society*, 21(3), 139-166.
- Chan, D., & Perry, M. (2017). Challenges and Opportunities in Media Mix Modeling. *Google Research*.
- Jin, Y., et al. (2017). Bayesian Methods for Media Mix Modeling with Carryover and Shape Effects. *Google Research*.

---

*Publicado por el equipo editorial de Tactics. Para consultas: editorial@tactics.es*
