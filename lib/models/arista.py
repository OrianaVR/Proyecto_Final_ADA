from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class Arista:
    """Representa la conexión dirigida o tramo entre dos destinos.
    
    Separa explícitamente el costo real (dinero), el tiempo de viaje
    y el peso combinado normalizado.
    """

    origen: int
    destino: int
    costo: float
    tiempo: float
    peso: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "origen": self.origen,
            "destino": self.destino,
            "costo": self.costo,
            "tiempo": self.tiempo,
            "peso": self.peso,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Arista:
        return cls(
            origen=int(data["origen"]),
            destino=int(data["destino"]),
            costo=float(data["costo"]),
            tiempo=float(data["tiempo"]),
            peso=float(data.get("peso", 0.0)),
        )

    def __str__(self) -> str:
        return (
            f"Tramo({self.origen} -> {self.destino} | "
            f"Costo: ${self.costo:.2f}, Tiempo: {self.tiempo:.1f}h, Peso: {self.peso:.4f})"
        )
