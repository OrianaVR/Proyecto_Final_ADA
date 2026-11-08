import random
import time
import pytest

from lib.algorithms.branch_and_bound import BranchAndBound, ResultadoBB
from lib.algorithms.fuerza_bruta import fuerza_bruta_rutas
from lib.algorithms.matriz_caminos import MatrizCaminos
from lib.structures.grafo import Grafo
from lib.structures.tabla_precedencias import TablaPrecedencias
from utils_grafos import crear_grafo


@pytest.fixture(scope="module")
def grafo():
    return Grafo.desde_json()


# ==============================================================================
# Prueba 1: 100 casos aleatorios de 5 a 7 destinos (semilla fija)
# ==============================================================================
def test_100_casos_aleatorios_coinciden_con_fuerza_bruta(grafo):
    """Verifica que Branch and Bound coincide exactamente con fuerza bruta en 100 casos."""
    rng = random.Random(42)
    k = 5

    for caso in range(100):
        num_destinos = rng.randint(5, 7)
        seleccion = rng.sample(range(grafo.num_destinos), num_destinos + 1)
        origen, destinos = seleccion[0], seleccion[1:]

        matriz = MatrizCaminos.construir(grafo, origen, destinos)
        presupuesto = rng.choice([700.0, 1200.0, 2000.0, float("inf")])
        ida_vuelta = rng.choice([True, False])

        # Opcionalmente agregar precedencias aleatorias válidas
        tabla = None
        if rng.random() < 0.3 and len(destinos) >= 2:
            tabla = TablaPrecedencias()
            a, b = rng.sample(destinos, 2)
            tabla.agregar_precedencia(a, b)

        bb = BranchAndBound(
            matriz,
            presupuesto=presupuesto,
            precedencias=tabla,
            k=k,
            ida_y_vuelta=ida_vuelta,
        ).mejores_rutas()

        fb = fuerza_bruta_rutas(
            matriz,
            presupuesto=presupuesto,
            precedencias=tabla,
            k=k,
            ida_y_vuelta=ida_vuelta,
        )

        assert len(bb.rutas) == len(fb), (
            f"Fallo en caso {caso}: BB devolvió {len(bb.rutas)} rutas y FB devolvió {len(fb)}."
        )

        for idx, (r_bb, r_fb) in enumerate(zip(bb.rutas, fb)):
            assert r_bb.peso_total == pytest.approx(r_fb.peso_total, rel=1e-5), (
                f"Fallo en caso {caso}, ruta {idx}: peso BB {r_bb.peso_total} != peso FB {r_fb.peso_total}."
            )
            # En la mejor ruta absoluta (costo mínimo global)
            if idx == 0:
                assert r_bb.peso_total == pytest.approx(fb[0].peso_total, rel=1e-5)


# ==============================================================================
# Prueba 2: Todas las rutas devueltas respetan precedencias y presupuesto
# ==============================================================================
def test_rutas_respetan_precedencias_y_presupuesto(grafo):
    matriz = MatrizCaminos.construir(grafo, 0, [1, 2, 3, 4, 5])
    tabla = TablaPrecedencias()
    tabla.agregar_precedencia(3, 1)  # 3 antes de 1
    tabla.agregar_precedencia(5, 2)  # 5 antes de 2

    presupuesto = 1200.0
    bb = BranchAndBound(
        matriz,
        presupuesto=presupuesto,
        precedencias=tabla,
        k=10,
    ).mejores_rutas()

    assert len(bb.rutas) > 0
    for ruta in bb.rutas:
        # 1. Respetar presupuesto (dinero real, no peso)
        assert ruta.costo_total <= presupuesto + 1e-9

        # 2. Respetar precedencias
        pos = {ciudad: i for i, ciudad in enumerate(ruta.destinos)}
        assert pos[3] < pos[1]
        assert pos[5] < pos[2]


# ==============================================================================
# Prueba 3: Un solo destino y ningún destino
# ==============================================================================
def test_un_solo_destino_y_ninguno(grafo):
    # Caso 0 destinos: solo origen
    m0 = MatrizCaminos.construir(grafo, 0, [])
    res0 = BranchAndBound(m0, presupuesto=500.0).mejores_rutas()
    assert len(res0.rutas) == 1
    assert res0.rutas[0].destinos == [0]
    assert res0.rutas[0].peso_total == 0.0
    assert res0.rutas[0].costo_total == 0.0

    # Caso 1 destino sin ida y vuelta
    m1 = MatrizCaminos.construir(grafo, 0, [4])
    res1 = BranchAndBound(m1, presupuesto=1000.0, ida_y_vuelta=False).mejores_rutas()
    assert len(res1.rutas) == 1
    assert res1.rutas[0].destinos == [0, 4]
    assert res1.rutas[0].peso_total == pytest.approx(m1.peso(0, 4))
    assert res1.rutas[0].costo_total == pytest.approx(m1.dinero(0, 4))

    # Caso 1 destino con ida y vuelta
    res1_iv = BranchAndBound(m1, presupuesto=1000.0, ida_y_vuelta=True).mejores_rutas()
    assert len(res1_iv.rutas) == 1
    assert res1_iv.rutas[0].destinos == [0, 4, 0]
    assert res1_iv.rutas[0].peso_total == pytest.approx(m1.peso(0, 4) + m1.peso(4, 0))
    assert res1_iv.rutas[0].costo_total == pytest.approx(m1.dinero(0, 4) + m1.dinero(4, 0))


# ==============================================================================
# Prueba 4: Presupuesto insuficiente retorna resultado vacío
# ==============================================================================
def test_presupuesto_insuficiente_retorna_vacio(grafo):
    matriz = MatrizCaminos.construir(grafo, 0, [1, 2, 4])
    # Presupuesto ínfimo (imposible de cubrir)
    res = BranchAndBound(matriz, presupuesto=5.0).mejores_rutas()
    assert res.rutas == []
    assert res.mejor_ruta is None
    assert res.garantizado_optimo is True
    assert res.estadisticas.podas_presupuesto > 0


# ==============================================================================
# Prueba 5: Presupuesto justo: ruta con dinero exactamente igual se acepta
# ==============================================================================
def test_presupuesto_justo_se_acepta(grafo):
    matriz = MatrizCaminos.construir(grafo, 0, [1, 4])
    # Hallar costo de la ruta óptima
    res_base = BranchAndBound(matriz, presupuesto=10000.0, k=1).mejores_rutas()
    assert len(res_base.rutas) == 1
    costo_exacto = res_base.rutas[0].costo_total

    # Probar con presupuesto exactamente igual al costo de la ruta
    res_justo = BranchAndBound(matriz, presupuesto=costo_exacto, k=1).mejores_rutas()
    assert len(res_justo.rutas) == 1
    assert res_justo.rutas[0].costo_total == pytest.approx(costo_exacto)


# ==============================================================================
# Prueba 6: Precedencias que restringen fuertemente el orden
# ==============================================================================
def test_precedencias_restringen_fuertemente_el_orden(grafo):
    destinos = [1, 2, 3, 4]
    matriz = MatrizCaminos.construir(grafo, 0, destinos)

    # Fijar cadena total: 4 -> 3 -> 2 -> 1
    tabla = TablaPrecedencias()
    tabla.agregar_precedencia(4, 3)
    tabla.agregar_precedencia(3, 2)
    tabla.agregar_precedencia(2, 1)

    res = BranchAndBound(matriz, presupuesto=10000.0, precedencias=tabla).mejores_rutas()
    assert len(res.rutas) == 1
    assert res.rutas[0].destinos == [0, 4, 3, 2, 1]


# ==============================================================================
# Prueba 7: Matriz donde pasar por ciudad intermedia es más barato (usa D, no aristas)
# ==============================================================================
def test_camino_indirecto_mas_barato_que_tramo_directo():
    # Grafo con 3 ciudades: 0 -> 2 directo cuesta 100, pero 0 -> 1 -> 2 cuesta 10 + 10 = 20
    costo = [
        [0.0, 10.0, 100.0],
        [10.0, 0.0, 10.0],
        [100.0, 10.0, 0.0],
    ]
    tiempo = [
        [0.0, 1.0, 10.0],
        [1.0, 0.0, 1.0],
        [10.0, 1.0, 0.0],
    ]
    g = crear_grafo(costo, tiempo, alfa=0.5, beta=0.5)
    matriz = MatrizCaminos.construir(g, origen=0, destinos=[2])

    res = BranchAndBound(matriz, presupuesto=500.0).mejores_rutas()
    assert len(res.rutas) == 1
    ruta = res.rutas[0]
    # La ruta usa la matriz D, por lo que incluye la ciudad de paso 1
    assert ruta.destinos == [0, 2]
    assert ruta.ciudades_paso == [1]
    assert ruta.costo_total == pytest.approx(20.0)


# ==============================================================================
# Prueba 8: Con ida y vuelta activado, el regreso suma a peso y dinero
# ==============================================================================
def test_ida_y_vuelta_suma_peso_y_dinero(grafo):
    matriz = MatrizCaminos.construir(grafo, 0, [1, 4])
    res_ida = BranchAndBound(matriz, presupuesto=10000.0, ida_y_vuelta=False, k=1).mejores_rutas()
    res_iv = BranchAndBound(matriz, presupuesto=10000.0, ida_y_vuelta=True, k=1).mejores_rutas()

    r_ida = res_ida.rutas[0]
    r_iv = res_iv.rutas[0]

    assert r_iv.destinos[0] == 0
    assert r_iv.destinos[-1] == 0
    ultimo_destino = r_iv.destinos[-2]

    regreso_peso = matriz.peso(ultimo_destino, 0)
    regreso_dinero = matriz.dinero(ultimo_destino, 0)

    assert r_iv.peso_total >= r_ida.peso_total
    assert r_iv.costo_total >= r_ida.costo_total


# ==============================================================================
# Prueba 9: El orden de salida es ascendente y respeta K
# ==============================================================================
def test_orden_ascendente_y_respeta_k(grafo):
    matriz = MatrizCaminos.construir(grafo, 0, [1, 2, 3, 4, 5])
    k_pedido = 6
    res = BranchAndBound(matriz, presupuesto=10000.0, k=k_pedido).mejores_rutas()

    assert len(res.rutas) == k_pedido
    for i in range(len(res.rutas) - 1):
        assert res.rutas[i].peso_total <= res.rutas[i + 1].peso_total + 1e-9


# ==============================================================================
# Prueba 10: Límite de nodos/tiempo agotado marca garantizado_optimo = False
# ==============================================================================
def test_limite_agotado_marca_no_optimo(grafo):
    matriz = MatrizCaminos.construir(grafo, 0, [1, 2, 3, 4, 5, 6, 7])

    # Límite muy estricto de nodos expandidos
    res_nodos = BranchAndBound(
        matriz, presupuesto=10000.0, k=10, limite_nodos=2
    ).mejores_rutas()
    assert res_nodos.garantizado_optimo is False

    # Límite muy estricto de tiempo (1 microsegundo)
    res_tiempo = BranchAndBound(
        matriz, presupuesto=10000.0, k=10, limite_segundos=1e-6
    ).mejores_rutas()
    assert res_tiempo.garantizado_optimo is False


# ==============================================================================
# Prueba 11: Verificar que la cota h nunca sobreestima (admisibilidad estricta)
# ==============================================================================
def test_cota_h_nunca_sobreestima_admisibilidad(grafo):
    """Compara h(e) contra el peso real restante mínimo en subproblemas pequeños."""
    import itertools

    rng = random.Random(123)
    for _ in range(15):
        destinos = rng.sample(range(grafo.num_destinos), 5)
        origen, d_sub = destinos[0], destinos[1:]
        matriz = MatrizCaminos.construir(grafo, origen, d_sub)

        for ida in (False, True):
            bb = BranchAndBound(matriz, presupuesto=10000.0, ida_y_vuelta=ida)

            # Evaluar distintos subconjuntos de destinos restantes R desde varios u
            for r_len in range(1, len(d_sub) + 1):
                r_subset = set(d_sub[:r_len])
                u = origen

                cota = bb.cota_peso(u, r_subset)

                # Calcular el peso real mínimo para visitar r_subset desde u
                peso_real_min = float("inf")
                for perm in itertools.permutations(r_subset):
                    seq = [u] + list(perm)
                    if ida:
                        seq.append(origen)
                    peso = sum(matriz.peso(a, b) for a, b in zip(seq, seq[1:]))
                    if peso < peso_real_min:
                        peso_real_min = peso

                # La cota h NUNCA debe sobreestimar el peso real
                assert cota <= peso_real_min + 1e-9, (
                    f"Cota inadmisible: cota={cota} > peso_real_min={peso_real_min}"
                )


# ==============================================================================
# Pruebas adicionales: Validaciones de límites y errores
# ==============================================================================
def test_mas_de_12_destinos_lanza_error(grafo):
    # Crear grafo sintético con 15 destinos
    n = 15
    costo = [[10.0 if i != j else 0.0 for j in range(n)] for i in range(n)]
    tiempo = [[1.0 if i != j else 0.0 for j in range(n)] for i in range(n)]
    g15 = crear_grafo(costo, tiempo)
    m = MatrizCaminos.construir(g15, origen=0, destinos=list(range(1, 14)))

    with pytest.raises(ValueError, match="Demasiados destinos"):
        BranchAndBound(m, presupuesto=1000.0)


def test_k_invalido_lanza_error(grafo):
    matriz = MatrizCaminos.construir(grafo, 0, [1, 2])
    with pytest.raises(ValueError, match="mayor que 0"):
        BranchAndBound(matriz, presupuesto=1000.0, k=0)
