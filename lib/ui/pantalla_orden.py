"""Segunda pantalla: configuración del orden de visita."""

from __future__ import annotations

from dataclasses import replace
from typing import Callable, Optional

import flet as ft

from lib.models.entrada import Entrada
from lib.services.planificador_viaje import PlanificadorViaje, ResultadoPlanificacion
from lib.structures.grafo import Grafo


class PantallaOrden(ft.Container):
    """Permite elegir sin orden, orden total o precedencias parciales."""

    MODO_LIBRE = "libre"
    MODO_SECUENCIA = "secuencia"
    MODO_PRECEDENCIAS = "precedencias"

    def __init__(
        self,
        grafo: Grafo,
        entrada_base: Entrada,
        on_calcular: Optional[Callable[[ResultadoPlanificacion], None]] = None,
        on_volver: Optional[Callable[[], None]] = None,
        planificador: Optional[PlanificadorViaje] = None,
    ):
        super().__init__(expand=True, padding=20)
        self.grafo = grafo
        self.entrada_base = entrada_base
        self.on_calcular = on_calcular
        self.on_volver = on_volver
        self.planificador = planificador or PlanificadorViaje(grafo)
        self._orden = list(entrada_base.destinos)
        self._precedencias: list[tuple[int, int]] = []
        self.mensaje = ft.Text(color=ft.Colors.RED)
        self.nombres = {destino.id: destino.nombre for destino in grafo.destinos}

        self.dd_modo = ft.Dropdown(
            label="Tipo de orden",
            value=self.MODO_LIBRE,
            width=360,
            options=[
                ft.dropdown.Option(
                    key=self.MODO_LIBRE,
                    text="Sin orden: el algoritmo decide",
                ),
                ft.dropdown.Option(
                    key=self.MODO_SECUENCIA,
                    text="Orden total: reordenar destinos",
                ),
                ft.dropdown.Option(
                    key=self.MODO_PRECEDENCIAS,
                    text="Precedencias: A antes que B",
                ),
            ],
            on_change=self._cambiar_modo,
        )

        self.lista_orden = ft.ReorderableListView(
            height=220,
            controls=[],
            on_reorder=self._reordenar,
        )
        self._actualizar_lista_orden()

        opciones = [
            ft.dropdown.Option(key=str(destino), text=self.nombres[destino])
            for destino in entrada_base.destinos
        ]
        self.dd_antes = ft.Dropdown(
            label="Visitar antes",
            width=200,
            options=list(opciones),
        )
        self.dd_despues = ft.Dropdown(
            label="que",
            width=200,
            options=list(opciones),
        )
        self.dd_primero = ft.Dropdown(
            label="Ciudad que va primero",
            width=240,
            options=list(opciones),
        )
        self.lista_precedencias = ft.Column()

        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.ARROW_BACK,
                            tooltip="Volver a datos del viaje",
                            on_click=lambda _event: (
                                self.on_volver() if self.on_volver else None
                            ),
                        ),
                        ft.Text(
                            "Orden de visita",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ]
                ),
                ft.Text(
                    "Elige cómo debe decidirse el recorrido. Puedes dejarlo "
                    "sin orden y continuar.",
                    size=13,
                ),
                ft.Text(
                    self._resumen_viaje(),
                    size=12,
                    color=ft.Colors.GREY_500,
                ),
                self.dd_modo,
                ft.Text(
                    "Orden total: arrastra los destinos para fijar la secuencia "
                    "completa.",
                    weight=ft.FontWeight.BOLD,
                ),
                self.lista_orden,
                ft.Text(
                    "Precedencias: agrega solo las reglas que quieras respetar.",
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Row(
                    [
                        self.dd_antes,
                        self.dd_despues,
                        ft.IconButton(
                            ft.Icons.ADD,
                            tooltip="Agregar regla A antes que B",
                            on_click=self._agregar_precedencia,
                        ),
                    ],
                    wrap=True,
                ),
                ft.Row(
                    [
                        self.dd_primero,
                        ft.TextButton(
                            text="Marcar este primero",
                            icon=ft.Icons.FLAG,
                            on_click=self._marcar_primero,
                        ),
                    ],
                    wrap=True,
                ),
                self.lista_precedencias,
                self.mensaje,
                ft.Row(
                    [
                        ft.OutlinedButton(
                            text="Volver a datos",
                            icon=ft.Icons.ARROW_BACK,
                            on_click=lambda _event: (
                                self.on_volver() if self.on_volver else None
                            ),
                        ),
                        ft.FilledButton(
                            text="Calcular rutas",
                            icon=ft.Icons.CALCULATE,
                            on_click=self._calcular,
                        ),
                    ],
                    wrap=True,
                ),
            ],
        )

    def _resumen_viaje(self) -> str:
        destinos = " → ".join(self.nombres[d] for d in self.entrada_base.destinos)
        ida_vuelta = "ida y vuelta" if self.entrada_base.ida_y_vuelta else "solo ida"
        return (
            f"Destinos seleccionados: {destinos} | "
            f"Presupuesto: ${self.entrada_base.presupuesto:,.2f} | {ida_vuelta}"
        )

    def _cambiar_modo(self, _event: ft.ControlEvent) -> None:
        self.mensaje.value = ""
        self.update()

    def _actualizar_lista_orden(self) -> None:
        self.lista_orden.controls = [
            ft.ListTile(
                key=str(destino),
                title=ft.Text(f"{posicion}. {self.nombres[destino]}"),
            )
            for posicion, destino in enumerate(self._orden, start=1)
        ]

    def _reordenar(self, evento: ft.ControlEvent) -> None:
        antiguo = int(evento.old_index)
        nuevo = int(evento.new_index)
        destino = self._orden.pop(antiguo)
        self._orden.insert(nuevo, destino)
        self._actualizar_lista_orden()
        self.update()

    def _agregar_precedencia(self, _event: ft.ControlEvent) -> None:
        if self.dd_antes.value is None or self.dd_despues.value is None:
            self.mensaje.value = "Selecciona las dos ciudades de la regla."
            self.update()
            return

        antes = int(self.dd_antes.value)
        despues = int(self.dd_despues.value)
        if antes == despues:
            self.mensaje.value = "Una ciudad no puede ir antes que sí misma."
            self.update()
            return
        if (antes, despues) not in self._precedencias:
            self._precedencias.append((antes, despues))
        self.mensaje.value = ""
        self._actualizar_lista_precedencias()
        self.update()

    def _marcar_primero(self, _event: ft.ControlEvent) -> None:
        if self.dd_primero.value is None:
            self.mensaje.value = "Selecciona la ciudad que debe ir primero."
            self.update()
            return

        primero = int(self.dd_primero.value)
        for destino in self.entrada_base.destinos:
            if destino != primero and (primero, destino) not in self._precedencias:
                self._precedencias.append((primero, destino))
        self.mensaje.value = ""
        self._actualizar_lista_precedencias()
        self.update()

    def _quitar_precedencia(self, par: tuple[int, int]) -> None:
        if par in self._precedencias:
            self._precedencias.remove(par)
        self._actualizar_lista_precedencias()
        self.update()

    def _actualizar_lista_precedencias(self) -> None:
        self.lista_precedencias.controls = [
            ft.Row(
                [
                    ft.Text(f"{self.nombres[antes]} → {self.nombres[despues]}"),
                    ft.IconButton(
                        ft.Icons.DELETE_OUTLINE,
                        tooltip="Quitar regla",
                        on_click=lambda _event, par=(antes, despues): self._quitar_precedencia(par),
                    ),
                ],
                tight=True,
            )
            for antes, despues in self._precedencias
        ]

    def _construir_precedencias(self) -> dict[int, set[int]]:
        resultado: dict[int, set[int]] = {}
        for antes, despues in self._precedencias:
            resultado.setdefault(despues, set()).add(antes)
        return resultado

    def _calcular(self, _event: ft.ControlEvent) -> None:
        modo = self.dd_modo.value or self.MODO_LIBRE
        entrada = replace(
            self.entrada_base,
            precedencias=(
                self._construir_precedencias()
                if modo == self.MODO_PRECEDENCIAS
                else {}
            ),
            secuencia_orden=(
                list(self._orden) if modo == self.MODO_SECUENCIA else None
            ),
        )

        resultado = self.planificador.planificar(entrada)
        if resultado.mensaje_error:
            self.mensaje.value = resultado.mensaje_error
            self.update()
            return
        if self.on_calcular:
            self.on_calcular(resultado)
