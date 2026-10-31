"""Pruebas del simulador, de su evidencia y de la seguridad de la poda."""

from collections import deque
from copy import deepcopy
from itertools import product
import json
import unittest

from recognizer.automata import AutomataPila, construir_pda
from recognizer.grammar import G, Gramatica, tokenizar
from recognizer.pda import describir, recognize, validar_recorrido
from recognizer.proyecto1.constants import EPSILON


def pda_externo():
    """PDA manual de aⁿbⁿ, n ≥ 1; no proviene de ninguna gramática."""
    return AutomataPila(
        estados={0, 1, 2}, alfabeto={"a", "b"}, inicial=0, aceptacion={2},
        alfabeto_pila={"Z", "A"}, simbolo_inicial_pila="Z",
        transiciones_pila={
            (0, "a", "Z"): {(0, ("A", "Z"))},
            (0, "a", "A"): {(0, ("A", "A"))},
            (0, "b", "A"): {(1, ())}, (1, "b", "A"): {(1, ())},
            (1, EPSILON, "Z"): {(2, ())},
        },
    )


class PruebasPDA(unittest.TestCase):
    def test_casos_minimos_readme(self):
        aceptadas = [
            "he cooks", "she drinks a beer", "the cat eats the meat with a fork in the oven",
            "a dog cuts she", " \the  cooks\n", "he cooks with she with he in a dog",
        ]
        rechazadas = ["", " \t", "he", "cooks he", "he eats cake", "he cooks with",
                      "he dances", "He cooks", "he cooks."]
        pda = construir_pda(G)
        for frase in aceptadas + rechazadas:
            with self.subTest(frase=frase):
                tokens = tokenizar(frase)
                resultado = recognize(tokens, pda=pda)
                self.assertEqual(resultado.estado, "aceptada" if frase in aceptadas else "rechazada")
                if resultado.estado == "aceptada":
                    recorrido = resultado.evidencia["recorrido_aceptante"]
                    self.assertTrue(validar_recorrido(pda, tokens, recorrido))

    def test_pila_y_lectura_epsilon(self):
        resultado = recognize(["he", "cooks"])
        recorrido = resultado.evidencia["recorrido_aceptante"]
        self.assertEqual(len(recorrido), 7)
        self.assertEqual(recorrido[1]["despues"]["pila"], ["NP", "VP", "Z0"])
        self.assertEqual(recorrido[0]["antes"]["posicion"], recorrido[0]["despues"]["posicion"])
        self.assertEqual(recorrido[-1]["despues"], {"estado": 2, "posicion": 2, "pila": ["Z0"]})
        self.assertEqual(describir(recorrido[-1]["despues"], resultado.tokens), "(q2, ε, Z0)")

    def test_entrada_pendiente_y_ruta_inventada(self):
        pda = construir_pda(G)
        recorrido = recognize(["he", "cooks"], pda=pda).evidencia["recorrido_aceptante"]
        self.assertFalse(validar_recorrido(pda, ["he", "cooks", "he"], recorrido))
        self.assertFalse(validar_recorrido(pda, ["he", "cooks"], recorrido[:-1]))
        self.assertFalse(validar_recorrido(pda, ["he", "cooks"], []))
        for campo, valor in (("destino", 9), ("apilar", ["VP", "NP"]), ("lectura", "he")):
            falsa = deepcopy(recorrido)
            falsa[0]["transicion"][campo] = valor
            self.assertFalse(validar_recorrido(pda, ["he", "cooks"], falsa))
        falsa = deepcopy(recorrido)
        falsa[1]["antes"]["pila"] = ["VP", "Z0"]
        self.assertFalse(validar_recorrido(pda, ["he", "cooks"], falsa))
        self.assertFalse(validar_recorrido(pda, ["he", "cooks"], [{}]))

    def test_desconocidas_y_serializacion(self):
        resultado = recognize(["He", "dances", "He"])
        self.assertEqual(resultado.evidencia["palabras_desconocidas"], ["He", "dances"])
        self.assertEqual(resultado.estado, "rechazada")
        self.assertIn("He, dances", resultado.motivo)
        self.assertEqual(resultado.operaciones["configuraciones_expandidas"], 0)
        self.assertEqual(json.loads(json.dumps(resultado.to_dict()))["n"], 3)

    def test_limite_inconcluso(self):
        resultado = recognize(["he", "cooks"], limite_configuraciones=1)
        self.assertEqual(resultado.estado, "inconclusa")
        self.assertEqual(resultado.evidencia["agotamiento"]["causa"], "limite_alcanzado")
        self.assertEqual(resultado.operaciones["configuraciones_expandidas"], 1)
        self.assertGreater(resultado.evidencia["agotamiento"]["frontera_pendiente"], 0)

    def test_limites_invalidos(self):
        for limite in (0, -1, 1.5, True):
            with self.assertRaises(ValueError):
                recognize([], limite_configuraciones=limite)

    def test_rechazo_por_agotamiento(self):
        resultado = recognize(["he", "eats", "cake"])
        self.assertEqual(resultado.estado, "rechazada")
        self.assertEqual(resultado.evidencia["agotamiento"]["causa"], "frontera_agotada")
        self.assertEqual(resultado.evidencia["agotamiento"]["frontera_pendiente"], 0)
        self.assertTrue(all(r["expandida"] for r in resultado.evidencia["configuraciones"]))

    def test_pda_externo_sin_poda(self):
        pda = pda_externo()
        for texto in ("ab", "aabb", "aaabbb"):
            resultado = recognize(list(texto), pda=pda)
            self.assertEqual(resultado.estado, "aceptada")
            self.assertFalse(resultado.evidencia["poda_longitud"])
            self.assertTrue(validar_recorrido(pda, list(texto), resultado.evidencia["recorrido_aceptante"]))
        for texto in ("", "a", "b", "aab", "abb", "abab"):
            self.assertEqual(recognize(list(texto), pda=pda).estado, "rechazada")
        with self.assertRaises(ValueError):
            recognize(list("ab"), pda=pda, poda_longitud=True)

    def test_cfg_epsilon_y_unitarias(self):
        g = Gramatica({"S", "A"}, {"a"}, {"S": (("A",),), "A": ((), ("a", "A"))}, "S")
        pda = construir_pda(g)
        self.assertFalse(pda.poda_longitud_segura)
        for tokens in ([], ["a"], ["a"] * 3):
            resultado = recognize(tokens, pda=pda, limite_configuraciones=500)
            self.assertEqual(resultado.estado, "aceptada")
            self.assertTrue(validar_recorrido(pda, tokens, resultado.evidencia["recorrido_aceptante"]))
        with self.assertRaises(ValueError):
            recognize([], pda=pda, poda_longitud=True)

    def test_repetidas_y_pilas_distintas(self):
        pda = AutomataPila(
            estados={0, 1}, alfabeto={"a"}, inicial=0, aceptacion={1},
            alfabeto_pila={"Z", "A", "B"}, simbolo_inicial_pila="Z",
            transiciones_pila={
                (0, EPSILON, "Z"): {(0, ("Z",)), (0, ("A",)), (0, ("B",))},
                (0, "a", "B"): {(1, ())},
            },
        )
        resultado = recognize(["a"], pda=pda)
        self.assertEqual(resultado.estado, "aceptada")
        self.assertEqual(resultado.operaciones["repetidas"], 1)
        pilas = [r["configuracion"]["pila"] for r in resultado.evidencia["configuraciones"]]
        self.assertIn(["A"], pilas)
        self.assertIn(["B"], pilas)

    def test_registros_y_contadores_reproducibles(self):
        tokens = ["he", "cooks"]
        primero = recognize(tokens)
        self.assertEqual(primero.to_dict(), recognize(tokens).to_dict())
        registros = primero.evidencia["configuraciones"]
        pda = construir_pda(G)
        for indice, registro in enumerate(registros):
            self.assertEqual(registro["id"], indice)
            if indice:
                padre = registro["padre"]
                self.assertLess(padre, indice)
                t = registro["transicion"]
                self.assertIn((t["destino"], tuple(t["apilar"])),
                              pda.transiciones_pila[(t["origen"], t["lectura"], t["cima"])])
        operaciones = primero.operaciones
        self.assertEqual(operaciones["configuraciones_generadas"], 1 + operaciones["transiciones_evaluadas"])
        self.assertEqual(operaciones["configuraciones_generadas"],
                         len(registros) + operaciones["podas"] + operaciones["repetidas"])
        self.assertEqual(operaciones["configuraciones_expandidas"], sum(r["expandida"] for r in registros))

    def test_poda_contra_derivaciones_cortas(self):
        # Enumeración independiente de derivaciones izquierdas de G, longitud máxima cuatro.
        maximo = 4
        pendientes = deque([("S",)])
        visitadas = {("S",)}
        lenguaje = set()
        while pendientes:
            forma = pendientes.popleft()
            indice = next((i for i, s in enumerate(forma) if s in G.variables), None)
            if indice is None:
                lenguaje.add(forma)
                continue
            for regla in G.producciones[forma[indice]]:
                nueva = forma[:indice] + regla + forma[indice + 1:]
                if len(nueva) <= maximo and nueva not in visitadas:
                    visitadas.add(nueva)
                    pendientes.append(nueva)
        pda = construir_pda(G)
        # Todas las frases derivadas (incluso con vocabulario fuera del alfabeto reducido).
        for tokens in sorted(lenguaje):
            self.assertEqual(recognize(list(tokens), pda=pda).estado, "aceptada", tokens)
        # Todos los candidatos de longitud <= 4 de un alfabeto reducido, incluidos rechazos.
        for n in range(maximo + 1):
            for tokens in product(("he", "cooks", "a", "cat"), repeat=n):
                esperado = "aceptada" if tokens in lenguaje else "rechazada"
                self.assertEqual(recognize(list(tokens), pda=pda).estado, esperado, tokens)

    def test_poda_contra_busqueda_sin_poda_en_aceptaciones(self):
        for frase in ("he cooks", "she drinks a beer", "he cooks with he"):
            con = recognize(tokenizar(frase))
            sin = recognize(tokenizar(frase), poda_longitud=False, limite_configuraciones=10000)
            self.assertEqual(con.estado, sin.estado)
            self.assertEqual(sin.estado, "aceptada")


if __name__ == "__main__":
    unittest.main()
