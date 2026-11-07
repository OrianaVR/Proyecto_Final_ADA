from __future__ import annotations
from typing import List, Optional, Union
from pathlib import Path

from lib.models.destino import Destino
from lib.models.arista import Arista
from lib.data.destinos_repository import DestinosRepository


class Grafo:
    """Grafo ponderado de destinos que modela costos, tiempos y pesos combinados normalizados.
    
    Implementa una matriz de adyacencia double[][] para costo, tiempo y peso combinado,
    garantizando que el costo y el tiempo se normalicen a la misma escala [0, 1]
    para que el costo (en miles) no domine al tiempo (en horas).
    """

    def __init__(
        self,
        destinos: List[Destino],
        matriz_costo: List[List[float]],
        matriz_tiempo: List[List[float]],
        alfa: float = 0.5,
        beta: float = 0.5,
    ):
        self._destinos = list(destinos)
        self._n = len(destinos)
        self._matriz_costo = [list(fila) for fila in matriz_costo]
        self._matriz_tiempo = [list(fila) for fila in matriz_tiempo]
        
        self._map_nombre_a_id = {d.nombre.lower(): d.id for d in self._destinos}
        
        # Parámetros de ponderación
        self._alfa = float(alfa)
        self._beta = float(beta)
        
        # Matrices normalizadas y matriz de peso combinado
        self._matriz_costo_norm: List[List[float]] = []
        self._matriz_tiempo_norm: List[List[float]] = []
        self._matriz_peso: List[List[float]] = []
        
        self._calcular_normalizacion()
        self._recalcular_pesos()

    @property
    def num_destinos(self) -> int:
        """Número de nodos/destinos en el grafo."""
        return self._n

    @property
    def destinos(self) -> List[Destino]:
        """Lista de destinos disponibles."""
        return list(self._destinos)

    @property
    def alfa(self) -> float:
        return self._alfa

    @property
    def beta(self) -> float:
        return self._beta

    def _calcular_normalizacion(self) -> None:
        """Normaliza costos y tiempos de aristas (i != j) a la escala [0, 1]."""
        n = self._n
        costos_aristas = [
            self._matriz_costo[i][j]
            for i in range(n)
            for j in range(n)
            if i != j
        ]
        tiempos_aristas = [
            self._matriz_tiempo[i][j]
            for i in range(n)
            for j in range(n)
            if i != j
        ]

        if costos_aristas:
            self._min_costo = min(costos_aristas)
            self._max_costo = max(costos_aristas)
        else:
            self._min_costo = 0.0
            self._max_costo = 1.0

        if tiempos_aristas:
            self._min_tiempo = min(tiempos_aristas)
            self._max_tiempo = max(tiempos_aristas)
        else:
            self._min_tiempo = 0.0
            self._max_tiempo = 1.0

        rango_costo = self._max_costo - self._min_costo
        rango_tiempo = self._max_tiempo - self._min_tiempo

        self._matriz_costo_norm = [[0.0] * n for _ in range(n)]
        self._matriz_tiempo_norm = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i == j:
                    self._matriz_costo_norm[i][j] = 0.0
                    self._matriz_tiempo_norm[i][j] = 0.0
                else:
                    if rango_costo > 0:
                        self._matriz_costo_norm[i][j] = (self._matriz_costo[i][j] - self._min_costo) / rango_costo
                    else:
                        self._matriz_costo_norm[i][j] = 1.0

                    if rango_tiempo > 0:
                        self._matriz_tiempo_norm[i][j] = (self._matriz_tiempo[i][j] - self._min_tiempo) / rango_tiempo
                    else:
                        self._matriz_tiempo_norm[i][j] = 1.0

    def _recalcular_pesos(self) -> None:
        """Aplica la fórmula peso(i,j) = alpha * costo_norm(i,j) + beta * tiempo_norm(i,j)."""
        n = self._n
        self._matriz_peso = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j:
                    self._matriz_peso[i][j] = 0.0
                else:
                    self._matriz_peso[i][j] = (
                        self._alfa * self._matriz_costo_norm[i][j]
                        + self._beta * self._matriz_tiempo_norm[i][j]
                    )

    def configurar_pesos(self, alfa: float, beta: float) -> None:
        """Actualiza los coeficientes alfa y beta y recalcula la matriz de pesos."""
        if alfa < 0 or beta < 0:
            raise ValueError(f"Los coeficientes alfa ({alfa}) y beta ({beta}) no pueden ser negativos.")
        self._alfa = float(alfa)
        self._beta = float(beta)
        self._recalcular_pesos()

    def peso(self, i: int, j: int) -> float:
        """Retorna el peso combinado normalizado del tramo entre i y j."""
        self._validar_indices(i, j)
        return self._matriz_peso[i][j]

    def costo(self, i: int, j: int) -> float:
        """Retorna el costo real en dinero del tramo entre i y j."""
        self._validar_indices(i, j)
        return self._matriz_costo[i][j]

    def tiempo(self, i: int, j: int) -> float:
        """Retorna el tiempo de viaje en horas del tramo entre i y j."""
        self._validar_indices(i, j)
        return self._matriz_tiempo[i][j]

    def costo_normalizado(self, i: int, j: int) -> float:
        """Retorna el costo normalizado en [0, 1] del tramo entre i y j."""
        self._validar_indices(i, j)
        return self._matriz_costo_norm[i][j]

    def tiempo_normalizado(self, i: int, j: int) -> float:
        """Retorna el tiempo normalizado en [0, 1] del tramo entre i y j."""
        self._validar_indices(i, j)
        return self._matriz_tiempo_norm[i][j]

    def vecinos(self, i: int) -> List[int]:
        """Retorna la lista de índices de destinos alcanzables directamente desde i."""
        if not (0 <= i < self._n):
            raise IndexError(f"Índice de destino fuera de rango: {i} (n={self._n})")
        # En una matriz completa, los vecinos son todos los j != i
        return [j for j in range(self._n) if j != i]

    def obtener_destino(self, i: int) -> Destino:
        """Retorna el objeto Destino correspondiente al identificador i."""
        if not (0 <= i < self._n):
            raise IndexError(f"Índice de destino fuera de rango: {i}")
        return self._destinos[i]

    def obtener_id(self, nombre: str) -> int:
        """Obtiene el identificador de un destino a partir de su nombre (case-insensitive)."""
        clave = nombre.strip().lower()
        if clave not in self._map_nombre_a_id:
            raise KeyError(f"No existe ningún destino con el nombre '{nombre}'.")
        return self._map_nombre_a_id[clave]

    def obtener_arista(self, i: int, j: int) -> Arista:
        """Construye y retorna un objeto Arista con costo, tiempo y peso calculados."""
        return Arista(
            origen=i,
            destino=j,
            costo=self.costo(i, j),
            tiempo=self.tiempo(i, j),
            peso=self.peso(i, j),
        )

    def _validar_indices(self, i: int, j: int) -> None:
        if not (0 <= i < self._n and 0 <= j < self._n):
            raise IndexError(f"Índices de arista fuera de rango: ({i}, {j}) con n={self._n}")

    @classmethod
    def desde_json(
        cls,
        ruta: Optional[Union[str, Path]] = None,
        alfa: float = 0.5,
        beta: float = 0.5,
    ) -> Grafo:
        """Carga los datos desde un archivo JSON y construye la instancia de Grafo."""
        destinos, costo, tiempo = DestinosRepository.cargar(ruta)
        return cls(destinos, costo, tiempo, alfa=alfa, beta=beta)
