"""Shell de escritorio y enrutamiento de las pantallas de TravelPath."""

from __future__ import annotations

import flet as ft

from lib.models.entrada import Entrada
from lib.services.planificador_viaje import ResultadoPlanificacion
from lib.structures.grafo import Grafo
from lib.ui.estilos import (
    DARK_BACKGROUND,
    PRIMARY,
    boton_principal,
    boton_secundario,
    encabezado,
    tema_claro,
    tema_oscuro,
)
from lib.ui.pantalla_formulario import PantallaFormulario
from lib.ui.pantalla_grafo import PantallaGrafo
from lib.ui.pantalla_orden import PantallaOrden
from lib.ui.pantalla_resultados import PantallaResultados


class _ShellEscritorio:
    """Construye la navegación lateral sin mezclarla con la lógica de dominio."""

    def __init__(self, page: ft.Page, grafo: Grafo):
        self.page = page
        self.grafo = grafo
        self.contenedor = ft.Container(expand=True)
        self.estado: dict[str, object] = {"resultado": None, "entrada": None}
        self._nav_buttons: dict[str, ft.Control] = {}

        self.boton_tema = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Cambiar a tema oscuro",
            on_click=self._alternar_tema,
        )
        self.boton_info = ft.IconButton(
            icon=ft.Icons.INFO_OUTLINE,
            tooltip="Cómo funciona TravelPath",
            on_click=self._mostrar_info,
        )
        self.barra_superior = self._crear_barra_superior()
        self.sidebar = self._crear_sidebar()
        self.layout = ft.Row(
            [
                self.sidebar,
                ft.VerticalDivider(width=1),
                ft.Container(
                    content=self.contenedor,
                    expand=True,
                    padding=ft.Padding(28, 24, 34, 28),
                ),
            ],
            expand=True,
            spacing=0,
        )

    def _crear_barra_superior(self) -> ft.Control:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(
                                    ft.Icons.ROUTE,
                                    color=ft.Colors.WHITE,
                                    size=20,
                                ),
                                width=38,
                                height=38,
                                alignment=ft.Alignment(0, 0),
                                bgcolor=PRIMARY,
                                border_radius=12,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        "TravelPath",
                                        size=19,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        "Planificador de viajes",
                                        size=11,
                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                    ),
                                ],
                                spacing=0,
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Row([self.boton_info, self.boton_tema], spacing=4),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.Padding(24, 12, 24, 12),
            bgcolor=ft.Colors.SURFACE,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=12,
                color=ft.Colors.with_opacity(0.12, ft.Colors.SHADOW),
                offset=ft.Offset(0, 2),
            ),
        )

    def _mostrar_info(self, _event: ft.ControlEvent) -> None:
        """Muestra una guía breve de uso dentro de la aplicación."""
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.INFO_OUTLINE, color=PRIMARY),
                    ft.Text("Cómo funciona TravelPath", weight=ft.FontWeight.BOLD),
                ],
                spacing=10,
            ),
            content=ft.Container(
                width=560,
                content=ft.Column(
                    [
                        ft.Text(
                            "Planifica un recorrido y compara las mejores alternativas "
                            "según costo, tiempo y restricciones de orden.",
                            size=14,
                        ),
                        ft.Divider(),
                        self._ayuda_bloque(
                            "1. Datos del viaje",
                            "Elige el origen, los destinos, el presupuesto, la cantidad "
                            "de rutas y la prioridad entre precio y tiempo.",
                        ),
                        self._ayuda_bloque(
                            "2. Orden de visita",
                            "Puedes dejar que el algoritmo decida, fijar una secuencia "
                            "completa o agregar reglas como «A antes que B».",
                        ),
                        self._ayuda_bloque(
                            "3. Resultados",
                            "La mejor ruta aparece primero. El peso sirve para ordenar; "
                            "el presupuesto siempre se compara contra el dinero real.",
                        ),
                        self._ayuda_bloque(
                            "4. Grafo y simulación",
                            "Usa «Ver en grafo» para observar los destinos, los pesos y "
                            "el recorrido tramo por tramo.",
                        ),
                    ],
                    spacing=12,
                    scroll=ft.ScrollMode.AUTO,
                ),
            ),
            actions=[
                ft.TextButton(
                    text="Cerrar",
                    on_click=lambda _event: self.page.close(dialog),
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.open(dialog)

    @staticmethod
    def _ayuda_bloque(titulo: str, descripcion: str) -> ft.Control:
        return ft.Column(
            [
                ft.Text(titulo, weight=ft.FontWeight.BOLD, color=PRIMARY),
                ft.Text(descripcion, size=13, color=ft.Colors.ON_SURFACE_VARIANT),
            ],
            spacing=3,
        )

    def _crear_sidebar(self) -> ft.Control:
        self._nav_buttons = {
            "planear": ft.TextButton(
                text="Planear viaje",
                icon=ft.Icons.EXPLORE,
                on_click=lambda _event: self.ver_formulario(),
            ),
            "rutas": ft.TextButton(
                text="Mis rutas",
                icon=ft.Icons.ROUTE,
                on_click=lambda _event: self._ir_a_resultados(),
            ),
            "grafo": ft.TextButton(
                text="Explorar grafo",
                icon=ft.Icons.ACCOUNT_TREE,
                on_click=lambda _event: self._ir_a_grafo(),
            ),
        }
        for boton in self._nav_buttons.values():
            boton.width = 190
            boton.height = 46
            boton.style = ft.ButtonStyle(
                alignment=ft.Alignment(-0.8, 0),
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.Padding(14, 0, 14, 0),
            )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("MENÚ", size=11, weight=ft.FontWeight.BOLD, color=PRIMARY),
                    self._nav_buttons["planear"],
                    self._nav_buttons["rutas"],
                    self._nav_buttons["grafo"],
                    ft.Divider(height=24),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.Icons.LIGHTBULB_OUTLINE, color=PRIMARY),
                                ft.Text(
                                    "Consejo",
                                    weight=ft.FontWeight.BOLD,
                                    size=13,
                                ),
                                ft.Text(
                                    "Ajusta precio y tiempo según tu prioridad.",
                                    size=11,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                            ],
                            spacing=6,
                        ),
                        padding=14,
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        border_radius=14,
                    ),
                ],
                spacing=6,
            ),
            width=230,
            padding=ft.Padding(20, 28, 16, 20),
            bgcolor=ft.Colors.SURFACE,
        )

    def _marcar_nav(self, activo: str) -> None:
        for nombre, boton in self._nav_buttons.items():
            boton.style = ft.ButtonStyle(
                color=PRIMARY if nombre == activo else ft.Colors.ON_SURFACE,
                bgcolor=(
                    ft.Colors.with_opacity(0.14, PRIMARY)
                    if nombre == activo
                    else ft.Colors.TRANSPARENT
                ),
                alignment=ft.Alignment(-0.8, 0),
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.Padding(14, 0, 14, 0),
            )

    def _alternar_tema(self, _event: ft.ControlEvent) -> None:
        if self.page.theme_mode == ft.ThemeMode.DARK:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.page.bgcolor = ft.Colors.SURFACE
            self.boton_tema.icon = ft.Icons.DARK_MODE
            self.boton_tema.tooltip = "Cambiar a tema oscuro"
        else:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.page.bgcolor = DARK_BACKGROUND
            self.boton_tema.icon = ft.Icons.LIGHT_MODE
            self.boton_tema.tooltip = "Cambiar a tema claro"
        self.page.update()

    def ver_formulario(self) -> None:
        self._marcar_nav("planear")
        self.contenedor.content = PantallaFormulario(
            grafo=self.grafo,
            on_continuar=self.ver_orden,
        )
        self.page.update()

    def ver_orden(self, entrada: Entrada) -> None:
        self.estado["entrada"] = entrada
        self._marcar_nav("planear")
        self.contenedor.content = PantallaOrden(
            grafo=self.grafo,
            entrada_base=entrada,
            on_calcular=self.ver_resultados,
            on_volver=self.ver_formulario,
        )
        self.page.update()

    def ver_resultados(self, resultado: ResultadoPlanificacion) -> None:
        self.estado["resultado"] = resultado
        self._marcar_nav("rutas")
        self.contenedor.content = PantallaResultados(
            grafo=self.grafo,
            resultado=resultado,
            presupuesto=resultado.presupuesto,
            on_ver_en_grafo=self.ver_grafo,
            on_volver=self.ver_formulario,
        )
        self.page.update()

    def ver_grafo(self, ruta) -> None:
        self._marcar_nav("grafo")
        self.contenedor.content = PantallaGrafo(
            grafo=self.grafo,
            ruta_seleccionada=ruta,
            on_volver=lambda: self.ver_resultados(self.estado["resultado"]),
        )
        self.page.update()

    def _ir_a_resultados(self) -> None:
        resultado = self.estado.get("resultado")
        if resultado is not None:
            self.ver_resultados(resultado)

    def _ir_a_grafo(self) -> None:
        resultado = self.estado.get("resultado")
        if resultado is not None and resultado.rutas:
            self.ver_grafo(resultado.rutas[0])


def main(page: ft.Page):
    page.title = "TravelPath · Planificador de viajes"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = tema_claro()
    page.dark_theme = tema_oscuro()
    page.bgcolor = ft.Colors.SURFACE
    page.padding = 0
    page.window.width = 1180
    page.window.height = 820
    page.window.min_width = 900
    page.window.min_height = 650

    shell = _ShellEscritorio(page, Grafo.desde_json())
    page.add(shell.barra_superior, shell.layout)
    shell.ver_formulario()


if __name__ == "__main__":
    ft.app(target=main)
