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
                    "gastar├í en tu negocio a lo largo de toda su relaci├│n contigo."
                ),
                "how_calculated": (
                    "Analizamos su historial de compras (cu├íntas veces compra, cu├ínto "
                    "tiempo hace de su ├║ltima compra, y cu├ínto gasta) y lo comparamos "
                    "con el comportamiento de clientes similares para proyectar sus "
                    "compras futuras."
                ),
                "business_impact": (
                    "Si identificas a tus mejores clientes (el 19% que generan el 67% de ingresos), "
                    "puedes enfocar tu presupuesto de retenci├│n donde realmente importa. "
                    "Esto puede significar proteger millones en ingresos con una fracci├│n del coste."
                ),
                "caveats": [
                    "Esta es una estimaci├│n estad├¡stica basada en datos hist├│ricos.",
                    "El valor real puede variar si el cliente cambia su comportamiento.",
                    "La proyecci├│n asume que las condiciones del mercado se mantienen similares."
                ]
            },
            "p_alive": {
                "what_it_means": (
                    "La probabilidad de que este cliente siga activo y vuelva a comprar. "
                    "Un valor alto significa que probablemente seguir├í siendo cliente."
                ),
                "how_calculated": (
                    "Comparamos el tiempo desde su ├║ltima compra y su frecuencia habitual "
                    "con patrones de miles de clientes. Si un cliente suele comprar cada "
                    "30 d├¡as y han pasado 60, su probabilidad de estar activo baja."
                ),
                "caveats": [
                    "Es una probabilidad, no una certeza. Un 80% significa que 8 de cada 10 clientes similares siguen activos.",
                    "No tiene en cuenta factores externos como cambios de vida del cliente.",
                    "Clientes nuevos tienen menos datos, por lo que la estimaci├│n es menos precisa."
                ]
            },
            "churn_probability": {
                "what_it_means": (
                    "El riesgo de que este cliente no vuelva a comprar. "
                    "Un valor alto indica que podr├¡a estar perdiendo inter├®s o haberse ido."
                ),
                "how_calculated": (
                    "Es el complemento de la probabilidad de estar activo. "
                    "Si hay un 70% de probabilidad de que siga activo, hay un 30% de que no vuelva."
                ),
                "business_impact": (
                    "Detectar clientes en riesgo ANTES de que se vayan te permite "
                    "lanzar ofertas de retenci├│n proactivas. Si tu radar detecta el 89% de los churners, "
                    "podr├¡as proteger Ôé¼142K anuales que se perder├¡an sin intervenci├│n."
                ),
                "caveats": [
                    "Un cliente puede volver despu├®s de mucho tiempo, aunque el modelo lo considere 'churned'.",
                    "Factores como estacionalidad pueden afectar temporalmente esta m├®trica.",
                    "No distingue entre clientes que se fueron o que simplemente tienen ciclos de compra largos."
                ]
            },
            "expected_purchases": {
                "what_it_means": (
                    "El n├║mero de compras que esperamos que este cliente realice "
                    "en el per├¡odo especificado, basado en su patr├│n hist├│rico."
                ),
                "how_calculated": (
                    "Usamos la frecuencia hist├│rica del cliente y su probabilidad de seguir "
                    "activo para proyectar cu├íntas compras har├í."
                ),
                "caveats": [
                    "Es un promedio esperado. El cliente puede comprar m├ís o menos veces.",
                    "Asume que mantendr├í su ritmo de compra habitual.",
                ]
            },
            "recency": {
                "what_it_means": (
                    "Cu├íntos d├¡as han pasado desde la ├║ltima compra de este cliente."
                ),
                "how_calculated": (
                    "Simplemente restamos la fecha de hoy menos la fecha de su ├║ltima compra."
                ),
                "caveats": [
                    "Un n├║mero alto no siempre es malo: algunos productos tienen ciclos de compra largos.",
                    "Comp├íralo con la frecuencia t├¡pica de este cliente espec├¡fico."
                ]
            },
            "segment": {
                "what_it_means": (
                    "Clasificaci├│n del cliente seg├║n su valor y actividad. "
                    "Ayuda a priorizar esfuerzos de retenci├│n y marketing."
                ),
                "how_calculated": (
                    "Combinamos el valor de vida (CLV) y la probabilidad de seguir activo "
                    "para clasificar en: VIP (alto valor, activo), En Riesgo (alto valor, "
                    "baja actividad), Regular (valor medio), o Perdido (baja actividad prolongada)."
                ),
                "caveats": [
                    "Los segmentos son simplificaciones ├║tiles, no categor├¡as absolutas.",
                    "Un cliente puede moverse entre segmentos con el tiempo."
                ]
            },
            "revenue_velocity": {
                "what_it_means": (
                    "Es la velocidad a la que crece el valor de este cliente. "
                    "Una velocidad alta indica un cliente que est├í acelerando su gasto."
                ),
                "how_calculated": (
                    "Calculamos la derivada del ingreso respecto al tiempo. Si un cliente "
                    "gastaba Ôé¼10/mes y ahora gasta Ôé¼20/mes, su velocidad ha duplicado."
                ),
                "business_impact": (
                    "Los clientes con alta velocidad son tus futuras estrellas. "
                    "Identificarlos permite incentivar ese crecimiento antes de que se estabilice."
                ),
                "caveats": [
                    "Picos puntuales pueden inflar la velocidad artificialmente.",
                    "Requiere al menos dos puntos de datos para ser calculada."
                ]
            },
            "attention_weight": {
                "what_it_means": (
                    "Indica qu├® per├¡odo de tiempo ha sido m├ís determinante para esta predicci├│n. "
                    "Es el 'foco' de nuestra Inteligencia Artificial."
                ),
                "how_calculated": (
                    "Usamos una capa de Atenci├│n en el modelo neuronal que asigna pesos "
                    "a cada mes. Los meses con m├ís peso han influido m├ís en el resultado final."
                ),
                "business_impact": (
                    "Saber qu├® evento caus├│ la predicci├│n te permite replicar ese ├®xito "
                    "o entender qu├® cambi├│ en la relaci├│n con el cliente."
                ),
                "caveats": [
                    "Es una medida de importancia relativa denro de la secuencia.",
                    "No indica causalidad directa, solo relevancia estad├¡stica para el modelo."
                ]
            }
        },
        
        # ---------------------------------------------------------------------
        # MMM (Media Mix Modeling)
        # ---------------------------------------------------------------------
        "mmm": {
            "roas": {
                "what_it_means": (
                    "Cu├íntos euros de ventas generas por cada euro que inviertes en este "
                    "canal de publicidad. Un ROAS de 3x significa que por cada Ôé¼1 invertido, "
                    "obtienes Ôé¼3 en ventas."
                ),
                "how_calculated": (
                    "Dividimos las ventas que podemos atribuir al canal entre la inversi├│n "
                    "total en ese canal. Usamos un modelo que considera que la publicidad "
                    "tiene efectos que duran m├ís all├í del d├¡a en que se muestra."
                ),
                "business_impact": (
                    "Si tu ROAS actual es 2.8x y el modelo detecta que puedes llegar a 3.4x "
                    "rebalanceando presupuesto, est├ís recuperando un 21% de eficiencia perdida. "
                    "Con Ôé¼100K de inversi├│n mensual, eso son Ôé¼21K al mes que ahora mismo tiras."
                ),
                "caveats": [
                    "La atribuci├│n nunca es 100% precisa. Algunas ventas ocurrir├¡an sin publicidad.",
                    "El ROAS no considera el margen: un ROAS alto con margen bajo puede no ser rentable.",
                    "Valores pasados no garantizan resultados futuros. El mercado cambia."
                ]
            },
            "saturation": {
                "what_it_means": (
                    "Indica cu├ínto margen hay para invertir m├ís en este canal antes de que "
                    "el retorno empiece a disminuir. Un valor cercano a 1 significa que el "
                    "canal est├í saturado."
                ),
                "how_calculated": (
                    "Analizamos c├│mo cambia el retorno a medida que aumenta la inversi├│n. "
                    "Cuando invertir m├ís genera cada vez menos ventas adicionales, el canal "
                    "se est├í saturando."
                ),
                "business_impact": (
                    "Si TV est├í al 72% de saturaci├│n y TikTok al 35%, cada Ôé¼1 adicional en TikTok "
                    "genera 3x m├ís ventas que en TV. Redistribuir te ahorra dinero sin perder alcance."
                ),
                "caveats": [
                    "La saturaci├│n puede variar por estacionalidad (Navidad vs. enero).",
                    "Cambios en creatividades o audiencias pueden 'desaturar' un canal.",
                    "Es una estimaci├│n basada en datos hist├│ricos."
                ]
            },
            "contribution": {
                "what_it_means": (
                    "La cantidad de ventas que estimamos son directamente atribuibles a "
                    "este canal de marketing. Es decir, ventas que probablemente no habr├¡an "
                    "ocurrido sin esta inversi├│n."
                ),
                "how_calculated": (
                    "Usamos un modelo estad├¡stico que separa las ventas 'base' (que ocurrir├¡an "
                    "sin publicidad) de las ventas incrementales generadas por cada canal."
                ),
                "caveats": [
                    "Es imposible saber con certeza qu├® ventas son incrementales.",
                    "El modelo hace suposiciones sobre c├│mo interact├║an los canales.",
                    "Factores externos (econom├¡a, competencia) pueden afectar los resultados."
                ]
            },
            "optimal_budget": {
                "what_it_means": (
                    "La inversi├│n que nuestro modelo sugiere como punto ├│ptimo para este "
                    "canal, donde el retorno por euro adicional empieza a ser menor."
                ),
                "how_calculated": (
                    "Simulamos diferentes niveles de inversi├│n y buscamos el punto donde "
                    "invertir Ôé¼1 m├ís genera menos de Ôé¼1 adicional de retorno marginal."
                ),
                "caveats": [
                    "Es una sugerencia basada en datos pasados, no una garant├¡a.",
                    "Las condiciones del mercado pueden haber cambiado.",
                    "No considera restricciones de presupuesto total o estrategia de marca."
                ]
            },
            "adstock": {
                "what_it_means": (
                    "El efecto residual de la publicidad. Cuando ves un anuncio hoy, "
                    "su impacto no desaparece ma├▒ana. El adstock mide cu├ínto dura este efecto."
                ),
                "how_calculated": (
                    "Observamos c├│mo las ventas responden a la publicidad en los d├¡as y semanas "
                    "siguientes, no solo el mismo d├¡a. Luego estimamos la 'vida media' del efecto."
                ),
                "caveats": [
                    "El efecto residual var├¡a mucho entre canales (TV dura m├ís que remarketing).",
                    "Es dif├¡cil de medir con precisi├│n en per├¡odos cortos de datos."
                ]
            },
            "synergy_index": {
                "what_it_means": (
                    "Mide el 'efecto eco' entre canales. Indica cu├ínto ayuda un canal "
                    "a que el resto de tu marketing sea m├ís efectivo."
                ),
                "how_calculated": (
                    "Analizamos las interacciones cruzadas con desfase temporal. Si el gasto "
                    "en Canal A precede sistem├íticamente a una mejora en Canal B, hay sinergia."
                ),
                "business_impact": (
                    "Optimizar sinergias permite que tu presupuesto rinda m├ís sin gastar m├ís. "
                    "Es como 'aceitar' el motor de marketing completo."
                ),
                "caveats": [
                    "Requiere datos de varios canales activos simult├íneamente.",
                    "Las sinergias pueden cambiar si cambia la estrategia creativa."
                ]
            },
            "multi_objective_balance": {
                "what_it_means": (
                    "El equilibrio elegido entre el volumen de crecimiento y la eficiencia (ROI)."
                ),
                "how_calculated": (
                    "Ajustamos el optimizador para que priorice una combinaci├│n pesada "
                    "de ingresos totales y retorno por euro invertido."
                ),
                "caveats": [
                    "Priorizar volumen puede reducir el ROAS a corto plazo.",
                    "Priorizar eficiencia puede limitar tu capacidad de escalar r├ípido."
                ]
            }
        },
        
        # ---------------------------------------------------------------------
        # ECLAT (Association Rules)
        # ---------------------------------------------------------------------
        "eclat": {
            "support": {
                "what_it_means": (
                    "El porcentaje de pedidos que contienen esta combinaci├│n de productos. "
                    "Un soporte del 12% significa que 12 de cada 100 pedidos incluyen ambos productos."
                ),
                "how_calculated": (
                    "Contamos cu├íntos pedidos contienen todos los productos de la combinaci├│n "
                    "y lo dividimos entre el total de pedidos."
                ),
                "caveats": [
                    "Un soporte alto no significa que debas crear un bundle; solo que ocurre frecuentemente.",
                    "Productos muy populares aparecer├ín en muchas combinaciones por puro volumen."
                ]
            },
            "confidence": {
                "what_it_means": (
                    "De los clientes que compran el producto A, qu├® porcentaje tambi├®n compra "
                    "el producto B. Una confianza del 45% significa que casi la mitad de los "
                    "compradores de A tambi├®n compran B."
                ),
                "how_calculated": (
                    "Dividimos el n├║mero de pedidos con ambos productos entre el n├║mero de "
                    "pedidos que tienen el producto A."
                ),
                "caveats": [
                    "La mitad que NO compra B puede simplemente no necesitarlo.",
                    "La confianza no indica causalidad, solo correlaci├│n.",
                    "Depende de c├│mo est├® organizada tu tienda y las recomendaciones actuales."
                ]
            },
            "lift": {
                "what_it_means": (
                    "Cu├íntas veces m├ís probable es que se compren juntos estos productos "
                    "comparado con lo que esperar├¡amos por azar. Un lift de 2 significa "
                    "que se compran juntos el doble de lo esperado."
                ),
                "how_calculated": (
                    "Comparamos la frecuencia real de la combinaci├│n con la frecuencia "
                    "que esperar├¡amos si las compras fueran independientes."
                ),
                "caveats": [
                    "Un lift alto con soporte bajo significa que es raro pero cuando ocurre, es fuerte.",
                    "Lift cercano a 1 significa que no hay relaci├│n especial entre los productos.",
                    "No indica cu├íl producto 'causa' la compra del otro."
                ]
            }
        },
        
        # ---------------------------------------------------------------------
        # THOMPSON SAMPLING
        # ---------------------------------------------------------------------
        "thompson": {
            "conversion_rate": {
                "what_it_means": (
                    "El porcentaje de veces que esta variante logr├│ el objetivo (click, "
                    "compra, etc.) cuando se mostr├│. Una tasa del 5% significa que 5 de "
                    "cada 100 exposiciones resultaron en conversi├│n."
                ),
                "how_calculated": (
                    "Dividimos el n├║mero de conversiones entre el n├║mero total de veces "
                    "que se mostr├│ esta variante."
                ),
                "caveats": [
                    "Con pocas muestras, la tasa puede ser muy variable y poco confiable.",
                    "Factores externos (hora, d├¡a, audiencia) pueden afectar las tasas.",
                    "Compara siempre con otras variantes, no con valores absolutos."
                ]
            },
            "samples": {
                "what_it_means": (
                    "Cu├íntas veces se ha probado esta variante. M├ís muestras significa "
                    "m├ís confianza en los resultados."
                ),
                "how_calculated": (
                    "Contamos cada vez que esta variante fue seleccionada y mostrada."
                ),
                "caveats": [
                    "Pocas muestras (<100) significan resultados preliminares.",
                    "El algoritmo naturalmente da m├ís muestras a variantes prometedoras."
                ]
            },
            "prob_best": {
                "what_it_means": (
                    "La probabilidad de que esta sea la mejor variante de todas las opciones. "
                    "Un valor del 70% significa que hay un 70% de probabilidad de que sea la ganadora."
                ),
                "how_calculated": (
                    "Simulamos miles de escenarios posibles basados en los datos observados "
                    "y contamos en cu├íntos esta variante resulta ser la mejor."
                ),
                "caveats": [
                    "Esta probabilidad cambia a medida que se recopilan m├ís datos.",
                    "Incluso con alta probabilidad, no es certeza. Puede haber sorpresas.",
                    "Considera el tama├▒o del efecto, no solo la probabilidad de ser mejor."
                ]
            }
        },
        
        # ---------------------------------------------------------------------
        # LinUCB
        # ---------------------------------------------------------------------
        "linucb": {
            "ucb_score": {
                "what_it_means": (
                    "Una puntuaci├│n que combina el rendimiento conocido de esta opci├│n "
                    "con un bonus por incertidumbre. Opciones poco probadas obtienen bonus "
                    "para fomentar la exploraci├│n."
                ),
                "how_calculated": (
                    "Sumamos la estimaci├│n del valor (explotaci├│n) m├ís un t├®rmino de "
                    "incertidumbre (exploraci├│n) que es mayor cuanto menos datos tenemos."
                ),
                "caveats": [
                    "El score no es directamente interpretable como probabilidad o retorno.",
                    "Es una herramienta de decisi├│n, no una m├®trica de rendimiento final.",
                    "Compara scores entre opciones, no en absoluto."
                ]
            },
            "exploitation": {
                "what_it_means": (
                    "La parte del score que representa lo que sabemos sobre esta opci├│n "
                    "basado en datos reales. Es nuestra mejor estimaci├│n de su valor."
                ),
                "how_calculated": (
                    "Usamos un modelo de regresi├│n que aprende de las caracter├¡sticas "
                    "del contexto (cliente, momento, etc.) y los resultados observados."
                ),
                "caveats": [
                    "Con pocos datos, esta estimaci├│n puede ser muy imprecisa.",
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
                    "Calculamos cu├ínta variaci├│n podr├¡a haber en nuestra estimaci├│n "
                    "dado los datos que tenemos. Menos datos = m├ís incertidumbre."
                ),
                "caveats": [
                    "Alta exploraci├│n no significa que la opci├│n sea buena, solo desconocida.",
                    "El balance exploraci├│n/explotaci├│n se ajusta con el par├ímetro alpha."
                ]
            }
        },
        
        # ---------------------------------------------------------------------
        # PROFIT / UNIT ECONOMICS
        # ---------------------------------------------------------------------
        "profit": {
            "net_margin": {
                "what_it_means": (
                    "El beneficio que queda despu├®s de restar todos los costes: "
                    "producto, env├¡o, almacenaje, y marketing. Es lo que realmente ganas."
                ),
                "how_calculated": (
                    "Precio de venta menos coste del producto (COGS) menos costes de "
                    "env├¡o y almacenaje menos coste de marketing atribuido."
                ),
                "caveats": [
                    "Los costes de marketing atribuidos son estimaciones.",
                    "No incluye costes fijos de la empresa (oficina, salarios, etc.).",
                    "El margen puede variar seg├║n el canal de venta."
                ]
            },
            "gross_margin": {
                "what_it_means": (
                    "El beneficio antes de considerar marketing y otros costes variables. "
                    "Es el precio de venta menos el coste directo del producto."
                ),
                "how_calculated": (
                    "Precio de venta menos coste del producto (COGS) menos env├¡o."
                ),
                "caveats": [
                    "No incluye costes de adquisici├│n del cliente.",
                    "Un margen bruto alto no significa rentabilidad si el marketing es caro."
                ]
            },
            "cogs": {
                "what_it_means": (
                    "Coste de los Bienes Vendidos. Lo que te cuesta el producto antes "
                    "de venderlo: fabricaci├│n, compra al proveedor, etc."
                ),
                "how_calculated": (
                    "Es el coste de compra o fabricaci├│n del producto, sin incluir "
                    "env├¡o ni almacenaje."
                ),
                "caveats": [
                    "Puede variar seg├║n volumen de compra y negociaci├│n con proveedores.",
                    "No incluye costes indirectos como almacenaje prolongado."
                ]
            }
        },
        
        # ---------------------------------------------------------------------
        # DATA INTEGRITY & ROBUSTNESS
        # ---------------------------------------------------------------------
        "integrity": {
            "duplicate": {
                "what_it_means": (
                    "Hemos detectado que algunos registros parecen estar repetidos. Esto suele "
                    "ocurrir cuando un sistema envía la misma información varias veces o "
                    "cuando se procesa un archivo de carga por duplicado."
                ),
                "how_calculated": (
                    "Buscamos transacciones que comparten el mismo ID único o que tienen "
                    "características idénticas (fecha, cliente e importe) en un periodo muy corto."
                ),
                "business_impact": (
                    "Si no se gestionan, los duplicados pueden inflar artificialmente tus "
                    "ingresos reportados o el ROAS. Intelligence 2.0 identifica estos casos "
                    "para que la predicción final no se vea 'engañada' por datos inflados."
                ),
                "caveats": [
                    "Podrían ser compras reales legítimas si el cliente compró lo mismo dos veces.",
                    "La detección se basa en patrones lógicos, no es una confirmación de error.",
                    "Sugerimos revisar la fuente de datos si el volumen de duplicados es alto."
                ]
            },
            "gap": {
                "what_it_means": (
                    "Parece haber periodos de tiempo sin actividad registrada. Por ejemplo, "
                    "varios días seguidos sin datos de una fuente que normalmente es diaria."
                ),
                "how_calculated": (
                    "Analizamos el flujo cronológico y detectamos 'silencios' estadísticamente "
                    "anómalos comparados con la frecuencia habitual de tu negocio."
                ),
                "business_impact": (
                    "Los huecos pueden hacer que parezca que el rendimiento ha caído "
                    "cuando en realidad es solo un retraso en la sincronización. Intelligence 2.0 "
                    "marca estas zonas como 'baja confianza' para evitar alarmas innecesarias."
                ),
                "caveats": [
                    "Podría ser una caída real de ventas o una pausa intencionada en campañas.",
                    "No necesariamente indica un fallo técnico, sino un cambio en el patrón de datos.",
                    "Si es recurrente, podría indicar una conexión de API inestable."
                ]
            },
            "critical_nan": {
                "what_it_means": (
                    "Faltan datos en campos que son esenciales para el análisis. Por ejemplo, "
                    "registros de ventas sin importe o sin fecha asociada."
                ),
                "how_calculated": (
                    "Escaneamos las columnas vitales para cada algoritmo y contamos cuántas "
                    "celdas están vacías o contienen valores inválidos."
                ),
                "business_impact": (
                    "Sin estos datos, los modelos tienen que 'estimar' o ignorar registros, "
                    "lo que reduce la precisión de tu LTV o MMM. Ayudamos a identificar qué "
                    "campos debes completar en tu CRM o ERP."
                ),
                "caveats": [
                    "A veces la falta de dato es normal (ej: un cliente nuevo sin histórico).",
                    "No siempre es un error, pero sí es un límite para la precisión de la IA.",
                    "Intelligence 2.0 usa 'fallbacks' seguros para operar incluso con estos vacíos."
                ]
            }
        },
        "business": {
            "mer": {
                "what_it_means": (
                    "Es el Marketing Efficiency Ratio. Mide cuántos euros de ingresos totales "
                    "generas por cada euro invertido en marketing total."
                ),
                "how_calculated": (
                    "Dividimos los Ingresos Brutos Totales entre la Inversión en Marketing Total. "
                    "A diferencia del ROAS, el MER ofrece una visión holística de todo tu ecosistema."
                ),
                "business_impact": (
                    "Un MER alto indica un crecimiento saludable y orgánico. Un MER bajo sugiere "
                    "que dependes demasiado de la captación pagada para mantener tus ingresos."
                ),
                "caveats": [
                    "No detecta qué canal específico está fallando, para eso mira el ROAS.",
                    "El MER óptimo varía según el sector y tu margen de producto.",
                    "A corto plazo puede bajar si estás invirtiendo mucho en marca (branding)."
                ]
            },
            "retention": {
                "what_it_means": (
                    "Es el porcentaje de clientes que vuelven a comprar después de su primera adquisición."
                ),
                "how_calculated": (
                    "Usamos análisis de cohortes real para ver qué porcentaje de los clientes "
                    "captados en un mes específico realizaron al menos una compra el mes siguiente."
                ),
                "business_impact": (
                    "Es la métrica de salud definitiva. Si la retención sube, tu LTV subirá "
                    "exponencialmente sin aumentar tu coste de captación."
                ),
                "caveats": [
                    "Requiere al menos 3-6 meses de histórico para ser estadísticamente relevante.",
                    "Un mes bajo no siempre es malo si vendes productos de compra esporádica.",
                    "Esta métrica alimenta a la IA para predecir el futuro de tus nuevos clientes."
                ]
            },
            "poas": {
                "what_it_means": "Profitability Over Ad Spend. Mide el beneficio bruto real tras descontar el coste del producto y el gasto en anuncios.",
                "how_calculated": "(Ventas - COGS) / Inversión de Marketing. Es mucho más preciso que el ROAS.",
                "business_impact": "Te dice cuánto dinero metes realmente en el banco por cada euro invertido, no solo cuánto facturas.",
                "caveats": ["Asume un margen estimado si no tenemos datos de coste de producto.", "Un POAS > 1 significa que la publicidad se paga a sí misma y cubre el coste del producto."]
            },
            "pareto": {
                "what_it_means": "Análisis de Concentración 80/20. Identifica qué porcentaje de tus ingresos depende de tu top 20% de clientes.",
                "how_calculated": "Sumamos el dinero gastado por el 20% de los clientes con mayor gasto y lo dividimos por la facturación total.",
                "business_impact": "Si este número es muy alto (ej: > 70%), tu negocio es vulnerable. Si pierdes a unos pocos clientes 'VIP', tus ingresos sufrirán mucho.",
                "caveats": ["Es normal que los VIP gasten más, pero la dependencia extrema es un riesgo.", "La IA usa esto para predecir si el LTV es estable o volátil."]
            },
            "reinforcement": {
                "what_it_means": "Refuerzo Algorítmico (Intelligence 2.0). La IA usa estas métricas de negocio para 'corregirse' a sí misma.",
                "how_calculated": "Usamos Priores Bayesianos. Si el modelo matemático es incierto pero el negocio es estable (buen MER/Retención), la IA se inclina hacia la estabilidad.",
                "business_impact": "Evita que la IA tome decisiones erráticas basadas en ruido o pocos datos, anclándola en la realidad probada de tu negocio.",
                "caveats": ["La IA sigue mandando, los métricas solo 'ayudan' en casos de duda.", "Esto aumenta la precisión en periodos de pocos datos o mucha volatilidad."]
            }
        }
    },
    
    # =========================================================================
    # ENGLISH
    # =========================================================================
    "en": {
        # ---------------------------------------------------------------------
        # LTV / CHURN
        # ---------------------------------------------------------------------
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
                "business_impact": (
                    "If you identify your best customers (the 19% who generate 67% of revenue), "
                    "you can focus your retention budget where it really matters. "
                    "This can mean protecting millions in revenue at a fraction of the cost."
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
            },
            "churn_probability": {
                "what_it_means": (
                    "The risk that this customer will not buy again. "
                    "A high value indicates they may be losing interest or have left."
                ),
                "how_calculated": (
                    "It is the complement of the probability of being active. "
                    "If there is a 70% chance they are still active, there is a 30% chance they won't return."
                ),
                "business_impact": (
                    "Detecting at-risk customers BEFORE they leave allows you to "
                    "launch proactive retention offers. If your radar detects 89% of churners, "
                    "you could protect $142K annually that would be lost without intervention."
                ),
                "caveats": [
                    "A customer may return after a long time, even if the model considers them 'churned'.",
                    "Factors like seasonality can temporarily affect this metric.",
                    "It doesn't distinguish between customers who left or simply have long purchase cycles."
                ]
            },
            "expected_purchases": {
                "what_it_means": (
                    "The number of purchases we expect this customer to make "
                    "in the specified period, based on their historical pattern."
                ),
                "how_calculated": (
                    "We use the customer's historical frequency and their probability of remaining "
                    "active to project how many purchases they will make."
                ),
                "caveats": [
                    "It's an expected average. The customer may buy more or fewer times.",
                    "Assumes they will maintain their usual purchase pace."
                ]
            },
            "recency": {
                "what_it_means": (
                    "How many days have passed since this customer's last purchase."
                ),
                "how_calculated": (
                    "We simply subtract today's date minus the date of their last purchase."
                ),
                "caveats": [
                    "A high number isn't always bad: some products have long purchase cycles.",
                    "Compare it with the typical frequency of this specific customer."
                ]
            },
            "segment": {
                "what_it_means": (
                    "Customer classification according to their value and activity. "
                    "Helps prioritize retention and marketing efforts."
                ),
                "how_calculated": (
                    "We combine Lifetime Value (CLV) and the probability of remaining active "
                    "to classify as: VIP (high value, active), At Risk (high value, "
                    "low activity), Regular (medium value), or Lost (prolonged low activity)."
                ),
                "caveats": [
                    "Segments are useful simplifications, not absolute categories.",
                    "A customer may move between segments over time."
                ]
            },
            "revenue_velocity": {
                "what_it_means": (
                    "The speed at which this customer's value is growing. "
                    "A high velocity indicates a customer who is accelerating their spend."
                ),
                "how_calculated": (
                    "We calculate the derivative of revenue with respect to time. If a customer "
                    "spent $10/month and now spends $20/month, their velocity has doubled."
                ),
                "business_impact": (
                    "High-velocity customers are your future stars. "
                    "Identifying them allows incentive for that growth before it stabilizes."
                ),
                "caveats": [
                    "One-off spikes can artificially inflate velocity.",
                    "Requires at least two data points to be calculated."
                ]
            },
            "attention_weight": {
                "what_it_means": (
                    "Indicates which time period was most decisive for this prediction. "
                    "It's the 'focus' of our Artificial Intelligence."
                ),
                "how_calculated": (
                    "We use an Attention layer in the neural model that assigns weights "
                    "to each month. Months with more weight have influenced the final result more."
                ),
                "business_impact": (
                    "Knowing what event caused the prediction allows you to replicate that success "
                    "or understand what changed in the customer relationship."
                ),
                "caveats": [
                    "It's a measure of relative importance within the sequence.",
                    "Does not indicate direct causality, only statistical relevance for the model."
                ]
            }
        },
        "mmm": {
            "roas": {
                "what_it_means": (
                    "How much revenue you generate for every dollar invested in this advertising channel. "
                    "A ROAS of 3x means for every $1 invested, you get $3 in sales."
                ),
                "how_calculated": (
                    "We divide sales attributable to the channel by the total investment in that channel. "
                    "We use a model that considers advertising effects last beyond the day it's shown."
                ),
                "caveats": [
                    "Attribution is never 100% precise. Some sales would happen without advertising.",
                    "ROAS doesn't consider margin: high ROAS with low margin may not be profitable."
                ]
            },
            "saturation": {
                "what_it_means": (
                    "Indicates how much room there is to invest more in this channel before "
                    "returns start to diminish. A value near 1 means the channel is saturated."
                ),
                "how_calculated": (
                    "We analyze how return changes as investment increases. When investing more "
                    "generates fewer additional sales, the channel is saturating."
                ),
                "caveats": [
                    "Saturation can vary by seasonality.",
                    "Changes in creatives or audiences can 'desaturate' a channel."
                ]
            }
        },
        "thompson": {
            "conversion_rate": {
                "what_it_means": "The percentage of times this variant achieved the goal when shown.",
                "how_calculated": "Conversions divided by total samples for this variant.",
                "caveats": ["With few samples, the rate can be very variable.", "External factors peuvent affecter rates."]
            },
            "prob_best": {
                "what_it_means": "The probability that this is the best variant among all options.",
                "how_calculated": "Simulation of thousands of scenarios based on observed data.",
                "caveats": ["This probability changes as more data is collected."]
            }
        },
        "integrity": {
            "duplicate": {
                "what_it_means": "We have detected records that appear to be repeated.",
                "how_calculated": "Search for transactions with same ID or identical features in short periods.",
                "business_impact": "Prevents artificial inflation of revenue or ROAS.",
                "caveats": ["Could be legitimate identical purchases in some cases."]
            },
            "gap": {
                "what_it_means": "There appear to be periods of time with no registered activity.",
                "how_calculated": "Chronological flow analysis for statistically anomalous 'silences'.",
                "business_impact": "Avoids false alarms about performance drops due to sync delays.",
                "caveats": ["Could be a real sales drop or intentional campaign pause."]
            }
        },
        "business": {
            "mer": {
                "what_it_means": "Marketing Efficiency Ratio. Total revenue divided by total marketing spend.",
                "how_calculated": "Total Gross Revenue / Total Ad Spend across all channels.",
                "business_impact": "A high MER indicates healthy organic growth; a low MER suggests over-reliance on paid ads.",
                "caveats": [
                    "High-level metric; doesn't show individual channel efficiency.",
                    "Healthy benchmarks vary by business model."
                ]
            },
            "retention": {
                "what_it_means": "The percentage of customers returning for repeat purchases.",
                "how_calculated": "Real-world cohort analysis identifying monthly return rates.",
                "business_impact": "Definitive health metric. If retention rises, LTV rises exponentially without increasing CAC.",
                "caveats": [
                    "Requires several months of data for accuracy.",
                    "Seasonal business may see normal fluctuations."
                ]
            },
            "poas": {
                "what_it_means": "Profitability Over Ad Spend. Measures real gross profit after product cost and ad spend.",
                "how_calculated": "(Sales - COGS) / Marketing Spend.",
                "business_impact": "Tells you how much money you actually put in the bank per dollar invested.",
                "caveats": ["Assumes estimated margin if product cost data is missing."]
            },
            "pareto": {
                "what_it_means": "80/20 Concentration Analysis. Identifies the percentage of revenue depending on top 20% of customers.",
                "how_calculated": "Revenue from top 20% high-spending customers / total revenue.",
                "business_impact": "Extremely high concentration (>70%) makes the business vulnerable to losing a few VIPs.",
                "caveats": ["Extreme dependency is a risk, even if VIPs naturally spend more."]
            }
        }
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
