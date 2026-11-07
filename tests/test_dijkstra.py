import random

import pytest

from lib.algorithms.dijkstra import (
    CaminoNoEncontradoError,
    dijkstra,
    dijkstra_desde,
    reconstruir_camino,
)
from lib.structures.grafo import Grafo
from utils_grafos import crear_grafo, mejor_valor_bruto


@pytest.fixture(scope="module")
def grafo():
    return Grafo.desde_json()


def grafo_triangulo(alfa=0.5, beta=0.5):
    """0 -> 2 directo es caro (500), pero 0 -> 1 -> 2 cuesta 110 en total."""
    costo = [
        [0, 100, 500, 400],
        [100, 0, 10, 400],
        [500, 10, 0, 10],
        [400, 400, 10, 0],
    ]
    tiempo = [
        [0, 5, 20, 15],
        [5, 0, 1, 15],
        [20, 1, 0, 1],
        [15, 15, 1, 0],
    ]
    return crear_grafo(costo, tiempo, alfa, beta)


# --------------------------------------------------------------------- correctitud
@pytest.mark.parametrize("metrica", ["peso", "dinero", "tiempo"])
def test_coincide_con_fuerza_bruta_en_datos_reales(grafo, metrica):
    rng = random.Random(11)
    for _ in range(25):
        seleccion = rng.sample(range(grafo.num_destinos), rng.randint(3, 5))
        a, b = rng.sample(seleccion, 2)
        resultado = dijkstra(grafo, a, b, metrica, prohibidos=seleccion)
        esperado = mejor_valor_bruto(grafo, a, b, metrica, prohibidos=seleccion)
        assert resultado.valor == pytest.approx(esperado, abs=1e-9)


def test_sin_prohibidos_coincide_con_fuerza_bruta_en_todos_los_pares():
    g = crear_grafo(
        [[0, 7, 9, 20, 3], [7, 0, 10, 15, 8], [9, 10, 0, 11, 4], [20, 15, 11, 0, 6], [3, 8, 4, 6, 0]],
        [[0, 2, 3, 9, 1], [2, 0, 4, 7, 3], [3, 4, 0, 5, 2], [9, 7, 5, 0, 2], [1, 3, 2, 2, 0]],
        alfa=0.7,
        beta=0.3,
    )
    for a in range(5):
        for b in range(5):
            for metrica in ("peso", "dinero", "tiempo"):
                assert dijkstra(g, a, b, metrica).valor == pytest.approx(
                    mejor_valor_bruto(g, a, b, metrica), abs=1e-9
                )


# --------------------------------------------------------------------- ciudades de paso
def test_ruta_indirecta_mas_barata_que_el_tramo_directo():
    g = grafo_triangulo()
    r = dijkstra(g, 0, 2, "dinero")
    assert r.camino == [0, 1, 2]
    assert r.ciudades_paso == [1]
    assert r.dinero == pytest.approx(110)
    assert r.dinero < g.costo(0, 2)  # el directo cuesta 500


def test_prohibido_bloquea_la_ciudad_de_paso():
    g = grafo_triangulo()
    # Bloqueando solo la 1, aún se puede pasar por la 3 (400 + 10 = 410 < 500).
    r = dijkstra(g, 0, 2, "dinero", prohibidos=[1])
    assert r.camino == [0, 3, 2]
    assert 1 not in r.ciudades_paso
    # Bloqueando ambas, solo queda el tramo directo.
    r = dijkstra(g, 0, 2, "dinero", prohibidos=[1, 3])
    assert r.camino == [0, 2]
    assert r.ciudades_paso == []
    assert r.dinero == pytest.approx(500)


def test_prohibido_puede_ser_el_destino_o_el_origen():
    g = grafo_triangulo()
    r = dijkstra(g, 0, 2, "dinero", prohibidos=[0, 2])
    assert r.camino == [0, 1, 2]


def test_tramo_directo_no_tiene_ciudades_de_paso(grafo):
    r = dijkstra(grafo, 3, 4, "dinero")  # Barranquilla -> Cartagena, 35
    assert r.ciudades_paso == []
    assert r.camino == [3, 4]


# --------------------------------------------------------------------- métrica elegible
def test_la_metrica_cambia_el_camino_elegido():
    # Directo: barato en dinero, lento. Por 1: caro en dinero, rápido.
    costo = [[0, 40, 10], [40, 0, 40], [10, 40, 0]]
    tiempo = [[0, 1, 20], [1, 0, 1], [20, 1, 0]]
    g = crear_grafo(costo, tiempo, alfa=0.0, beta=1.0)
    assert dijkstra(g, 0, 2, "dinero").camino == [0, 2]
    assert dijkstra(g, 0, 2, "tiempo").camino == [0, 1, 2]
    assert dijkstra(g, 0, 2, "peso").camino == [0, 1, 2]  # con beta=1 pesa solo el tiempo


def test_costo_es_sinonimo_de_dinero(grafo):
    a = dijkstra(grafo, 0, 9, "costo")
    b = dijkstra(grafo, 0, 9, "dinero")
    assert a.camino == b.camino
    assert a.metrica == "dinero"


def test_metrica_invalida(grafo):
    with pytest.raises(ValueError):
        dijkstra(grafo, 0, 1, "distancia")


def test_peso_dinero_y_tiempo_se_reportan_juntos_y_son_consistentes(grafo):
    r = dijkstra(grafo, 0, 9, "peso", prohibidos=[0, 9])
    pares = list(zip(r.camino, r.camino[1:]))
    assert r.peso == pytest.approx(sum(grafo.peso(a, b) for a, b in pares))
    assert r.dinero == pytest.approx(sum(grafo.costo(a, b) for a, b in pares))
    assert r.tiempo == pytest.approx(sum(grafo.tiempo(a, b) for a, b in pares))
    assert r.valor == pytest.approx(r.peso)
    assert len(r.tramos) == len(pares)
    for tramo, (a, b) in zip(r.tramos, pares):
        assert (tramo.origen, tramo.destino) == (a, b)


# --------------------------------------------------------------------- bordes y errores
def test_origen_igual_a_destino(grafo):
    r = dijkstra(grafo, 2, 2, "dinero")
    assert r.camino == [2]
    assert r.valor == 0
    assert r.tramos == []
    assert r.ciudades_paso == []


def test_indices_fuera_de_rango(grafo):
    with pytest.raises(IndexError):
        dijkstra(grafo, -1, 2)
    with pytest.raises(IndexError):
        dijkstra(grafo, 0, 99)


def test_dijkstra_desde_alcanza_todos_los_nodos(grafo):
    dist, previo = dijkstra_desde(grafo, 0, "dinero")
    assert set(dist) == set(range(grafo.num_destinos))
    assert dist[0] == 0 and previo[0] is None
    for destino in range(1, grafo.num_destinos):
        camino = reconstruir_camino(previo, 0, destino)
        assert camino[0] == 0 and camino[-1] == destino
        assert dist[destino] == pytest.approx(dijkstra(grafo, 0, destino, "dinero").valor)


def test_reconstruir_camino_de_nodo_inalcanzable(grafo):
    _, previo = dijkstra_desde(grafo, 0, "dinero")
    with pytest.raises(CaminoNoEncontradoError):
        reconstruir_camino({0: None}, 0, 5)


def test_aristas_de_peso_cero_no_rompen_dijkstra():
    # Con la normalización, la arista más barata tiene peso 0; debe funcionar igual.
    g = crear_grafo(
        [[0, 1, 5], [1, 0, 1], [5, 1, 0]],
        [[0, 1, 5], [1, 0, 1], [5, 1, 0]],
    )
    assert g.peso(0, 1) == 0
    r = dijkstra(g, 0, 2, "peso")
    assert r.camino == [0, 1, 2]
    assert r.valor == pytest.approx(0)
