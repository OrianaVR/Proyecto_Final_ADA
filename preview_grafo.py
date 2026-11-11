"""Previsualización aislada de la Pantalla 3 (grafo visual) - HU-13 y HU-14.

Monta el flujo resultados -> grafo sin pasar por el formulario del equipo:
calcula rutas reales con el planificador y muestra la pantalla de resultados
con su botón "Ver en grafo", que abre la pantalla de grafo de ESA ruta y
permite simular el recorrido animado.

Uso:
    python preview_grafo.py
"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import flet as ft

from lib.models.entrada import Entrada
from lib.services.planificador_viaje import PlanificadorViaje
from lib.structures.grafo import Grafo
from lib.ui.pantalla_grafo import PantallaGrafo
from lib.ui.pantalla_resultados import PantallaResultados


def main(page: ft.Page):
    page.title = "TravelPath - Preview grafo (HU-13 / HU-14)"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 960
    page.window.height = 760

    grafo = Grafo.desde_json()

    # Entrada de ejemplo: origen + algunos destinos, orden parcial (Branch and
    # Bound). Toda la lógica la resuelve el planificador; aquí solo mostramos.
    destinos = [d.id for d in grafo.destinos[1:5]]
    entrada = Entrada(
        origen=grafo.destinos[0].id,
        destinos=destinos,
        presupuesto=1_000_000.0,  # holgado, para que todas las rutas quepan
        k=5,
        ida_y_vuelta=True,
    )
    resultado = PlanificadorViaje(grafo).planificar(entrada)

    contenedor = ft.Container(expand=True)

    def ver_resultados():
        contenedor.content = PantallaResultados(
            grafo=grafo,
            resultado=resultado,
            presupuesto=entrada.presupuesto,
            on_ver_en_grafo=ver_grafo,
        )
        page.update()

    def ver_grafo(ruta):
        contenedor.content = PantallaGrafo(
            grafo=grafo,
            ruta_seleccionada=ruta,
            on_volver=ver_resultados,
        )
        page.update()

    page.add(contenedor)
    ver_resultados()


if __name__ == "__main__":
    ft.app(target=main)
