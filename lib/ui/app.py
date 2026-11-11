"""Punto de inicio y enrutamiento base de la aplicación visual en Flet."""

import flet as ft
from lib.structures.grafo import Grafo
from lib.ui.pantalla_formulario import PantallaFormulario
from lib.ui.pantalla_resultados import PantallaResultados
from lib.ui.pantalla_grafo import PantallaGrafo


def main(page: ft.Page):
    page.title = "TravelPath"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 980
    page.window.height = 760

    grafo = Grafo.desde_json()

    contenedor = ft.Container(expand=True)

    # Guarda el último resultado para poder volver de grafo a resultados.
    estado = {"resultado": None}

    # --- Interruptor de tema claro / oscuro ---
    boton_tema = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE,
        tooltip="Cambiar a tema claro",
    )

    def alternar_tema(_event):
        if page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
            boton_tema.icon = ft.Icons.DARK_MODE
            boton_tema.tooltip = "Cambiar a tema oscuro"
        else:
            page.theme_mode = ft.ThemeMode.DARK
            boton_tema.icon = ft.Icons.LIGHT_MODE
            boton_tema.tooltip = "Cambiar a tema claro"
        page.update()

    boton_tema.on_click = alternar_tema

    barra_superior = ft.Row(
        [
            ft.Text("TravelPath", size=18, weight=ft.FontWeight.BOLD),
            boton_tema,
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    def ver_formulario():
        contenedor.content = PantallaFormulario(
            grafo=grafo,
            on_calcular=ver_resultados,
        )
        page.update()

    def ver_resultados(resultado):
        estado["resultado"] = resultado
        contenedor.content = PantallaResultados(
            grafo=grafo,
            resultado=resultado,
            presupuesto=resultado.presupuesto,
            on_ver_en_grafo=ver_grafo,
            on_volver=ver_formulario,
        )
        page.update()

    def ver_grafo(ruta):
        contenedor.content = PantallaGrafo(
            grafo=grafo,
            ruta_seleccionada=ruta,
            on_volver=lambda: ver_resultados(estado["resultado"]),
        )
        page.update()

    page.add(
        ft.Container(content=barra_superior, padding=ft.Padding(16, 8, 16, 0)),
        contenedor,
    )
    ver_formulario()


if __name__ == "__main__":
    ft.app(target=main)
