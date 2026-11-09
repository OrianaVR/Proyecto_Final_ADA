"""Pantalla textual de comparación de rutas."""

from typing import Callable, Optional

import flet as ft

from lib.models.ruta import Ruta
from lib.services.planificador_viaje import ResultadoPlanificacion
from lib.structures.grafo import Grafo


class PantallaResultados(ft.Container):
    """Muestra rutas ordenadas, sus tramos y el presupuesto restante."""

    def __init__(
        self,
        grafo: Grafo,
        resultado: Optional[ResultadoPlanificacion] = None,
        presupuesto: Optional[float] = None,
        rutas: Optional[list[Ruta]] = None,
        on_ver_en_grafo: Optional[Callable] = None,
        on_volver: Optional[Callable] = None,
    ):
        super().__init__(expand=True, padding=20)
        self.grafo = grafo
        self.resultado = resultado
        self.presupuesto = presupuesto
        self.rutas = sorted(
            list(rutas or (resultado.rutas if resultado else [])),
            key=lambda ruta: ruta.peso_total,
        )
        self.on_ver_en_grafo = on_ver_en_grafo
        self.on_volver = on_volver
        self._nombres = {
            destino.id: destino.nombre for destino in grafo.destinos
        }

        controles: list[ft.Control] = [
            ft.Row(
                [
                    ft.IconButton(
                        ft.Icons.ARROW_BACK,
                        on_click=lambda _: (
                            self.on_volver() if self.on_volver else None
                        ),
                    ),
                    ft.Text(
                        "Resultados de itinerarios",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                    ),
                ]
            )
        ]
        if resultado and resultado.mensaje_error and not self.rutas:
            controles.append(ft.Text(resultado.mensaje_error, color=ft.Colors.RED))
        elif not self.rutas:
            controles.append(ft.Text("No se encontraron rutas factibles."))
        else:
            if not resultado or resultado.garantizado_optimo is False:
                controles.append(
                    ft.Text(
                        "Mejor encontrada, no garantizada como óptima.",
                        color=ft.Colors.AMBER,
                    )
                )
            controles.extend(
                ft.Card(
                    color=ft.Colors.with_opacity(
                        0.18 if indice == 0 else 0.08, ft.Colors.PRIMARY
                    ),
                    content=ft.Container(
                        padding=15,
                        content=ft.Column(self._detalle_ruta(ruta, indice)),
                    ),
                )
                for indice, ruta in enumerate(self.rutas)
            )
        self.content = ft.Column(controls=controles, scroll=ft.ScrollMode.AUTO)

    def _detalle_ruta(self, ruta: Ruta, indice: int) -> list[ft.Control]:
        ciudades = " -> ".join(
            self._nombres.get(ciudad, str(ciudad)) for ciudad in ruta.destinos
        )
        tramos = [
            ft.Text(
                f"  {self._nombres.get(tramo.origen, str(tramo.origen))} -> "
                f"{self._nombres.get(tramo.destino, str(tramo.destino))}: "
                f"${tramo.costo:.2f}, {tramo.tiempo:.1f} h"
            )
            for tramo in ruta.tramos
        ]
        sobra = (
            f"Presupuesto restante: ${self.presupuesto - ruta.costo_total:.2f}"
            if self.presupuesto is not None
            else ""
        )
        return [
            ft.Text(
                f"{'★ Mejor ruta' if indice == 0 else f'Ruta {indice + 1}'}: {ciudades}",
                weight=ft.FontWeight.BOLD,
            ),
            ft.Text(
                f"Peso: {ruta.peso_total:.4f} | Dinero: ${ruta.costo_total:.2f} | "
                f"Tiempo: {ruta.tiempo_total:.1f} h"
            ),
            ft.Text(sobra) if sobra else ft.Text(""),
            ft.Text("Desglose por tramo:"),
            *tramos,
        ]
