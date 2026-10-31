"""Exploración BFS de un PDA dado, sin producciones codificadas en el simulador."""

from collections import deque
from typing import Any

from .automata import AutomataPila, construir_pda
from .grammar import G
from .proyecto1.constants import EPSILON
from .resultado import Resultado

Configuracion = tuple[int, int, tuple[str, ...]]


def _configuracion(configuracion: Configuracion) -> dict[str, Any]:
    estado, posicion, pila = configuracion
    return {"estado": estado, "posicion": posicion, "pila": list(pila)}


def describir(configuracion: dict[str, Any], tokens: list[str]) -> str:
    pendiente = " ".join(tokens[configuracion["posicion"]:]) or EPSILON
    pila = " ".join(configuracion["pila"]) or EPSILON
    return f"(q{configuracion['estado']}, {pendiente}, {pila})"


def validar_recorrido(
    pda: AutomataPila, tokens: list[str], recorrido: list[dict[str, Any]]
) -> bool:
    """Comprueba inicio, continuidad, transiciones, pila y aceptación con consumo total."""
    actual = (pda.inicial, 0, (pda.simbolo_inicial_pila,))
    if any(token not in pda.alfabeto for token in tokens):
        return False
    try:
        for paso in recorrido:
            if paso["antes"] != _configuracion(actual):
                return False
            estado, posicion, pila = actual
            transicion = paso["transicion"]
            lectura = transicion["lectura"]
            destino = transicion["destino"]
            apilar = tuple(transicion["apilar"])
            if not pila or transicion["origen"] != estado or transicion["cima"] != pila[0]:
                return False
            destinos = pda.transiciones_pila.get((estado, lectura, pila[0]), frozenset())
            if (destino, apilar) not in destinos:
                return False
            if lectura != EPSILON:
                if posicion >= len(tokens) or tokens[posicion] != lectura:
                    return False
                posicion += 1
            actual = (destino, posicion, apilar + pila[1:])
            if paso["despues"] != _configuracion(actual):
                return False
    except (KeyError, TypeError, ValueError, IndexError):
        return False
    return actual[0] in pda.aceptacion and actual[1] == len(tokens)


def recognize(
    tokens: list[str], *, pda: AutomataPila | None = None,
    poda_longitud: bool | None = None, limite_configuraciones: int | None = None,
) -> Resultado:
    """None elige la poda certificada; True exige certificado; el límite cuenta expansiones."""
    if limite_configuraciones is not None and (
        isinstance(limite_configuraciones, bool)
        or not isinstance(limite_configuraciones, int) or limite_configuraciones <= 0
    ):
        raise ValueError("El límite de configuraciones debe ser un entero positivo")
    if pda is None:
        pda = construir_pda(G)
    if poda_longitud is True and not pda.poda_longitud_segura:
        raise ValueError("La poda de longitud no está certificada para este PDA")
    usar_poda = pda.poda_longitud_segura if poda_longitud is None else poda_longitud
    tokens = list(tokens)
    n = len(tokens)
    operaciones = dict.fromkeys((
        "configuraciones_generadas", "configuraciones_expandidas", "transiciones_evaluadas",
        "consultas_transiciones", "simbolos_copiados_pila", "podas", "repetidas",
    ), 0)
    evidencia: dict[str, Any] = {
        "configuraciones": [], "recorrido_aceptante": [], "agotamiento": None,
        "poda_longitud": usar_poda, "limite_configuraciones": limite_configuraciones,
        "palabras_desconocidas": sorted(set(tokens) - pda.alfabeto),
    }

    def resultado(estado: str, motivo: str, causa: str | None = None) -> Resultado:
        if causa is not None:
            evidencia["agotamiento"] = {
                "causa": causa, "exploradas": operaciones["configuraciones_expandidas"],
                "podadas": operaciones["podas"], "repetidas": operaciones["repetidas"],
                "frontera_pendiente": len(frontera),
            }
        return Resultado("pda", estado, tokens, n, operaciones, evidencia, motivo)

    frontera: deque[int] = deque()
    if evidencia["palabras_desconocidas"]:
        palabras = ", ".join(evidencia["palabras_desconocidas"])
        return resultado("rechazada", f"Palabras fuera del alfabeto: {palabras}", "fuera_del_alfabeto")
    inicial = (pda.inicial, 0, (pda.simbolo_inicial_pila,))
    configuraciones: list[Configuracion] = [inicial]
    visitados = {inicial}
    registros = evidencia["configuraciones"]
    registros.append({"id": 0, "padre": None, "transicion": None,
                      "configuracion": _configuracion(inicial), "expandida": False})
    frontera.append(0)
    operaciones["configuraciones_generadas"] = 1
    operaciones["simbolos_copiados_pila"] = 1
    while frontera:
        identificador = frontera[0]
        estado, posicion, pila = configuraciones[identificador]
        if estado in pda.aceptacion and posicion == n:
            pasos = []
            while registros[identificador]["padre"] is not None:
                registro = registros[identificador]
                padre = registro["padre"]
                pasos.append({
                    "antes": registros[padre]["configuracion"],
                    "transicion": registro["transicion"], "despues": registro["configuracion"],
                })
                identificador = padre
            evidencia["recorrido_aceptante"] = list(reversed(pasos))
            return resultado("aceptada", "Estado final alcanzado con toda la entrada consumida")
        if limite_configuraciones is not None:
            if operaciones["configuraciones_expandidas"] >= limite_configuraciones:
                return resultado("inconclusa", "Límite de configuraciones alcanzado", "limite_alcanzado")
        frontera.popleft()
        registros[identificador]["expandida"] = True
        operaciones["configuraciones_expandidas"] += 1
        if not pila:
            continue
        lecturas = [EPSILON]
        if posicion < n:
            lecturas.append(tokens[posicion])
        for lectura in lecturas:
            operaciones["consultas_transiciones"] += 1
            destinos = pda.transiciones_pila.get((estado, lectura, pila[0]), frozenset())
            for destino, apilar in sorted(destinos):
                operaciones["transiciones_evaluadas"] += 1
                nueva_pila = apilar + pila[1:]
                # Cuenta las referencias copiadas por el corte y la concatenación de tuplas.
                operaciones["simbolos_copiados_pila"] += len(pila) - 1 + len(nueva_pila)
                nueva_posicion = posicion + (lectura != EPSILON)
                nueva = (destino, nueva_posicion, nueva_pila)
                operaciones["configuraciones_generadas"] += 1
                if usar_poda and len(nueva_pila) - 1 > n - nueva_posicion:
                    operaciones["podas"] += 1
                    continue
                if nueva in visitados:
                    operaciones["repetidas"] += 1
                    continue
                visitados.add(nueva)
                nuevo_id = len(configuraciones)
                configuraciones.append(nueva)
                registros.append({
                    "id": nuevo_id, "padre": identificador,
                    "configuracion": _configuracion(nueva), "expandida": False,
                    "transicion": {"origen": estado, "lectura": lectura, "cima": pila[0],
                                   "destino": destino, "apilar": list(apilar)},
                })
                frontera.append(nuevo_id)
    return resultado("rechazada", "Frontera agotada sin aceptación", "frontera_agotada")
