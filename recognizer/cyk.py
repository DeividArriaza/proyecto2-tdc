"""CYK sobre una gramática CNF; registra tabla, testigos y una derivación aceptante."""

from typing import Any

from .grammar import G, Gramatica, es_cnf
from .resultado import Resultado

# (produccion, corte): corte None en reglas léxicas; longitud izquierda en reglas binarias.
Testigo = tuple[tuple[str, ...], int | None]
Tabla = dict[tuple[int, int], dict[str, Testigo]]

CONTADORES = (
    "celdas", "consultas_lexicas", "cortes", "comprobaciones_binarias",
    "reglas_satisfechas", "variables_agregadas",
)


def _agregar(celda: dict[str, Testigo], variable: str, testigo: Testigo,
             operaciones: dict[str, int]) -> None:
    """Conserva el primer testigo hallado; el orden de los bucles lo hace reproducible."""
    operaciones["reglas_satisfechas"] += 1
    if variable not in celda:
        celda[variable] = testigo
        operaciones["variables_agregadas"] += 1


def _arbol(tabla: Tabla, tokens: list[str], inicio: int, longitud: int,
           variable: str) -> dict[str, Any]:
    produccion, corte = tabla[(inicio, longitud)][variable]
    if corte is None:
        hijos = [{"terminal": tokens[inicio], "posicion": inicio}]
    else:
        hijos = [
            _arbol(tabla, tokens, inicio, corte, produccion[0]),
            _arbol(tabla, tokens, inicio + corte, longitud - corte, produccion[1]),
        ]
    return {"variable": variable, "produccion": list(produccion), "hijos": hijos}


def derivacion_izquierda(arbol: dict[str, Any]) -> list[str]:
    """Formas sentenciales de la derivación izquierda que representa el árbol."""
    forma = [arbol]
    pasos = [arbol["variable"]]
    while True:
        indice = next((i for i, nodo in enumerate(forma) if "variable" in nodo), None)
        if indice is None:
            return pasos
        forma[indice:indice + 1] = forma[indice]["hijos"]
        pasos.append(" ".join(nodo.get("variable", nodo.get("terminal")) for nodo in forma))


def recognize(tokens: list[str], *, gramatica: Gramatica = G) -> Resultado:
    """Llena la tabla completa por longitudes crecientes y acepta si S deriva toda la entrada."""
    if not es_cnf(gramatica):
        raise ValueError("CYK requiere una gramática en CNF estricta")
    tokens = list(tokens)
    n = len(tokens)
    alternativas = [(a, regla) for a, reglas in gramatica.producciones.items() for regla in reglas]
    lexicas = sorted((a, regla) for a, regla in alternativas if len(regla) == 1)
    binarias = sorted((a, regla) for a, regla in alternativas if len(regla) == 2)
    operaciones = dict.fromkeys(CONTADORES, 0)
    tabla: Tabla = {}

    for inicio, token in enumerate(tokens):
        celda = tabla[(inicio, 1)] = {}
        operaciones["celdas"] += 1
        for variable, regla in lexicas:
            operaciones["consultas_lexicas"] += 1
            if regla[0] == token:
                _agregar(celda, variable, (regla, None), operaciones)

    for longitud in range(2, n + 1):
        for inicio in range(n - longitud + 1):
            celda = tabla[(inicio, longitud)] = {}
            operaciones["celdas"] += 1
            for corte in range(1, longitud):
                operaciones["cortes"] += 1
                izquierda = tabla[(inicio, corte)]
                derecha = tabla[(inicio + corte, longitud - corte)]
                for variable, regla in binarias:
                    operaciones["comprobaciones_binarias"] += 1
                    if regla[0] in izquierda and regla[1] in derecha:
                        _agregar(celda, variable, (regla, corte), operaciones)

    final = tabla.get((0, n), {})
    aceptada = gramatica.inicial in final
    desconocidas = sorted(set(tokens) - gramatica.terminales)
    arbol = _arbol(tabla, tokens, 0, n, gramatica.inicial) if aceptada else None
    evidencia = {
        "tabla": [
            {"inicio": i, "longitud": l, "variables": sorted(celda)}
            for (i, l), celda in tabla.items()
        ],
        "testigos": [
            {"inicio": i, "longitud": l, "variable": variable,
             "produccion": list(produccion), "corte": corte}
            for (i, l), celda in tabla.items()
            for variable, (produccion, corte) in sorted(celda.items())
        ],
        "celda_final": {"inicio": 0, "longitud": n, "variables": sorted(final)} if n else None,
        "arbol": arbol,
        "derivacion": derivacion_izquierda(arbol) if arbol else [],
        "palabras_desconocidas": desconocidas,
    }
    if n == 0:
        motivo = "Entrada vacía: tabla vacía y G no deriva ε"
    elif aceptada:
        motivo = f"{gramatica.inicial} está en la celda final (inicio 0, longitud {n})"
    else:
        motivo = f"{gramatica.inicial} no está en la celda final (inicio 0, longitud {n})"
        if desconocidas:
            motivo += "; fuera del alfabeto: " + ", ".join(desconocidas)
    estado = "aceptada" if aceptada else "rechazada"
    return Resultado("cyk", estado, tokens, n, operaciones, evidencia, motivo)
