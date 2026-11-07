"""Estructura de la Pantalla 3: Visualización del Grafo (Framework Flet).

Capa de UI asignada a Integrante 5 (CustomPainter / Canvas en círculo).
"""

from typing import Callable, Optional
import flet as ft
import flet.canvas as cv
from lib.structures.grafo import Grafo


class PantallaGrafo(ft.Container):
    """Estructura base para dibujo del grafo y simulación."""

    def __init__(
        self,
        grafo: Grafo,
        ruta_seleccionada: Optional[object] = None,
        on_volver: Optional[Callable] = None,
    ):
        super().__init__(expand=True, padding=20)
        self.grafo = grafo
        self.ruta_seleccionada = ruta_seleccionada
        self.on_volver = on_volver

        self.canvas = cv.Canvas(
            shapes=[],
            width=500,
            height=400,
        )

        self.content = ft.Column(
            controls=[
                ft.Row([
                    ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: self.on_volver() if self.on_volver else None),
                    ft.Text("Visualización del Grafo y Simulación", size=22, weight=ft.FontWeight.BOLD),
                ]),
                ft.Text("Canvas del grafo circular (a implementar por Integrante 5):"),
                ft.Container(content=self.canvas, alignment=ft.Alignment(0, 0)),
            ]
        )
