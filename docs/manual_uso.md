# Manual de uso — TravelPath

TravelPath planifica itinerarios turísticos entre ciudades combinando el costo
del transporte y el tiempo de viaje, respetando tu presupuesto y el orden en que
quieras visitar los destinos. Este manual explica cómo usar la aplicación paso a
paso.

---

## 1. Pantalla de formulario

Es la primera pantalla. Define el viaje que quieres planificar.

### Origen
Elige en el desplegable la ciudad desde la que sales. Es el punto de partida del
recorrido.

### Destinos
Selecciona con los chips las ciudades que quieres visitar. Puedes elegir **hasta
12 destinos**; si intentas más, la aplicación lo rechaza (ver sección 4). El
origen no cuenta como destino y no puede repetirse en la lista.

### Presupuesto
Escribe el presupuesto en pesos. Es un **límite duro sobre el dinero real**: la
aplicación solo propone rutas cuyo costo total en pesos cabe dentro de esa cifra.
El presupuesto nunca se compara contra el «peso» (ver más abajo), sino contra el
dinero.

### Cantidad de rutas (K)
Indica cuántas rutas quieres ver como máximo. Por defecto, 10. La aplicación
devuelve las **K mejores** ordenadas de menor a mayor peso.

### Ida y vuelta
Si activas este interruptor, el recorrido suma el **tramo de regreso al origen**
tanto al peso como al dinero. Si lo dejas apagado, el viaje termina en el último
destino (solo ida).

### Ajustar precio / tiempo (ponderaciones α y β)
El «peso» de cada tramo combina costo y tiempo con la fórmula:

```
peso(i, j) = α · costo_normalizado(i, j) + β · tiempo_normalizado(i, j)
```

El deslizador α/β te permite decidir qué priorizar:

- **Más hacia α (precio):** se minimiza sobre todo el dinero. Útil si el
  presupuesto es ajustado.
- **Más hacia β (tiempo):** se minimiza sobre todo el tiempo de viaje. Útil si
  tienes prisa.

El costo y el tiempo se **normalizan** antes de combinarlos, de modo que el
dinero (que se mide en miles) no aplaste al tiempo (que se mide en horas).

### Definir orden (opcional)
Con el interruptor «Definir orden» puedes influir en la secuencia de visita:

- **Reordenar la lista:** arrastra los destinos para fijar una secuencia
  completa. En ese caso la aplicación respeta ese orden exacto y calcula el
  camino más barato entre cada par consecutivo.
- **«Este primero» / precedencias:** marca que una ciudad debe visitarse antes
  que otra. La aplicación busca el mejor orden que respete esas reglas.

Si no defines ningún orden, la aplicación busca libremente el mejor orden
posible.

### Calcular
Pulsa **«Calcular»** para generar las rutas. Pasas a la pantalla de resultados.

---

## 2. Pantalla de resultados

Muestra las rutas encontradas, de la mejor a la peor según su peso.

- La **mejor ruta** aparece resaltada y marcada con una estrella (★).
- Cada ruta indica su **peso** (adimensional, solo para ordenar), su **dinero**
  en pesos y su **tiempo** total en horas.
- Se muestra el **presupuesto restante** de cada ruta (cuánto sobra).
- El **desglose por tramo** lista cada salto del recorrido con su costo y tiempo,
  incluyendo las **ciudades de paso** (ciudades por las que se pasa aunque no
  las hayas seleccionado, cuando pasar por ellas resulta más barato).
- Si la búsqueda se detuvo por límite de tiempo o de nodos, verás el aviso
  **«Mejor encontrada, no garantizada como óptima»**.

Cada ruta tiene un botón **«Ver en grafo»** que abre la pantalla de grafo con esa
ruta concreta.

---

## 3. Pantalla de grafo visual

Dibuja los destinos como nodos distribuidos en círculo.

- Cada **conexión** entre ciudades se dibuja con su **peso** como etiqueta.
- El **nodo origen** se resalta con un color distinto (ámbar).
- La **ruta seleccionada** se resalta en verde sobre el resto del grafo.

### Simular el recorrido
Pulsa **«Simular recorrido»** para animar la ruta. La animación ilumina el
recorrido **tramo por tramo en el orden de la ruta**:

- El **tramo actual** se marca en naranja y más grueso.
- Los tramos **ya recorridos** quedan en verde.
- Los tramos **pendientes** se ven en verde tenue.
- El **nodo al que llega** cada tramo se marca como activo.

La animación respeta el regreso al origen (si activaste ida y vuelta) y las
ciudades de paso, porque recorre los tramos tal como se calcularon.

Usa la flecha **«Volver»** para regresar a los resultados.

---

## 4. Mensajes de error y cómo interpretarlos

La aplicación valida tu entrada y muestra mensajes claros cuando algo no cuadra:

| Mensaje | Qué significa | Cómo resolverlo |
| --- | --- | --- |
| **«Ninguna ruta cabe en tu presupuesto; el mínimo necesario es $X»** | Ni la ruta más barata entra en tu presupuesto. | Aumenta el presupuesto al menos hasta el mínimo indicado, o quita destinos. |
| **Precedencias en ciclo** (menciona las ciudades) | Pusiste reglas contradictorias (A antes que B y B antes que A). | Revisa las precedencias y elimina el ciclo. |
| **Secuencia que viola una precedencia** (menciona las ciudades) | El orden que fijaste no respeta una regla «A antes que B». | Reordena los destinos para cumplir la precedencia. |
| **«Demasiados destinos»** | Seleccionaste más de 12 destinos. | Reduce la selección a 12 o menos. |

---

## 5. Notas importantes

- El **listado completo** de rutas se implementa como el **listado ordenado de
  las K mejores**. Con muchos destinos el número de órdenes posibles crece como
  `n!` (millones a partir de 10 destinos), por lo que la aplicación lista las K
  mejores en vez de todas. Consulta el [informe de poda](tabla_poda.md) para el
  detalle.
- El **peso** es adimensional y solo sirve para ordenar y optimizar. El
  **presupuesto** siempre se compara contra el **dinero real** en pesos.
