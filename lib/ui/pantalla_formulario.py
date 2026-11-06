"""Estructura de la Pantalla 1: Formulario de Entrada (Framework Flet).

Capa de UI asignada a Integrante 4.
"""

from typing import Callable, Optional
import flet as ft
from lib.structures.grafo import Grafo


class PantallaFormulario(ft.Container):
    """Estructura base del formulario de entrada de parámetros."""

    def __init__(
        self,
        grafo: Grafo,
        on_calcular: Optional[Callable] = None,
    ):
        super().__init__(expand=True, padding=20)
        self.grafo = grafo
        self.on_calcular = on_calcular

        self.dd_origen = ft.Dropdown(
            label="Ciudad de Origen",
            options=[ft.dropdown.Option(key=str(d.id), text=d.nombre) for d in grafo.destinos],
            width=300,
        )
        self.chips_destinos = ft.Row(
            wrap=True,
            spacing=10,
            controls=[ft.FilterChip(label=ft.Text(d.nombre), data=d.id) for d in grafo.destinos],
        )
        self.txt_presupuesto = ft.TextField(label="Presupuesto ($)", value="500", width=200)
        self.txt_k = ft.TextField(label="Rutas K", value="10", width=120)
        self.sw_ida_vuelta = ft.Switch(label="Ida y vuelta", value=False)
        self.slider_alfa = ft.Slider(min=0.0, max=1.0, value=0.5, divisions=10, label="α: {value}")

        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("TravelPath: Formulario de Planificación", size=22, weight=ft.FontWeight.BOLD),
                self.dd_origen,
                ft.Text("Destinos a visitar (máx 12):"),
                self.chips_destinos,
                ft.Row([self.txt_presupuesto, self.txt_k, self.sw_ida_vuelta]),
                ft.Text("Ponderación Costo (α) vs Tiempo (β):"),
                self.slider_alfa,
                ft.ElevatedButton("Calcular", icon=ft.Icons.CALCULATE, on_click=lambda _: None),
            ],
        )
