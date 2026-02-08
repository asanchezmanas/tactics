"""
Template Store for Explainer Engine

Contains all human-readable text templates for metric explanations.
Supports multiple locales (es, en).

Structure:
    TEMPLATES[locale][category][metric_id] = {
        "what_it_means": str,
        "how_calculated": str,
        "caveats": List[str]
    }
"""

from typing import Dict, List, Any

TEMPLATES: Dict[str, Dict[str, Dict[str, Any]]] = {
    # =========================================================================
    # SPANISH (Default)
    # =========================================================================
    "es": {
        # ---------------------------------------------------------------------
        # LTV / CHURN
        # ---------------------------------------------------------------------
        "ltv": {
            "clv": {
                "what_it_means": (
                    "Es la cantidad total de dinero que estimamos que este cliente "
                    "gastará en tu negocio a lo largo de toda su relación contigo."
                ),
                "how_calculated": (
                    "Analizamos su historial de compras (cuántas veces compra, cuánto "
                    "tiempo hace de su última compra, y cuánto gasta) y lo comparamos "
                    "con el comportamiento de clientes similares para proyectar sus "
                    "compras futuras."
                ),
                "caveats": [
                    "Esta es una estimación estadística basada en datos históricos.",
                    "El valor real puede variar si el cliente cambia su comportamiento.",
                    "La proyección asume que las condiciones del mercado se mantienen similares."
                ]
            },
            "p_alive": {
                "what_it_means": (
                    "La probabilidad de que este cliente siga activo y vuelva a comprar. "
                    "Un valor alto significa que probablemente seguirá siendo cliente."
                ),
                "how_calculated": (
                    "Comparamos el tiempo desde su última compra y su frecuencia habitual "
                    "con patrones de miles de clientes. Si un cliente suele comprar cada "
                    "30 días y han pasado 60, su probabilidad de estar activo baja."
                ),
                "caveats": [
                    "Es una probabilidad, no una certeza. Un 80% significa que 8 de cada 10 clientes similares siguen activos.",
                    "No tiene en cuenta factores externos como cambios de vida del cliente.",
                    "Clientes nuevos tienen menos datos, por lo que la estimación es menos precisa."
                ]
            },
            "churn_probability": {
                "what_it_means": (
                    "El riesgo de que este cliente no vuelva a comprar. "
                    "Un valor alto indica que podría estar perdiendo interés o haberse ido."
                ),
                "how_calculated": (
                    "Es el complemento de la probabilidad de estar activo. "
                    "Si hay un 70% de probabilidad de que siga activo, hay un 30% de que no vuelva."
                ),
                "caveats": [
                    "Un cliente puede volver después de mucho tiempo, aunque el modelo lo considere 'churned'.",
                    "Factores como estacionalidad pueden afectar temporalmente esta métrica.",
                    "No distingue entre clientes que se fueron o que simplemente tienen ciclos de compra largos."
                ]
            },
            "expected_purchases": {
                "what_it_means": (
                    "El número de compras que esperamos que este cliente realice "
                    "en el período especificado, basado en su patrón histórico."
                ),
                "how_calculated": (
                    "Usamos la frecuencia histórica del cliente y su probabilidad de seguir "
                    "activo para proyectar cuántas compras hará."
                ),
                "caveats": [
                    "Es un promedio esperado. El cliente puede comprar más o menos veces.",
                    "Asume que mantendrá su ritmo de compra habitual.",
                ]
            },
            "recency": {
                "what_it_means": (
                    "Cuántos días han pasado desde la última compra de este cliente."
                ),
                "how_calculated": (
                    "Simplemente restamos la fecha de hoy menos la fecha de su última compra."
                ),
                "caveats": [
                    "Un número alto no siempre es malo: algunos productos tienen ciclos de compra largos.",
                    "Compáralo con la frecuencia típica de este cliente específico."
                ]
            },
            "segment": {
                "what_it_means": (
                    "Clasificación del cliente según su valor y actividad. "
                    "Ayuda a priorizar esfuerzos de retención y marketing."
                ),
                "how_calculated": (
                    "Combinamos el valor de vida (CLV) y la probabilidad de seguir activo "
                    "para clasificar en: VIP (alto valor, activo), En Riesgo (alto valor, "
                    "baja actividad), Regular (valor medio), o Perdido (baja actividad prolongada)."
                ),
                "caveats": [
                    "Los segmentos son simplificaciones útiles, no categorías absolutas.",
                    "Un cliente puede moverse entre segmentos con el tiempo."
                ]
            }
        },
        
        # ---------------------------------------------------------------------
        # MMM (Media Mix Modeling)
        # ---------------------------------------------------------------------
        "mmm": {
            "roas": {
                "what_it_means": (
                    "Cuántos euros de ventas generas por cada euro que inviertes en este "
                    "canal de publicidad. Un ROAS de 3x significa que por cada €1 invertido, "
                    "obtienes €3 en ventas."
                ),
                "how_calculated": (
                    "Dividimos las ventas que podemos atribuir al canal entre la inversión "
                    "total en ese canal. Usamos un modelo que considera que la publicidad "
                    "tiene efectos que duran más allá del día en que se muestra."
                ),
                "caveats": [
                    "La atribución nunca es 100% precisa. Algunas ventas ocurrirían sin publicidad.",
                    "El ROAS no considera el margen: un ROAS alto con margen bajo puede no ser rentable.",
                    "Valores pasados no garantizan resultados futuros. El mercado cambia."
                ]
            },
            "saturation": {
                "what_it_means": (
                    "Indica cuánto margen hay para invertir más en este canal antes de que "
                    "el retorno empiece a disminuir. Un valor cercano a 1 significa que el "
                    "canal está saturado."
                ),
                "how_calculated": (
                    "Analizamos cómo cambia el retorno a medida que aumenta la inversión. "
                    "Cuando invertir más genera cada vez menos ventas adicionales, el canal "
                    "se está saturando."
                ),
                "caveats": [
                    "La saturación puede variar por estacionalidad (Navidad vs. enero).",
                    "Cambios en creatividades o audiencias pueden 'desaturar' un canal.",
                    "Es una estimación basada en datos históricos."
                ]
            },
            "contribution": {
                "what_it_means": (
                    "La cantidad de ventas que estimamos son directamente atribuibles a "
                    "este canal de marketing. Es decir, ventas que probablemente no habrían "
                    "ocurrido sin esta inversión."
                ),
                "how_calculated": (
                    "Usamos un modelo estadístico que separa las ventas 'base' (que ocurrirían "
                    "sin publicidad) de las ventas incrementales generadas por cada canal."
                ),
                "caveats": [
                    "Es imposible saber con certeza qué ventas son incrementales.",
                    "El modelo hace suposiciones sobre cómo interactúan los canales.",
                    "Factores externos (economía, competencia) pueden afectar los resultados."
                ]
            },
            "optimal_budget": {
                "what_it_means": (
                    "La inversión que nuestro modelo sugiere como punto óptimo para este "
                    "canal, donde el retorno por euro adicional empieza a ser menor."
                ),
                "how_calculated": (
                    "Simulamos diferentes niveles de inversión y buscamos el punto donde "
                    "invertir €1 más genera menos de €1 adicional de retorno marginal."
                ),
                "caveats": [
                    "Es una sugerencia basada en datos pasados, no una garantía.",
                    "Las condiciones del mercado pueden haber cambiado.",
                    "No considera restricciones de presupuesto total o estrategia de marca."
                ]
            },
            "adstock": {
                "what_it_means": (
                    "El efecto residual de la publicidad. Cuando ves un anuncio hoy, "
                    "su impacto no desaparece mañana. El adstock mide cuánto dura este efecto."
                ),
                "how_calculated": (
                    "Observamos cómo las ventas responden a la publicidad en los días y semanas "
                    "siguientes, no solo el mismo día. Luego estimamos la 'vida media' del efecto."
                ),
                "caveats": [
                    "El efecto residual varía mucho entre canales (TV dura más que remarketing).",
                    "Es difícil de medir con precisión en períodos cortos de datos."
                ]
            }
        },
        
        # ---------------------------------------------------------------------
        # ECLAT (Association Rules)
        # ---------------------------------------------------------------------
        "eclat": {
            "support": {
                "what_it_means": (
                    "El porcentaje de pedidos que contienen esta combinación de productos. "
                    "Un soporte del 12% significa que 12 de cada 100 pedidos incluyen ambos productos."
                ),
                "how_calculated": (
                    "Contamos cuántos pedidos contienen todos los productos de la combinación "
                    "y lo dividimos entre el total de pedidos."
                ),
                "caveats": [
                    "Un soporte alto no significa que debas crear un bundle; solo que ocurre frecuentemente.",
                    "Productos muy populares aparecerán en muchas combinaciones por puro volumen."
                ]
            },
            "confidence": {
                "what_it_means": (
                    "De los clientes que compran el producto A, qué porcentaje también compra "
                    "el producto B. Una confianza del 45% significa que casi la mitad de los "
                    "compradores de A también compran B."
                ),
                "how_calculated": (
                    "Dividimos el número de pedidos con ambos productos entre el número de "
                    "pedidos que tienen el producto A."
                ),
                "caveats": [
                    "La mitad que NO compra B puede simplemente no necesitarlo.",
                    "La confianza no indica causalidad, solo correlación.",
                    "Depende de cómo esté organizada tu tienda y las recomendaciones actuales."
                ]
            },
            "lift": {
                "what_it_means": (
                    "Cuántas veces más probable es que se compren juntos estos productos "
                    "comparado con lo que esperaríamos por azar. Un lift de 2 significa "
                    "que se compran juntos el doble de lo esperado."
                ),
                "how_calculated": (
                    "Comparamos la frecuencia real de la combinación con la frecuencia "
                    "que esperaríamos si las compras fueran independientes."
                ),
                "caveats": [
                    "Un lift alto con soporte bajo significa que es raro pero cuando ocurre, es fuerte.",
                    "Lift cercano a 1 significa que no hay relación especial entre los productos.",
                    "No indica cuál producto 'causa' la compra del otro."
                ]
            }
        },
        
        # ---------------------------------------------------------------------
        # THOMPSON SAMPLING
        # ---------------------------------------------------------------------
        "thompson": {
            "conversion_rate": {
                "what_it_means": (
                    "El porcentaje de veces que esta variante logró el objetivo (click, "
                    "compra, etc.) cuando se mostró. Una tasa del 5% significa que 5 de "
                    "cada 100 exposiciones resultaron en conversión."
                ),
                "how_calculated": (
                    "Dividimos el número de conversiones entre el número total de veces "
                    "que se mostró esta variante."
                ),
                "caveats": [
                    "Con pocas muestras, la tasa puede ser muy variable y poco confiable.",
                    "Factores externos (hora, día, audiencia) pueden afectar las tasas.",
                    "Compara siempre con otras variantes, no con valores absolutos."
                ]
            },
            "samples": {
                "what_it_means": (
                    "Cuántas veces se ha probado esta variante. Más muestras significa "
                    "más confianza en los resultados."
                ),
                "how_calculated": (
                    "Contamos cada vez que esta variante fue seleccionada y mostrada."
                ),
                "caveats": [
                    "Pocas muestras (<100) significan resultados preliminares.",
                    "El algoritmo naturalmente da más muestras a variantes prometedoras."
                ]
            },
            "prob_best": {
                "what_it_means": (
                    "La probabilidad de que esta sea la mejor variante de todas las opciones. "
                    "Un valor del 70% significa que hay un 70% de probabilidad de que sea la ganadora."
                ),
                "how_calculated": (
                    "Simulamos miles de escenarios posibles basados en los datos observados "
                    "y contamos en cuántos esta variante resulta ser la mejor."
                ),
                "caveats": [
                    "Esta probabilidad cambia a medida que se recopilan más datos.",
                    "Incluso con alta probabilidad, no es certeza. Puede haber sorpresas.",
                    "Considera el tamaño del efecto, no solo la probabilidad de ser mejor."
                ]
            }
        },
        
        # ---------------------------------------------------------------------
        # LinUCB
        # ---------------------------------------------------------------------
        "linucb": {
            "ucb_score": {
                "what_it_means": (
                    "Una puntuación que combina el rendimiento conocido de esta opción "
                    "con un bonus por incertidumbre. Opciones poco probadas obtienen bonus "
                    "para fomentar la exploración."
                ),
                "how_calculated": (
                    "Sumamos la estimación del valor (explotación) más un término de "
                    "incertidumbre (exploración) que es mayor cuanto menos datos tenemos."
                ),
                "caveats": [
                    "El score no es directamente interpretable como probabilidad o retorno.",
                    "Es una herramienta de decisión, no una métrica de rendimiento final.",
                    "Compara scores entre opciones, no en absoluto."
                ]
            },
            "exploitation": {
                "what_it_means": (
                    "La parte del score que representa lo que sabemos sobre esta opción "
                    "basado en datos reales. Es nuestra mejor estimación de su valor."
                ),
                "how_calculated": (
                    "Usamos un modelo de regresión que aprende de las características "
                    "del contexto (cliente, momento, etc.) y los resultados observados."
                ),
                "caveats": [
                    "Con pocos datos, esta estimación puede ser muy imprecisa.",
                    "Asume que el contexto captura las variables relevantes."
                ]
            },
            "exploration": {
                "what_it_means": (
                    "La parte del score que representa nuestra incertidumbre. "
                    "Opciones menos probadas tienen mayor incertidumbre y por tanto "
                    "mayor potencial de sorpresa positiva."
                ),
                "how_calculated": (
                    "Calculamos cuánta variación podría haber en nuestra estimación "
                    "dado los datos que tenemos. Menos datos = más incertidumbre."
                ),
                "caveats": [
                    "Alta exploración no significa que la opción sea buena, solo desconocida.",
                    "El balance exploración/explotación se ajusta con el parámetro alpha."
                ]
            }
        },
        
        # ---------------------------------------------------------------------
        # PROFIT / UNIT ECONOMICS
        # ---------------------------------------------------------------------
        "profit": {
            "net_margin": {
                "what_it_means": (
                    "El beneficio que queda después de restar todos los costes: "
                    "producto, envío, almacenaje, y marketing. Es lo que realmente ganas."
                ),
                "how_calculated": (
                    "Precio de venta menos coste del producto (COGS) menos costes de "
                    "envío y almacenaje menos coste de marketing atribuido."
                ),
                "caveats": [
                    "Los costes de marketing atribuidos son estimaciones.",
                    "No incluye costes fijos de la empresa (oficina, salarios, etc.).",
                    "El margen puede variar según el canal de venta."
                ]
            },
            "gross_margin": {
                "what_it_means": (
                    "El beneficio antes de considerar marketing y otros costes variables. "
                    "Es el precio de venta menos el coste directo del producto."
                ),
                "how_calculated": (
                    "Precio de venta menos coste del producto (COGS) menos envío."
                ),
                "caveats": [
                    "No incluye costes de adquisición del cliente.",
                    "Un margen bruto alto no significa rentabilidad si el marketing es caro."
                ]
            },
            "cogs": {
                "what_it_means": (
                    "Coste de los Bienes Vendidos. Lo que te cuesta el producto antes "
                    "de venderlo: fabricación, compra al proveedor, etc."
                ),
                "how_calculated": (
                    "Es el coste de compra o fabricación del producto, sin incluir "
                    "envío ni almacenaje."
                ),
                "caveats": [
                    "Puede variar según volumen de compra y negociación con proveedores.",
                    "No incluye costes indirectos como almacenaje prolongado."
                ]
            }
        }
    },
    
    # =========================================================================
    # ENGLISH
    # =========================================================================
    "en": {
        "ltv": {
            "clv": {
                "what_it_means": (
                    "The total amount of money we estimate this customer will spend "
                    "with your business over their entire relationship with you."
                ),
                "how_calculated": (
                    "We analyze their purchase history (how often they buy, how long "
                    "since their last purchase, and how much they spend) and compare it "
                    "with similar customers to project their future purchases."
                ),
                "caveats": [
                    "This is a statistical estimate based on historical data.",
                    "The actual value may vary if the customer changes their behavior.",
                    "The projection assumes market conditions remain similar."
                ]
            },
            "p_alive": {
                "what_it_means": (
                    "The probability that this customer is still active and will make "
                    "another purchase. A high value means they're likely still a customer."
                ),
                "how_calculated": (
                    "We compare the time since their last purchase and their usual frequency "
                    "with patterns from thousands of customers. If a customer usually buys every "
                    "30 days and 60 have passed, their probability of being active drops."
                ),
                "caveats": [
                    "It's a probability, not certainty. 80% means 8 out of 10 similar customers are still active.",
                    "It doesn't account for external factors like life changes.",
                    "New customers have less data, making estimates less precise."
                ]
            }
            # ... (remaining English translations follow same pattern)
        }
        # ... (remaining categories)
    }
}


def get_template(locale: str, category: str, metric_id: str) -> Dict[str, Any]:
    """
    Get template for a specific metric.
    
    Falls back to Spanish if locale not found.
    Falls back to empty strings if metric not found.
    """
    fallback = {
        "what_it_means": "",
        "how_calculated": "",
        "caveats": []
    }
    
    if locale not in TEMPLATES:
        locale = "es"
    
    return TEMPLATES.get(locale, {}).get(category, {}).get(metric_id, fallback)


def get_available_locales() -> List[str]:
    """Return list of available locales."""
    return list(TEMPLATES.keys())


def get_available_categories(locale: str = "es") -> List[str]:
    """Return list of available categories for a locale."""
    return list(TEMPLATES.get(locale, {}).keys())
