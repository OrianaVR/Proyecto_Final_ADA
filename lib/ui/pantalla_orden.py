"""Segunda pantalla: configuración del orden de visita."""

from __future__ import annotations

from dataclasses import replace
from typing import Callable, Optional

import flet as ft

from lib.models.entrada import Entrada
from lib.services.planificador_viaje import PlanificadorViaje, ResultadoPlanificacion
from lib.ui.estilos import boton_principal, boton_secundario, encabezado, pasos, tarjeta_seccion, texto_ayuda
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
                    text="Dejar que TravelPath decida",
                ),
                ft.dropdown.Option(
                    key=self.MODO_SECUENCIA,
                    text="Elegir el orden completo",
                ),
                ft.dropdown.Option(
                    key=self.MODO_PRECEDENCIAS,
                    text="Indicar prioridades entre destinos",
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
            label="Primero debe visitarse",
            width=200,
            options=list(opciones),
        )
        self.dd_despues = ft.Dropdown(
            label="Después se visita",
            width=200,
            options=list(opciones),
        )
        self.dd_primero = ft.Dropdown(
            label="Quiero comenzar por...",
            width=240,
            options=list(opciones),
        )
        self.lista_precedencias = ft.Column()

        self.ayuda_modo = texto_ayuda(
            "Si no tienes una preferencia, elige la primera opción y TravelPath "
            "buscará automáticamente una buena combinación."
        )
        self.seccion_orden_total = ft.Container(
            content=tarjeta_seccion(
                ft.Column(
                    [
                        texto_ayuda(
                            "Arrastra las ciudades para decidir exactamente el "
                            "orden en el que quieres visitarlas."
                        ),
                        self.lista_orden,
                    ],
                    spacing=12,
                ),
                "Quiero elegir todo el orden",
                ft.Icons.FORMAT_LIST_NUMBERED,
            ),
            visible=False,
        )
        self.seccion_precedencias = ft.Container(
            content=tarjeta_seccion(
                ft.Column(
                    [
                        texto_ayuda(
                            "Indica solo las prioridades importantes. TravelPath "
                            "decidirá el resto del recorrido."
                        ),
                        ft.Row(
                            [
                                self.dd_antes,
                                self.dd_despues,
                                ft.IconButton(
                                    ft.Icons.ADD_CIRCLE,
                                    tooltip="Añadir prioridad",
                                    on_click=self._agregar_precedencia,
                                ),
                            ],
                            wrap=True,
                            spacing=12,
                        ),
                        ft.Row(
                            [
                                self.dd_primero,
                                ft.TextButton(
                                    text="Empezar por esta ciudad",
                                    icon=ft.Icons.FLAG,
                                    on_click=self._marcar_primero,
                                ),
                            ],
                            wrap=True,
                            spacing=12,
                        ),
                        self.lista_precedencias,
                    ],
                    spacing=12,
                ),
                "Quiero establecer algunas prioridades",
                ft.Icons.ACCOUNT_TREE,
            ),
            visible=False,
        )

        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=18,
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
                        encabezado(
                            "Orden de visita",
                            "Define cómo debe organizarse el recorrido",
                            ft.Icons.SORT,
                        ),
                    ],
                    spacing=8,
                ),
                pasos(3),
                tarjeta_seccion(
                    ft.Column(
                        [
                            ft.Text(
                                self._resumen_viaje(),
                                size=13,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                            ),
                            self.dd_modo,
                            self.ayuda_modo,
                        ],
                        spacing=12,
                    ),
                    "Configuración del orden",
                    ft.Icons.TUNE,
                ),
                self.seccion_orden_total,
                self.seccion_precedencias,
                self.mensaje,
                ft.Row(
                    [
                        boton_secundario(
                            "Volver a datos",
                            ft.Icons.ARROW_BACK,
                            lambda _event: (
                                self.on_volver() if self.on_volver else None
                            ),
                        ),
                        boton_principal(
                            "Buscar mejores rutas",
                            ft.Icons.AUTO_AWESOME,
                            self._calcular,
                        ),
                    ],
                    wrap=True,
                    spacing=12,
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
        modo = self.dd_modo.value or self.MODO_LIBRE
        self.seccion_orden_total.visible = modo == self.MODO_SECUENCIA
        self.seccion_precedencias.visible = modo == self.MODO_PRECEDENCIAS
        if modo == self.MODO_SECUENCIA:
            self.ayuda_modo.value = (
                "Arrastra las ciudades de la lista hasta obtener el recorrido "
                "exacto que quieres realizar."
            )
        elif modo == self.MODO_PRECEDENCIAS:
            self.ayuda_modo.value = (
                "Agrega solo las reglas importantes; TravelPath elegirá el resto "
                "del orden automáticamente."
            )
        else:
            self.ayuda_modo.value = (
                "TravelPath comparará las combinaciones posibles y buscará una "
                "ruta conveniente para ti."
            )
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
            self.mensaje.value = "Selecciona las dos ciudades para crear la prioridad."
            self.update()
            return

        antes = int(self.dd_antes.value)
        despues = int(self.dd_despues.value)
        if antes == despues:
            self.mensaje.value = "Elige dos ciudades diferentes."
            self.update()
            return
        if (antes, despues) not in self._precedencias:
            self._precedencias.append((antes, despues))
        self.mensaje.value = ""
        self._actualizar_lista_precedencias()
        self.update()

    def _marcar_primero(self, _event: ft.ControlEvent) -> None:
        if self.dd_primero.value is None:
            self.mensaje.value = "Selecciona la ciudad desde la que quieres comenzar."
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
        if resultado.mensaje_error and not resultado.rutas_fuera_presupuesto:
            self.mensaje.value = resultado.mensaje_error
            self.update()
            return
        if self.on_calcular:
            # Aunque el presupuesto sea insuficiente, pasamos a resultados
            # cuando existe una alternativa para que el usuario pueda verla.
            self.on_calcular(resultado)
