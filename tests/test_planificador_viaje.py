import pytest

from lib.algorithms.matriz_caminos import MatrizCaminos
from lib.models.entrada import Entrada
from lib.services.planificador_viaje import PlanificadorViaje
from lib.structures.grafo import Grafo
from lib.structures.tabla_precedencias import TablaPrecedencias


@pytest.fixture
def planificador():
    return PlanificadorViaje(Grafo.desde_json())


def test_usa_dijkstra_para_secuencia_total(planificador):
    resultado = planificador.planificar(
        Entrada(origen=0, destinos=[1, 4], presupuesto=1000, secuencia_orden=[1, 4])
    )
    assert resultado.exitosa
    assert resultado.modalidad == "dijkstra_por_tramos"
    assert resultado.rutas[0].destinos == [0, 1, 4]


def test_usa_branch_and_bound_para_orden_parcial(planificador):
    resultado = planificador.planificar(
        Entrada(origen=0, destinos=[1, 4], presupuesto=1000, secuencia_orden=[1])
    )
    assert resultado.exitosa
    assert resultado.modalidad == "branch_and_bound"


def test_rechaza_ciclo_y_menciona_destinos(planificador):
    resultado = planificador.planificar(
        Entrada(
            origen=0,
            destinos=[1, 4],
            presupuesto=1000,
            precedencias={1: {4}, 4: {1}},
        )
    )
    assert not resultado.exitosa
    assert "ciclo" in (resultado.mensaje_error or "").lower()
    assert "Medellín" in (resultado.mensaje_error or "")


def test_rechaza_secuencia_que_viola_precedencia(planificador):
    resultado = planificador.planificar(
        Entrada(
            origen=0,
            destinos=[1, 4],
            presupuesto=1000,
            precedencias={1: {4}},
            secuencia_orden=[1, 4],
        )
    )
    assert not resultado.exitosa
    assert "Cartagena" in (resultado.mensaje_error or "")
    assert "Medellín" in (resultado.mensaje_error or "")


def test_rechaza_mas_de_12_destinos(planificador):
    resultado = planificador.planificar(
        Entrada(origen=0, destinos=list(range(1, 14)), presupuesto=1000)
    )
    assert "Demasiados destinos" in (resultado.mensaje_error or "")


def test_informa_minimo_de_presupuesto(planificador):
    resultado = planificador.planificar(
        Entrada(
            origen=0,
            destinos=[1, 4],
            presupuesto=1,
            secuencia_orden=[1, 4],
        )
    )
    assert not resultado.exitosa
    assert resultado.minimo_necesario is not None
    assert len(resultado.rutas_fuera_presupuesto) == 1
    assert "Ninguna ruta cabe en tu presupuesto" in (
        resultado.mensaje_error or ""
    )



def test_minimo_de_presupuesto_respeta_precedencias(planificador):
    """El mínimo mostrado no debe ser solo la cota sin restricciones."""
    destinos = [1, 2, 3, 4]
    sin_reglas = Entrada(origen=0, destinos=destinos, presupuesto=10000)
    con_regla = Entrada(
        origen=0,
        destinos=destinos,
        presupuesto=10000,
        precedencias={1: {4}},  # Medellín después de Cartagena
    )

    matriz = MatrizCaminos.construir(planificador.grafo, 0, destinos)
    minimo_sin_reglas = PlanificadorViaje._minimo_dinero_factible(
        matriz, TablaPrecedencias()
    )
    tabla = TablaPrecedencias({1: {4}})
    minimo_con_regla = PlanificadorViaje._minimo_dinero_factible(matriz, tabla)

    assert minimo_con_regla >= minimo_sin_reglas

    resultado = planificador.planificar(
        Entrada(
            origen=0,
            destinos=destinos,
            presupuesto=minimo_con_regla - 0.01,
            precedencias={1: {4}},
        )
    )
    assert not resultado.exitosa
    assert resultado.minimo_necesario == pytest.approx(minimo_con_regla)
