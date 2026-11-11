# Manual de uso — TravelPath

TravelPath planifica itinerarios turísticos entre ciudades combinando el costo
del transporte y el tiempo de viaje, respetando tu presupuesto y el orden en que
quieras visitar los destinos. Este manual explica cómo usar la aplicación paso a
paso.

---

## 1. Pantalla de datos del viaje

Es la primera pantalla. Define los parámetros generales del viaje.

### Origen
Elige en el desplegable la ciudad desde la que sales. Es el punto de partida del
recorrido.

### Destinos
Selecciona con las casillas las ciudades que quieres visitar. Puedes elegir
**hasta 12 destinos**; el origen no puede repetirse como destino.

### Presupuesto
Escribe el presupuesto en pesos. Es un **límite duro sobre el dinero real**: la
aplicación solo propone rutas cuyo costo total en pesos cabe dentro de esa cifra.
El presupuesto nunca se compara contra el «peso».

### Cantidad de alternativas

Indica cuántas opciones quieres comparar como máximo. Por defecto, se muestran
10 alternativas ordenadas según tus preferencias.

### Prioridad del viaje

Mueve el control entre estas opciones:

- **Ahorrar tiempo:** prioriza recorridos más rápidos.
- **Equilibrar:** combina tiempo y dinero por igual.
- **Ahorrar dinero:** prioriza recorridos más económicos.

Internamente estas preferencias se convierten en ponderaciones para el peso
combinado, pero no necesitas conocer esos términos técnicos para usar la
aplicación.

### Ida y vuelta
Si activas este interruptor, el recorrido suma el **tramo de regreso al origen**
tanto al peso como al dinero. Si lo dejas apagado, el viaje termina en el último
destino (solo ida).

### Prioridad del viaje

Mueve el control entre **Ahorrar tiempo**, **Equilibrar** y **Ahorrar dinero**.
La aplicación normaliza costo y tiempo antes de combinarlos para que ninguna
unidad domine injustamente. El usuario no necesita conocer α ni β para utilizar
esta opción.

Pulsa **«Continuar al orden de visita»** para pasar a la segunda pantalla.

---

## 2. Pantalla de orden de visita

La segunda pantalla recibe los datos del viaje y te permite elegir cómo quieres
organizar el recorrido.

### Sin orden
El algoritmo decide libremente el mejor orden de visita respetando el
presupuesto y la configuración de ida y vuelta.

### Orden total
Selecciona **«Elegir el orden completo»** y arrastra las ciudades hasta obtener
la secuencia deseada. La aplicación respeta ese orden exacto y calcula el
camino más barato entre cada par consecutivo.

### Precedencias parciales
Selecciona **«Indicar prioridades entre destinos»** y agrega reglas como «Bogotá
antes que Medellín». También puedes indicar por qué ciudad quieres comenzar. Puedes eliminar cualquier regla
antes de calcular.

Si las reglas se contradicen, la aplicación informa el ciclo de precedencias.
Cuando no hay una ruta dentro del presupuesto, el mensaje de mínimo necesario
respeta las precedencias configuradas.

Pulsa **«Buscar mejores rutas»** para obtener los resultados, o **«Volver a
datos»** para modificar la selección inicial.

---

## 3. Pantalla de resultados

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

Si ninguna ruta cabe en el presupuesto, la aplicación muestra el mínimo
necesario y también ofrece **«Ver rutas de todos modos»** para revisar la mejor
alternativa aunque supere el límite.

---

## 4. Pantalla de grafo visual

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

## 5. Mensajes de error y cómo interpretarlos

La aplicación valida tu entrada y muestra mensajes claros cuando algo no cuadra:

| Mensaje | Qué significa | Cómo resolverlo |
| --- | --- | --- |
| **«Ninguna ruta cabe en tu presupuesto; el mínimo necesario es $X»** | Ni la ruta más barata entra en tu presupuesto. | Aumenta el presupuesto al menos hasta el mínimo indicado, o quita destinos. |
| **Precedencias en ciclo** (menciona las ciudades) | Pusiste reglas contradictorias (A antes que B y B antes que A). | Revisa las precedencias y elimina el ciclo. |
| **Secuencia que viola una precedencia** (menciona las ciudades) | El orden que fijaste no respeta una regla «A antes que B». | Reordena los destinos para cumplir la precedencia. |
| **«Demasiados destinos»** | Seleccionaste más de 12 destinos. | Reduce la selección a 12 o menos. |

---

## 6. Notas importantes

- La aplicación muestra la cantidad de alternativas que solicites, ordenadas de
  mejor a peor. Con muchos destinos el número de órdenes posibles crece como
  `n!` (millones a partir de 10 destinos), por lo que se muestran las mejores
  opciones en vez de todas. Consulta el [informe de poda](tabla_poda.md) para
  el detalle.
- El **peso** es adimensional y solo sirve para ordenar y optimizar. El
  **presupuesto** siempre se compara contra el **dinero real** en pesos.
