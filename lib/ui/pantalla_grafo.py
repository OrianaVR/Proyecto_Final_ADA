"""Pantalla 3: Visualización del grafo de destinos (HU-13 y HU-14).

Capa de UI asignada a Integrante 5. Esta pantalla SOLO dibuja y anima: toma los
datos ya calculados del `Grafo` y de una `Ruta` opcional y los pinta sobre un
`flet.canvas.Canvas`. No contiene lógica de algoritmos (Dijkstra, Branch and
Bound, normalización, etc.): esa responsabilidad vive en `structures/` y
`algorithms/`.

Criterios de aceptación cubiertos:
- HU-13: nodos en círculo con x = cx + r·cos(2πk/n), y = cy + r·sin(2πk/n);
  aristas con su peso como etiqueta; nodo origen resaltado; solo dibujo.
- HU-14: simulación animada que ilumina el recorrido tramo por tramo en el
  orden de la ruta (incluye ida y vuelta y ciudades de paso, que ya vienen
  reflejadas en `ruta.tramos`).
"""

from __future__ import annotations

import math
import time
from typing import Callable, List, Optional, Tuple

import flet as ft
import flet.canvas as cv

from lib.models.ruta import Ruta
from lib.structures.grafo import Grafo


# --- Parámetros de dibujo (constantes de presentación, no de dominio) ---
_ANCHO = 600
_ALTO = 480
_RADIO_CIRCULO = 180          # radio de la circunferencia donde se ubican los nodos
_RADIO_NODO = 18              # radio de cada nodo
_SEPARACION_ETIQUETA = 11     # desplazamiento perpendicular de la etiqueta de peso
_LARGO_FLECHA = 12            # largo de la punta de flecha en los tramos de la ruta

_COLOR_NODO = ft.Colors.BLUE_400
_COLOR_NODO_ORIGEN = ft.Colors.AMBER_400
_COLOR_NODO_ACTIVO = ft.Colors.ORANGE_ACCENT_400
_COLOR_ARISTA_BASE = ft.Colors.with_opacity(0.30, ft.Colors.ON_SURFACE)
_COLOR_ARISTA_BASE_TENUE = ft.Colors.with_opacity(0.10, ft.Colors.ON_SURFACE)
_COLOR_ARISTA_RUTA = ft.Colors.GREEN_400          # tramo de la ruta ya recorrido
_COLOR_ARISTA_ACTIVA = ft.Colors.ORANGE_ACCENT_400  # tramo que se está iluminando
_COLOR_ARISTA_PENDIENTE = ft.Colors.with_opacity(0.35, ft.Colors.GREEN_200)
# Colores de texto que se adaptan al tema (claro/oscuro) de Flet: ON_SURFACE es
# oscuro en tema claro y claro en tema oscuro, así el texto siempre contrasta.
_COLOR_TEXTO = ft.Colors.ON_SURFACE
_COLOR_TEXTO_PESO = ft.Colors.with_opacity(0.7, ft.Colors.ON_SURFACE)
_COLOR_TEXTO_PESO_TENUE = ft.Colors.with_opacity(0.25, ft.Colors.ON_SURFACE)

# Duración (segundos) que cada tramo permanece como "activo" en la animación.
_DURACION_TRAMO = 0.7


class PantallaGrafo(ft.Container):
    """Dibuja los destinos en círculo, resalta una ruta y la anima."""

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

        # --- Estado de la animación (HU-14) ---
        # Número de tramos ya recorridos (pintados en verde).
        self._tramos_recorridos = 0
        # Índice del tramo que se está iluminando ahora mismo (None = ninguno).
        self._tramo_activo: Optional[int] = None
        # Marca para poder interrumpir una animación en curso.
        self._animando = False

        self.canvas = cv.Canvas(
            shapes=self._construir_formas(),
            width=_ANCHO,
            height=_ALTO,
        )

        self._boton_simular = ft.ElevatedButton(
            "Simular recorrido",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self._on_simular,
            disabled=not self._tiene_tramos(),
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
                self._panel_info_ruta(),
                ft.Row([self._boton_simular]),
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

    def _tiene_tramos(self) -> bool:
        return bool(self.ruta_seleccionada and self.ruta_seleccionada.tramos)

    def _animacion_en_curso(self) -> bool:
        """True si hay una simulación activa (para atenuar el grafo base)."""
        return self._tramos_recorridos > 0 or self._tramo_activo is not None

    # ------------------------------------------------------------------ #
    # Construcción de las formas del canvas
    # ------------------------------------------------------------------ #
    def _construir_formas(self) -> List[cv.Shape]:
        """Ensambla aristas base, tramos de la ruta, nodos y etiquetas."""
        formas: List[cv.Shape] = []
        formas.extend(self._formas_aristas_base())
        formas.extend(self._formas_tramos_ruta())
        formas.extend(self._formas_nodos())
        return formas

    @staticmethod
    def _offset_perpendicular(
        x1: float, y1: float, x2: float, y2: float, distancia: float
    ) -> Tuple[float, float]:
        """Devuelve el punto medio desplazado perpendicular a la línea.

        Sirve para separar la etiqueta de peso de la propia arista y evitar que
        el texto quede montado sobre la línea.
        """
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        longitud = math.hypot(dx, dy) or 1.0
        # Vector perpendicular normalizado.
        px, py = -dy / longitud, dx / longitud
        return mx + px * distancia, my + py * distancia

    def _formas_aristas_base(self) -> List[cv.Shape]:
        """Dibuja las conexiones del grafo en gris, con su peso.

        Se recorre solo la mitad superior de la matriz (i < j) para no duplicar
        la línea ni la etiqueta de un par de nodos. Los tramos que forman parte
        de la ruta se dibujan aparte en `_formas_tramos_ruta`. Durante la
        animación, el grafo base se atenúa para que la ruta resalte.
        """
        formas: List[cv.Shape] = []
        destinos = self.grafo.destinos
        n = len(destinos)
        pares_ruta = {
            frozenset((t.origen, t.destino)) for t in self.ruta_seleccionada.tramos
        } if self.ruta_seleccionada else set()

        atenuado = self._animacion_en_curso()
        color_linea = _COLOR_ARISTA_BASE_TENUE if atenuado else _COLOR_ARISTA_BASE
        color_texto = _COLOR_TEXTO_PESO_TENUE if atenuado else _COLOR_TEXTO_PESO

        for i in range(n):
            for j in range(i + 1, n):
                id_i = destinos[i].id
                id_j = destinos[j].id
                if frozenset((id_i, id_j)) in pares_ruta:
                    continue  # lo dibuja _formas_tramos_ruta
                x1, y1 = self._posiciones[id_i]
                x2, y2 = self._posiciones[id_j]
                formas.append(
                    cv.Line(
                        x1=x1,
                        y1=y1,
                        x2=x2,
                        y2=y2,
                        paint=ft.Paint(stroke_width=1, color=color_linea),
                    )
                )
                peso = self.grafo.peso(id_i, id_j)
                ex, ey = self._offset_perpendicular(x1, y1, x2, y2, _SEPARACION_ETIQUETA)
                formas.append(
                    cv.Text(
                        x=ex,
                        y=ey,
                        text=f"{peso:.2f}",
                        style=ft.TextStyle(size=10, color=color_texto),
                        alignment=ft.Alignment(0, 0),
                    )
                )
        return formas

    def _formas_tramos_ruta(self) -> List[cv.Shape]:
        """Dibuja los tramos de la ruta en el orden del recorrido.

        El color de cada tramo depende del estado de la animación (HU-14):
        - índice < tramos_recorridos  -> ya recorrido (verde)
        - índice == tramo_activo       -> iluminándose ahora (naranja, grueso)
        - resto                        -> pendiente (verde tenue)

        Cada tramo lleva una punta de flecha que indica el sentido del viaje.
        """
        if not self.ruta_seleccionada:
            return []
        formas: List[cv.Shape] = []
        for indice, tramo in enumerate(self.ruta_seleccionada.tramos):
            if (
                tramo.origen not in self._posiciones
                or tramo.destino not in self._posiciones
            ):
                continue
            x1, y1 = self._posiciones[tramo.origen]
            x2, y2 = self._posiciones[tramo.destino]

            if indice == self._tramo_activo:
                color, grosor = _COLOR_ARISTA_ACTIVA, 5
            elif indice < self._tramos_recorridos:
                color, grosor = _COLOR_ARISTA_RUTA, 3
            else:
                color, grosor = _COLOR_ARISTA_PENDIENTE, 2

            formas.append(
                cv.Line(
                    x1=x1,
                    y1=y1,
                    x2=x2,
                    y2=y2,
                    paint=ft.Paint(stroke_width=grosor, color=color),
                )
            )
            formas.extend(self._formas_flecha(x1, y1, x2, y2, color, grosor))

            peso = tramo.peso
            ex, ey = self._offset_perpendicular(x1, y1, x2, y2, _SEPARACION_ETIQUETA)
            formas.append(
                cv.Text(
                    x=ex,
                    y=ey,
                    text=f"{peso:.2f}",
                    style=ft.TextStyle(
                        size=11,
                        color=color,
                        weight=ft.FontWeight.BOLD,
                    ),
                    alignment=ft.Alignment(0, 0),
                )
            )
        return formas

    def _formas_flecha(
        self, x1: float, y1: float, x2: float, y2: float, color: str, grosor: int
    ) -> List[cv.Shape]:
        """Punta de flecha cerca del nodo destino que marca el sentido del tramo."""
        dx, dy = x2 - x1, y2 - y1
        longitud = math.hypot(dx, dy) or 1.0
        ux, uy = dx / longitud, dy / longitud
        # Punto de la flecha: justo antes del borde del nodo destino.
        bx, by = x2 - ux * _RADIO_NODO, y2 - uy * _RADIO_NODO
        ang = math.atan2(uy, ux)
        a1 = ang + math.radians(150)
        a2 = ang - math.radians(150)
        p1 = (bx + _LARGO_FLECHA * math.cos(a1), by + _LARGO_FLECHA * math.sin(a1))
        p2 = (bx + _LARGO_FLECHA * math.cos(a2), by + _LARGO_FLECHA * math.sin(a2))
        paint = ft.Paint(stroke_width=grosor, color=color)
        return [
            cv.Line(x1=bx, y1=by, x2=p1[0], y2=p1[1], paint=paint),
            cv.Line(x1=bx, y1=by, x2=p2[0], y2=p2[1], paint=paint),
        ]

    def _formas_nodos(self) -> List[cv.Shape]:
        """Dibuja cada nodo como un círculo con su nombre.

        El origen se resalta (ámbar) y, durante la animación, el nodo al que
        acaba de llegar el recorrido se marca como activo (naranja). Si hay
        ruta, se numera el orden de visita junto al nodo.
        """
        formas: List[cv.Shape] = []
        id_origen = self._id_origen()
        id_activo = self._id_nodo_activo()
        orden_visita = self._orden_visita()
        for destino in self.grafo.destinos:
            x, y = self._posiciones[destino.id]
            if destino.id == id_activo:
                color_nodo = _COLOR_NODO_ACTIVO
            elif destino.id == id_origen:
                color_nodo = _COLOR_NODO_ORIGEN
            else:
                color_nodo = _COLOR_NODO
            formas.append(
                cv.Circle(
                    x=x,
                    y=y,
                    radius=_RADIO_NODO,
                    paint=ft.Paint(color=color_nodo),
                )
            )
            # Número de orden de visita dentro del nodo (si pertenece a la ruta).
            if destino.id in orden_visita:
                formas.append(
                    cv.Text(
                        x=x,
                        y=y,
                        text=str(orden_visita[destino.id]),
                        style=ft.TextStyle(
                            size=13,
                            color=ft.Colors.BLACK,
                            weight=ft.FontWeight.BOLD,
                        ),
                        alignment=ft.Alignment(0, 0),
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

    def _orden_visita(self) -> dict[int, int]:
        """Mapa id_destino -> número de orden (1-based) de primera visita."""
        if not self.ruta_seleccionada:
            return {}
        orden: dict[int, int] = {}
        for posicion, ciudad in enumerate(self.ruta_seleccionada.destinos):
            if ciudad not in orden:  # el origen puede repetirse al cerrar el ciclo
                orden[ciudad] = posicion + 1
        return orden

    def _id_nodo_activo(self) -> Optional[int]:
        """Destino al que llega el tramo que se está iluminando, si hay uno."""
        if self._tramo_activo is None or not self.ruta_seleccionada:
            return None
        if 0 <= self._tramo_activo < len(self.ruta_seleccionada.tramos):
            return self.ruta_seleccionada.tramos[self._tramo_activo].destino
        return None

    # ------------------------------------------------------------------ #
    # Simulación animada (HU-14)
    # ------------------------------------------------------------------ #
    def _refrescar_canvas(self) -> None:
        """Recalcula las formas según el estado actual y actualiza el canvas."""
        self.canvas.shapes = self._construir_formas()
        self.canvas.update()

    def _on_simular(self, _event: ft.ControlEvent) -> None:
        """Lanza la animación en un hilo para no bloquear la interfaz."""
        if self._animando or not self._tiene_tramos():
            return
        # page.run_thread ejecuta la animación fuera del hilo de eventos de UI.
        self.page.run_thread(self._animar)

    def _animar(self) -> None:
        """Ilumina el recorrido tramo por tramo en el orden de la ruta."""
        self._animando = True
        self._boton_simular.disabled = True
        self._boton_simular.update()

        total = len(self.ruta_seleccionada.tramos)
        # Reinicia el estado visual antes de empezar.
        self._tramos_recorridos = 0
        self._tramo_activo = None
        self._refrescar_canvas()

        for indice in range(total):
            self._tramo_activo = indice
            self._refrescar_canvas()
            time.sleep(_DURACION_TRAMO)
            # El tramo pasa a "recorrido" y se apaga el activo.
            self._tramos_recorridos = indice + 1
            self._tramo_activo = None
            self._refrescar_canvas()

        self._animando = False
        self._boton_simular.disabled = False
        self._boton_simular.update()

    # ------------------------------------------------------------------ #
    # Panel de información y leyenda
    # ------------------------------------------------------------------ #
    def _panel_info_ruta(self) -> ft.Control:
        """Tarjeta con peso, dinero, tiempo y secuencia de la ruta seleccionada."""
        if not self.ruta_seleccionada:
            return ft.Container(
                content=ft.Text(
                    "Grafo completo de destinos. Vuelve a resultados y usa "
                    "«Ver en grafo» para resaltar y simular una ruta.",
                    size=12,
                    italic=True,
                    color=ft.Colors.with_opacity(0.7, ft.Colors.ON_SURFACE),
                ),
                padding=ft.Padding(0, 0, 0, 6),
            )
        r = self.ruta_seleccionada
        nombres = {d.id: d.nombre for d in self.grafo.destinos}
        secuencia = " → ".join(nombres.get(c, str(c)) for c in r.destinos)
        return ft.Card(
            content=ft.Container(
                padding=12,
                content=ft.Column(
                    [
                        ft.Text(secuencia, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            f"Peso: {r.peso_total:.4f}   |   "
                            f"Dinero: ${r.costo_total:,.2f}   |   "
                            f"Tiempo: {r.tiempo_total:.1f} h",
                            size=12,
                            color=ft.Colors.with_opacity(0.75, ft.Colors.ON_SURFACE),
                        ),
                    ],
                    spacing=4,
                ),
            ),
        )

    def _leyenda(self) -> ft.Control:
        elementos: List[ft.Control] = [
            self._item_leyenda(_COLOR_NODO, "Destino"),
            self._item_leyenda(_COLOR_NODO_ORIGEN, "Origen"),
        ]
        if self.ruta_seleccionada:
            elementos.append(self._item_leyenda(_COLOR_ARISTA_ACTIVA, "Tramo actual"))
            elementos.append(self._item_leyenda(_COLOR_ARISTA_RUTA, "Recorrido"))
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
