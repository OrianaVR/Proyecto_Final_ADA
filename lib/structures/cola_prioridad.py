from __future__ import annotations
import math
from typing import Any, Generic, List, Tuple, TypeVar

T = TypeVar("T")


class ColaVaciaError(IndexError):
    """Se intentó extraer o consultar el menor de una cola sin elementos."""

    def __init__(self) -> None:
        super().__init__("La cola de prioridad está vacía.")

class ColaPrioridad(Generic[T]):

    def __init__(self) -> None:
        # Cada entrada del heap es (prioridad, contador_de_llegada, elemento).
        self._heap: List[Tuple[Any, int, T]] = []
        self._contador = 0

    # ------------------------------------------------------------------ consulta
    def __len__(self) -> int:
        return len(self._heap)

    def __bool__(self) -> bool:
        return bool(self._heap)

    def esta_vacia(self) -> bool:
        """True si no quedan elementos."""
        return not self._heap

    def ver_menor(self) -> Tuple[T, Any]:
        """Retorna (elemento, prioridad) del menor SIN extraerlo. O(1)."""
        if not self._heap:
            raise ColaVaciaError()
        prioridad, _, elemento = self._heap[0]
        return elemento, prioridad

    # ------------------------------------------------------------------ escritura
    def insertar(self, elemento: T, prioridad: Any) -> None:
        """Agrega un elemento con su prioridad. O(log n)."""
        if isinstance(prioridad, float) and math.isnan(prioridad):
            raise ValueError("La prioridad no puede ser NaN.")
        self._heap.append((prioridad, self._contador, elemento))
        self._contador += 1
        self._subir(len(self._heap) - 1)

    def extraer_menor(self) -> Tuple[T, Any]:
        """Quita y retorna (elemento, prioridad) con la menor prioridad. O(log n)."""
        if not self._heap:
            raise ColaVaciaError()
        menor = self._heap[0]
        ultimo = self._heap.pop()
        if self._heap:
            self._heap[0] = ultimo
            self._bajar(0)
        prioridad, _, elemento = menor
        return elemento, prioridad

    def vaciar(self) -> None:
        """Elimina todos los elementos."""
        self._heap.clear()

    # ------------------------------------------------------------------ interno
    def _antes(self, a: int, b: int) -> bool:
        """True si la entrada en la posición a debe salir antes que la de b."""
        # Compara (prioridad, contador): el contador desempata y evita comparar elementos.
        return self._heap[a][:2] < self._heap[b][:2]

    def _subir(self, i: int) -> None:
        while i > 0:
            padre = (i - 1) // 2
            if self._antes(i, padre):
                self._heap[i], self._heap[padre] = self._heap[padre], self._heap[i]
                i = padre
            else:
                break

    def _bajar(self, i: int) -> None:
        n = len(self._heap)
        while True:
            izq = 2 * i + 1
            der = izq + 1
            menor = i
            if izq < n and self._antes(izq, menor):
                menor = izq
            if der < n and self._antes(der, menor):
                menor = der
            if menor == i:
                break
            self._heap[i], self._heap[menor] = self._heap[menor], self._heap[i]
            i = menor
