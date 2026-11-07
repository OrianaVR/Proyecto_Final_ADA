from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Set


@dataclass
class Restricciones:
    """Restricciones operativas del viaje: orden parcial, presupuesto y límites."""

    precedencias: Dict[int, Set[int]] = field(default_factory=dict)
    presupuesto: float = float("inf")
    max_destinos: int = 12

    def to_dict(self) -> Dict[str, Any]:
        return {
            "precedencias": {k: list(v) for k, v in self.precedencias.items()},
            "presupuesto": self.presupuesto,
            "max_destinos": self.max_destinos,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Restricciones:
        raw_prec = data.get("precedencias", {})
        precedencias_parsed = {
            int(k): set(int(x) for x in v) for k, v in raw_prec.items()
        }
        return cls(
            precedencias=precedencias_parsed,
            presupuesto=float(data.get("presupuesto", float("inf"))),
            max_destinos=int(data.get("max_destinos", 12)),
        )
