import pytest
from lib.structures.tabla_precedencias import TablaPrecedencias, CicloPrecedenciasError


def test_tabla_hash_almacenamiento_predecesores():
    """HU-3: Las restricciones se guardan en dict[int, set[int]] donde predecesores[B] = {A}."""
    tp = TablaPrecedencias()
    # A=0 (Bogotá) antes que B=1 (Medellín)
    tp.agregar_precedencia(antes=0, despues=1)
    
    assert 1 in tp.predecesores
    assert tp.predecesores[1] == {0}

    # Agregar otra restricción para B: C=2 (Cali) también antes que B=1 (Medellín)
    tp.agregar_precedencia(antes=2, despues=1)
    assert tp.predecesores[1] == {0, 2}

    # Obtener predecesores directos
    assert tp.obtener_predecesores(1) == {0, 2}
    assert tp.obtener_predecesores(0) == set()


def test_validacion_puede_visitar_en_o1():
    """HU-3: puedeVisitar(destino, visitados) devuelve true solo si todos sus predecesores están visitados."""
    tp = TablaPrecedencias()
    tp.agregar_precedencia(antes=0, despues=1)  # 0 antes que 1
    tp.agregar_precedencia(antes=2, despues=1)  # 2 antes que 1

    # Sin visitar ningún predecesor
    visitados = set()
    assert tp.puede_visitar(destino=1, visitados=visitados) is False
    assert tp.puedeVisitar(destino=1, visitados=visitados) is False  # soporte de alias camelCase

    # Un destino sin restricciones siempre se puede visitar
    assert tp.puede_visitar(destino=0, visitados=visitados) is True
    assert tp.puede_visitar(destino=2, visitados=visitados) is True

    # Visitando solo uno de los dos requeridos
    visitados.add(0)
    assert tp.puede_visitar(destino=1, visitados=visitados) is False

    # Visitando ambos requeridos
    visitados.add(2)
    assert tp.puede_visitar(destino=1, visitados=visitados) is True


def test_marcar_x_primero():
    """HU-3: «X primero» agrega X como predecesor de todos los demás destinos."""
    tp = TablaPrecedencias()
    todos = [0, 1, 2, 3, 4]
    x_primero = 2  # Cali primero

    tp.establecer_primero(primero=x_primero, todos_los_destinos=todos)

    # 2 no tiene predecesores
    assert tp.obtener_predecesores(2) == set()

    # Todos los demás tienen a 2 en sus predecesores
    for d in [0, 1, 3, 4]:
        assert 2 in tp.obtener_predecesores(d)

    # Solo se puede visitar 2 si visitados está vacío
    visitados = set()
    assert tp.puede_visitar(destino=2, visitados=visitados) is True
    assert tp.puede_visitar(destino=0, visitados=visitados) is False
    assert tp.puede_visitar(destino=1, visitados=visitados) is False


def test_deteccion_de_ciclos_directos_y_largos():
    """HU-3: Rechazo e información detallada de ciclos (A antes que B y B antes que A, o cadenas más largas)."""
    # Caso 1: Ciclo directo A <-> B (0 antes que 1 y 1 antes que 0)
    tp1 = TablaPrecedencias()
    tp1.agregar_precedencia(antes=0, despues=1)
    tp1.agregar_precedencia(antes=1, despues=0)

    ciclo1 = tp1.detectar_ciclo()
    assert ciclo1 is not None
    assert (ciclo1 == [0, 1, 0]) or (ciclo1 == [1, 0, 1])

    with pytest.raises(CicloPrecedenciasError) as exc_info:
        tp1.validar_sin_ciclos(nombres_map={0: "Bogotá", 1: "Medellín"})
    assert "Bogotá" in str(exc_info.value)
    assert "Medellín" in str(exc_info.value)

    # Caso 2: Ciclo triangular A -> B -> C -> A
    tp2 = TablaPrecedencias()
    tp2.agregar_precedencia(antes=0, despues=1)  # 0 -> 1
    tp2.agregar_precedencia(antes=1, despues=2)  # 1 -> 2
    tp2.agregar_precedencia(antes=2, despues=0)  # 2 -> 0

    ciclo2 = tp2.detectar_ciclo()
    assert ciclo2 is not None
    assert len(ciclo2) == 4  # e.g. [0, 1, 2, 0]
    assert ciclo2[0] == ciclo2[-1]

    # Caso 3: Sin ciclo (Grafo Acíclico Dirigido DAG)
    tp3 = TablaPrecedencias()
    tp3.agregar_precedencia(antes=0, despues=1)
    tp3.agregar_precedencia(antes=1, despues=2)
    tp3.agregar_precedencia(antes=0, despues=2)  # Transitividad legítima
    assert tp3.detectar_ciclo() is None
    tp3.validar_sin_ciclos()  # No debe lanzar excepción


def test_validar_secuencia_completa():
    """HU-3: Verifica que una secuencia dada cumpla o avise si viola alguna precedencia."""
    tp = TablaPrecedencias()
    tp.agregar_precedencia(antes=0, despues=1)  # Bogotá antes que Medellín

    nombres = {0: "Bogotá", 1: "Medellín", 2: "Cali"}

    # Secuencia válida: [Bogotá, Cali, Medellín]
    valida, err = tp.validar_secuencia([0, 2, 1], nombres_map=nombres)
    assert valida is True
    assert err is None

    # Secuencia inválida: [Medellín, Bogotá, Cali] (Medellín antes que Bogotá)
    invalida, err_msg = tp.validar_secuencia([1, 0, 2], nombres_map=nombres)
    assert invalida is False
    assert "Bogotá debe visitarse antes que Medellín" in err_msg
