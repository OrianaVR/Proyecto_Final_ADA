from __future__ import annotations
from typing import Dict, Iterable, List, Optional, Set, Tuple


class CicloPrecedenciasError(Exception):
    """Excepción lanzada cuando existe una contradicción cíclica en las precedencias."""

    def __init__(self, ciclo: List[int], nombres_map: Optional[Dict[int, str]] = None):
        self.ciclo = ciclo
        self.nombres_map = nombres_map or {}
        if nombres_map:
            ciclo_str = " -> ".join(nombres_map.get(nodo, str(nodo)) for nodo in ciclo)
        else:
            ciclo_str = " -> ".join(str(nodo) for nodo in ciclo)
        super().__init__(
            f"Se detectó un ciclo en las precedencias: {ciclo_str}. "
            "Es imposible cumplir el orden solicitado."
        )


class TablaPrecedencias:
    """Gestiona y valida restricciones de orden parcial entre destinos de viaje.
    
    Estructura interna:
        Map<int, Set<int>> / Dict[int, Set[int]] donde
        predecesores[B] = {A} significa estrictamente «A se visita antes que B».
    """

    def __init__(self, precedencias_iniciales: Optional[Dict[int, Set[int]]] = None):
        self._predecesores: Dict[int, Set[int]] = {}
        if precedencias_iniciales:
            for destino, preds in precedencias_iniciales.items():
                self._predecesores[int(destino)] = set(int(p) for p in preds)

    @property
    def predecesores(self) -> Dict[int, Set[int]]:
        """Retorna una vista de la tabla hash de predecesores."""
        return {k: set(v) for k, v in self._predecesores.items()}

    def agregar_precedencia(self, antes: int, despues: int) -> None:
        """Registra la restricción: 'antes' debe ser visitado antes que 'despues'."""
        if despues not in self._predecesores:
            self._predecesores[despues] = set()
        self._predecesores[despues].add(antes)

    def establecer_primero(self, primero: int, todos_los_destinos: Iterable[int]) -> None:
        """Marca 'primero' como el destino que debe visitarse antes de todos los demás."""
        for destino in todos_los_destinos:
            if destino != primero:
                self.agregar_precedencia(antes=primero, despues=destino)

    def puede_visitar(self, destino: int, visitados: Set[int]) -> bool:
        """Validación O(1) en promedio:

        Retorna True si y solo si todos los predecesores requeridos para 'destino'
        ya están contenidos en el conjunto de 'visitados'.
        """
        preds = self._predecesores.get(destino)
        if not preds:
            return True
        return preds.issubset(visitados)

    # Alias camelCase requerido por la especificación y compatibilidad
    def puedeVisitar(self, destino: int, visitados: Set[int]) -> bool:
        return self.puede_visitar(destino, visitados)

    def obtener_predecesores(self, destino: int) -> Set[int]:
        """Retorna los predecesores directos del destino especificado."""
        return set(self._predecesores.get(destino, set()))

    def todos_los_nodos(self) -> Set[int]:
        """Retorna el conjunto de todos los nodos involucrados en alguna precedencia."""
        nodos = set(self._predecesores.keys())
        for preds in self._predecesores.values():
            nodos.update(preds)
        return nodos

    def detectar_ciclo(self) -> Optional[List[int]]:
        """Detecta si existe algún ciclo en las precedencias mediante DFS con colores.
        
        Una arista dirigida u -> v significa que 'u' debe visitarse antes que 'v'
        (es decir, u in predecesores[v]).
        
        Retorna:
            Lista ordenada de IDs que forman el ciclo (ej. [A, B, A]), o None si es un DAG acíclico.
        """
        # Construcción del grafo directo de precedencias: u precede a v -> u -> v
        adj: Dict[int, List[int]] = {}
        for nodo in self.todos_los_nodos():
            adj[nodo] = []

        for v, preds in self._predecesores.items():
            for u in preds:
                if u not in adj:
                    adj[u] = []
                adj[u].append(v)

        # Estados de visita: 0: NO_VISITADO, 1: VISITANDO (en pila), 2: VISITADO
        estado: Dict[int, int] = {nodo: 0 for nodo in adj}
        padre: Dict[int, Optional[int]] = {nodo: None for nodo in adj}
        ciclo_encontrado: List[int] = []

        def dfs(u: int, camino_actual: List[int]) -> bool:
            estado[u] = 1  # VISITANDO
            camino_actual.append(u)

            for v in adj.get(u, []):
                if v == u:
                    # Bucle a sí mismo (A antes que A)
                    ciclo_encontrado.extend([u, u])
                    return True

                if estado.get(v, 0) == 1:
                    # Encontrada arista de retroceso: ciclo detectado
                    idx = camino_actual.index(v)
                    ciclo_encontrado.extend(camino_actual[idx:] + [v])
                    return True
                elif estado.get(v, 0) == 0:
                    padre[v] = u
                    if dfs(v, camino_actual):
                        return True

            camino_actual.pop()
            estado[u] = 2  # VISITADO
            return False

        for nodo in sorted(adj.keys()):
            if estado.get(nodo, 0) == 0:
                if dfs(nodo, []):
                    return ciclo_encontrado

        return None

    def validar_sin_ciclos(self, nombres_map: Optional[Dict[int, str]] = None) -> None:
        """Verifica que no existan ciclos. Si se detecta alguno, lanza CicloPrecedenciasError."""
        ciclo = self.detectar_ciclo()
        if ciclo is not None:
            raise CicloPrecedenciasError(ciclo, nombres_map)

    def validar_secuencia(
        self, secuencia: List[int], nombres_map: Optional[Dict[int, str]] = None
    ) -> Tuple[bool, Optional[str]]:
        """Verifica si una secuencia ordenada de visitas cumple con todas las precedencias.
        
        Retorna:
            (True, None) si la secuencia es válida.
            (False, "mensaje de error") si alguna precedencia es violada.
        """
        visitados: Set[int] = set()
        posicion = {nodo: idx for idx, nodo in enumerate(secuencia)}

        for nodo in secuencia:
            preds = self._predecesores.get(nodo, set())
            for p in preds:
                if p in posicion and p not in visitados:
                    nom_p = nombres_map.get(p, str(p)) if nombres_map else str(p)
                    nom_nodo = nombres_map.get(nodo, str(nodo)) if nombres_map else str(nodo)
                    return (
                        False,
                        f"La secuencia viola la precedencia: {nom_p} debe visitarse antes que {nom_nodo}.",
                    )
            visitados.add(nodo)

        return True, None

    def limpiar(self) -> None:
        """Elimina todas las restricciones de precedencia registradas."""
        self._predecesores.clear()
