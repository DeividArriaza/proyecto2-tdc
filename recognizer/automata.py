"""Extensión real de AFN y construcción CFG → PDA con cima en índice cero."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from .grammar import Gramatica
from .proyecto1.constants import EPSILON
from .proyecto1.errors import AutomataValidationError
from .proyecto1.models import AFN

TransicionesPila = Mapping[tuple[int, str, str], frozenset[tuple[int, tuple[str, ...]]]]


@dataclass(frozen=True, slots=True, kw_only=True)
class AutomataPila(AFN):
    alfabeto_pila: frozenset[str]
    simbolo_inicial_pila: str
    transiciones_pila: TransicionesPila = field(default_factory=dict)
    # Certificado privado de la construcción; no se acepta como opción del constructor.
    _poda_longitud_segura: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        AFN.__post_init__(self)
        if self.transiciones:
            raise AutomataValidationError("Use transiciones_pila; las transiciones AFN deben estar vacías")
        alfabeto = frozenset(self.alfabeto_pila)
        if any(not isinstance(s, str) or not s or s == EPSILON for s in alfabeto):
            raise AutomataValidationError("Símbolos de pila no vacíos y distintos de épsilon")
        if self.simbolo_inicial_pila not in alfabeto:
            raise AutomataValidationError("El fondo debe pertenecer al alfabeto de pila")
        normalizadas = {}
        for (origen, lectura, cima), destinos in self.transiciones_pila.items():
            if origen not in self.estados or cima not in alfabeto:
                raise AutomataValidationError("Origen o cima no declarados")
            if lectura != EPSILON and lectura not in self.alfabeto:
                raise AutomataValidationError("Lectura no declarada")
            congelados = frozenset((destino, tuple(apilar)) for destino, apilar in destinos)
            for destino, apilar in congelados:
                if destino not in self.estados or any(s not in alfabeto for s in apilar):
                    raise AutomataValidationError("Destino o símbolos apilados no declarados")
            if congelados:
                normalizadas[(origen, lectura, cima)] = congelados
        object.__setattr__(self, "alfabeto_pila", alfabeto)
        object.__setattr__(self, "transiciones_pila", MappingProxyType(normalizadas))

    @property
    def poda_longitud_segura(self) -> bool:
        return self._poda_longitud_segura


def construir_pda(gramatica: Gramatica) -> AutomataPila:
    """Construcción de tres estados, válida también con reglas unitarias y vacías."""
    fondo = "Z0"
    while fondo in gramatica.variables | gramatica.terminales:
        fondo += "_"
    transiciones: dict[tuple[int, str, str], set[tuple[int, tuple[str, ...]]]] = {
        (0, EPSILON, fondo): {(1, (gramatica.inicial, fondo))},
        (1, EPSILON, fondo): {(2, (fondo,))},
    }
    for variable, alternativas in gramatica.producciones.items():
        for derecha in alternativas:
            transiciones.setdefault((1, EPSILON, variable), set()).add((1, derecha))
    for terminal in gramatica.terminales:
        transiciones[(1, terminal, terminal)] = {(1, ())}
    pda = AutomataPila(
        estados=frozenset({0, 1, 2}), alfabeto=gramatica.terminales,
        inicial=0, aceptacion=frozenset({2}),
        alfabeto_pila=gramatica.variables | gramatica.terminales | {fondo},
        simbolo_inicial_pila=fondo,
        transiciones_pila={clave: frozenset(destinos) for clave, destinos in transiciones.items()},
    )
    # Sin reglas vacías, ninguna variable puede derivar ε (tampoco mediante reglas unitarias).
    segura = all(regla for alternativas in gramatica.producciones.values() for regla in alternativas)
    object.__setattr__(pda, "_poda_longitud_segura", segura)
    return pda
