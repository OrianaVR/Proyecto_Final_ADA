from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from lib.algorithms.branch_and_bound import BranchAndBound
from lib.algorithms.matriz_caminos import MatrizCaminos
from lib.algorithms.orden_total import (
    PresupuestoInsuficienteError,
    ruta_por_secuencia,
)
from lib.models.entrada import Entrada
from lib.models.ruta import Ruta
from lib.structures.grafo import Grafo
from lib.structures.tabla_precedencias import (
    CicloPrecedenciasError,
    TablaPrecedencias,
)


@dataclass
class ResultadoPlanificacion:
    """Respuesta uniforme del coordinador para la aplicación y la UI."""

    rutas: List[Ruta] = field(default_factory=list)
    modalidad: Optional[str] = None
    mensaje_error: Optional[str] = None
    minimo_necesario: Optional[float] = None
    garantizado_optimo: bool = True

    @property
    def exitosa(self) -> bool:
        return bool(self.rutas)


class PlanificadorViaje:
    """Coordina validaciones, matrices de caminos y el algoritmo adecuado."""

    def __init__(self, grafo: Grafo):
        self.grafo = grafo

    def planificar(self, entrada: Entrada) -> ResultadoPlanificacion:
        nombres = {destino.id: destino.nombre for destino in self.grafo.destinos}
        try:
            tabla = self._validar_entrada(entrada, nombres)
        except (ValueError, CicloPrecedenciasError) as error:
            return ResultadoPlanificacion(mensaje_error=str(error))

        try:
            self.grafo.configurar_pesos(entrada.alfa, entrada.beta)
            if self._tiene_secuencia_total(entrada):
                ruta = ruta_por_secuencia(
                    self.grafo,
                    entrada.origen,
                    entrada.secuencia_orden or [],
                    presupuesto=entrada.presupuesto,
                    precedencias=tabla,
                    ida_y_vuelta=entrada.ida_y_vuelta,
                )
                return ResultadoPlanificacion(
                    rutas=[ruta],
                    modalidad="dijkstra_por_tramos",
                )

            matriz = MatrizCaminos.construir(
                self.grafo, entrada.origen, entrada.destinos
            )
            planificador = BranchAndBound(
                matriz,
                presupuesto=entrada.presupuesto,
                precedencias=tabla,
                k=entrada.k,
                ida_y_vuelta=entrada.ida_y_vuelta,
            )
            resultado = planificador.mejores_rutas()
            if not resultado.rutas:
                minimo = planificador.cota_dinero(
                    entrada.origen, entrada.destinos
                )
                return ResultadoPlanificacion(
                    modalidad="branch_and_bound",
                    mensaje_error=self._mensaje_presupuesto(
                        entrada.presupuesto, minimo
                    ),
                    minimo_necesario=minimo,
                    garantizado_optimo=resultado.garantizado_optimo,
                )
            return ResultadoPlanificacion(
                rutas=resultado.rutas,
                modalidad="branch_and_bound",
                garantizado_optimo=resultado.garantizado_optimo,
            )
        except PresupuestoInsuficienteError as error:
            return ResultadoPlanificacion(
                modalidad="dijkstra_por_tramos",
                mensaje_error=self._mensaje_presupuesto(
                    entrada.presupuesto, error.minimo_necesario
                ),
                minimo_necesario=error.minimo_necesario,
            )
        except (IndexError, ValueError, KeyError) as error:
            return ResultadoPlanificacion(mensaje_error=str(error))

    def _validar_entrada(
        self, entrada: Entrada, nombres: dict[int, str]
    ) -> TablaPrecedencias:
        if len(entrada.destinos) > 12:
            raise ValueError(
                f"Demasiados destinos: se recibieron {len(entrada.destinos)}, "
                "pero el máximo permitido es 12."
            )
        if len(set(entrada.destinos)) != len(entrada.destinos):
            raise ValueError("La lista de destinos tiene ciudades repetidas.")
        if entrada.origen in entrada.destinos:
            raise ValueError(
                f"El origen ({entrada.origen}) no puede estar entre los destinos."
            )
        if entrada.presupuesto < 0:
            raise ValueError("El presupuesto no puede ser negativo.")
        if entrada.k <= 0:
            raise ValueError("La cantidad de rutas K debe ser mayor que 0.")
        if entrada.alfa < 0 or entrada.beta < 0:
            raise ValueError("Las ponderaciones α y β no pueden ser negativas.")

        todos = set(entrada.destinos)
        tabla = TablaPrecedencias(entrada.precedencias)
        tabla.validar_sin_ciclos(nombres)

        if entrada.secuencia_orden is not None:
            secuencia = list(entrada.secuencia_orden)
            if len(set(secuencia)) != len(secuencia):
                raise ValueError("La secuencia tiene ciudades repetidas.")
            if not set(secuencia).issubset(todos):
                raise ValueError(
                    "La secuencia solo puede contener destinos seleccionados."
                )
            valida, mensaje = tabla.validar_secuencia(
                [entrada.origen] + secuencia, nombres
            )
            if not valida:
                raise ValueError(mensaje or "La secuencia viola una precedencia.")
        for ciudad in [entrada.origen] + entrada.destinos:
            if not 0 <= ciudad < self.grafo.num_destinos:
                raise IndexError(
                    f"Ciudad fuera de rango: {ciudad} "
                    f"(el grafo tiene {self.grafo.num_destinos} destinos)."
                )
        return tabla

    @staticmethod
    def _tiene_secuencia_total(entrada: Entrada) -> bool:
        return (
            entrada.secuencia_orden is not None
            and len(entrada.secuencia_orden) == len(entrada.destinos)
            and set(entrada.secuencia_orden) == set(entrada.destinos)
        )

    @staticmethod
    def _mensaje_presupuesto(presupuesto: float, minimo: float) -> str:
        return (
            "Ninguna ruta cabe en tu presupuesto; "
            f"el mínimo necesario es ${minimo:,.2f}."
        )
