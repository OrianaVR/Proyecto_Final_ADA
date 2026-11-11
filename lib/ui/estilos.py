"""Sistema visual compartido de TravelPath.

Contiene únicamente presentación. No incluye reglas de negocio ni cálculos de
rutas. Las pantallas reutilizan estos estilos para mantener una apariencia
consistente en formulario, orden, resultados y grafo.
"""

from __future__ import annotations

import flet as ft

# Paleta de marca.
PRIMARY = "#14B8A6"       # turquesa
PRIMARY_DARK = "#0F766E"
SECONDARY = "#38BDF8"     # azul cielo
SUCCESS = "#22C55E"
WARNING = "#F59E0B"
ERROR = "#F87171"
DARK_BACKGROUND = "#0B1220"
DARK_SURFACE = "#121D2E"
DARK_SURFACE_ALT = "#18263A"
LIGHT_BACKGROUND = "#F4F7FB"
LIGHT_SURFACE = "#FFFFFF"
LIGHT_SURFACE_ALT = "#E8F0F7"


def tema_oscuro() -> ft.Theme:
    """Tema oscuro de la aplicación."""
    return ft.Theme(
        color_scheme_seed=PRIMARY,
        use_material3=True,
        font_family="Segoe UI",
        scaffold_bgcolor=DARK_BACKGROUND,
        canvas_color=DARK_BACKGROUND,
        card_color=DARK_SURFACE,
        divider_color="#2A3A50",
    )


def tema_claro() -> ft.Theme:
    """Tema claro de la aplicación."""
    return ft.Theme(
        color_scheme_seed=PRIMARY,
        use_material3=True,
        font_family="Segoe UI",
        scaffold_bgcolor=LIGHT_BACKGROUND,
        canvas_color=LIGHT_BACKGROUND,
        card_color=LIGHT_SURFACE,
        divider_color="#CBD5E1",
    )


def encabezado(
    titulo: str,
    subtitulo: str,
    icono: str | ft.Icons,
) -> ft.Control:
    """Crea un encabezado consistente para las pantallas."""
    return ft.Row(
        [
            ft.Container(
                content=ft.Icon(icono, color=ft.Colors.WHITE, size=26),
                width=48,
                height=48,
                alignment=ft.Alignment(0, 0),
                bgcolor=PRIMARY,
                border_radius=14,
            ),
            ft.Column(
                [
                    ft.Text(titulo, size=27, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        subtitulo,
                        size=13,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                ],
                spacing=2,
                expand=True,
            ),
        ],
        spacing=14,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


def tarjeta_seccion(
    contenido: ft.Control,
    titulo: str | None = None,
    icono: str | ft.Icons | None = None,
) -> ft.Control:
    """Envuelve controles en una superficie visual con jerarquía."""
    controles: list[ft.Control] = []
    if titulo:
        cabecera: list[ft.Control] = []
        if icono:
            cabecera.append(ft.Icon(icono, color=PRIMARY, size=20))
        cabecera.append(ft.Text(titulo, size=16, weight=ft.FontWeight.BOLD))
        controles.append(ft.Row(cabecera, spacing=8))
    controles.append(contenido)
    return ft.Container(
        content=ft.Column(controles, spacing=12),
        padding=20,
        bgcolor=ft.Colors.SURFACE,
        border=ft.Border(
            top=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
            right=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
            bottom=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
            left=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
        ),
        border_radius=16,
    )


def texto_ayuda(texto: str) -> ft.Text:
    """Texto secundario legible para instrucciones."""
    return ft.Text(
        texto,
        size=13,
        color=ft.Colors.ON_SURFACE_VARIANT,
    )


def boton_principal(texto: str, icono: str | ft.Icons, on_click) -> ft.FilledButton:
    """Botón principal con tamaño y jerarquía consistentes."""
    return ft.FilledButton(
        text=texto,
        icon=icono,
        on_click=on_click,
        height=46,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.Padding(20, 0, 20, 0),
        ),
    )


def boton_secundario(texto: str, icono: str | ft.Icons, on_click) -> ft.OutlinedButton:
    """Botón secundario con estilo consistente."""
    return ft.OutlinedButton(
        text=texto,
        icon=icono,
        on_click=on_click,
        height=44,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.Padding(18, 0, 18, 0),
        ),
    )


def pasos(activo: int) -> ft.Control:
    """Indicador visual de las etapas principales del planificador."""
    nombres = [(1, "Lugares"), (2, "Preferencias"), (3, "Orden")]
    controles: list[ft.Control] = []
    for indice, nombre in nombres:
        completado = indice < activo
        actual = indice == activo
        color = PRIMARY if completado or actual else ft.Colors.OUTLINE
        etiqueta = "✓" if completado else str(indice)
        controles.append(
            ft.Column(
                [
                    ft.Container(
                        content=ft.Text(
                            etiqueta,
                            color=ft.Colors.WHITE if completado or actual else ft.Colors.ON_SURFACE_VARIANT,
                            size=12,
                            weight=ft.FontWeight.BOLD,
                        ),
                        width=32,
                        height=32,
                        alignment=ft.Alignment(0, 0),
                        bgcolor=color if completado or actual else ft.Colors.TRANSPARENT,
                        border=ft.Border(
                            top=ft.BorderSide(1, color),
                            right=ft.BorderSide(1, color),
                            bottom=ft.BorderSide(1, color),
                            left=ft.BorderSide(1, color),
                        ),
                        border_radius=16,
                    ),
                    ft.Text(
                        nombre,
                        size=11,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
            )
        )
        if indice < len(nombres):
            controles.append(
                ft.Container(
                    content=ft.Divider(
                        height=1,
                        color=PRIMARY if indice < activo else ft.Colors.OUTLINE_VARIANT,
                    ),
                    expand=True,
                    margin=ft.Margin(0, 15, 0, 0),
                )
            )
    return ft.Row(controles, vertical_alignment=ft.CrossAxisAlignment.START)
