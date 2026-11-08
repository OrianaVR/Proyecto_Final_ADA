# Tabla de Poda: Branch and Bound vs Búsqueda Exhaustiva (n!)

Documento de análisis empírico y sustento teórico para la sustentación del proyecto **TravelPath** (Integrante 3).

---

## 1. Justificación Teórica de la Poda

En un recorrido turístico con $n$ destinos seleccionados a partir de una ciudad de origen, el espacio de búsqueda exhaustivo consta de $n!$ permutaciones posibles.

El algoritmo **Branch and Bound** (Ramificación y Poda) implementado en `BranchAndBound` utiliza una estrategia **Best-First Search** guiada por una cota inferior admisible $h(e)$:

$$h(e) = \sum_{d \in R} \min_{x \in R \cup \{u\}, x \neq d} D_{\text{peso}}[x][d]$$

Junto con la cota de dinero sobre la matriz $D_{\min}$:

$$\text{cota\_dinero}(e) = \sum_{d \in R} \min_{x \in R \cup \{u\}, x \neq d} D_{\min}[x][d]$$

Gracias a la admisibilidad matemática de las cotas y al ordenamiento en la cola de prioridad por $f = g + h$, al extraer la $K$-ésima ruta completa, se garantiza que ninguna rama pendiente en la cola puede mejorar las soluciones halladas. Esto permite podar la totalidad de nodos restantes en la cola (**Poda por Mejor Costo**), además de descartar anticipadamente ramas inviables por precedencia o presupuesto.

---

## 2. Resultados Empíricos (n = 5 a 10)

Mediciones promedio obtenidas sobre múltiples matrices de distancias calculadas con el grafo de ciudades colombianas (`assets/destinos.json`) para $K = 10$:

| $n$ (destinos) | Espacio total ($n!$) | Nodos Generados | Nodos Expandidos | Poda por Costo (cola) | Poda Presupuesto | % Espacio Podado | Tiempo Promedio |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **5** | 120 | 90.5 | 38.5 | 42.0 | 0.0 | **67.92%** | 1.51 ms |
| **6** | 720 | 208.5 | 74.7 | 123.8 | 0.0 | **89.62%** | 3.18 ms |
| **7** | 5,040 | 675.9 | 209.7 | 456.2 | 0.0 | **95.84%** | 11.03 ms |
| **8** | 40,320 | 3,088.1 | 960.7 | 2,117.4 | 0.0 | **97.62%** | 52.41 ms |
| **9** | 362,880 | 13,216.0 | 4,007.2 | 9,198.8 | 0.0 | **98.90%** | 243.72 ms |
| **10** | 3,628,800 | 20,895.2 | 4,775.5 | 16,109.8 | 0.0 | **99.87%** | 489.43 ms |

---

## 3. Conclusiones para la Sustentación

1. **Escalabilidad exponencial del espacio vs. linealidad controlada del B&B:**
   Mientras que para $n = 10$ el espacio factorial explota a más de 3.6 millones de permutaciones, el algoritmo Branch and Bound solo requiere expandir alrededor de 4,775 nodos (< 0.15% del árbol total).
2. **Efectividad de la Poda:**
   El porcentaje de poda supera el **95%** a partir de $n \ge 7$ y alcanza el **99.87%** en $n = 10$, manteniendo tiempos de respuesta interactivos (< 0.5 segundos) ideales para la interfaz gráfica del usuario.
3. **Poda por Presupuesto:**
   Cuando el presupuesto del usuario es ajustado, la cota inferior monetaria `cota_dinero` descarta ramas en niveles superiores del árbol, reduciendo aún más el número de nodos generados.
