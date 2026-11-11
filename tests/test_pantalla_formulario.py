import types

from lib.models.entrada import Entrada
from lib.models.ruta import Ruta
from lib.services.planificador_viaje import ResultadoPlanificacion
from lib.structures.grafo import Grafo
from lib.ui.pantalla_formulario import PantallaFormulario
from lib.ui.pantalla_orden import PantallaOrden


class PlanificadorCaptura:
    def __init__(self):
        self.entrada = None

    def planificar(self, entrada):
        self.entrada = entrada
        return ResultadoPlanificacion(
            rutas=[
                Ruta(
                    destinos=[entrada.origen, *entrada.destinos],
                    peso_total=0,
                    costo_total=0,
                    tiempo_total=0,
                )
            ],
            presupuesto=entrada.presupuesto,
        )


def crear_entrada():
    return Entrada(
        origen=0,
        destinos=[1, 4, 5],
        presupuesto=10000,
        k=5,
        alfa=0.5,
        beta=0.5,
    )


def crear_orden():
    planificador = PlanificadorCaptura()
    pantalla = PantallaOrden(
        grafo=Grafo.desde_json(),
        entrada_base=crear_entrada(),
        planificador=planificador,
    )
    pantalla.update = lambda: None
    return pantalla, planificador


def test_formulario_pasa_datos_basicos_a_la_segunda_pantalla():
    capturado = []
    formulario = PantallaFormulario(
        grafo=Grafo.desde_json(),
        on_continuar=capturado.append,
    )
    formulario.update = lambda: None
    formulario.dd_origen.value = "0"
    formulario.txt_presupuesto.value = "10000"
    formulario.txt_k.value = "5"

    for indice in (1, 4, 5):
        control = formulario.chips_destinos.controls[indice]
        control.value = True
        formulario._cambiar_destino(types.SimpleNamespace(control=control))

    formulario._continuar(None)

    assert len(capturado) == 1
    assert capturado[0].origen == 0
    assert capturado[0].destinos == [1, 4, 5]
    assert capturado[0].presupuesto == 10000


def test_precedencias_se_envian_al_planificador():
    pantalla, planificador = crear_orden()
    pantalla.dd_modo.value = PantallaOrden.MODO_PRECEDENCIAS
    pantalla.dd_antes.value = "1"
    pantalla.dd_despues.value = "4"
    pantalla._agregar_precedencia(None)
    pantalla.dd_antes.value = "1"
    pantalla.dd_despues.value = "5"
    pantalla._agregar_precedencia(None)

    pantalla._calcular(None)

    assert planificador.entrada.precedencias == {4: {1}, 5: {1}}
    assert planificador.entrada.secuencia_orden is None


def test_orden_total_se_envia_sin_precedencias():
    pantalla, planificador = crear_orden()
    pantalla.dd_modo.value = PantallaOrden.MODO_SECUENCIA
    pantalla._orden = [5, 1, 4]
    pantalla._calcular(None)

    assert planificador.entrada.secuencia_orden == [5, 1, 4]
    assert planificador.entrada.precedencias == {}


def test_pantalla_orden_expone_los_tres_modos():
    pantalla, _ = crear_orden()
    valores = {opcion.key for opcion in pantalla.dd_modo.options}

    assert valores == {
        PantallaOrden.MODO_LIBRE,
        PantallaOrden.MODO_SECUENCIA,
        PantallaOrden.MODO_PRECEDENCIAS,
    }
    assert pantalla.lista_orden.visible is True
    assert pantalla.dd_antes.options
    assert pantalla.dd_despues.options
