"""Gramática inmutable; cada alternativa cuenta como una producción."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from .proyecto1.constants import EPSILON


@dataclass(frozen=True, slots=True)
class Gramatica:
    variables: frozenset[str]
    terminales: frozenset[str]
    producciones: Mapping[str, tuple[tuple[str, ...], ...]]
    inicial: str

    def __post_init__(self) -> None:
        variables = frozenset(self.variables)
        terminales = frozenset(self.terminales)
        if self.inicial not in variables:
            raise ValueError("El símbolo inicial debe ser una variable")
        if variables & terminales or EPSILON in variables | terminales:
            raise ValueError("Alfabetos disjuntos y sin épsilon explícito; use () para una regla vacía")
        if any(not isinstance(s, str) or not s for s in variables | terminales):
            raise ValueError("Los símbolos deben ser cadenas no vacías")
        reglas = {}
        for variable, alternativas in self.producciones.items():
            if variable not in variables:
                raise ValueError("Lado izquierdo no declarado")
            normalizadas = tuple(tuple(derecha) for derecha in alternativas)
            if any(s not in variables | terminales for regla in normalizadas for s in regla):
                raise ValueError("Símbolo no declarado en una producción")
            reglas[variable] = normalizadas
        object.__setattr__(self, "variables", variables)
        object.__setattr__(self, "terminales", terminales)
        object.__setattr__(self, "producciones", MappingProxyType(reglas))


def tokenizar(cadena: str) -> list[str]:
    """Separa cualquier espacio en blanco; conserva mayúsculas y puntuación."""
    return cadena.split()


def es_cnf(gramatica: Gramatica) -> bool:
    """CNF estricta: A → BC o A → a; no incluye la excepción S → ε."""
    return all(
        (len(regla) == 1 and regla[0] in gramatica.terminales)
        or (len(regla) == 2 and all(s in gramatica.variables for s in regla))
        for alternativas in gramatica.producciones.values()
        for regla in alternativas
    )


_VERBOS = ("cooks", "drinks", "eats", "cuts")
_NOMBRES = ("cat", "dog", "beer", "cake", "juice", "meat", "soup", "fork", "knife", "oven", "spoon")

G = Gramatica(
    variables=frozenset({"S", "VP", "PP", "NP", "V", "P", "N", "Det"}),
    terminales=frozenset(_VERBOS + _NOMBRES + ("he", "she", "in", "with", "a", "the")),
    producciones={
        "S": (("NP", "VP"),),
        "VP": (("VP", "PP"), ("V", "NP")) + tuple((v,) for v in _VERBOS),
        "PP": (("P", "NP"),),
        "NP": (("Det", "N"), ("he",), ("she",)),
        "V": tuple((v,) for v in _VERBOS),
        "P": (("in",), ("with",)),
        "N": tuple((n,) for n in _NOMBRES),
        "Det": (("a",), ("the",)),
    },
    inicial="S",
)
