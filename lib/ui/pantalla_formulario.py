"""Primera pantalla: datos básicos del viaje."""

from __future__ import annotations

from typing import Callable, Optional

import flet as ft

from lib.models.entrada import Entrada
from lib.services.planificador_viaje import PlanificadorViaje, ResultadoPlanificacion
from lib.structures.grafo import Grafo


class PantallaFormulario(ft.Container):
    """Recoge origen, destinos y parámetros generales del viaje.

    La configuración del orden se realiza en ``PantallaOrden``. Separarla evita
    mezclar selección de destinos con reglas de precedencia en una sola vista.
    """

    def __init__(
        self,
        grafo: Grafo,
        on_continuar: Optional[Callable[[Entrada], None]] = None,
        planificador: Optional[PlanificadorViaje] = None,
    ):
        super().__init__(expand=True, padding=20)
        self.grafo = grafo
        self.on_continuar = on_continuar
        self.planificador = planificador or PlanificadorViaje(grafo)
        self._destinos_seleccionados: list[int] = []
        self.mensaje = ft.Text(color=ft.Colors.RED)

        self.dd_origen = ft.Dropdown(
            label="Ciudad de origen",
            options=[
                ft.dropdown.Option(key=str(destino.id), text=destino.nombre)
                for destino in grafo.destinos
            ],
            width=320,
        )
        self.chips_destinos = ft.Row(wrap=True, spacing=10)
        self.lbl_contador = ft.Text("0 / 12 destinos", size=12)
        self.txt_presupuesto = ft.TextField(
            label="Presupuesto ($)", value="500", width=210
        )
        self.txt_k = ft.TextField(label="Rutas K", value="10", width=130)
        self.sw_ida_vuelta = ft.Switch(label="Ida y vuelta", value=False)
        self.slider_alfa = ft.Slider(
            min=0.0,
            max=1.0,
            value=0.5,
            divisions=10,
            label="α: {value}",
            on_change=self._actualizar_ponderaciones,
        )
        self.lbl_ponderaciones = ft.Text("α: 0.50 | β: 0.50")

        for destino in grafo.destinos:
            self.chips_destinos.controls.append(
                ft.Checkbox(
                    label=destino.nombre,
                    value=False,
                    data=destino.id,
                    on_change=self._cambiar_destino,
                )
            )

        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text(
                    "TravelPath: Datos del viaje",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "Selecciona el origen y los destinos. En el siguiente paso "
                    "podrás definir el orden de visita.",
                    size=13,
                ),
                self.dd_origen,
                ft.Text("Destinos a visitar (máximo 12):"),
                self.chips_destinos,
                self.lbl_contador,
                ft.Row(
                    [
                        self.txt_presupuesto,
                        self.txt_k,
                        self.sw_ida_vuelta,
                    ],
                    wrap=True,
                ),
                ft.Text("Prioridad precio / tiempo:"),
                self.slider_alfa,
                self.lbl_ponderaciones,
                self.mensaje,
                ft.FilledButton(
                    text="Continuar al orden de visita",
                    icon=ft.Icons.ARROW_FORWARD,
                    on_click=self._continuar,
                ),
            ],
        )

    def _cambiar_destino(self, evento: ft.ControlEvent) -> None:
        destino = int(evento.control.data)
        seleccionado = bool(evento.control.value)
        if seleccionado and destino not in self._destinos_seleccionados:
            if len(self._destinos_seleccionados) >= 12:
                evento.control.value = False
                self.mensaje.value = "Puedes seleccionar como máximo 12 destinos."
            else:
                self._destinos_seleccionados.append(destino)
        elif not seleccionado and destino in self._destinos_seleccionados:
            self._destinos_seleccionados.remove(destino)

        self.lbl_contador.value = f"{len(self._destinos_seleccionados)} / 12 destinos"
        self.update()

    def _actualizar_ponderaciones(self, evento: ft.ControlEvent) -> None:
        alfa = float(evento.control.value)
        self.lbl_ponderaciones.value = f"α: {alfa:.2f} | β: {1 - alfa:.2f}"
        self.update()

    def _continuar(self, _event: ft.ControlEvent) -> None:
        self.mensaje.value = ""
        if self.dd_origen.value is None:
            self.mensaje.value = "Selecciona una ciudad de origen."
            self.update()
            return
        if not self._destinos_seleccionados:
            self.mensaje.value = "Selecciona al menos un destino."
            self.update()
            return

        try:
            origen = int(self.dd_origen.value)
            destinos = list(self._destinos_seleccionados)
            if origen in destinos:
                nombre = next(d.nombre for d in self.grafo.destinos if d.id == origen)
                self.mensaje.value = (
                    f"El origen ({nombre}) no puede estar entre los destinos."
                )
                self.update()
                return
            entrada = Entrada(
                origen=origen,
                destinos=destinos,
                presupuesto=float(self.txt_presupuesto.value or 0),
                k=int(self.txt_k.value or 0),
                ida_y_vuelta=bool(self.sw_ida_vuelta.value),
                alfa=float(self.slider_alfa.value),
                beta=1 - float(self.slider_alfa.value),
            )
        except (TypeError, ValueError):
            self.mensaje.value = "Revisa el presupuesto y la cantidad de rutas K."
            self.update()
            return

        if self.on_continuar:
            self.on_continuar(entrada)
