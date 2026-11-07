from __future__ import annotations
from typing import Dict, List, Sequence

from lib.algorithms.dijkstra import (
    METRICA_DINERO,
    METRICA_PESO,
    CaminoMinimo,
    armar_camino,
    dijkstra_desde,
    reconstruir_camino,
)
from lib.structures.grafo import Grafo


class MatrizCaminos:

    def __init__(
        self,
        grafo: Grafo,
        nodos: List[int],
        caminos_peso: Dict[int, Dict[int, CaminoMinimo]],
        caminos_dinero: Dict[int, Dict[int, CaminoMinimo]],
    ):
        self.grafo = grafo
        self.nodos: List[int] = list(nodos)
        self._pos: Dict[int, int] = {nodo: i for i, nodo in enumerate(self.nodos)}
        self._caminos_peso = caminos_peso
        self._caminos_dinero = caminos_dinero

        n = len(self.nodos)
        self.d_peso: List[List[float]] = [[0.0] * n for _ in range(n)]
        self.d_dinero: List[List[float]] = [[0.0] * n for _ in range(n)]
        self.d_min: List[List[float]] = [[0.0] * n for _ in range(n)]
        for a in self.nodos:
            for b in self.nodos:
                i, j = self._pos[a], self._pos[b]
                self.d_peso[i][j] = caminos_peso[a][b].peso
                self.d_dinero[i][j] = caminos_peso[a][b].dinero
                self.d_min[i][j] = caminos_dinero[a][b].dinero

    # ------------------------------------------------------------------ construcción
    @classmethod
    def construir(
        cls, grafo: Grafo, origen: int, destinos: Sequence[int]
    ) -> "MatrizCaminos":
        """Corre Dijkstra desde cada nodo (con peso y con dinero) y arma la matriz.

        Lanza ValueError si hay destinos repetidos o si el origen está entre los
        destinos; IndexError si algún id no existe en el grafo.
        """
        destinos = list(destinos)
        if origen in destinos:
            raise ValueError(f"El origen ({origen}) no puede estar entre los destinos a visitar.")
        if len(set(destinos)) != len(destinos):
            raise ValueError("La lista de destinos tiene ciudades repetidas.")

        nodos = [origen] + destinos
        for nodo in nodos:
            if not (0 <= nodo < grafo.num_destinos):
                raise IndexError(
                    f"Ciudad fuera de rango: {nodo} (el grafo tiene {grafo.num_destinos} destinos)."
                )
        seleccionadas = set(nodos)

        caminos_peso: Dict[int, Dict[int, CaminoMinimo]] = {}
        caminos_dinero: Dict[int, Dict[int, CaminoMinimo]] = {}
        for a in nodos:
            caminos_peso[a] = cls._desde(grafo, a, nodos, seleccionadas, METRICA_PESO)
            caminos_dinero[a] = cls._desde(grafo, a, nodos, seleccionadas, METRICA_DINERO)
        return cls(grafo, nodos, caminos_peso, caminos_dinero)

    @staticmethod
    def _desde(
        grafo: Grafo, a: int, nodos: List[int], seleccionadas: set, metrica: str
    ) -> Dict[int, CaminoMinimo]:
        # Un solo Dijkstra por origen sirve para todos los destinos de la matriz.
        _, previo = dijkstra_desde(grafo, a, metrica, prohibidos=seleccionadas)
        resultado: Dict[int, CaminoMinimo] = {}
        for b in nodos:
            camino = [a] if a == b else reconstruir_camino(previo, a, b)
            resultado[b] = armar_camino(grafo, camino, metrica)
        return resultado

    # ------------------------------------------------------------------ consulta por id
    def _validar(self, a: int, b: int) -> None:
        for x in (a, b):
            if x not in self._pos:
                raise KeyError(f"La ciudad {x} no pertenece a la matriz (nodos: {self.nodos}).")

    def posicion(self, ciudad: int) -> int:
        """Posición de una ciudad dentro de las matrices crudas."""
        self._validar(ciudad, ciudad)
        return self._pos[ciudad]

    def peso(self, a: int, b: int) -> float:
        """Peso combinado mínimo de a a b."""
        self._validar(a, b)
        return self.d_peso[self._pos[a]][self._pos[b]]

    def dinero(self, a: int, b: int) -> float:
        """Dinero del camino de menor peso de a a b."""
        self._validar(a, b)
        return self.d_dinero[self._pos[a]][self._pos[b]]

    def dinero_min(self, a: int, b: int) -> float:
        """Dinero mínimo posible de a a b."""
        self._validar(a, b)
        return self.d_min[self._pos[a]][self._pos[b]]

    def camino_peso(self, a: int, b: int) -> CaminoMinimo:
        """Camino de menor peso de a a b (con sus ciudades de paso)."""
        self._validar(a, b)
        return self._caminos_peso[a][b]

    def camino_dinero(self, a: int, b: int) -> CaminoMinimo:
        """Camino de menor dinero de a a b (con sus ciudades de paso)."""
        self._validar(a, b)
        return self._caminos_dinero[a][b]
