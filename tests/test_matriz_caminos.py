import random

import pytest

from lib.algorithms.dijkstra import dijkstra
from lib.algorithms.matriz_caminos import MatrizCaminos
from lib.structures.grafo import Grafo
from utils_grafos import crear_grafo, mejor_valor_bruto


@pytest.fixture(scope="module")
def grafo():
    return Grafo.desde_json()


def test_forma_y_diagonal(grafo):
    m = MatrizCaminos.construir(grafo, 0, [1, 4, 7])
    assert m.nodos == [0, 1, 4, 7]
    for matriz in (m.d_peso, m.d_dinero, m.d_min):
        assert len(matriz) == 4 and all(len(fila) == 4 for fila in matriz)
        assert all(matriz[i][i] == 0 for i in range(4))


@pytest.mark.parametrize("alfa,beta", [(0.5, 0.5), (0.9, 0.1), (0.0, 1.0)])
def test_las_tres_matrices_coinciden_con_fuerza_bruta(alfa, beta):
    g = Grafo.desde_json(alfa=alfa, beta=beta)
    rng = random.Random(5)
    for _ in range(6):
        seleccion = rng.sample(range(g.num_destinos), rng.randint(3, 5))
        origen, destinos = seleccion[0], seleccion[1:]
        m = MatrizCaminos.construir(g, origen, destinos)
        for a in m.nodos:
            for b in m.nodos:
                assert m.peso(a, b) == pytest.approx(
                    mejor_valor_bruto(g, a, b, "peso", seleccion), abs=1e-9
                )
                assert m.dinero_min(a, b) == pytest.approx(
                    mejor_valor_bruto(g, a, b, "dinero", seleccion), abs=1e-9
                )


def test_dinero_es_el_del_camino_de_menor_peso_y_nunca_baja_del_minimo(grafo):
    m = MatrizCaminos.construir(grafo, 0, [2, 5, 9])
    for a in m.nodos:
        for b in m.nodos:
            assert m.dinero(a, b) == pytest.approx(m.camino_peso(a, b).dinero)
            assert m.dinero_min(a, b) <= m.dinero(a, b) + 1e-9


def test_coincide_con_dijkstra_par_por_par(grafo):
    destinos = [3, 6, 8]
    m = MatrizCaminos.construir(grafo, 1, destinos)
    seleccion = {1, *destinos}
    for a in m.nodos:
        for b in m.nodos:
            esperado = dijkstra(grafo, a, b, "peso", prohibidos=seleccion)
            assert m.camino_peso(a, b).camino == esperado.camino
            assert m.peso(a, b) == pytest.approx(esperado.peso)


def test_los_caminos_no_pasan_por_otras_ciudades_seleccionadas(grafo):
    m = MatrizCaminos.construir(grafo, 0, [1, 2, 6])
    seleccion = set(m.nodos)
    for a in m.nodos:
        for b in m.nodos:
            for camino in (m.camino_peso(a, b), m.camino_dinero(a, b)):
                assert not (set(camino.ciudades_paso) & seleccion)


def test_hay_ciudades_de_paso_cuando_conviene():
    # 0 -> 2 directo cuesta 500; por la ciudad 1 (no seleccionada) cuesta 110.
    costo = [[0, 100, 500, 400], [100, 0, 10, 400], [500, 10, 0, 10], [400, 400, 10, 0]]
    tiempo = [[0, 5, 20, 15], [5, 0, 1, 15], [20, 1, 0, 1], [15, 15, 1, 0]]
    g = crear_grafo(costo, tiempo)
    m = MatrizCaminos.construir(g, 0, [2, 3])
    assert m.dinero_min(0, 2) == pytest.approx(110)
    assert m.camino_dinero(0, 2).ciudades_paso == [1]


def test_incluye_el_regreso_al_origen(grafo):
    m = MatrizCaminos.construir(grafo, 0, [4, 7])
    assert m.peso(4, 0) > 0
    assert m.dinero_min(7, 0) > 0


def test_consulta_por_id_y_posicion(grafo):
    m = MatrizCaminos.construir(grafo, 3, [8, 1])
    assert m.posicion(3) == 0 and m.posicion(8) == 1 and m.posicion(1) == 2
    assert m.d_peso[m.posicion(8)][m.posicion(1)] == m.peso(8, 1)


def test_ciudad_que_no_esta_en_la_matriz(grafo):
    m = MatrizCaminos.construir(grafo, 0, [1, 2])
    with pytest.raises(KeyError):
        m.peso(0, 9)


def test_entradas_invalidas(grafo):
    with pytest.raises(ValueError):
        MatrizCaminos.construir(grafo, 0, [1, 0])  # origen entre los destinos
    with pytest.raises(ValueError):
        MatrizCaminos.construir(grafo, 0, [1, 1])  # repetido
    with pytest.raises(IndexError):
        MatrizCaminos.construir(grafo, 0, [1, 99])


def test_sin_destinos_solo_queda_el_origen(grafo):
    m = MatrizCaminos.construir(grafo, 2, [])
    assert m.nodos == [2] and m.d_peso == [[0.0]]
