from __future__ import annotations
import json
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

from lib.models.destino import Destino


class ErrorCargaDatos(Exception):
    """Excepción base para errores al cargar datos de destinos."""
    pass


class DestinosRepository:
    """Repositorio responsable de cargar y validar la matriz fuente de destinos."""

    DEFAULT_ASSET_PATH = Path(__file__).resolve().parent.parent.parent / "assets" / "destinos.json"

    @classmethod
    def resolver_ruta(cls, ruta: Optional[str | Path] = None) -> Path:
        """Resuelve la ruta del archivo JSON, buscando la predeterminada si no se especifica."""
        if ruta is None:
            if cls.DEFAULT_ASSET_PATH.exists():
                return cls.DEFAULT_ASSET_PATH
            # Intento de búsqueda alternativa en el directorio de trabajo actual
            cwd_path = Path.cwd() / "assets" / "destinos.json"
            if cwd_path.exists():
                return cwd_path
            return cls.DEFAULT_ASSET_PATH
        return Path(ruta)

    @classmethod
    def cargar(
        cls, ruta: Optional[str | Path] = None, min_destinos: int = 8, max_destinos: int = 10
    ) -> Tuple[List[Destino], List[List[float]], List[List[float]]]:
        """Carga y valida el archivo JSON de destinos.
        
        Retorna:
            (destinos, matriz_costo, matriz_tiempo)
            
        Lanza:
            ErrorCargaDatos si el formato, dimensiones o valores no cumplen los criterios.
        """
        path = cls.resolver_ruta(ruta)
        if not path.exists():
            raise ErrorCargaDatos(f"No se encontró el archivo de datos en: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise ErrorCargaDatos(f"Error al parsear el archivo JSON: {e}")

        return cls.validar_y_procesar(data, min_destinos=min_destinos, max_destinos=max_destinos)

    @classmethod
    def validar_y_procesar(
        cls, data: Dict[str, Any], min_destinos: int = 8, max_destinos: int = 10
    ) -> Tuple[List[Destino], List[List[float]], List[List[float]]]:
        """Valida las reglas de negocio de la matriz fuente."""
        for campo in ["destinos", "costo", "tiempo"]:
            if campo not in data:
                raise ErrorCargaDatos(f"El archivo JSON carece del campo obligatorio '{campo}'.")

        raw_destinos = data["destinos"]
        raw_costo = data["costo"]
        raw_tiempo = data["tiempo"]

        if not isinstance(raw_destinos, list):
            raise ErrorCargaDatos("El campo 'destinos' debe ser una lista.")
        if not isinstance(raw_costo, list):
            raise ErrorCargaDatos("El campo 'costo' debe ser una matriz (lista de listas).")
        if not isinstance(raw_tiempo, list):
            raise ErrorCargaDatos("El campo 'tiempo' debe ser una matriz (lista de listas).")

        n = len(raw_destinos)
        if not (min_destinos <= n <= max_destinos):
            raise ErrorCargaDatos(
                f"El archivo contiene {n} ciudades. Debe contener entre {min_destinos} y {max_destinos} ciudades."
            )

        nombres_vistos = set()
        destinos: List[Destino] = []
        for i, nombre in enumerate(raw_destinos):
            if not isinstance(nombre, str) or not nombre.strip():
                raise ErrorCargaDatos(f"El destino en el índice {i} no es un nombre válido.")
            nombre_limpio = nombre.strip()
            if nombre_limpio in nombres_vistos:
                raise ErrorCargaDatos(f"Destino duplicado encontrado: '{nombre_limpio}'.")
            nombres_vistos.add(nombre_limpio)
            destinos.append(Destino(id=i, nombre=nombre_limpio))

        # Validación de dimensiones cuadradas de costo
        if len(raw_costo) != n:
            raise ErrorCargaDatos(
                f"La matriz 'costo' tiene {len(raw_costo)} filas, pero hay {n} destinos."
            )
        matriz_costo: List[List[float]] = []
        for i, fila in enumerate(raw_costo):
            if not isinstance(fila, list) or len(fila) != n:
                raise ErrorCargaDatos(
                    f"Fila {i} de 'costo' tiene dimensión inválida (esperada: {n})."
                )
            fila_flotantes: List[float] = []
            for j, val in enumerate(fila):
                try:
                    num = float(val)
                except (ValueError, TypeError):
                    raise ErrorCargaDatos(f"Valor no numérico en costo[{i}][{j}]: {val}")
                if i == j and num != 0:
                    raise ErrorCargaDatos(f"La diagonal costo[{i}][{i}] debe ser 0, se encontró: {num}")
                if i != j and num < 0:
                    raise ErrorCargaDatos(f"Costo negativo no permitido en costo[{i}][{j}]: {num}")
                fila_flotantes.append(num)
            matriz_costo.append(fila_flotantes)

        # Validación de dimensiones cuadradas de tiempo
        if len(raw_tiempo) != n:
            raise ErrorCargaDatos(
                f"La matriz 'tiempo' tiene {len(raw_tiempo)} filas, pero hay {n} destinos."
            )
        matriz_tiempo: List[List[float]] = []
        for i, fila in enumerate(raw_tiempo):
            if not isinstance(fila, list) or len(fila) != n:
                raise ErrorCargaDatos(
                    f"Fila {i} de 'tiempo' tiene dimensión inválida (esperada: {n})."
                )
            fila_flotantes = []
            for j, val in enumerate(fila):
                try:
                    num = float(val)
                except (ValueError, TypeError):
                    raise ErrorCargaDatos(f"Valor no numérico en tiempo[{i}][{j}]: {val}")
                if i == j and num != 0:
                    raise ErrorCargaDatos(f"La diagonal tiempo[{i}][{i}] debe ser 0, se encontró: {num}")
                if i != j and num < 0:
                    raise ErrorCargaDatos(f"Tiempo negativo no permitido en tiempo[{i}][{j}]: {num}")
                fila_flotantes.append(num)
            matriz_tiempo.append(fila_flotantes)

        return destinos, matriz_costo, matriz_tiempo
