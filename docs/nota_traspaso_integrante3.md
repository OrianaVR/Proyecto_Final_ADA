### Nota de Traspaso: Integrante 3 -> Integrante 4 (UI / Integración)
1. `BranchAndBound(matriz, presupuesto, precedencias=None, k=10, ida_y_vuelta=False, limite_nodos=None, limite_segundos=None)`: Constructor.
2. `bb.mejores_rutas() -> ResultadoBB`: Retorna las top-K rutas óptimas en orden ascendente de peso combinado.
3. `ResultadoBB.rutas: List[Ruta]`: Lista de itinerarios con destinos, peso_total, costo_total ($), tiempo_total, tramos y ciudades_paso.
4. `ResultadoBB.mejor_ruta -> Optional[Ruta]`: Retorna la mejor ruta encontrada o None si no hubo solución factible.
5. `ResultadoBB.garantizado_optimo: bool`: True si se demostró optimalidad; False si se agotó límite de tiempo o nodos.
6. `ResultadoBB.estadisticas: EstadisticasPoda`: Nodos generados, expandidos, podas (precedencia, presupuesto, costo) y tiempo.
7. `bb.cota_peso(u, restantes)` y `bb.cota_dinero(u, restantes)`: Cotas inferiores admisibles para peso y dinero ($).
8. `fuerza_bruta_rutas(matriz, presupuesto, precedencias=None, k=10, ida_y_vuelta=False) -> List[Ruta]`: Oráculo de tests.
9. Validaciones: Lanza ValueError si destinos > 12 o k <= 0; presupuesto compara contra dinero, nunca contra peso.