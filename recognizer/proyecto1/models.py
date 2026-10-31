# Origen: primer-proyecto-tdc/src/automatas/models.py, commit 750243e.
# Adaptación: únicamente imports automatas.x a .x; sin cambios de lógica.
"""Modelos comunes de autómata finito no determinista y determinista."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from .constants import EPSILON
from .errors import AutomataValidationError

TransicionesAFN = Mapping[tuple[int, str], frozenset[int]]
TransicionesAFD = Mapping[tuple[int, str], int]


def _congelar_estados(estados: Iterable[int]) -> frozenset[int]:
    return frozenset(estados)


def _validar_alfabeto(alfabeto: frozenset[str]) -> None:
    if EPSILON in alfabeto:
        raise AutomataValidationError(
            "El alfabeto no puede contener el símbolo épsilon"
        )
    for simbolo in alfabeto:
        if not simbolo:
            raise AutomataValidationError(
                "El alfabeto no puede contener un símbolo vacío"
            )


def _validar_estados_declarados(
    estados: frozenset[int], inicial: int, aceptacion: frozenset[int]
) -> None:
    if not estados:
        raise AutomataValidationError("El autómata debe tener al menos un estado")
    if inicial not in estados:
        raise AutomataValidationError(
            f"El estado inicial {inicial} no pertenece al conjunto de estados"
        )
    sobrantes = aceptacion - estados
    if sobrantes:
        faltantes = ", ".join(str(estado) for estado in sorted(sobrantes))
        raise AutomataValidationError(
            f"Estados de aceptación inexistentes: {faltantes}"
        )


@dataclass(frozen=True, slots=True)
class AFN:
    """Autómata finito no determinista con transiciones épsilon."""

    estados: frozenset[int]
    alfabeto: frozenset[str]
    inicial: int
    aceptacion: frozenset[int]
    transiciones: TransicionesAFN = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "estados", _congelar_estados(self.estados))
        object.__setattr__(self, "alfabeto", frozenset(self.alfabeto))
        object.__setattr__(self, "aceptacion", _congelar_estados(self.aceptacion))

        _validar_alfabeto(self.alfabeto)
        _validar_estados_declarados(self.estados, self.inicial, self.aceptacion)

        normalizadas: dict[tuple[int, str], frozenset[int]] = {}
        for (origen, simbolo), destinos in self.transiciones.items():
            if origen not in self.estados:
                raise AutomataValidationError(
                    f"La transición parte del estado inexistente {origen}"
                )
            if simbolo != EPSILON and simbolo not in self.alfabeto:
                raise AutomataValidationError(
                    f"El símbolo {simbolo!r} no pertenece al alfabeto"
                )
            congelados = frozenset(destinos)
            ausentes = congelados - self.estados
            if ausentes:
                faltantes = ", ".join(str(estado) for estado in sorted(ausentes))
                raise AutomataValidationError(
                    f"La transición llega a estados inexistentes: {faltantes}"
                )
            if congelados:
                normalizadas[(origen, simbolo)] = congelados

        object.__setattr__(self, "transiciones", MappingProxyType(normalizadas))

    def mover(self, estado: int, simbolo: str) -> frozenset[int]:
        """Devuelve los destinos alcanzables desde un estado con un símbolo."""
        if estado not in self.estados:
            raise AutomataValidationError(f"El estado {estado} no existe")
        return self.transiciones.get((estado, simbolo), frozenset())

    @property
    def simbolos_usados(self) -> frozenset[str]:
        """Símbolos del alfabeto que aparecen en alguna transición."""
        return frozenset(
            simbolo for _, simbolo in self.transiciones if simbolo != EPSILON
        )


@dataclass(frozen=True, slots=True)
class AFD:
    """Autómata finito determinista sin transiciones épsilon."""

    estados: frozenset[int]
    alfabeto: frozenset[str]
    inicial: int
    aceptacion: frozenset[int]
    transiciones: TransicionesAFD = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "estados", _congelar_estados(self.estados))
        object.__setattr__(self, "alfabeto", frozenset(self.alfabeto))
        object.__setattr__(self, "aceptacion", _congelar_estados(self.aceptacion))

        _validar_alfabeto(self.alfabeto)
        _validar_estados_declarados(self.estados, self.inicial, self.aceptacion)

        normalizadas: dict[tuple[int, str], int] = {}
        for (origen, simbolo), destino in self.transiciones.items():
            if origen not in self.estados:
                raise AutomataValidationError(
                    f"La transición parte del estado inexistente {origen}"
                )
            if simbolo == EPSILON:
                raise AutomataValidationError(
                    "Un AFD no admite transiciones épsilon"
                )
            if simbolo not in self.alfabeto:
                raise AutomataValidationError(
                    f"El símbolo {simbolo!r} no pertenece al alfabeto"
                )
            if destino not in self.estados:
                raise AutomataValidationError(
                    f"La transición llega al estado inexistente {destino}"
                )
            normalizadas[(origen, simbolo)] = destino

        object.__setattr__(self, "transiciones", MappingProxyType(normalizadas))

    def mover(self, estado: int, simbolo: str) -> int | None:
        """Devuelve el destino de una transición o ``None`` si no existe."""
        if estado not in self.estados:
            raise AutomataValidationError(f"El estado {estado} no existe")
        return self.transiciones.get((estado, simbolo))

    def es_completo(self) -> bool:
        """Indica si cada estado define una transición por cada símbolo."""
        return all(
            (estado, simbolo) in self.transiciones
            for estado in self.estados
            for simbolo in self.alfabeto
        )
