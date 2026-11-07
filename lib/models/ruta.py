from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List
from lib.models.arista import Arista


@dataclass
class Ruta:
    """Representa un itinerario o ruta completa encontrada.
    
    IMPORTANTE: Separa de manera estricta el acumulador de peso combinado
    (peso_total, adimensional, utilizado únicamente para optimizar el orden)
    del acumulador de costo real (costo_total, en pesos, utilizado para el presupuesto).
    """

    destinos: List[int]
    peso_total: float
    costo_total: float
    tiempo_total: float
    tramos: List[Arista] = field(default_factory=list)
    ciudades_paso: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "destinos": list(self.destinos),
            "peso_total": self.peso_total,
            "costo_total": self.costo_total,
            "tiempo_total": self.tiempo_total,
            "tramos": [t.to_dict() for t in self.tramos],
            "ciudades_paso": list(self.ciudades_paso),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Ruta:
        return cls(
            destinos=[int(d) for d in data.get("destinos", [])],
            peso_total=float(data.get("peso_total", 0.0)),
            costo_total=float(data.get("costo_total", 0.0)),
            tiempo_total=float(data.get("tiempo_total", 0.0)),
            tramos=[Arista.from_dict(t) for t in data.get("tramos", [])],
            ciudades_paso=[int(c) for c in data.get("ciudades_paso", [])],
        )

    def __str__(self) -> str:
        ciudades_str = " -> ".join(map(str, self.destinos))
        return (
            f"Ruta([{ciudades_str}] | Peso: {self.peso_total:.4f}, "
            f"Costo: ${self.costo_total:.2f}, Tiempo: {self.tiempo_total:.1f}h)"
        )
