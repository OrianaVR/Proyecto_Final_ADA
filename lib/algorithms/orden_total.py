from __future__ import annotations
from typing import List, Optional, Sequence

from lib.algorithms.dijkstra import METRICA_DINERO, METRICA_PESO, CaminoMinimo, dijkstra
from lib.models.arista import Arista
from lib.models.ruta import Ruta
from lib.structures.grafo import Grafo
from lib.structures.tabla_precedencias import TablaPrecedencias

# Tolerancia para comparar dinero con el presupuesto sin falsos rechazos por decimales.
_EPS = 1e-9


class PresupuestoInsuficienteError(Exception):
    """Ninguna ruta con el orden pedido cabe en el presupuesto."""

    def __init__(self, minimo_necesario: float, presupuesto: float):
        self.minimo_necesario = minimo_necesario
        self.presupuesto = presupuesto
        super().__init__(
            f"Ninguna ruta cabe en tu presupuesto (${presupuesto:,.0f}); "
            f"el mínimo necesario es ${minimo_necesario:,.0f}."
        )


class SecuenciaInvalidaError(Exception):
    """La secuencia del usuario es inválida o viola una precedencia."""


def _armar_ruta(recorrido: List[int], legs: List[CaminoMinimo]) -> Ruta:
    """Une los tramos Dijkstra en una sola Ruta."""
    tramos: List[Arista] = [t for leg in legs for t in leg.tramos]
    paso: List[int] = [c for leg in legs for c in leg.ciudades_paso]
    return Ruta(
        destinos=list(recorrido),
        peso_total=sum(leg.peso for leg in legs),
        costo_total=sum(leg.dinero for leg in legs),
        tiempo_total=sum(leg.tiempo for leg in legs),
        tramos=tramos,
        ciudades_paso=paso,
    )


def _recorrer(
    grafo: Grafo, recorrido: List[int], prohibidos: set, metrica: str
) -> Ruta:
    legs = [
        dijkstra(grafo, a, b, metrica=metrica, prohibidos=prohibidos)
        for a, b in zip(recorrido, recorrido[1:])
    ]
    return _armar_ruta(recorrido, legs)


def ruta_por_secuencia(
    grafo: Grafo,
    origen: int,
    secuencia: Sequence[int],
    presupuesto: Optional[float] = None,
    precedencias: Optional[TablaPrecedencias] = None,
    ida_y_vuelta: bool = False,
) -> Ruta:

    secuencia = list(secuencia)
    if secuencia and secuencia[0] == origen:
        secuencia = secuencia[1:]
    if not secuencia:
        raise ValueError("La secuencia de destinos está vacía.")
    if origen in secuencia:
        raise ValueError(f"El origen ({origen}) no puede repetirse dentro de la secuencia.")
    if len(set(secuencia)) != len(secuencia):
        raise ValueError("La secuencia tiene ciudades repetidas.")
    for ciudad in [origen] + secuencia:
        if not (0 <= ciudad < grafo.num_destinos):
            raise IndexError(
                f"Ciudad fuera de rango: {ciudad} (el grafo tiene {grafo.num_destinos} destinos)."
            )

    recorrido = [origen] + secuencia
    if precedencias is not None:
        nombres = {d.id: d.nombre for d in grafo.destinos}
        ok, mensaje = precedencias.validar_secuencia(recorrido, nombres)
        if not ok:
            raise SecuenciaInvalidaError(mensaje)
    if ida_y_vuelta:
        recorrido = recorrido + [origen]

    prohibidos = set(recorrido)
    ruta = _recorrer(grafo, recorrido, prohibidos, METRICA_PESO)
    if presupuesto is None or ruta.costo_total <= presupuesto + _EPS:
        return ruta

    # La ruta de menor peso se pasa del presupuesto: probar con la de menor dinero.
    ruta_barata = _recorrer(grafo, recorrido, prohibidos, METRICA_DINERO)
    if ruta_barata.costo_total <= presupuesto + _EPS:
        return ruta_barata
    raise PresupuestoInsuficienteError(ruta_barata.costo_total, presupuesto)
