"""Punto de inicio y enrutamiento base de la aplicación visual en Flet."""

import flet as ft
from lib.structures.grafo import Grafo
from lib.ui.pantalla_formulario import PantallaFormulario
from lib.ui.pantalla_resultados import PantallaResultados
from lib.ui.pantalla_grafo import PantallaGrafo


def main(page: ft.Page):
    page.title = "TravelPath"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 900
    page.window.height = 700

    grafo = Grafo.desde_json()

    contenedor = ft.Container(expand=True)

    def ver_formulario():
        contenedor.content = PantallaFormulario(
            grafo=grafo,
            on_calcular=ver_resultados,
        )
        page.update()

    def ver_resultados(resultado):
        contenedor.content = PantallaResultados(
            grafo=grafo,
            resultado=resultado,
            presupuesto=resultado.presupuesto,
            on_volver=ver_formulario,
        )
        page.update()

    page.add(contenedor)
    ver_formulario()


if __name__ == "__main__":
    ft.app(target=main)
