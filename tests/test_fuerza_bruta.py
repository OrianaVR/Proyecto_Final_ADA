import pytest

from lib.algorithms.fuerza_bruta import fuerza_bruta_rutas
from lib.algorithms.matriz_caminos import MatrizCaminos
from lib.structures.grafo import Grafo
from lib.structures.tabla_precedencias import TablaPrecedencias
from utils_grafos import crear_grafo


@pytest.fixture(scope="module")
def grafo():
    return Grafo.desde_json()


def test_fuerza_bruta_orden_y_top_k(grafo):
    matriz = MatrizCaminos.construir(grafo, 0, [1, 2, 3])
    rutas = fuerza_bruta_rutas(matriz, presupuesto=10000, k=2)
    assert len(rutas) == 2
    # Deben estar ordenadas por peso ascendente
    assert rutas[0].peso_total <= rutas[1].peso_total
    # Todas parten del origen
    assert rutas[0].destinos[0] == 0


def test_fuerza_bruta_respeta_precedencias(grafo):
    matriz = MatrizCaminos.construir(grafo, 0, [1, 4])
    tabla = TablaPrecedencias()
    tabla.agregar_precedencia(4, 1)  # 4 debe ir antes que 1
    rutas = fuerza_bruta_rutas(matriz, presupuesto=10000, precedencias=tabla)
    assert len(rutas) == 1
    assert rutas[0].destinos == [0, 4, 1]


def test_fuerza_bruta_filtra_por_presupuesto(grafo):
    matriz = MatrizCaminos.construir(grafo, 0, [1, 4])
    # Sin dinero suficiente
    rutas = fuerza_bruta_rutas(matriz, presupuesto=10)
    assert rutas == []


def test_fuerza_bruta_ida_y_vuelta(grafo):
    matriz = MatrizCaminos.construir(grafo, 0, [1, 2])
    rutas = fuerza_bruta_rutas(matriz, presupuesto=10000, ida_y_vuelta=True)
    assert len(rutas) > 0
    assert rutas[0].destinos[0] == 0
    assert rutas[0].destinos[-1] == 0


def test_fuerza_bruta_sin_destinos(grafo):
    matriz = MatrizCaminos.construir(grafo, 0, [])
    rutas = fuerza_bruta_rutas(matriz, presupuesto=100)
    assert len(rutas) == 1
    assert rutas[0].destinos == [0]
