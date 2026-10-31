# Origen: primer-proyecto-tdc/src/automatas/constants.py, commit 750243e.
# Adaptación: únicamente imports automatas.x a .x; sin cambios de lógica.
EPSILON = "ε"
ALIAS_EPSILON = "~"

UNION = "|"
CONCATENACION = "."
CERRADURA_KLEENE = "*"
UNA_O_MAS = "+"
CERO_O_UNA = "?"

OPERADORES_BINARIOS = frozenset({UNION, CONCATENACION})
OPERADORES_UNARIOS = frozenset({CERRADURA_KLEENE, UNA_O_MAS, CERO_O_UNA})
OPERADORES = OPERADORES_BINARIOS | OPERADORES_UNARIOS
