from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class Destino:
    """Representa una ciudad o destino en el sistema TravelPath."""

    id: int
    nombre: str
    alias: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "alias": self.alias,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Destino:
        return cls(
            id=int(data["id"]),
            nombre=str(data["nombre"]),
            alias=str(data.get("alias", "")),
        )

    def __str__(self) -> str:
        return f"{self.nombre} (ID: {self.id})"
