"""Pantalla de resultados con resumen destacado y alternativas."""

from __future__ import annotations

from typing import Callable, Optional

import flet as ft

from lib.models.ruta import Ruta
from lib.services.planificador_viaje import ResultadoPlanificacion
from lib.structures.grafo import Grafo
from lib.ui.estilos import (
    PRIMARY,
    SUCCESS,
    boton_secundario,
    encabezado,
    texto_ayuda,
)


_COLOR_DESTINOS = ["#FF6B4A", "#D95DAA", "#7257E8", "#16A879", "#F59E0B"]
_COLOR_MEJOR = "#123F34"


class PantallaResultados(ft.Container):
    """Muestra la mejor ruta y el resto de alternativas."""

    def __init__(
        self,
        grafo: Grafo,
        resultado: Optional[ResultadoPlanificacion] = None,
        presupuesto: Optional[float] = None,
        rutas: Optional[list[Ruta]] = None,
        on_ver_en_grafo: Optional[Callable] = None,
        on_volver: Optional[Callable] = None,
    ):
        super().__init__(expand=True, padding=0)
        self.grafo = grafo
        self.resultado = resultado
        self.presupuesto = presupuesto
        self.rutas = sorted(
            list(rutas or (resultado.rutas if resultado else [])),
            key=lambda ruta: ruta.peso_total,
        )
        self.rutas_fuera_presupuesto = list(
            resultado.rutas_fuera_presupuesto if resultado else []
        )
        self.on_ver_en_grafo = on_ver_en_grafo
        self.on_volver = on_volver
        self._nombres = {destino.id: destino.nombre for destino in grafo.destinos}

        controles: list[ft.Control] = [self._encabezado_pantalla()]
        if resultado and resultado.mensaje_error and not self.rutas:
            if self.rutas_fuera_presupuesto:
                controles.append(
                    self._tarjeta_fuera_presupuesto(
                        resultado.mensaje_error,
                        self.rutas_fuera_presupuesto[0],
                    )
                )
            else:
                controles.append(self._estado_vacio(resultado.mensaje_error))
        elif not self.rutas:
            controles.append(self._estado_vacio("No se encontraron rutas factibles."))
        else:
            if not resultado or resultado.garantizado_optimo is False:
                controles.append(
                    ft.Container(
                        content=ft.Text(
                            "Mejor encontrada, no garantizada como óptima.",
                            color=ft.Colors.ON_ERROR_CONTAINER,
                        ),
                        padding=12,
                        bgcolor=ft.Colors.ERROR_CONTAINER,
                        border_radius=12,
                    )
                )
            controles.extend(
                [
                    self._tarjeta_mejor(self.rutas[0]),
                    ft.Row(
                        [
                            ft.Text("Otras alternativas", size=20, weight=ft.FontWeight.BOLD),
                            texto_ayuda(f"{max(len(self.rutas) - 1, 0)} rutas adicionales"),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    *[
                        self._tarjeta_alternativa(ruta, indice)
                        for indice, ruta in enumerate(self.rutas[1:], start=2)
                    ],
                ]
            )

        self.content = ft.Column(
            controls=controles,
            spacing=18,
            scroll=ft.ScrollMode.AUTO,
        )

    def _encabezado_pantalla(self) -> ft.Control:
        return ft.Row(
            [
                ft.IconButton(
                    ft.Icons.ARROW_BACK,
                    tooltip="Volver a datos del viaje",
                    on_click=lambda _event: (
                        self.on_volver() if self.on_volver else None
                    ),
                ),
                encabezado(
                    "Rutas encontradas",
                    "Compara las alternativas y visualiza el recorrido que prefieras",
                    ft.Icons.ROUTE,
                ),
            ],
            spacing=8,
        )

    def _tarjeta_fuera_presupuesto(self, mensaje: str, ruta: Ruta) -> ft.Control:
        """Muestra la mejor alternativa sin presentarla como válida."""
        ciudades = " → ".join(
            self._nombres.get(ciudad, str(ciudad)) for ciudad in ruta.destinos
        )
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.WARNING_AMBER, color=ft.Colors.ON_ERROR_CONTAINER),
                            ft.Text(
                                "El presupuesto no alcanza",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.ON_ERROR_CONTAINER,
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Text(mensaje, color=ft.Colors.ON_ERROR_CONTAINER),
                    ft.Text(
                        "Puedes revisar la mejor alternativa aunque supere el "
                        "presupuesto indicado.",
                        size=13,
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Mejor alternativa", weight=ft.FontWeight.BOLD),
                                ft.Text(ciudades, size=14),
                                ft.Row(
                                    [
                                        self._metrica("Dinero", f"${ruta.costo_total:,.2f}"),
                                        self._metrica("Tiempo", f"{ruta.tiempo_total:.1f} h"),
                                        self._metrica("Peso", f"{ruta.peso_total:.4f}"),
                                    ],
                                    wrap=True,
                                    spacing=8,
                                ),
                            ],
                            spacing=10,
                        ),
                        padding=16,
                        bgcolor=ft.Colors.SURFACE,
                        border_radius=14,
                    ),
                    boton_secundario(
                        "Ver rutas de todos modos",
                        ft.Icons.ACCOUNT_TREE,
                        lambda _event: (
                            self.on_ver_en_grafo(ruta)
                            if self.on_ver_en_grafo
                            else None
                        ),
                    ),
                ],
                spacing=14,
            ),
            padding=22,
            bgcolor=ft.Colors.ERROR_CONTAINER,
            border_radius=18,
        )

    def _estado_vacio(self, mensaje: str) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.ROUTE_OUTLINED, size=48, color=PRIMARY),
                    ft.Text("No hay rutas disponibles", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(mensaje, text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=50,
            alignment=ft.Alignment(0, 0),
            bgcolor=ft.Colors.SURFACE,
            border_radius=18,
        )

    def _tarjeta_mejor(self, ruta: Ruta) -> ft.Control:
        ciudades = " → ".join(
            self._nombres.get(ciudad, str(ciudad)) for ciudad in ruta.destinos
        )
        restante = self._presupuesto_restante(ruta)
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.AUTO_AWESOME, color="#A7F3D0", size=16),
                                    ft.Text(
                                        "MEJOR OPCIÓN",
                                        size=11,
                                        color="#A7F3D0",
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                                spacing=6,
                            ),
                            ft.Text("1 de " + str(len(self.rutas)), color="#CDE9DF", size=12),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    self._timeline(ruta),
                    ft.Divider(color="#4B7668", height=1),
                    ft.Row(
                        [
                            self._metrica_oscura("Costo estimado", f"${ruta.costo_total:,.2f}"),
                            self._metrica_oscura("Tiempo en tránsito", f"{ruta.tiempo_total:.1f} h"),
                        ],
                        spacing=30,
                    ),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED, size=17, color="#A7F3D0"),
                                ft.Text(
                                    f"Te quedan {restante} del presupuesto",
                                    color="#A7F3D0",
                                    size=12,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        padding=11,
                        bgcolor="#245947",
                        border_radius=10,
                    ),
                    ft.FilledButton(
                        text="Ver recorrido en el grafo",
                        icon=ft.Icons.ACCOUNT_TREE,
                        on_click=lambda _event, r=ruta: (
                            self.on_ver_en_grafo(r) if self.on_ver_en_grafo else None
                        ),
                        style=ft.ButtonStyle(
                            bgcolor="#245947",
                            color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=11),
                        ),
                    ),
                ],
                spacing=16,
            ),
            padding=22,
            bgcolor=_COLOR_MEJOR,
            border_radius=20,
        )

    def _tarjeta_alternativa(self, ruta: Ruta, indice: int) -> ft.Control:
        ciudades = " → ".join(
            self._nombres.get(ciudad, str(ciudad)) for ciudad in ruta.destinos
        )
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text(str(indice), weight=ft.FontWeight.BOLD),
                        width=34,
                        height=34,
                        alignment=ft.Alignment(0, 0),
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        border_radius=10,
                    ),
                    ft.Column(
                        [
                            ft.Text(ciudades, weight=ft.FontWeight.BOLD, size=14),
                            ft.Text(
                                f"{ruta.tiempo_total:.1f} h · Peso {ruta.peso_total:.4f}",
                                size=12,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                            ),
                        ],
                        spacing=3,
                        expand=True,
                    ),
                    ft.Text(
                        f"${ruta.costo_total:,.2f}",
                        weight=ft.FontWeight.BOLD,
                        color=PRIMARY,
                    ),
                    ft.IconButton(
                        ft.Icons.ACCOUNT_TREE_OUTLINED,
                        tooltip="Ver en grafo",
                        on_click=lambda _event, r=ruta: (
                            self.on_ver_en_grafo(r) if self.on_ver_en_grafo else None
                        ),
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=14,
            bgcolor=ft.Colors.SURFACE,
            border=ft.Border(
                top=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
                right=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
                bottom=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
                left=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
            ),
            border_radius=14,
        )

    def _timeline(self, ruta: Ruta) -> ft.Control:
        controles: list[ft.Control] = []
        destinos = ruta.destinos
        for indice, ciudad in enumerate(destinos):
            color = _COLOR_DESTINOS[indice % len(_COLOR_DESTINOS)]
            controles.append(
                ft.Column(
                    [
                        ft.Container(
                            content=ft.Text(
                                str(indice + 1),
                                color=ft.Colors.WHITE,
                                size=12,
                                weight=ft.FontWeight.BOLD,
                            ),
                            width=28,
                            height=28,
                            alignment=ft.Alignment(0, 0),
                            bgcolor=color,
                            border_radius=14,
                        ),
                        ft.Text(
                            self._nombres.get(ciudad, str(ciudad)),
                            color=ft.Colors.WHITE,
                            size=10,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                )
            )
            if indice < len(destinos) - 1:
                controles.append(
                    ft.Container(
                        content=ft.Divider(color="#6D9A8A", height=1),
                        expand=True,
                        margin=ft.Margin(0, 14, 0, 0),
                    )
                )
        return ft.Row(controles, vertical_alignment=ft.CrossAxisAlignment.START)

    @staticmethod
    def _metrica(nombre: str, valor: str) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(nombre, size=11, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Text(valor, size=14, weight=ft.FontWeight.BOLD),
                ],
                spacing=2,
            ),
            padding=ft.Padding(10, 7, 10, 7),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border_radius=9,
        )

    def _metrica_oscura(self, nombre: str, valor: str) -> ft.Control:
        return ft.Column(
            [
                ft.Text(nombre, color="#B8D5CA", size=11),
                ft.Text(valor, color=ft.Colors.WHITE, size=19, weight=ft.FontWeight.BOLD),
            ],
            spacing=3,
            expand=True,
        )

    def _presupuesto_restante(self, ruta: Ruta) -> str:
        if self.presupuesto is None:
            return "sin límite"
        return f"${self.presupuesto - ruta.costo_total:,.2f}"
