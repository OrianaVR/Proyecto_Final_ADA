"""Formulario de parámetros para solicitar una planificación."""

from typing import Callable, Optional

import flet as ft

from lib.models.entrada import Entrada
from lib.services.planificador_viaje import PlanificadorViaje, ResultadoPlanificacion
from lib.structures.grafo import Grafo


class PantallaFormulario(ft.Container):
    """Permite configurar una entrada y enviarla al coordinador."""

    def __init__(
        self,
        grafo: Grafo,
        on_calcular: Optional[Callable[[ResultadoPlanificacion], None]] = None,
        planificador: Optional[PlanificadorViaje] = None,
    ):
        super().__init__(expand=True, padding=20)
        self.grafo = grafo
        self.on_calcular = on_calcular
        self.planificador = planificador or PlanificadorViaje(grafo)
        self._destinos_seleccionados: list[int] = []
        self._orden: list[int] = []

        self.dd_origen = ft.Dropdown(
            label="Ciudad de origen",
            options=[
                ft.dropdown.Option(key=str(destino.id), text=destino.nombre)
                for destino in grafo.destinos
            ],
            width=300,
        )
        self.chips_destinos = ft.Row(wrap=True, spacing=10)
        self.txt_presupuesto = ft.TextField(
            label="Presupuesto ($)", value="500", width=200
        )
        self.txt_k = ft.TextField(label="Rutas K", value="10", width=120)
        self.sw_ida_vuelta = ft.Switch(label="Ida y vuelta", value=False)
        self.sw_definir_orden = ft.Switch(
            label="Definir orden", value=False, on_change=self._cambiar_modo_orden
        )
        self.slider_alfa = ft.Slider(
            min=0.0,
            max=1.0,
            value=0.5,
            divisions=10,
            label="α: {value}",
            on_change=self._actualizar_ponderaciones,
        )
        self.lbl_ponderaciones = ft.Text("α: 0.50 | β: 0.50")
        self.lista_orden = ft.ReorderableListView(
            visible=False, height=180, on_reorder=self._reordenar
        )
        self.mensaje = ft.Text(color=ft.Colors.RED)

        for destino in grafo.destinos:
            self.chips_destinos.controls.append(
                ft.Chip(
                    label=destino.nombre,
                    data=destino.id,
                    on_select=self._cambiar_destino,
                )
            )

        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text(
                    "TravelPath: Formulario de planificación",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                ),
                self.dd_origen,
                ft.Text("Destinos a visitar (máximo 12):"),
                self.chips_destinos,
                ft.Row(
                    [
                        self.txt_presupuesto,
                        self.txt_k,
                        self.sw_ida_vuelta,
                        self.sw_definir_orden,
                    ],
                    wrap=True,
                ),
                self.lista_orden,
                ft.Text("Prioridad precio / tiempo:"),
                self.slider_alfa,
                self.lbl_ponderaciones,
                self.mensaje,
                ft.FilledButton(
                    content=ft.Text("Calcular"),
                    icon=ft.Icons.CALCULATE,
                    on_click=self._calcular,
                ),
            ],
        )

    def _cambiar_destino(self, evento: ft.ControlEvent) -> None:
        destino = int(evento.control.data)
        if evento.control.selected:
            if len(self._destinos_seleccionados) >= 12:
                evento.control.selected = False
                self.mensaje.value = "Puedes seleccionar como máximo 12 destinos."
            else:
                self._destinos_seleccionados.append(destino)
                self._orden.append(destino)
        else:
            self._destinos_seleccionados.remove(destino)
            self._orden.remove(destino)
        self._actualizar_lista_orden()
        self.update()

    def _cambiar_modo_orden(self, evento: ft.ControlEvent) -> None:
        self.lista_orden.visible = bool(evento.control.value)
        self._actualizar_lista_orden()
        self.update()

    def _actualizar_lista_orden(self) -> None:
        nombres = {destino.id: destino.nombre for destino in self.grafo.destinos}
        if not self._orden:
            self.lista_orden.controls = []
            return
        if self.sw_definir_orden.value:
            self.lista_orden.controls = [
                ft.ListTile(
                    key=str(destino),
                    title=ft.Text(f"{posicion}. {nombres[destino]}"),
                )
                for posicion, destino in enumerate(self._orden, start=1)
            ]
        else:
            self.lista_orden.controls = []

    def _reordenar(self, evento: ft.ControlEvent) -> None:
        antiguo = int(evento.old_index)
        nuevo = int(evento.new_index)
        destino = self._orden.pop(antiguo)
        self._orden.insert(nuevo, destino)
        self._actualizar_lista_orden()
        self.update()

    def _actualizar_ponderaciones(self, evento: ft.ControlEvent) -> None:
        alfa = float(evento.control.value)
        self.lbl_ponderaciones.value = f"α: {alfa:.2f} | β: {1 - alfa:.2f}"
        self.update()

    def _calcular(self, _: ft.ControlEvent) -> None:
        self.mensaje.value = ""
        try:
            origen = int(self.dd_origen.value)
            alfa = float(self.slider_alfa.value)
            entrada = Entrada(
                origen=origen,
                destinos=list(self._destinos_seleccionados),
                presupuesto=float(self.txt_presupuesto.value or 0),
                k=int(self.txt_k.value or 0),
                ida_y_vuelta=bool(self.sw_ida_vuelta.value),
                alfa=alfa,
                beta=1 - alfa,
                secuencia_orden=(
                    list(self._orden) if self.sw_definir_orden.value else None
                ),
            )
        except (TypeError, ValueError):
            self.mensaje.value = (
                "Revisa el origen, el presupuesto y la cantidad de rutas K."
            )
            self.update()
            return

        resultado = self.planificador.planificar(entrada)
        if resultado.mensaje_error:
            self.mensaje.value = resultado.mensaje_error
            self.update()
            return
        if self.on_calcular:
            self.on_calcular(resultado)
