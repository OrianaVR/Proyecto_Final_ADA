import pytest

from lib.algorithms.dijkstra import dijkstra
from lib.algorithms.orden_total import (
    PresupuestoInsuficienteError,
    SecuenciaInvalidaError,
    ruta_por_secuencia,
)
from lib.structures.grafo import Grafo
from lib.structures.tabla_precedencias import TablaPrecedencias
from utils_grafos import crear_grafo


@pytest.fixture(scope="module")
def grafo():
    return Grafo.desde_json()


# Bogotá=0, Medellín=1, Cali=2, Cartagena=4, Pereira=6
def test_ruta_basica_suma_los_tramos_dijkstra(grafo):
    ruta = ruta_por_secuencia(grafo, 0, [1, 4])
    prohibidos = {0, 1, 4}
    leg1 = dijkstra(grafo, 0, 1, "peso", prohibidos=prohibidos)
    leg2 = dijkstra(grafo, 1, 4, "peso", prohibidos=prohibidos)

    assert ruta.destinos == [0, 1, 4]
    assert ruta.peso_total == pytest.approx(leg1.peso + leg2.peso)
    assert ruta.costo_total == pytest.approx(leg1.dinero + leg2.dinero)
    assert ruta.tiempo_total == pytest.approx(leg1.tiempo + leg2.tiempo)


def test_los_tramos_forman_un_recorrido_continuo(grafo):
    ruta = ruta_por_secuencia(grafo, 0, [2, 7, 5])
    assert ruta.tramos[0].origen == 0
    assert ruta.tramos[-1].destino == 5
    for anterior, siguiente in zip(ruta.tramos, ruta.tramos[1:]):
        assert anterior.destino == siguiente.origen
    assert sum(t.costo for t in ruta.tramos) == pytest.approx(ruta.costo_total)
    assert sum(t.peso for t in ruta.tramos) == pytest.approx(ruta.peso_total)
    # Cada destino seleccionado aparece en el recorrido, en el orden pedido.
    visitadas = [t.destino for t in ruta.tramos]
    posiciones = [visitadas.index(c) for c in (2, 7, 5)]
    assert posiciones == sorted(posiciones)


def test_ciudades_de_paso_no_son_ciudades_seleccionadas(grafo):
    ruta = ruta_por_secuencia(grafo, 0, [2, 7, 5], ida_y_vuelta=True)
    assert not (set(ruta.ciudades_paso) & set(ruta.destinos))


def test_la_secuencia_puede_empezar_con_el_origen(grafo):
    a = ruta_por_secuencia(grafo, 0, [1, 4])
    b = ruta_por_secuencia(grafo, 0, [0, 1, 4])
    assert a.destinos == b.destinos == [0, 1, 4]
    assert a.costo_total == pytest.approx(b.costo_total)


def test_ida_y_vuelta_agrega_el_regreso(grafo):
    ida = ruta_por_secuencia(grafo, 0, [1, 4])
    ida_vuelta = ruta_por_secuencia(grafo, 0, [1, 4], ida_y_vuelta=True)
    regreso = dijkstra(grafo, 4, 0, "peso", prohibidos={0, 1, 4})
    assert ida_vuelta.destinos == [0, 1, 4, 0]
    assert ida_vuelta.costo_total == pytest.approx(ida.costo_total + regreso.dinero)
    assert ida_vuelta.peso_total == pytest.approx(ida.peso_total + regreso.peso)


def test_un_solo_destino(grafo):
    ruta = ruta_por_secuencia(grafo, 0, [6])
    assert ruta.destinos == [0, 6]
    assert ruta.costo_total > 0


# --------------------------------------------------------------------- presupuesto
def test_presupuesto_justo_se_acepta(grafo):
    base = ruta_por_secuencia(grafo, 0, [1, 4])
    ruta = ruta_por_secuencia(grafo, 0, [1, 4], presupuesto=base.costo_total)
    assert ruta.costo_total == pytest.approx(base.costo_total)


def test_presupuesto_insuficiente_informa_el_minimo(grafo):
    with pytest.raises(PresupuestoInsuficienteError) as error:
        ruta_por_secuencia(grafo, 0, [1, 4], presupuesto=10)
    minimo = error.value.minimo_necesario
    # El mínimo es la suma de los tramos más baratos en dinero.
    prohibidos = {0, 1, 4}
    esperado = (
        dijkstra(grafo, 0, 1, "dinero", prohibidos=prohibidos).dinero
        + dijkstra(grafo, 1, 4, "dinero", prohibidos=prohibidos).dinero
    )
    assert minimo == pytest.approx(esperado)
    assert "mínimo necesario" in str(error.value)
    # Y con exactamente ese mínimo la ruta sí se puede armar.
    assert ruta_por_secuencia(grafo, 0, [1, 4], presupuesto=minimo).costo_total <= minimo + 1e-6


def test_el_presupuesto_se_compara_contra_dinero_no_contra_peso(grafo):
    # El peso combinado es adimensional y pequeño (< 3); si se confundiera con el
    # dinero, un presupuesto de 5 pesos pasaría. No debe pasar.
    ruta = ruta_por_secuencia(grafo, 0, [1, 4])
    assert ruta.peso_total < 5
    with pytest.raises(PresupuestoInsuficienteError):
        ruta_por_secuencia(grafo, 0, [1, 4], presupuesto=5)


def test_si_la_ruta_de_menor_peso_no_cabe_se_usa_la_de_menor_dinero():
    # 0 -> 2: directo = 10 pesos y lento; por 1 = 80 pesos y rápido. Con beta=1 gana el rápido.
    costo = [[0, 40, 10], [40, 0, 40], [10, 40, 0]]
    tiempo = [[0, 1, 20], [1, 0, 1], [20, 1, 0]]
    g = crear_grafo(costo, tiempo, alfa=0.0, beta=1.0)

    sin_tope = ruta_por_secuencia(g, 0, [2])
    assert sin_tope.ciudades_paso == [1] and sin_tope.costo_total == pytest.approx(80)

    con_tope = ruta_por_secuencia(g, 0, [2], presupuesto=50)
    assert con_tope.ciudades_paso == [] and con_tope.costo_total == pytest.approx(10)

    with pytest.raises(PresupuestoInsuficienteError) as error:
        ruta_por_secuencia(g, 0, [2], presupuesto=5)
    assert error.value.minimo_necesario == pytest.approx(10)


def test_sin_presupuesto_no_hay_tope(grafo):
    assert ruta_por_secuencia(grafo, 0, [9, 3, 8], presupuesto=None).costo_total > 0


# --------------------------------------------------------------------- precedencias y entradas inválidas
def test_secuencia_que_respeta_las_precedencias(grafo):
    tabla = TablaPrecedencias()
    tabla.agregar_precedencia(1, 4)  # Medellín antes que Cartagena
    ruta = ruta_por_secuencia(grafo, 0, [1, 4], precedencias=tabla)
    assert ruta.destinos == [0, 1, 4]


def test_secuencia_que_viola_una_precedencia(grafo):
    tabla = TablaPrecedencias()
    tabla.agregar_precedencia(4, 1)  # Cartagena antes que Medellín
    with pytest.raises(SecuenciaInvalidaError) as error:
        ruta_por_secuencia(grafo, 0, [1, 4], precedencias=tabla)
    assert "Cartagena" in str(error.value) and "Medellín" in str(error.value)


def test_secuencia_vacia_repetida_o_fuera_de_rango(grafo):
    with pytest.raises(ValueError):
        ruta_por_secuencia(grafo, 0, [])
    with pytest.raises(ValueError):
        ruta_por_secuencia(grafo, 0, [1, 4, 1])
    with pytest.raises(ValueError):
        ruta_por_secuencia(grafo, 0, [1, 0, 4])
    with pytest.raises(IndexError):
        ruta_por_secuencia(grafo, 0, [1, 99])
