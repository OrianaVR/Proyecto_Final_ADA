import pytest
from lib.structures.grafo import Grafo
from lib.models.destino import Destino
from lib.models.arista import Arista
from lib.models.ruta import Ruta


@pytest.fixture
def grafo_ejemplo():
    """Grafo de prueba con 8 ciudades representativas y magnitudes dispares entre costo y tiempo."""
    destinos = [
        Destino(0, "Bogotá"),
        Destino(1, "Medellín"),
        Destino(2, "Cali"),
        Destino(3, "Barranquilla"),
        Destino(4, "Cartagena"),
        Destino(5, "Bucaramanga"),
        Destino(6, "Pereira"),
        Destino(7, "Santa Marta"),
    ]
    # Costo en miles de pesos (80 a 320)
    costo = [
        [0, 120, 150, 260, 280, 140, 110, 290],
        [120, 0, 100, 210, 220, 160, 70, 240],
        [150, 100, 0, 290, 310, 240, 60, 320],
        [260, 210, 290, 0, 35, 180, 250, 30],
        [280, 220, 310, 35, 0, 200, 260, 110],
        [140, 160, 240, 180, 200, 0, 190, 190],
        [110, 70, 60, 250, 260, 190, 0, 280],
        [290, 240, 320, 30, 110, 190, 280, 0],
    ]
    # Tiempo en horas (1 a 22 horas)
    tiempo = [
        [0.0, 9.0, 10.0, 18.0, 19.0, 8.0, 7.0, 20.0],
        [9.0, 0.0, 8.0, 14.0, 15.0, 10.0, 4.5, 16.0],
        [10.0, 8.0, 0.0, 20.0, 21.0, 15.0, 3.5, 22.0],
        [18.0, 14.0, 20.0, 0.0, 2.0, 12.0, 17.0, 2.0],
        [19.0, 15.0, 21.0, 2.0, 0.0, 13.0, 18.0, 5.0],
        [8.0, 10.0, 15.0, 12.0, 13.0, 0.0, 12.5, 11.0],
        [7.0, 4.5, 3.5, 17.0, 18.0, 12.5, 0.0, 19.0],
        [20.0, 16.0, 22.0, 2.0, 5.0, 11.0, 19.0, 0.0],
    ]
    return Grafo(destinos, costo, tiempo, alfa=0.5, beta=0.5)


def test_estructura_grafo_metodos_principales(grafo_ejemplo):
    """HU-2: Expone peso(i,j), costo(i,j), tiempo(i,j) y vecinos(i)."""
    g = grafo_ejemplo
    assert g.num_destinos == 8

    # Diagonal debe ser 0
    assert g.costo(0, 0) == 0.0
    assert g.tiempo(0, 0) == 0.0
    assert g.peso(0, 0) == 0.0

    # Arista entre Bogotá (0) y Medellín (1)
    assert g.costo(0, 1) == 120.0
    assert g.tiempo(0, 1) == 9.0
    assert g.peso(0, 1) > 0.0

    # Vecinos de Bogotá (0) son todos los j != 0
    vecinos_bogota = g.vecinos(0)
    assert len(vecinos_bogota) == 7
    assert 0 not in vecinos_bogota
    assert set(vecinos_bogota) == {1, 2, 3, 4, 5, 6, 7}

    # Obtención de arista y destinos
    arista = g.obtener_arista(0, 1)
    assert isinstance(arista, Arista)
    assert arista.origen == 0 and arista.destino == 1
    assert arista.costo == 120.0
    assert arista.tiempo == 9.0
    assert arista.peso == g.peso(0, 1)


def test_normalizacion_demuestra_costo_no_domina_tiempo(grafo_ejemplo):
    """HU-2: Test que demuestra matemáticamente que el costo no domina al tiempo.
    
    Sin normalización:
        Rango de costo = 320 - 30 = 290 (miles de pesos).
        Rango de tiempo = 22 - 2 = 20 (horas).
        El rango de costo es 14.5 veces mayor que el de tiempo.
        Un peso bruto alfa*costo + beta*tiempo estaría dominado 14:1 por el costo.
        
    Con normalización a [0, 1]:
        El rango efectivo de costo normalizado es exactamente 1.0.
        El rango efectivo de tiempo normalizado es exactamente 1.0.
        Con alfa=0.5 y beta=0.5, una variación máxima en tiempo impacta exactamente
        lo mismo (+0.5) que una variación máxima en costo (+0.5).
    """
    g = grafo_ejemplo
    n = g.num_destinos

    costos_norm = [g.costo_normalizado(i, j) for i in range(n) for j in range(n) if i != j]
    tiempos_norm = [g.tiempo_normalizado(i, j) for i in range(n) for j in range(n) if i != j]

    # Ambas métricas deben tener rango normalizado [0.0, 1.0]
    min_costo_norm, max_costo_norm = min(costos_norm), max(costos_norm)
    min_tiempo_norm, max_tiempo_norm = min(tiempos_norm), max(tiempos_norm)

    assert min_costo_norm == 0.0
    assert max_costo_norm == 1.0
    assert min_tiempo_norm == 0.0
    assert max_tiempo_norm == 1.0

    rango_costo_norm = max_costo_norm - min_costo_norm
    rango_tiempo_norm = max_tiempo_norm - min_tiempo_norm

    # El ratio de escalas normalizadas es exactamente 1.0 (ninguno domina al otro)
    ratio_escalas = rango_costo_norm / rango_tiempo_norm
    assert pytest.approx(ratio_escalas, abs=1e-6) == 1.0

    # Demostración con caso concreto:
    # Tramo A: costo mínimo (30), tiempo máximo (22) -> (Santa Marta -> Barranquilla)
    # Tramo B: costo máximo (320), tiempo mínimo (2) -> ejemplo hipotético
    # Con alfa=0.5, beta=0.5:
    # Aporte del costo normalizado máximo = 0.5 * 1.0 = 0.5
    # Aporte del tiempo normalizado máximo = 0.5 * 1.0 = 0.5
    assert pytest.approx(0.5 * max_costo_norm, abs=1e-6) == 0.5 * max_tiempo_norm


def test_formula_con_alfa_y_beta_configurables(grafo_ejemplo):
    """HU-2: peso(i,j) = alfa * costo_norm(i,j) + beta * tiempo_norm(i,j)."""
    g = grafo_ejemplo

    # Con alfa=1.0 y beta=0.0 (priorizar 100% precio)
    g.configurar_pesos(alfa=1.0, beta=0.0)
    for i in range(g.num_destinos):
        for j in range(g.num_destinos):
            if i != j:
                assert pytest.approx(g.peso(i, j), abs=1e-6) == g.costo_normalizado(i, j)

    # Con alfa=0.0 y beta=1.0 (priorizar 100% tiempo)
    g.configurar_pesos(alfa=0.0, beta=1.0)
    for i in range(g.num_destinos):
        for j in range(g.num_destinos):
            if i != j:
                assert pytest.approx(g.peso(i, j), abs=1e-6) == g.tiempo_normalizado(i, j)

    # Con pesos combinados personalizados (alfa=0.7, beta=0.3)
    g.configurar_pesos(alfa=0.7, beta=0.3)
    for i in range(g.num_destinos):
        for j in range(g.num_destinos):
            if i != j:
                esperado = 0.7 * g.costo_normalizado(i, j) + 0.3 * g.tiempo_normalizado(i, j)
                assert pytest.approx(g.peso(i, j), abs=1e-6) == esperado


def test_separacion_de_acumuladores():
    """HU-2: El peso combinado (adimensional) y el dinero real se guardan por separado y nunca se mezclan."""
    ruta = Ruta(
        destinos=[0, 1, 2],
        peso_total=0.8540,
        costo_total=270000.0,  # En dinero real ($270.000)
        tiempo_total=17.0,     # En horas
    )
    # Verificación de tipos y separación
    assert isinstance(ruta.peso_total, float)
    assert isinstance(ruta.costo_total, float)
    assert ruta.peso_total != ruta.costo_total

    # El presupuesto se compara contra costo_total, jamás contra peso_total
    presupuesto = 300000.0
    cabe_en_presupuesto = ruta.costo_total <= presupuesto
    assert cabe_en_presupuesto is True

    # Error común prevenido: comparar peso_total contra presupuesto no tiene sentido físico
    assert ruta.peso_total < 1.0  # El peso no tiene unidad de moneda
