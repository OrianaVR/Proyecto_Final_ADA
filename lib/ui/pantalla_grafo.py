"""Pantalla 3: Visualización del grafo de destinos (HU-13).

Capa de UI asignada a Integrante 5. Esta pantalla SOLO dibuja: toma los datos
ya calculados del `Grafo` y de una `Ruta` opcional y los pinta sobre un
`flet.canvas.Canvas`. No contiene lógica de algoritmos (Dijkstra, Branch and
Bound, normalización, etc.): esa responsabilidad vive en `structures/` y
`algorithms/`.

Criterios de aceptación cubiertos (HU-13):
- Nodos en círculo con la fórmula x = cx + r·cos(2πk/n), y = cy + r·sin(2πk/n).
- Aristas con su peso combinado como etiqueta.
- Nodo origen resaltado con un color distinto.
- Separación de capas: la clase únicamente dibuja.
"""

from __future__ import annotations

import math
from typing import Callable, List, Optional, Tuple

import flet as ft
import flet.canvas as cv

from lib.models.ruta import Ruta
from lib.structures.grafo import Grafo


# --- Parámetros de dibujo (constantes de presentación, no de dominio) ---
_ANCHO = 560
_ALTO = 460
_RADIO_CIRCULO = 170          # radio de la circunferencia donde se ubican los nodos
_RADIO_NODO = 18              # radio de cada nodo
_COLOR_NODO = ft.Colors.BLUE_400
_COLOR_NODO_ORIGEN = ft.Colors.AMBER_400
_COLOR_ARISTA_BASE = ft.Colors.with_opacity(0.22, ft.Colors.GREY_400)
_COLOR_ARISTA_RUTA = ft.Colors.GREEN_400
_COLOR_TEXTO = ft.Colors.WHITE
_COLOR_TEXTO_PESO = ft.Colors.GREY_300


class PantallaGrafo(ft.Container):
    """Dibuja los destinos en círculo y, si se entrega, resalta una ruta."""

    def __init__(
        self,
        grafo: Grafo,
        ruta_seleccionada: Optional[Ruta] = None,
        on_volver: Optional[Callable] = None,
    ):
        super().__init__(expand=True, padding=20)
        self.grafo = grafo
        self.ruta_seleccionada = ruta_seleccionada
        self.on_volver = on_volver

        # Centro del lienzo.
        self._cx = _ANCHO / 2
        self._cy = _ALTO / 2

        # Posiciones (x, y) de cada nodo, indexadas por id de destino.
        self._posiciones: dict[int, Tuple[float, float]] = self._calcular_posiciones()

        self.canvas = cv.Canvas(
            shapes=self._construir_formas(),
            width=_ANCHO,
            height=_ALTO,
        )

        self.content = ft.Column(
            controls=[
                ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.ARROW_BACK,
                            tooltip="Volver",
                            on_click=lambda _: (
                                self.on_volver() if self.on_volver else None
                            ),
                        ),
                        ft.Text(
                            "Visualización del grafo",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ]
                ),
                self._leyenda(),
                ft.Container(
                    content=self.canvas,
                    alignment=ft.Alignment(0, 0),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        )

    # ------------------------------------------------------------------ #
    # Geometría de los nodos
    # ------------------------------------------------------------------ #
    def _calcular_posiciones(self) -> dict[int, Tuple[float, float]]:
        """Distribuye los nodos en círculo con la fórmula de la HU-13.

        x = cx + r·cos(2πk/n), y = cy + r·sin(2πk/n)
        """
        posiciones: dict[int, Tuple[float, float]] = {}
        n = self.grafo.num_destinos
        if n == 0:
            return posiciones
        for k, destino in enumerate(self.grafo.destinos):
            angulo = 2 * math.pi * k / n
            x = self._cx + _RADIO_CIRCULO * math.cos(angulo)
            y = self._cy + _RADIO_CIRCULO * math.sin(angulo)
            posiciones[destino.id] = (x, y)
        return posiciones

    def _id_origen(self) -> Optional[int]:
        """El origen es el primer destino de la ruta, si hay ruta."""
        if self.ruta_seleccionada and self.ruta_seleccionada.destinos:
            return self.ruta_seleccionada.destinos[0]
        return None

    # ------------------------------------------------------------------ #
    # Construcción de las formas del canvas
    # ------------------------------------------------------------------ #
    def _construir_formas(self) -> List[cv.Shape]:
        """Ensambla aristas base, aristas de la ruta, nodos y etiquetas."""
        formas: List[cv.Shape] = []
        formas.extend(self._formas_aristas_base())
        formas.extend(self._formas_nodos())
        return formas

    def _pares_ruta(self) -> set[frozenset[int]]:
        """Conjunto de pares (sin dirección) que forman los tramos de la ruta."""
        if not self.ruta_seleccionada:
            return set()
        return {
            frozenset((tramo.origen, tramo.destino))
            for tramo in self.ruta_seleccionada.tramos
        }

    def _formas_aristas_base(self) -> List[cv.Shape]:
        """Dibuja cada conexión del grafo una sola vez, con su peso.

        Se recorre solo la mitad superior de la matriz (i < j) para no duplicar
        la línea ni la etiqueta de un par de nodos. Si el par pertenece a la
        ruta seleccionada, la línea se dibuja resaltada; en caso contrario, en
        gris tenue. La etiqueta de peso se dibuja UNA vez por par, con el color
        acorde (así no se superponen dos textos sobre el mismo punto).
        """
        formas: List[cv.Shape] = []
        destinos = self.grafo.destinos
        n = len(destinos)
        pares_ruta = self._pares_ruta()
        for i in range(n):
            for j in range(i + 1, n):
                id_i = destinos[i].id
                id_j = destinos[j].id
                x1, y1 = self._posiciones[id_i]
                x2, y2 = self._posiciones[id_j]
                en_ruta = frozenset((id_i, id_j)) in pares_ruta
                formas.append(
                    cv.Line(
                        x1=x1,
                        y1=y1,
                        x2=x2,
                        y2=y2,
                        paint=ft.Paint(
                            stroke_width=3 if en_ruta else 1,
                            color=_COLOR_ARISTA_RUTA if en_ruta else _COLOR_ARISTA_BASE,
                        ),
                    )
                )
                # Etiqueta de peso en el punto medio de la arista (una sola vez).
                peso = self.grafo.peso(id_i, id_j)
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                formas.append(
                    cv.Text(
                        x=mx,
                        y=my,
                        text=f"{peso:.2f}",
                        style=ft.TextStyle(
                            size=11 if en_ruta else 10,
                            color=_COLOR_ARISTA_RUTA if en_ruta else _COLOR_TEXTO_PESO,
                            weight=ft.FontWeight.BOLD if en_ruta else None,
                        ),
                    )
                )
        return formas

    def _formas_nodos(self) -> List[cv.Shape]:
        """Dibuja cada nodo como un círculo con su nombre; origen en otro color."""
        formas: List[cv.Shape] = []
        id_origen = self._id_origen()
        for destino in self.grafo.destinos:
            x, y = self._posiciones[destino.id]
            es_origen = destino.id == id_origen
            formas.append(
                cv.Circle(
                    x=x,
                    y=y,
                    radius=_RADIO_NODO,
                    paint=ft.Paint(
                        color=_COLOR_NODO_ORIGEN if es_origen else _COLOR_NODO,
                    ),
                )
            )
            etiqueta = destino.alias or destino.nombre
            formas.append(
                cv.Text(
                    x=x,
                    y=y + _RADIO_NODO + 2,
                    text=etiqueta,
                    style=ft.TextStyle(
                        size=12,
                        color=_COLOR_TEXTO,
                        weight=ft.FontWeight.BOLD,
                    ),
                    alignment=ft.Alignment(0, 0),
                )
            )
        return formas

    # ------------------------------------------------------------------ #
    # Leyenda
    # ------------------------------------------------------------------ #
    def _leyenda(self) -> ft.Control:
        elementos: List[ft.Control] = [
            self._item_leyenda(_COLOR_NODO, "Destino"),
            self._item_leyenda(_COLOR_NODO_ORIGEN, "Origen"),
        ]
        if self.ruta_seleccionada:
            elementos.append(self._item_leyenda(_COLOR_ARISTA_RUTA, "Ruta seleccionada"))
        elementos.append(self._item_leyenda(_COLOR_ARISTA_BASE, "Conexión (peso)"))
        return ft.Row(elementos, wrap=True, spacing=16)

    @staticmethod
    def _item_leyenda(color: str, texto: str) -> ft.Control:
        return ft.Row(
            [
                ft.Container(width=14, height=14, bgcolor=color, border_radius=3),
                ft.Text(texto, size=12),
            ],
            spacing=5,
            tight=True,
        )
