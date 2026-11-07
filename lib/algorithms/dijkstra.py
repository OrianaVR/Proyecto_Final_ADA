from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Set, Tuple

from lib.models.arista import Arista
from lib.structures.cola_prioridad import ColaPrioridad
from lib.structures.grafo import Grafo

# Métricas disponibles. "costo" es sinónimo de "dinero".
METRICA_PESO = "peso"
METRICA_DINERO = "dinero"
METRICA_TIEMPO = "tiempo"
METRICAS_VALIDAS = (METRICA_PESO, METRICA_DINERO, METRICA_TIEMPO)


class CaminoNoEncontradoError(Exception):
    """No existe camino entre los dos destinos con las restricciones dadas."""

    def __init__(self, origen: int, destino: int):
        self.origen = origen
        self.destino = destino
        super().__init__(f"No existe un camino de {origen} a {destino}.")


@dataclass
class CaminoMinimo:

    origen: int
    destino: int
    camino: List[int]
    metrica: str
    valor: float
    peso: float
    dinero: float
    tiempo: float
    tramos: List[Arista] = field(default_factory=list)

    @property
    def ciudades_paso(self) -> List[int]:
        """Ciudades intermedias (sin origen ni destino). Vacía si el tramo es directo."""
        return self.camino[1:-1]


def normalizar_metrica(metrica: str) -> str:
    """Valida y normaliza el nombre de la métrica ("costo" -> "dinero")."""
    nombre = str(metrica).strip().lower()
    if nombre == "costo":
        nombre = METRICA_DINERO
    if nombre not in METRICAS_VALIDAS:
        raise ValueError(
            f"Métrica inválida: '{metrica}'. Use una de: peso, dinero (o costo), tiempo."
        )
    return nombre


def _funcion_metrica(grafo: Grafo, metrica: str) -> Callable[[int, int], float]:
    if metrica == METRICA_PESO:
        return grafo.peso
    if metrica == METRICA_DINERO:
        return grafo.costo
    return grafo.tiempo


def _validar_nodo(grafo: Grafo, nodo: int, nombre: str) -> None:
    if not (0 <= nodo < grafo.num_destinos):
        raise IndexError(
            f"{nombre} fuera de rango: {nodo} (el grafo tiene {grafo.num_destinos} destinos)."
        )


def dijkstra_desde(
    grafo: Grafo,
    origen: int,
    metrica: str = METRICA_PESO,
    prohibidos: Optional[Iterable[int]] = None,
    destino: Optional[int] = None,
) -> Tuple[Dict[int, float], Dict[int, Optional[int]]]:

    metrica = normalizar_metrica(metrica)
    _validar_nodo(grafo, origen, "Origen")
    if destino is not None:
        _validar_nodo(grafo, destino, "Destino")
    bloqueados: Set[int] = set(prohibidos) if prohibidos is not None else set()
    bloqueados.discard(origen)  # el origen siempre puede expandirse

    medir = _funcion_metrica(grafo, metrica)
    dist: Dict[int, float] = {origen: 0.0}
    previo: Dict[int, Optional[int]] = {origen: None}
    cerrados: Set[int] = set()

    cola: ColaPrioridad[int] = ColaPrioridad()
    cola.insertar(origen, 0.0)

    while cola:
        u, d_u = cola.extraer_menor()
        if u in cerrados:
            continue  # entrada vieja: u ya se cerró con una distancia mejor
        cerrados.add(u)
        if destino is not None and u == destino:
            break
        if u in bloqueados:
            continue  # se puede llegar a u, pero no pasar por u
        for v in grafo.vecinos(u):
            if v in cerrados:
                continue
            nuevo = d_u + medir(u, v)
            if v not in dist or nuevo < dist[v]:
                dist[v] = nuevo
                previo[v] = u
                cola.insertar(v, nuevo)

    return dist, previo


def reconstruir_camino(
    previo: Dict[int, Optional[int]], origen: int, destino: int
) -> List[int]:
    """Sigue `previo` hacia atrás y retorna [origen, ..., destino]."""
    if destino not in previo:
        raise CaminoNoEncontradoError(origen, destino)
    camino = [destino]
    actual = destino
    while actual != origen:
        padre = previo[actual]
        if padre is None:  # no debería ocurrir si destino es alcanzable
            raise CaminoNoEncontradoError(origen, destino)
        camino.append(padre)
        actual = padre
    camino.reverse()
    return camino


def armar_camino(
    grafo: Grafo, camino: List[int], metrica: str
) -> CaminoMinimo:
    """Construye un CaminoMinimo calculando peso, dinero y tiempo a lo largo de `camino`."""
    metrica = normalizar_metrica(metrica)
    tramos = [grafo.obtener_arista(a, b) for a, b in zip(camino, camino[1:])]
    peso = sum(t.peso for t in tramos)
    dinero = sum(t.costo for t in tramos)
    tiempo = sum(t.tiempo for t in tramos)
    valor = {METRICA_PESO: peso, METRICA_DINERO: dinero, METRICA_TIEMPO: tiempo}[metrica]
    return CaminoMinimo(
        origen=camino[0],
        destino=camino[-1],
        camino=list(camino),
        metrica=metrica,
        valor=valor,
        peso=peso,
        dinero=dinero,
        tiempo=tiempo,
        tramos=tramos,
    )


def dijkstra(
    grafo: Grafo,
    origen: int,
    destino: int,
    metrica: str = METRICA_PESO,
    prohibidos: Optional[Iterable[int]] = None,
) -> CaminoMinimo:

    metrica = normalizar_metrica(metrica)
    if origen == destino:
        _validar_nodo(grafo, origen, "Origen")
        return armar_camino(grafo, [origen], metrica)
    _, previo = dijkstra_desde(grafo, origen, metrica, prohibidos, destino=destino)
    camino = reconstruir_camino(previo, origen, destino)
    return armar_camino(grafo, camino, metrica)
