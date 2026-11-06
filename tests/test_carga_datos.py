import pytest
from pathlib import Path
from lib.data.destinos_repository import DestinosRepository, ErrorCargaDatos
from lib.models.destino import Destino
from lib.models.arista import Arista
from lib.models.ruta import Ruta
from lib.models.entrada import Entrada
from lib.models.restricciones import Restricciones


def test_carga_archivo_destinos_json():
    """HU-1: Archivo de datos existe, contiene entre 8 y 10 ciudades, matrices cuadradas y diagonal 0."""
    ruta_json = Path(__file__).resolve().parent.parent / "assets" / "destinos.json"
    assert ruta_json.exists(), f"El archivo {ruta_json} debe existir."

    destinos, costo, tiempo = DestinosRepository.cargar(ruta_json)

    # Validar cantidad de destinos entre 8 y 10
    n = len(destinos)
    assert 8 <= n <= 10, f"Debe contener entre 8 y 10 destinos, se obtuvieron {n}."

    # Validar nombres de destinos
    nombres = [d.nombre for d in destinos]
    assert len(set(nombres)) == n, "Los nombres de los destinos deben ser únicos."
    assert all(isinstance(nom, str) and len(nom.strip()) > 0 for nom in nombres)

    # Validar dimensiones cuadradas
    assert len(costo) == n, f"La matriz costo debe tener {n} filas."
    assert all(len(fila) == n for fila in costo), f"Cada fila de costo debe tener {n} columnas."

    assert len(tiempo) == n, f"La matriz tiempo debe tener {n} filas."
    assert all(len(fila) == n for fila in tiempo), f"Cada fila de tiempo debe tener {n} columnas."

    # Validar diagonal en 0
    for i in range(n):
        assert costo[i][i] == 0, f"La diagonal costo[{i}][{i}] debe ser 0."
        assert tiempo[i][i] == 0, f"La diagonal tiempo[{i}][{i}] debe ser 0."

    # Validar valores fuera de la diagonal positivos
    for i in range(n):
        for j in range(n):
            if i != j:
                assert costo[i][j] > 0, f"costo[{i}][{j}] debe ser mayor a 0."
                assert tiempo[i][j] > 0, f"tiempo[{i}][{j}] debe ser mayor a 0."


def test_modelos_de_dominio():
    """HU-1: Existen las clases Destino, Arista, Ruta, Entrada y Restricciones con serialización."""
    # Destino
    dest = Destino(id=0, nombre="Bogotá", alias="BOG")
    assert dest.id == 0
    assert dest.nombre == "Bogotá"
    assert Destino.from_dict(dest.to_dict()) == dest

    # Arista
    arista = Arista(origen=0, destino=1, costo=120.0, tiempo=9.0, peso=0.45)
    assert arista.origen == 0
    assert arista.destino == 1
    assert arista.costo == 120.0
    assert arista.tiempo == 9.0
    assert arista.peso == 0.45
    assert Arista.from_dict(arista.to_dict()) == arista

    # Ruta
    ruta = Ruta(
        destinos=[0, 1, 2],
        peso_total=1.25,
        costo_total=220.0,
        tiempo_total=17.0,
        tramos=[arista],
        ciudades_paso=[3],
    )
    assert ruta.destinos == [0, 1, 2]
    assert ruta.peso_total == 1.25
    assert ruta.costo_total == 220.0
    assert ruta.tiempo_total == 17.0
    assert len(ruta.tramos) == 1
    assert ruta.ciudades_paso == [3]
    ruta_dict = ruta.to_dict()
    ruta_rec = Ruta.from_dict(ruta_dict)
    assert ruta_rec.destinos == ruta.destinos
    assert ruta_rec.peso_total == ruta.peso_total
    assert ruta_rec.costo_total == ruta.costo_total

    # Entrada
    entrada = Entrada(
        origen=0,
        destinos=[1, 2, 4],
        presupuesto=300.0,
        k=5,
        ida_y_vuelta=True,
        alfa=0.7,
        beta=0.3,
        precedencias={2: {1}},
        secuencia_orden=[0, 1, 2, 4, 0],
    )
    assert entrada.origen == 0
    assert entrada.presupuesto == 300.0
    assert entrada.k == 5
    assert entrada.ida_y_vuelta is True
    assert entrada.precedencias == {2: {1}}
    entrada_dict = entrada.to_dict()
    entrada_rec = Entrada.from_dict(entrada_dict)
    assert entrada_rec.destinos == entrada.destinos
    assert entrada_rec.precedencias == {2: {1}}

    # Restricciones
    rest = Restricciones(precedencias={4: {2}}, presupuesto=400.0, max_destinos=12)
    assert rest.presupuesto == 400.0
    assert rest.max_destinos == 12
    assert Restricciones.from_dict(rest.to_dict()).max_destinos == 12


def test_validaciones_robustas_carga():
    """HU-1: Valida rechazo ante datos corruptos o no conformes."""
    # Diagonal distinta de 0
    datos_diag_mala = {
        "destinos": ["A", "B", "C", "D", "E", "F", "G", "H"],
        "costo": [[5 if i == j else 10 for j in range(8)] for i in range(8)],
        "tiempo": [[0 if i == j else 2 for j in range(8)] for i in range(8)],
    }
    with pytest.raises(ErrorCargaDatos, match="diagonal"):
        DestinosRepository.validar_y_procesar(datos_diag_mala)

    # Matriz no cuadrada
    datos_no_cuadrada = {
        "destinos": ["A", "B", "C", "D", "E", "F", "G", "H"],
        "costo": [[10] * 8 for _ in range(7)],
        "tiempo": [[2] * 8 for _ in range(8)],
    }
    with pytest.raises(ErrorCargaDatos, match="filas"):
        DestinosRepository.validar_y_procesar(datos_no_cuadrada)

    # Menos de 8 destinos
    datos_pocos_destinos = {
        "destinos": ["A", "B", "C"],
        "costo": [[0] * 3 for _ in range(3)],
        "tiempo": [[0] * 3 for _ in range(3)],
    }
    with pytest.raises(ErrorCargaDatos, match="ciudades"):
        DestinosRepository.validar_y_procesar(datos_pocos_destinos)

    # Destinos duplicados
    datos_duplicados = {
        "destinos": ["A", "B", "C", "D", "E", "F", "G", "A"],
        "costo": [[0] * 8 for _ in range(8)],
        "tiempo": [[0] * 8 for _ in range(8)],
    }
    with pytest.raises(ErrorCargaDatos, match="duplicado"):
        DestinosRepository.validar_y_procesar(datos_duplicados)
