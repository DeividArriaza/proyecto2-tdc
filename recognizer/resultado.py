"""Resultado común, independiente de los algoritmos de reconocimiento."""

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


@dataclass(slots=True)
class Resultado:
    metodo: Literal["pda", "cyk"]
    estado: Literal["aceptada", "rechazada", "inconclusa"]
    tokens: list[str]
    n: int
    operaciones: dict[str, int] = field(default_factory=dict)
    evidencia: dict[str, Any] = field(default_factory=dict)
    motivo: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Copia independiente compuesta por valores serializables a JSON."""
        return asdict(self)
