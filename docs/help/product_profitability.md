# Rentabilidad por Producto

> Descubre qué productos realmente te dan dinero y cuáles te lo quitan después de descontar TODOS los costes.

---

## ¿Qué es la Rentabilidad por Producto?

La mayoría de negocios miran el **precio de venta** y el **coste del producto** para calcular margen. Pero eso ignora muchos otros costes:

| Lo que muchos miran | Lo que Tactics analiza |
|---------------------|------------------------|
| Precio venta: 50€ | Precio venta: 50€ |
| Coste producto: 15€ | Coste producto: 15€ |
| **Margen: 35€** (70%) | Coste envío: 4€ |
| | Coste almacén: 0,50€ |
| | Publicidad atribuida: 8€ |
| | **Margen REAL: 22,50€** (45%) |

Esos 12,50€ de diferencia multiplicados por miles de ventas son una fortuna escondida (o perdida).

---

## ¿Cómo lo calcula Tactics?

### Costes que descontamos:

1. **Coste del producto (COGS)**: Lo que pagas al proveedor
2. **Coste de envío**: Tu coste medio por pedido
3. **Coste de almacenaje**: Por unidad/mes si aplica
4. **Publicidad atribuida**: Parte proporcional del gasto en ads
5. **Coste de devolución** (si hay): Envío de retorno + gestión

### Fórmula simplificada:

> **Margen Neto** = Precio venta - COGS - Envío - Almacén - Publicidad - Devoluciones

---

## ¿Dónde lo veo?

### En la vista de Productos:
- Columna **"Margen Neto"** junto a cada producto
- Columna **"Margen %"** en porcentaje
- Indicador visual: 🟢 rentable / 🟡 ajustado / 🔴 pérdida

### En el Dashboard:
- **Widget "Productos con pérdida"**: Número de productos con margen negativo
- **"Top 10 productos rentables"**: Los que más beneficio generan

---

## Clasificación de productos

Tactics clasifica automáticamente tus productos:

| Categoría | Descripción | Acción recomendada |
|-----------|-------------|-------------------|
| 🐋 **Ballena de beneficio** | Alto margen + alto volumen | Promocionar más, nunca descontar |
| ⭐ **Rentable** | Margen positivo saludable | Mantener estrategia actual |
| ⚠️ **Margen ajustado** | Margen positivo pero bajo (< 15%) | Revisar costes o subir precio |
| 🔴 **Pérdida** | Margen negativo | Subir precio, reducir ads, o descatalogar |
| 🐌 **Lento** | Rentable pero se vende poco | Considerar bundles o promociones |

---

## El problema de los "productos trampa"

Algunos productos parecen populares pero destruyen beneficio:

### Ejemplo real:

| Producto | Ventas | Precio | Margen aparente | Margen REAL |
|----------|--------|--------|-----------------|-------------|
| Camiseta básica | 500/mes | 19,90€ | 8€ (40%) | -2€ 🔴 |

¿Cómo es posible? El coste de publicidad por venta (CPA) era de 12€, convirtiendo cada venta en una pérdida.

**Sin Tactics**: "¡Genial, vendemos 500 camisetas!"  
**Con Tactics**: "Cada camiseta nos cuesta 2€. Hemos perdido 1,000€ este mes."

---

## Qué hacer con cada tipo de producto

### 🐋 Ballenas de beneficio
- **Método**: Escalar todo lo posible
- **Acciones**: Más presupuesto en ads, mejor posición en web, nunca descontar

### 🔴 Productos con pérdida
1. **Revisar el precio**: ¿Puedes subirlo un 10-15%?
2. **Reducir publicidad**: Excluir de campañas hasta que sea rentable orgánicamente
3. **Analizar costes**: ¿Puedes negociar mejor con el proveedor?
4. **Último recurso**: Descatalogar

### 🐌 Productos lentos (rentables pero no se venden)
- **Opción A**: Crear bundle con producto popular
- **Opción B**: Promoción limitada para mover stock
- **Opción C**: Reducir inventario y mantener solo bajo pedido

---

## Cómo proporcionar datos de coste

Para que Tactics calcule el margen real, necesita los costes:

### Opción 1: Automático desde Shopify
Si tienes el campo "Coste por artículo" relleno en Shopify, Tactics lo detecta automáticamente.

### Opción 2: Subir archivo
Ve a **Configuración → Costes de producto** y sube un CSV:

```csv
sku,coste_producto,coste_envio
CAM-001,8.50,2.10
PAN-002,12.00,3.50
```

### Opción 3: Estimación global
Si no tienes datos exactos, indica un margen medio estimado:
> "Mi margen medio es del 45%"

Tactics usará esta estimación hasta que tengas datos reales.

---

## El coste de publicidad atribuida

Tactics distribuye tu gasto en publicidad entre los productos que promocionas:

### Ejemplo:
- Gastas 1,000€ en Meta Ads
- Esa campaña genera 100 ventas
- De esas, 40 son del producto A, 60 del producto B

**Atribución**:
- Producto A: 400€ de publicidad (40%)
- Producto B: 600€ de publicidad (60%)

Esto se refleja en el margen neto de cada producto.

---

## Preguntas frecuentes

### "¿Por qué algunos productos muestran 'Datos insuficientes'?"

Para calcular la publicidad atribuida, necesitamos al menos 10 ventas de ese producto en los últimos 90 días. Con menos ventas, el cálculo sería poco fiable.

### "¿Los descuentos afectan al margen?"

Sí. Si vendes un producto a 50€ normal pero con 20% de descuento a 40€, el margen se calcula sobre 40€, no sobre 50€.

### "¿Cómo sé si debo descatalogar un producto?"

Si un producto tiene:
- Margen negativo por más de 3 meses
- No es estratégico (no atrae tráfico que compra otras cosas)
- No hay forma de mejorar su margen

...probablemente deberías descatalogarlo.

### "¿Puedo ver el margen por variante (tallas, colores)?"

Si tu tienda tiene datos de coste por variante, sí. Si solo tienes coste por producto padre, Tactics usa el mismo coste para todas las variantes.

---

## Siguiente paso

→ [Recomendador de Bundles](./bundle_recommendations.md) — Combinaciones que aumentan el ticket

---

**¿Dudas?** soporte@tactics.es
