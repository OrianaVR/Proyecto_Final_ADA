from __future__ import annotations

from dataclasses import dataclass, field
import time
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set

from lib.algorithms.matriz_caminos import MatrizCaminos
from lib.models.arista import Arista
from lib.models.ruta import Ruta
from lib.structures.cola_prioridad import ColaPrioridad
from lib.structures.tabla_precedencias import TablaPrecedencias

# Tolerancia estándar para comparaciones monetarias en punto flotante
_EPS = 1e-9


@dataclass
class EstadisticasPoda:
    """Métricas y estadísticas de desempeño y poda del algoritmo Branch and Bound."""

    nodos_generados: int = 0
    nodos_expandidos: int = 0
    podas_precedencia: int = 0
    podas_presupuesto: int = 0
    podas_mejor_costo: int = 0
    tiempo_segundos: float = 0.0

    @property
    def tiempo_usado(self) -> float:
        """Alias de compatibilidad para tiempo_segundos."""
        return self.tiempo_segundos

    @property
    def podas_costo(self) -> int:
        """Alias de compatibilidad para podas_mejor_costo."""
        return self.podas_mejor_costo

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodos_generados": self.nodos_generados,
            "nodos_expandidos": self.nodos_expandidos,
            "podas_precedencia": self.podas_precedencia,
            "podas_presupuesto": self.podas_presupuesto,
            "podas_mejor_costo": self.podas_mejor_costo,
            "tiempo_segundos": self.tiempo_segundos,
            "tiempo_usado": self.tiempo_segundos,
        }


@dataclass
class ResultadoBB:
    """Resultado retornado por el planificador Branch and Bound."""

    rutas: List[Ruta]
    estadisticas: EstadisticasPoda
    garantizado_optimo: bool

    @property
    def mejor_ruta(self) -> Optional[Ruta]:
        """Retorna la mejor ruta encontrada o None si no hay rutas factibles."""
        return self.rutas[0] if self.rutas else None

    def __len__(self) -> int:
        return len(self.rutas)

    def __bool__(self) -> bool:
        return len(self.rutas) > 0

    def __iter__(self):
        return iter(self.rutas)

    def __getitem__(self, index: int) -> Ruta:
        return self.rutas[index]


@dataclass
class Estado:
    """Representa un nodo en el árbol de búsqueda de Branch and Bound.
    
    Campos alineados con la especificación del proyecto:
    ruta (lista), visitados (bitmask entero), g (peso acumulado), m (dinero acumulado), f = g + h.
    """

    ruta: List[int]
    visitados: int  # Bitmask de destinos visitados
    g: float        # Peso acumulado (criterio de optimización)
    m: float        # Dinero acumulado en $ (restricción dura)
    f: float        # Función de evaluación f = g + h
    longitud_negativa: int = field(init=False, default=0)

    def __post_init__(self):
        # Desempate secundario: a igual f, explorar primero rutas más profundas
        self.longitud_negativa = -len(self.ruta)

    @property
    def ultimo(self) -> int:
        """Último destino alcanzado en el recorrido parcial."""
        return self.ruta[-1]

    def __lt__(self, other: Estado) -> bool:
        if abs(self.f - other.f) > 1e-9:
            return self.f < other.f
        return len(self.ruta) > len(other.ruta)


def _armar_ruta_desde_secuencia(secuencia: List[int], matriz: MatrizCaminos) -> Ruta:
    """Construye un objeto Ruta integrando tramos y ciudades de paso desde MatrizCaminos."""
    if len(secuencia) <= 1:
        return Ruta(
            destinos=list(secuencia),
            peso_total=0.0,
            costo_total=0.0,
            tiempo_total=0.0,
            tramos=[],
            ciudades_paso=[],
        )

    tramos: List[Arista] = []
    ciudades_paso: List[int] = []
    peso_total = 0.0
    costo_total = 0.0
    tiempo_total = 0.0

    for a, b in zip(secuencia, secuencia[1:]):
        camino = matriz.camino_peso(a, b)
        tramos.extend(camino.tramos)
        ciudades_paso.extend(camino.ciudades_paso)
        peso_total += camino.peso
        costo_total += camino.dinero
        tiempo_total += camino.tiempo

    return Ruta(
        destinos=list(secuencia),
        peso_total=peso_total,
        costo_total=costo_total,
        tiempo_total=tiempo_total,
        tramos=tramos,
        ciudades_paso=ciudades_paso,
    )


class BranchAndBound:
    """Planificador de rutas turísticas mediante Branch and Bound con poda y top-K.

    Resuelve el problema tipo TSP con restricciones de precedencia y presupuesto
    usando exploración Best-First guiada por cotas inferiores admisibles.
    """

    def __init__(
        self,
        matriz: MatrizCaminos,
        presupuesto: float,
        precedencias: Optional[TablaPrecedencias | Dict[int, Set[int]]] = None,
        k: int = 10,
        ida_y_vuelta: bool = False,
        limite_nodos: Optional[int] = None,
        limite_segundos: Optional[float] = None,
    ):
        self.matriz = matriz
        self.presupuesto = float(presupuesto)
        self.k = int(k)
        if self.k <= 0:
            raise ValueError("El parámetro k debe ser mayor que 0.")

        self.ida_y_vuelta = bool(ida_y_vuelta)
        self.limite_nodos = limite_nodos
        self.limite_segundos = limite_segundos

        self.origen: int = matriz.nodos[0]
        self.destinos: List[int] = list(matriz.nodos[1:])

        # Validación obligatoria: máximo 12 destinos
        if len(self.destinos) > 12:
            raise ValueError(
                f"Demasiados destinos: se recibieron {len(self.destinos)}, pero el máximo permitido es 12."
            )

        if precedencias is None:
            self.precedencias: Optional[TablaPrecedencias] = None
        elif isinstance(precedencias, TablaPrecedencias):
            precedencias.validar_sin_ciclos()
            self.precedencias = precedencias
        elif isinstance(precedencias, dict):
            tp = TablaPrecedencias(precedencias)
            tp.validar_sin_ciclos()
            self.precedencias = tp
        else:
            raise TypeError("Precedencias debe ser TablaPrecedencias, dict o None.")

        # Acceso O(1) a posiciones y matrices precalculadas
        self._pos = matriz._pos
        self._d_peso = matriz.d_peso
        self._d_dinero = matriz.d_dinero
        self._d_min = matriz.d_min

    def _peso(self, a: int, b: int) -> float:
        return self._d_peso[self._pos[a]][self._pos[b]]

    def _dinero(self, a: int, b: int) -> float:
        return self._d_dinero[self._pos[a]][self._pos[b]]

    def _dinero_min(self, a: int, b: int) -> float:
        return self._d_min[self._pos[a]][self._pos[b]]

    def cota_peso(self, u: int, restantes: Iterable[int]) -> float:
        """Calcula la cota inferior admisible h para el peso restante.

        Fórmula:
            h(e) = Σ_{d ∈ R} min_{x ∈ R ∪ {u}, x ≠ d} D_peso[x][d]
            (si ida_y_vuelta: suma además el mínimo de regreso al origen desde R o u).
        """
        r_set = set(restantes)
        if not r_set:
            if self.ida_y_vuelta:
                return self._peso(u, self.origen)
            return 0.0

        candidatos_base = r_set | {u}
        cota = 0.0

        for d in r_set:
            min_ingreso = min(
                self._peso(x, d) for x in candidatos_base if x != d
            )
            cota += min_ingreso

        if self.ida_y_vuelta:
            cota += min(self._peso(x, self.origen) for x in r_set)

        return cota

    def cota_dinero(self, u: int, restantes: Iterable[int]) -> float:
        """Calcula la cota inferior admisible para el dinero restante usando D_min."""
        r_set = set(restantes)
        if not r_set:
            if self.ida_y_vuelta:
                return self._dinero_min(u, self.origen)
            return 0.0

        candidatos_base = r_set | {u}
        cota = 0.0

        for d in r_set:
            min_dinero = min(
                self._dinero_min(x, d) for x in candidatos_base if x != d
            )
            cota += min_dinero

        if self.ida_y_vuelta:
            cota += min(self._dinero_min(x, self.origen) for x in r_set)

        return cota

    def mejores_rutas(self) -> ResultadoBB:
        """Ejecuta Branch and Bound y devuelve hasta K rutas en orden ascendente de peso."""
        t_inicio = time.perf_counter()
        estadisticas = EstadisticasPoda()

        # Caso borde: 0 destinos a visitar
        if not self.destinos:
            estadisticas.tiempo_segundos = time.perf_counter() - t_inicio
            if 0.0 <= self.presupuesto + _EPS:
                ruta_vacia = _armar_ruta_desde_secuencia([self.origen], self.matriz)
                return ResultadoBB(
                    rutas=[ruta_vacia],
                    estadisticas=estadisticas,
                    garantizado_optimo=True,
                )
            return ResultadoBB(
                rutas=[],
                estadisticas=estadisticas,
                garantizado_optimo=True,
            )

        n = len(self.destinos)
        mascara_todos = (1 << n) - 1

        destinos_iniciales = set(self.destinos)
        h_inicial = self.cota_peso(self.origen, destinos_iniciales)
        cota_dinero_inicial = self.cota_dinero(self.origen, destinos_iniciales)

        # Si ni siquiera la cota mínima de dinero cabe en el presupuesto
        if cota_dinero_inicial > self.presupuesto + _EPS:
            estadisticas.podas_presupuesto += 1
            estadisticas.tiempo_segundos = time.perf_counter() - t_inicio
            return ResultadoBB(
                rutas=[],
                estadisticas=estadisticas,
                garantizado_optimo=True,
            )

        cola: ColaPrioridad[Estado] = ColaPrioridad()
        estado_raiz = Estado(
            ruta=[self.origen],
            visitados=0,
            g=0.0,
            m=0.0,
            f=h_inicial,
        )
        cola.insertar(estado_raiz, (round(h_inicial, 9), -1))
        estadisticas.nodos_generados += 1

        mejores: List[Ruta] = []
        limite_alcanzado = False

        while cola and len(mejores) < self.k:
            # Control de límite de tiempo
            if self.limite_segundos is not None:
                if (time.perf_counter() - t_inicio) >= self.limite_segundos:
                    limite_alcanzado = True
                    break

            # Control de límite de expansiones
            if self.limite_nodos is not None:
                if estadisticas.nodos_expandidos >= self.limite_nodos:
                    limite_alcanzado = True
                    break

            e, _ = cola.extraer_menor()

            # Verificación de ruta completa
            if e.visitados == mascara_todos:
                if self.ida_y_vuelta:
                    peso_regreso = self._peso(e.ultimo, self.origen)
                    dinero_regreso = self._dinero(e.ultimo, self.origen)
                    g_final = e.g + peso_regreso
                    m_final = e.m + dinero_regreso
                    ruta_completa = e.ruta + [self.origen]
                else:
                    g_final = e.g
                    m_final = e.m
                    ruta_completa = e.ruta

                if m_final <= self.presupuesto + _EPS:
                    ruta_obj = _armar_ruta_desde_secuencia(ruta_completa, self.matriz)
                    mejores.append(ruta_obj)
                else:
                    estadisticas.podas_presupuesto += 1
                continue

            estadisticas.nodos_expandidos += 1
            ultimo = e.ultimo
            visitados_set = set(e.ruta)

            for idx, d in enumerate(self.destinos):
                if e.visitados & (1 << idx):
                    continue  # Ya visitado en este camino

                estadisticas.nodos_generados += 1

                # 1. Poda por precedencia
                if self.precedencias is not None and not self.precedencias.puede_visitar(d, visitados_set):
                    estadisticas.podas_precedencia += 1
                    continue

                g2 = e.g + self._peso(ultimo, d)
                m2 = e.m + self._dinero(ultimo, d)

                # Calcular destinos restantes tras visitar d
                mascara_hijo = e.visitados | (1 << idx)
                restantes_hijo = [
                    dest for j, dest in enumerate(self.destinos) if not (mascara_hijo & (1 << j))
                ]

                # 2. Poda por presupuesto (usando cota_dinero con D_min)
                c_dinero = self.cota_dinero(d, restantes_hijo)
                if m2 + c_dinero > self.presupuesto + _EPS:
                    estadisticas.podas_presupuesto += 1
                    continue

                # 3. Cálculo de cota f = g + h y cola de prioridad
                c_peso = self.cota_peso(d, restantes_hijo)
                f2 = g2 + c_peso
                nueva_ruta = e.ruta + [d]

                nuevo_estado = Estado(
                    ruta=nueva_ruta,
                    visitados=mascara_hijo,
                    g=g2,
                    m=m2,
                    f=f2,
                )
                # La prioridad desempata primero por f y luego por profundidad
                cola.insertar(nuevo_estado, (round(f2, 9), -len(nueva_ruta)))

        estadisticas.podas_mejor_costo = len(cola)
        estadisticas.tiempo_segundos = time.perf_counter() - t_inicio
        garantizado_optimo = not limite_alcanzado

        return ResultadoBB(
            rutas=mejores,
            estadisticas=estadisticas,
            garantizado_optimo=garantizado_optimo,
        )
