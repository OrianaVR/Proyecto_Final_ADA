"""Previsualización aislada de la Pantalla 3 (grafo visual) - HU-13.

Abre directamente `PantallaGrafo` con el grafo real y una ruta de ejemplo,
sin pasar por el formulario. Útil para ver la pantalla en vivo mientras el
resto de la UI del equipo sigue en desarrollo.

Uso:
    python preview_grafo.py
"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import flet as ft

from lib.models.ruta import Ruta
from lib.structures.grafo import Grafo
from lib.ui.pantalla_grafo import PantallaGrafo


def main(page: ft.Page):
    page.title = "TravelPath - Preview grafo (HU-13)"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 900
    page.window.height = 700

    grafo = Grafo.desde_json()

    # Ruta de ejemplo: visita los primeros destinos en orden, usando los
    # tramos directos del grafo. Solo sirve para demostrar el resaltado.
    secuencia = [d.id for d in grafo.destinos[:4]]
    tramos = [
        grafo.obtener_arista(secuencia[i], secuencia[i + 1])
        for i in range(len(secuencia) - 1)
    ]
    ruta_demo = Ruta(
        destinos=secuencia,
        peso_total=sum(t.peso for t in tramos),
        costo_total=sum(t.costo for t in tramos),
        tiempo_total=sum(t.tiempo for t in tramos),
        tramos=tramos,
    )

    contenedor = ft.Container(expand=True)

    def mostrar(ruta):
        contenedor.content = PantallaGrafo(
            grafo=grafo,
            ruta_seleccionada=ruta,
            on_volver=lambda: None,
        )
        page.update()

    # Botones para alternar entre grafo completo y grafo con ruta resaltada.
    page.add(
        ft.Row(
            [
                ft.ElevatedButton(
                    "Solo grafo", on_click=lambda _: mostrar(None)
                ),
                ft.ElevatedButton(
                    "Grafo + ruta demo", on_click=lambda _: mostrar(ruta_demo)
                ),
            ]
        ),
        contenedor,
    )
    mostrar(ruta_demo)


if __name__ == "__main__":
    ft.app(target=main)
