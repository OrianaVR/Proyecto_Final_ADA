### Nota de Traspaso: Integrante 1 (Nandez) -> Integrante 2
1. `Grafo.desde_json(ruta=None, alfa=0.5, beta=0.5) -> Grafo`: Carga JSON y calcula matrices normalizadas.
2. `grafo.peso(i: int, j: int) -> float`: Retorna peso combinado normalizado para Dijkstra Dpeso.
3. `grafo.costo(i: int, j: int) -> float`: Retorna costo real en dinero ($) para Dijkstra Ddinero / Dmin.
4. `grafo.tiempo(i: int, j: int) -> float`: Retorna duración real en horas del tramo entre i y j.
5. `grafo.vecinos(i: int) -> List[int]`: Retorna IDs de ciudades accesibles desde i (excluye i).
6. `grafo.configurar_pesos(alfa: float, beta: float) -> None`: Actualiza pesos según prioridad.
7. `TablaPrecedencias()` / `tabla.agregar_precedencia(antes: int, despues: int) -> None`: Guarda orden parcial.
8. `tabla.puede_visitar(destino: int, visitados: Set[int]) -> bool`: Valida en O(1) si destino puede visitarse.
9. `tabla.detectar_ciclo() -> Optional[List[int]]`: Retorna ciclo o None; `tabla.validar_sin_ciclos()` lanza excepción.
10. Modelos base: `Destino(id, nombre)`, `Arista(u, v, costo, tiempo, peso)`, `Ruta`, `Entrada`, `Restricciones`.
