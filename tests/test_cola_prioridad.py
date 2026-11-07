import heapq
import random

import pytest

from lib.structures.cola_prioridad import ColaPrioridad, ColaVaciaError


def test_cola_nueva_esta_vacia():
    cola = ColaPrioridad()
    assert cola.esta_vacia()
    assert len(cola) == 0
    assert not cola


def test_extrae_en_orden_ascendente_1000_valores_aleatorios():
    rng = random.Random(7)
    valores = [rng.uniform(-500, 500) for _ in range(1000)]
    cola = ColaPrioridad()
    for i, v in enumerate(valores):
        cola.insertar(i, v)
    assert len(cola) == 1000

    salida = []
    while cola:
        _, prioridad = cola.extraer_menor()
        salida.append(prioridad)

    assert salida == sorted(valores)
    assert cola.esta_vacia()


def test_devuelve_elemento_y_prioridad():
    cola = ColaPrioridad()
    cola.insertar("Cali", 120.0)
    cola.insertar("Pereira", 60.0)
    cola.insertar("Bogotá", 90.0)
    assert cola.extraer_menor() == ("Pereira", 60.0)
    assert cola.extraer_menor() == ("Bogotá", 90.0)
    assert cola.extraer_menor() == ("Cali", 120.0)


def test_desempate_fifo_con_prioridades_iguales():
    cola = ColaPrioridad()
    for nombre in ["a", "b", "c", "d", "e"]:
        cola.insertar(nombre, 1.0)
    assert [cola.extraer_menor()[0] for _ in range(5)] == ["a", "b", "c", "d", "e"]


def test_elementos_no_comparables_no_rompen_el_desempate():
    # Los diccionarios no se pueden comparar con <; la cola no debe intentarlo.
    cola = ColaPrioridad()
    cola.insertar({"ruta": [0, 1]}, 5)
    cola.insertar({"ruta": [0, 2]}, 5)
    cola.insertar({"ruta": [0, 3]}, 5)
    assert cola.extraer_menor()[0] == {"ruta": [0, 1]}
    assert cola.extraer_menor()[0] == {"ruta": [0, 2]}


def test_acepta_tuplas_como_prioridad():
    cola = ColaPrioridad()
    cola.insertar("x", (2.0, 10))
    cola.insertar("y", (1.0, 99))
    cola.insertar("z", (1.0, 5))
    assert [cola.extraer_menor()[0] for _ in range(3)] == ["z", "y", "x"]


def test_ver_menor_no_extrae():
    cola = ColaPrioridad()
    cola.insertar("a", 3)
    cola.insertar("b", 1)
    assert cola.ver_menor() == ("b", 1)
    assert len(cola) == 2
    assert cola.extraer_menor() == ("b", 1)


def test_extraer_o_ver_en_cola_vacia_lanza_error():
    cola = ColaPrioridad()
    with pytest.raises(ColaVaciaError):
        cola.extraer_menor()
    with pytest.raises(ColaVaciaError):
        cola.ver_menor()
    assert issubclass(ColaVaciaError, IndexError)


def test_rechaza_nan():
    cola = ColaPrioridad()
    with pytest.raises(ValueError):
        cola.insertar("x", float("nan"))
    assert len(cola) == 0


def test_vaciar():
    cola = ColaPrioridad()
    for i in range(10):
        cola.insertar(i, i)
    cola.vaciar()
    assert cola.esta_vacia()
    cola.insertar("nuevo", 1)
    assert cola.extraer_menor() == ("nuevo", 1)


def test_mezcla_de_inserciones_y_extracciones_coincide_con_heapq():
    # Oráculo: heapq con (prioridad, contador). Mismas operaciones, mismo resultado.
    rng = random.Random(2024)
    cola = ColaPrioridad()
    oraculo = []
    contador = 0
    for _ in range(3000):
        if oraculo and rng.random() < 0.4:
            prioridad, orden = heapq.heappop(oraculo)
            assert cola.extraer_menor() == (orden, prioridad)
        else:
            prioridad = rng.randint(0, 50)  # muchos empates a propósito
            heapq.heappush(oraculo, (prioridad, contador))
            cola.insertar(contador, prioridad)
            contador += 1
        assert len(cola) == len(oraculo)
