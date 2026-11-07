from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class Entrada:
    """Parámetros de entrada proporcionados por el usuario para planificar el viaje."""

    origen: int
    destinos: List[int]
    presupuesto: float
    k: int = 10
    ida_y_vuelta: bool = False
    alfa: float = 0.5
    beta: float = 0.5
    precedencias: Dict[int, Set[int]] = field(default_factory=dict)
    secuencia_orden: Optional[List[int]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "origen": self.origen,
            "destinos": list(self.destinos),
            "presupuesto": self.presupuesto,
            "k": self.k,
            "ida_y_vuelta": self.ida_y_vuelta,
            "alfa": self.alfa,
            "beta": self.beta,
            "precedencias": {k: list(v) for k, v in self.precedencias.items()},
            "secuencia_orden": list(self.secuencia_orden) if self.secuencia_orden is not None else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Entrada:
        raw_prec = data.get("precedencias", {})
        precedencias_parsed = {
            int(k): set(int(x) for x in v) for k, v in raw_prec.items()
        }
        secuencia = data.get("secuencia_orden")
        return cls(
            origen=int(data["origen"]),
            destinos=[int(d) for d in data.get("destinos", [])],
            presupuesto=float(data["presupuesto"]),
            k=int(data.get("k", 10)),
            ida_y_vuelta=bool(data.get("ida_y_vuelta", False)),
            alfa=float(data.get("alfa", 0.5)),
            beta=float(data.get("beta", 0.5)),
            precedencias=precedencias_parsed,
            secuencia_orden=[int(x) for x in secuencia] if secuencia is not None else None,
        )
