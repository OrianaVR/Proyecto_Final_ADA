# Nota de traspaso - HU-10 a HU-12

1. `PlanificadorViaje` es el coordinador único de validaciones y algoritmos.
2. La secuencia completa usa Dijkstra por tramos.
3. La secuencia parcial o ausente usa Branch and Bound.
4. `PantallaFormulario` construye `Entrada` y muestra errores al usuario.
5. `PantallaResultados` ordena por peso y detalla cada tramo.
6. El callback de la aplicación transfiere el `ResultadoPlanificacion`.
7. La suite ejecutada validó los algoritmos existentes y el coordinador: 94 pruebas aprobadas.
8. La validación funcional confirmó los flujos de orden total y orden parcial hasta resultados.
9. Se verificaron los mensajes de ciclo, precedencia, exceso de destinos y presupuesto insuficiente.
10. También se confirmó el orden ascendente por peso, el desglose por tramo y el presupuesto restante.
