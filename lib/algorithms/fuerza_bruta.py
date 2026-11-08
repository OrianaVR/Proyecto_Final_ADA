from __future__ import annotations

import itertools
from typing import List, Optional

from lib.algorithms.matriz_caminos import MatrizCaminos
from lib.models.arista import Arista
from lib.models.ruta import Ruta
from lib.structures.tabla_precedencias import TablaPrecedencias

# Tolerancia para comparaciones monetarias en punto flotante
_EPS = 1e-9


def _armar_ruta_desde_secuencia(secuencia: List[int], matriz: MatrizCaminos) -> Ruta:
    """Construye una instancia de Ruta a partir de una secuencia ordenada de ciudades."""
    if len(secuencia) <= 1:
        return Ruta(
            destinos=list(secuencia),
            peso_total=0.0,
            costo_total=0.0,
            tiempo_total=0.0,
            tramos=[],
            ciudades_paso=[],
        )

    tramos: List[Arista] = []
    ciudades_paso: List[int] = []
    peso_total = 0.0
    costo_total = 0.0
    tiempo_total = 0.0

    for a, b in zip(secuencia, secuencia[1:]):
        camino = matriz.camino_peso(a, b)
        tramos.extend(camino.tramos)
        ciudades_paso.extend(camino.ciudades_paso)
        peso_total += camino.peso
        costo_total += camino.dinero
        tiempo_total += camino.tiempo

    return Ruta(
        destinos=list(secuencia),
        peso_total=peso_total,
        costo_total=costo_total,
        tiempo_total=tiempo_total,
        tramos=tramos,
        ciudades_paso=ciudades_paso,
    )


def fuerza_bruta_rutas(
    matriz: MatrizCaminos,
    presupuesto: float,
    precedencias: Optional[TablaPrecedencias] = None,
    k: int = 10,
    ida_y_vuelta: bool = False,
) -> List[Ruta]:
    """Genera todas las permutaciones posibles de destinos y devuelve las top-K mejores.
    
    Este método actúa como oráculo exacto e independiente para verificar
    la corrección de Branch and Bound en las pruebas unitarias.
    
    Args:
        matriz: MatrizCaminos con distancias precalculadas D_peso, D_dinero y D_min.
        presupuesto: Dinero máximo disponible en pesos colombianos ($).
        precedencias: TablaPrecedencias opcional con restricciones de orden parcial.
        k: Cantidad máxima de rutas a retornar (por defecto 10).
        ida_y_vuelta: Si True, el recorrido debe finalizar regresando al origen.
        
    Returns:
        Lista de hasta K rutas válidas ordenadas ascendentemente por peso total.
    """
    origen = matriz.nodos[0]
    destinos = matriz.nodos[1:]

    # Caso base sin destinos: solo se visita el origen
    if not destinos:
        if 0.0 <= presupuesto + _EPS:
            return [_armar_ruta_desde_secuencia([origen], matriz)]
        return []

    candidatas: List[Ruta] = []

    for perm in itertools.permutations(destinos):
        # 1. Validar precedencias secuencialmente
        if precedencias is not None:
            visitados = {origen}
            es_valido = True
            for d in perm:
                if not precedencias.puede_visitar(d, visitados):
                    es_valido = False
                    break
                visitados.add(d)
            if not es_valido:
                continue

        # 2. Formar la secuencia completa
        secuencia = [origen] + list(perm)
        if ida_y_vuelta:
            secuencia.append(origen)

        # 3. Calcular acumulador de dinero y validar presupuesto
        dinero_total = sum(
            matriz.dinero(a, b) for a, b in zip(secuencia, secuencia[1:])
        )
        if dinero_total > presupuesto + _EPS:
            continue

        # 4. Construir Ruta con tramos y métricas completas
        ruta = _armar_ruta_desde_secuencia(secuencia, matriz)
        candidatas.append(ruta)

    # Ordenar por peso total ascendente (y costo como desempate secundario)
    candidatas.sort(key=lambda r: (round(r.peso_total, 9), round(r.costo_total, 4), r.destinos))
    return candidatas[:k]
