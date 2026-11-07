"""Estructura de la Pantalla 2: Resultados (Framework Flet).

Capa de UI asignada a Integrante 4.
"""

from typing import Callable, List, Optional
import flet as ft
from lib.structures.grafo import Grafo


class PantallaResultados(ft.Container):
    """Estructura base para la visualización de rutas encontradas."""

    def __init__(
        self,
        grafo: Grafo,
        rutas: Optional[List] = None,
        on_ver_en_grafo: Optional[Callable] = None,
        on_volver: Optional[Callable] = None,
    ):
        super().__init__(expand=True, padding=20)
        self.grafo = grafo
        self.rutas = rutas or []
        self.on_ver_en_grafo = on_ver_en_grafo
        self.on_volver = on_volver

        self.content = ft.Column(
            controls=[
                ft.Row([
                    ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: self.on_volver() if self.on_volver else None),
                    ft.Text("Resultados de Itinerarios", size=22, weight=ft.FontWeight.BOLD),
                ]),
                ft.Text("Lista de mejores rutas (a integrar por Integrante 4):", size=14),
                ft.Card(
                    content=ft.Container(
                        padding=15,
                        content=ft.Text("Aquí se desplegarán las rutas ordenadas por peso combinado con su costo y tiempo."),
                    )
                ),
            ]
        )
