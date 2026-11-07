"""Utilidades compartidas por los tests de Dijkstra, la matriz de caminos y el orden total.

- crear_grafo: arma un Grafo pequeño a mano a partir de matrices.
- mejor_valor_bruto: oráculo independiente. Enumera TODOS los caminos simples entre
  dos ciudades (solo pasando por ciudades permitidas) y devuelve el menor valor de una
  métrica. Sirve para comprobar que Dijkstra no se equivoca sin depender de él.
"""

from typing import Iterable, List, Optional

from lib.models.destino import Destino
from lib.structures.grafo import Grafo


def crear_grafo(
    costo: List[List[float]],
    tiempo: List[List[float]],
    alfa: float = 0.5,
    beta: float = 0.5,
) -> Grafo:
    n = len(costo)
    destinos = [Destino(id=i, nombre=f"C{i}") for i in range(n)]
    return Grafo(destinos, costo, tiempo, alfa=alfa, beta=beta)


def mejor_valor_bruto(
    grafo: Grafo,
    a: int,
    b: int,
    metrica: str,
    prohibidos: Optional[Iterable[int]] = None,
) -> float:
    """Menor valor de `metrica` entre a y b, recorriendo todos los caminos simples."""
    medir = {"peso": grafo.peso, "dinero": grafo.costo, "tiempo": grafo.tiempo}[metrica]
    bloqueados = set(prohibidos or [])
    if a == b:
        return 0.0
    mejor = [float("inf")]

    def explorar(u: int, visitados: set, acumulado: float) -> None:
        if acumulado > mejor[0]:
            return
        for v in range(grafo.num_destinos):
            if v == u or v in visitados:
                continue
            nuevo = acumulado + medir(u, v)
            if v == b:
                mejor[0] = min(mejor[0], nuevo)
            elif v not in bloqueados:
                explorar(v, visitados | {v}, nuevo)

    explorar(a, {a}, 0.0)
    return mejor[0]
